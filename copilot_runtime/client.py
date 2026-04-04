from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from types import SimpleNamespace
from typing import Any

from tokenizers.pre_tokenizers import ByteLevel
try:
    from openai.types import CompletionUsage
except ImportError:  # pragma: no cover - exercised by test stubs that replace openai
    class CompletionUsage(SimpleNamespace):
        def __init__(self, *, prompt_tokens: int, completion_tokens: int, total_tokens: int):
            super().__init__(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            )

        def model_dump(self, *, exclude_none: bool = False) -> dict[str, int]:
            _ = exclude_none
            return {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            }

from .contract import InferenceRequest
from .provider import CopilotInferenceProvider
from .types import InferenceConfig

@lru_cache(maxsize=None)
def _pretokenizer() -> ByteLevel:
    """Cache the shared ByteLevel pre-tokenizer used for offline token-count estimates."""
    return ByteLevel(add_prefix_space=False, use_regex=True)


def estimate_tokens_from_text(text: str, *, model: str | None = None) -> int:
    """Return a library-derived token estimate for text."""
    _ = model
    if not text:
        return 0
    return len(_pretokenizer().pre_tokenize_str(text))


def _coerce_usage_mapping(usage: Any) -> Mapping[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, CompletionUsage):
        return usage.model_dump(exclude_none=True)
    if isinstance(usage, Mapping):
        return usage
    if hasattr(usage, "model_dump"):
        dumped = usage.model_dump(exclude_none=True)
        if isinstance(dumped, Mapping):
            return dumped
    return {
        key: value
        for key in ("prompt_tokens", "completion_tokens", "output_tokens", "total_tokens")
        if (value := getattr(usage, key, None)) is not None
    }


def _coerce_usage_int(value: Any) -> int | None:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return None


def build_completion_usage(
    usage: Any,
    *,
    messages: list[dict[str, Any]],
    text: str,
    model: str | None = None,
) -> CompletionUsage:
    usage_mapping = _coerce_usage_mapping(usage)
    prompt_tokens = _coerce_usage_int(usage_mapping.get("prompt_tokens"))
    completion_tokens = _coerce_usage_int(usage_mapping.get("completion_tokens"))
    if completion_tokens is None:
        completion_tokens = _coerce_usage_int(usage_mapping.get("output_tokens"))

    resolved_prompt_tokens = prompt_tokens if prompt_tokens is not None else estimate_prompt_tokens(messages, model=model)
    resolved_completion_tokens = (
        completion_tokens if completion_tokens is not None else estimate_tokens_from_text(text, model=model)
    )
    total_tokens = _coerce_usage_int(usage_mapping.get("total_tokens"))
    resolved_total_tokens = (
        total_tokens if total_tokens is not None else resolved_prompt_tokens + resolved_completion_tokens
    )

    return CompletionUsage(
        prompt_tokens=resolved_prompt_tokens,
        completion_tokens=resolved_completion_tokens,
        total_tokens=resolved_total_tokens,
    )


def estimate_prompt_tokens(messages: list[dict[str, Any]], *, model: str | None = None) -> int:
    return sum(
        estimate_tokens_from_text(str(message["content"]), model=model)
        for message in messages
        if isinstance(message.get("content"), str) and message["content"]
    )


def _as_choice_message(text: str) -> Any:
    return SimpleNamespace(message=SimpleNamespace(content=text))


class _ProviderResponses:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self._client = client

    async def create(self, *, model: str, input: str, metadata: dict[str, Any] | None = None, **_unused: Any) -> Any:
        return await self._client._responses_create(model=model, input_text=input, metadata=metadata)


class _ProviderChatCompletions:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self._client = client

    async def create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
        **_unused: Any,
    ) -> Any:
        return await self._client._chat_completions_create(model=model, messages=messages, metadata=metadata)


class _ProviderChat:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self.completions = _ProviderChatCompletions(client)


class ProviderBackedOpenAIClient:
    def __init__(self, provider: CopilotInferenceProvider, *, default_model: str):
        self.provider = provider
        self.default_model = default_model
        self.responses = _ProviderResponses(self)
        self.chat = _ProviderChat(self)

    async def _responses_create(self, *, model: str, input_text: str, metadata: dict[str, Any] | None = None) -> Any:
        result = await self.provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": input_text}],
                model=model or self.default_model,
                metadata={"interaction": "responses.create", **(metadata or {})},
            )
        )
        return SimpleNamespace(
            output_text=result.text,
            usage=result.usage,
            raw=result.raw,
            finish_reason=result.finish_reason,
        )

    async def _chat_completions_create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        result = await self.provider.generate(
            InferenceRequest(
                messages=messages,
                model=model or self.default_model,
                metadata={"interaction": "chat.completions.create", **(metadata or {})},
            )
        )
        usage = build_completion_usage(result.usage, messages=messages, text=result.text, model=model or self.default_model)
        return SimpleNamespace(
            choices=[_as_choice_message(result.text)],
            usage=usage,
            raw=result.raw,
            finish_reason=result.finish_reason,
        )


def build_runtime_client(
    model_settings: dict[str, Any],
    *,
    provider_config: InferenceConfig,
) -> tuple[ProviderBackedOpenAIClient, dict[str, Any]]:
    provider = CopilotInferenceProvider(provider_config, model_settings=model_settings)
    client = ProviderBackedOpenAIClient(provider, default_model=str(model_settings["model"]))
    return client, model_settings
