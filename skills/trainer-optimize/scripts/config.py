from __future__ import annotations

import os
from pathlib import Path
import shlex
from typing import Any

from inference.config import InferenceConfig
from training.lightning_integration import build_runtime_client


DEFAULT_GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
DEFAULT_GITHUB_GRADIENT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_GITHUB_APPLY_EDIT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_COPILOT_MODEL = "default"


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


def resolve_model_settings(prompt_file: str) -> dict[str, str | None]:
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

    openai_active = any(
        pick(name) not in (None, "") for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL")
    )
    github_markers = any(
        pick(name) not in (None, "")
        for name in (
            "GITHUB_MODELS_API_KEY",
            "GITHUB_MODELS_ENDPOINT",
            "GITHUB_MODELS_MODEL",
            "GITHUB_MODELS_GRADIENT_MODEL",
            "GITHUB_MODELS_APPLY_EDIT_MODEL",
        )
    )
    copilot_provider = pick("INFERENCE_PROVIDER")
    copilot_markers = copilot_provider == "github_copilot" or any(
        pick(name) not in (None, "")
        for name in (
            "COPILOT_INFERENCE_MODE",
            "COPILOT_MODEL",
            "COPILOT_BUNDLED_CLI_PATH",
            "COPILOT_INFERENCE_COMMAND",
        )
    )

    if openai_active:
        inference_model = pick("OPENAI_MODEL")
        gradient_model = pick("OPENAI_GRADIENT_MODEL", inference_model)
        apply_edit_model = pick("OPENAI_APPLY_EDIT_MODEL", gradient_model or inference_model)
        return {
            "provider": "openai",
            "api_key": pick("OPENAI_API_KEY"),
            "base_url": pick("OPENAI_BASE_URL"),
            "inference_model": inference_model,
            "gradient_model": gradient_model,
            "apply_edit_model": apply_edit_model,
            "repo_root": str(repo_root),
        }

    if github_markers:
        api_key = pick("GITHUB_MODELS_API_KEY")
        if not api_key:
            raise ValueError("GitHub Models configuration requires GITHUB_MODELS_API_KEY.")
        gradient_model = pick(
            "GITHUB_MODELS_GRADIENT_MODEL",
            pick("GITHUB_MODELS_MODEL", DEFAULT_GITHUB_GRADIENT_MODEL),
        )
        inference_model = pick(
            "GITHUB_MODELS_MODEL",
            gradient_model or DEFAULT_GITHUB_GRADIENT_MODEL,
        )
        apply_edit_model = pick(
            "GITHUB_MODELS_APPLY_EDIT_MODEL",
            gradient_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
        )
        return {
            "provider": "github",
            "api_key": api_key,
            "base_url": pick("GITHUB_MODELS_ENDPOINT", DEFAULT_GITHUB_MODELS_ENDPOINT),
            "inference_model": inference_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            "gradient_model": gradient_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            "apply_edit_model": apply_edit_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
            "repo_root": str(repo_root),
        }

    if copilot_markers:
        copilot_mode = pick("COPILOT_INFERENCE_MODE", "local_cli") or "local_cli"
        inference_model = pick("COPILOT_MODEL", DEFAULT_COPILOT_MODEL) or DEFAULT_COPILOT_MODEL
        return {
            "provider": "github_copilot",
            "api_key": None,
            "base_url": f"copilot://{copilot_mode}",
            "inference_model": inference_model,
            "gradient_model": inference_model,
            "apply_edit_model": inference_model,
            "repo_root": str(repo_root),
            "copilot_mode": copilot_mode,
            "copilot_bundled_cli_path": pick("COPILOT_BUNDLED_CLI_PATH"),
            "copilot_cli_command": pick("COPILOT_INFERENCE_COMMAND"),
        }

    return {
        "provider": "openai",
        "api_key": pick("OPENAI_API_KEY"),
        "base_url": pick("OPENAI_BASE_URL"),
        "inference_model": pick("OPENAI_MODEL"),
        "gradient_model": pick("OPENAI_GRADIENT_MODEL", pick("OPENAI_MODEL")),
        "apply_edit_model": pick("OPENAI_APPLY_EDIT_MODEL", pick("OPENAI_GRADIENT_MODEL", pick("OPENAI_MODEL"))),
        "repo_root": str(repo_root),
    }


def create_openai_client(prompt_file: str) -> tuple[Any, dict[str, str | None]]:
    from openai import AsyncOpenAI

    model_settings = resolve_model_settings(prompt_file)
    if model_settings.get("provider") == "github_copilot":
        cli_command = model_settings.get("copilot_cli_command")
        provider_config = InferenceConfig(
            provider="github_copilot",
            mode=str(model_settings.get("copilot_mode") or "local_cli"),
            model=str(model_settings.get("inference_model") or DEFAULT_COPILOT_MODEL),
            bundled_cli_path=str(model_settings["copilot_bundled_cli_path"])
            if model_settings.get("copilot_bundled_cli_path")
            else None,
            cli_command=tuple(shlex.split(cli_command)) if isinstance(cli_command, str) and cli_command.strip() else None,
        )
        return build_runtime_client(model_settings, provider_config=provider_config)
    client_kwargs: dict[str, str] = {}
    if model_settings.get("api_key"):
        client_kwargs["api_key"] = str(model_settings["api_key"])
    if model_settings.get("base_url"):
        client_kwargs["base_url"] = str(model_settings["base_url"])
    return AsyncOpenAI(**client_kwargs), model_settings
