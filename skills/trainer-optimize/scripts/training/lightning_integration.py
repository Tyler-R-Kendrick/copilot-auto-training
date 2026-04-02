from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotInferenceProvider


def _usage_to_prompt_tokens(usage: dict[str, Any] | None) -> int:
    if not usage:
        return 0
    value = usage.get("prompt_tokens", 0)
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _usage_to_completion_tokens(usage: dict[str, Any] | None, text: str) -> int:
    if not usage:
        return _estimate_tokens_from_text(text)
    value = usage.get("completion_tokens", usage.get("output_tokens", 0))
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return _estimate_tokens_from_text(text)


def _estimate_tokens_from_text(text: str) -> int:
    """Fallback heuristic when the provider does not return token usage."""
    return max(1, len(text) // 4) if text else 0


def _estimate_prompt_tokens(messages: list[dict[str, Any]]) -> int:
    return sum(_estimate_tokens_from_text(str(message.get("content", ""))) for message in messages if message.get("content"))


def _as_choice_message(text: str) -> Any:
    return SimpleNamespace(message=SimpleNamespace(content=text))


class _ProviderResponses:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self._client = client

    async def create(self, *, model: str, input: str, metadata: dict[str, Any] | None = None) -> Any:
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
    ) -> Any:
        return await self._client._chat_completions_create(model=model, messages=messages, metadata=metadata)


class _ProviderChat:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self.completions = _ProviderChatCompletions(client)


class ProviderBackedOpenAIClient:
    def __init__(
        self,
        provider: CopilotInferenceProvider,
        *,
        default_model: str,
    ):
        self.provider = provider
        self.default_model = default_model
        self.responses = _ProviderResponses(self)
        self.chat = _ProviderChat(self)

    async def judge_score(self, rendered_prompt: str) -> float:
        result = await self.provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": rendered_prompt}],
                model=self.default_model,
                metadata={"interaction": "judge_score"},
            )
        )
        for token in result.text.replace(",", " ").split():
            try:
                score = float(token)
            except ValueError:
                continue
            if 0.0 <= score <= 1.0:
                return score
        raise ValueError("Copilot judge response must include a score between 0.0 and 1.0")

    async def _responses_create(
        self,
        *,
        model: str,
        input_text: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
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
        prompt_tokens = _estimate_prompt_tokens(messages)
        usage = dict(result.usage or {})
        usage.setdefault("prompt_tokens", _usage_to_prompt_tokens(result.usage) or prompt_tokens)
        usage.setdefault("completion_tokens", _usage_to_completion_tokens(result.usage, result.text))
        usage.setdefault("total_tokens", usage["prompt_tokens"] + usage["completion_tokens"])
        return SimpleNamespace(
            choices=[_as_choice_message(result.text)],
            usage=SimpleNamespace(
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                total_tokens=usage["total_tokens"],
            ),
            raw=result.raw,
            finish_reason=result.finish_reason,
        )


def build_runtime_client(
    model_settings: dict[str, Any],
    *,
    provider_config: InferenceConfig,
) -> tuple[ProviderBackedOpenAIClient, dict[str, Any]]:
    provider = CopilotInferenceProvider(provider_config, model_settings=model_settings)
    client = ProviderBackedOpenAIClient(provider, default_model=str(model_settings["inference_model"]))
    return client, model_settings
