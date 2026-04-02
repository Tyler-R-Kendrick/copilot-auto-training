from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InferenceConfig:
    provider: str = "github_copilot"
    mode: str = "local_cli"
    model: str = "default"
    timeout_seconds: int = 60
    max_tokens: int = 1500
    temperature: float = 0.2
    retries: int = 2
    bundled_cli_path: str | None = None
    cli_command: tuple[str, ...] | None = None
