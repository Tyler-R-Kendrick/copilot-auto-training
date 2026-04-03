from __future__ import annotations

import os
from pathlib import Path
from typing import Any, TypedDict

from inference.config import InferenceConfig
from training.lightning_integration import build_runtime_client


DEFAULT_COPILOT_MODEL = "default"
DEFAULT_COPILOT_TIMEOUT_SECONDS = 180


class ModelSettings(TypedDict):
    model: str
    repo_root: str
    timeout_seconds: int


def find_repo_root(start_path: str) -> Path:
    path = Path(start_path).resolve()
    candidates = [path.parent, *path.parents]
    for candidate in candidates:
        if (candidate / ".env").exists():
            return candidate
    for candidate in candidates:
        if any((candidate / marker).exists() for marker in ("requirements.txt", ".git", "README.md")):
            return candidate
    return path.parent


def load_dotenv_file(dotenv_path: Path) -> dict[str, str]:
    if not dotenv_path.exists():
        return {}
    parsed: dict[str, str] = {}
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed


def _pick_int_setting(
    name: str,
    *,
    dotenv_values: dict[str, str],
    dotenv_present: bool,
    default: int,
    minimum: int = 1,
) -> int:
    """Return a validated integer setting or the safe default.

    The repository `.env` takes precedence when it exists, even if the key is
    missing there. Process-level environment variables are only consulted when
    no repository `.env` file is present. Non-integer values and values smaller
    than `minimum` fall back to `default`.
    """
    raw_value = dotenv_values.get(name)
    if raw_value in (None, "") and not dotenv_present:
        raw_value = os.getenv(name)
    if raw_value in (None, ""):
        return default
    try:
        parsed = int(str(raw_value).strip())
    except ValueError:
        return default
    return parsed if parsed >= minimum else default


def resolve_model_settings(prompt_file: str) -> ModelSettings:
    repo_root = find_repo_root(prompt_file)
    dotenv_path = repo_root / ".env"
    dotenv_values = load_dotenv_file(dotenv_path)
    dotenv_present = dotenv_path.exists()

    def pick(name: str, default: str | None = None) -> str | None:
        dotenv_value = dotenv_values.get(name)
        process_value = os.getenv(name)
        if dotenv_value not in (None, ""):
            return dotenv_value
        if dotenv_present:
            return default
        if process_value not in (None, ""):
            return process_value
        return default

    model = pick("COPILOT_MODEL", DEFAULT_COPILOT_MODEL) or DEFAULT_COPILOT_MODEL
    return {
        "model": model,
        "repo_root": str(repo_root),
        "timeout_seconds": _pick_int_setting(
            "COPILOT_TIMEOUT_SECONDS",
            dotenv_values=dotenv_values,
            dotenv_present=dotenv_present,
            default=DEFAULT_COPILOT_TIMEOUT_SECONDS,
        ),
    }


def create_openai_client(prompt_file: str) -> tuple[Any, ModelSettings]:
    model_settings = resolve_model_settings(prompt_file)
    provider_config = InferenceConfig(
        model=str(model_settings.get("model") or DEFAULT_COPILOT_MODEL),
        timeout_seconds=int(model_settings.get("timeout_seconds") or DEFAULT_COPILOT_TIMEOUT_SECONDS),
    )
    return build_runtime_client(model_settings, provider_config=provider_config)
