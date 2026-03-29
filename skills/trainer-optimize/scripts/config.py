from __future__ import annotations

import os
from pathlib import Path
from typing import Any


DEFAULT_GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
DEFAULT_GITHUB_GRADIENT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_GITHUB_APPLY_EDIT_MODEL = "openai/gpt-4.1-mini"


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
    dotenv_values = load_dotenv_file(repo_root / ".env")
    github_names = (
        "GITHUB_MODELS_API_KEY",
        "GITHUB_MODELS_ENDPOINT",
        "GITHUB_MODELS_MODEL",
        "GITHUB_MODELS_GRADIENT_MODEL",
        "GITHUB_MODELS_APPLY_EDIT_MODEL",
    )
    dotenv_github = any(dotenv_values.get(name) not in (None, "") for name in github_names)
    process_github = any(os.getenv(name) not in (None, "") for name in github_names)

    def pick(name: str, default: str | None = None, *, dotenv_only: bool = False) -> str | None:
        dotenv_value = dotenv_values.get(name)
        process_value = os.getenv(name)
        if dotenv_only:
            return dotenv_value if dotenv_value not in (None, "") else default
        if process_value not in (None, ""):
            return process_value
        if dotenv_value not in (None, ""):
            return dotenv_value
        return default

    if dotenv_github or process_github:
        dotenv_only = dotenv_github
        api_key = pick("GITHUB_MODELS_API_KEY", dotenv_only=dotenv_only) or pick(
            "OPENAI_API_KEY", dotenv_only=dotenv_only
        )
        if not api_key:
            raise ValueError("GitHub Models configuration requires GITHUB_MODELS_API_KEY or OPENAI_API_KEY.")
        gradient_model = pick(
            "GITHUB_MODELS_GRADIENT_MODEL",
            pick("GITHUB_MODELS_MODEL", DEFAULT_GITHUB_GRADIENT_MODEL, dotenv_only=dotenv_only),
            dotenv_only=dotenv_only,
        )
        inference_model = pick(
            "GITHUB_MODELS_MODEL",
            gradient_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            dotenv_only=dotenv_only,
        )
        apply_edit_model = pick(
            "GITHUB_MODELS_APPLY_EDIT_MODEL",
            gradient_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
            dotenv_only=dotenv_only,
        )
        return {
            "provider": "github",
            "api_key": api_key,
            "base_url": pick("GITHUB_MODELS_ENDPOINT", DEFAULT_GITHUB_MODELS_ENDPOINT, dotenv_only=dotenv_only),
            "inference_model": inference_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            "gradient_model": gradient_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            "apply_edit_model": apply_edit_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
            "repo_root": str(repo_root),
        }

    return {
        "provider": "openai",
        "api_key": pick("OPENAI_API_KEY"),
        "base_url": pick("OPENAI_BASE_URL"),
        "inference_model": pick("OPENAI_MODEL"),
        "gradient_model": DEFAULT_GITHUB_GRADIENT_MODEL,
        "apply_edit_model": DEFAULT_GITHUB_APPLY_EDIT_MODEL,
        "repo_root": str(repo_root),
    }


def create_openai_client(prompt_file: str) -> tuple[Any, dict[str, str | None]]:
    from openai import AsyncOpenAI

    model_settings = resolve_model_settings(prompt_file)
    client_kwargs: dict[str, str] = {}
    if model_settings.get("api_key"):
        client_kwargs["api_key"] = str(model_settings["api_key"])
    if model_settings.get("base_url"):
        client_kwargs["base_url"] = str(model_settings["base_url"])
    return AsyncOpenAI(**client_kwargs), model_settings