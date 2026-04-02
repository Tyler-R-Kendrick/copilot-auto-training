from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InferenceConfig:
    model: str = "default"
    timeout_seconds: int = 60
    max_tokens: int = 1500
    temperature: float = 0.2
    retries: int = 2
    retry_backoff_seconds: float = 0.5
    session_history_limit: int = 40
