from __future__ import annotations

from pathlib import Path
import types

from copilot_runtime import ProviderBackedOpenAIClient, create_runtime_client, resolve_model_settings


def _write_repo_env(tmp_path: Path, *lines: str) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
    (repo_root / ".env").write_text("\n".join([*lines, ""]), encoding="utf-8")
    prompt_path = repo_root / "prompts" / "prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text("Prompt body\n", encoding="utf-8")
    return prompt_path


def test_resolve_model_settings_uses_copilot_model(tmp_path: Path):
    prompt_path = _write_repo_env(tmp_path, "COPILOT_MODEL=default")

    settings = resolve_model_settings(str(prompt_path))

    assert settings["model"] == "default"


def test_create_runtime_client_returns_provider_backed_client(tmp_path: Path, monkeypatch):
    prompt_path = _write_repo_env(tmp_path, "COPILOT_MODEL=default")

    class _StubSDKClient:
        async def start(self):
            return None

    monkeypatch.setattr(
        "copilot_runtime.provider.CopilotInferenceProvider._init_client",
        lambda self: _StubSDKClient(),
    )

    client, settings = create_runtime_client(str(prompt_path))

    assert isinstance(client, ProviderBackedOpenAIClient)
    assert settings["model"] == "default"


def test_create_runtime_client_allows_model_override(tmp_path: Path, monkeypatch):
    prompt_path = _write_repo_env(tmp_path, "COPILOT_MODEL=default")

    monkeypatch.setattr(
        "copilot_runtime.provider.CopilotInferenceProvider._init_client",
        lambda self: types.SimpleNamespace(start=lambda: None),
    )

    client, settings = create_runtime_client(str(prompt_path), model="custom-model")

    assert isinstance(client, ProviderBackedOpenAIClient)
    assert settings["model"] == "custom-model"
