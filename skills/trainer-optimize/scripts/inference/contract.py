from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class InferenceRequest:
    messages: list[dict[str, Any]]
    model: str
    temperature: float | None = None
    max_tokens: int | None = None
    tools: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class InferenceResult:
    text: str
    model: str
    finish_reason: str | None
    usage: dict[str, Any] | None
    raw: Any


class InferenceProvider(Protocol):
    async def generate(self, request: InferenceRequest) -> InferenceResult: ...
