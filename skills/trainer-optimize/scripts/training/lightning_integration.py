"""AgentLightning-facing client adapters for trainer-optimize.

This module is the bridge between the Copilot-backed inference provider and the
OpenAI-shaped client surface consumed by ``agentlightning.APO`` and
``agentlightning.VERL`` in ``run_optimize.py``. The core integration contract
is that ``run_optimize`` receives a ``ProviderBackedOpenAIClient`` from this
module and passes that concrete client into AgentLightning algorithms.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any
import sys

_MODULE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _MODULE_DIR.parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from copilot_runtime.client import build_completion_usage
from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotInferenceProvider

def _as_choice_message(text: str) -> Any:
    return SimpleNamespace(message=SimpleNamespace(content=text))


class _ProviderResponses:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self._client = client

    async def create(
        self,
        *,
        model: str,
        input: str,
        metadata: dict[str, Any] | None = None,
        **_unused: Any,
    ) -> Any:
        # Some OpenAI-compatible callers pass extra kwargs (for example temperature
        # or max_tokens) that the Copilot-backed provider does not use. Accept and
        # ignore them here so those callers remain compatible with this wrapper.
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
        # Keep parity with OpenAI-shaped call sites that may forward unsupported
        # kwargs such as temperature, max_tokens, or tools. The Copilot-backed
        # provider only consumes model, messages, and metadata.
        return await self._client._chat_completions_create(model=model, messages=messages, metadata=metadata)


class _ProviderChat:
    def __init__(self, client: "ProviderBackedOpenAIClient"):
        self.completions = _ProviderChatCompletions(client)


class ProviderBackedOpenAIClient:
    """OpenAI-compatible client passed directly into AgentLightning algorithms."""

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
    """Build the AgentLightning client returned by ``config.create_openai_client``.

    The returned ``ProviderBackedOpenAIClient`` is the concrete client instance
    passed into ``agl.APO`` and ``agl.VERL`` by ``run_optimize``.
    """

    provider = CopilotInferenceProvider(provider_config, model_settings=model_settings)
    client = ProviderBackedOpenAIClient(provider, default_model=str(model_settings["model"]))
    return client, model_settings
