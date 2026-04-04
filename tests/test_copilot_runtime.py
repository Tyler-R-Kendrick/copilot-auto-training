from __future__ import annotations

from pathlib import Path
import types

from tokenizers.pre_tokenizers import ByteLevel

from copilot_runtime import ProviderBackedOpenAIClient, create_runtime_client, resolve_model_settings
from copilot_runtime.client import build_completion_usage, estimate_prompt_tokens, estimate_tokens_from_text


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


def test_estimate_tokens_from_text_uses_tokenizers_bytelevel():
    text = "hello world"
    expected = len(ByteLevel(add_prefix_space=False, use_regex=True).pre_tokenize_str(text))

    assert estimate_tokens_from_text(text) == expected


def test_estimate_prompt_tokens_sums_message_token_counts():
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Summarize this."},
    ]

    byte_level = ByteLevel(add_prefix_space=False, use_regex=True)
    expected = sum(len(byte_level.pre_tokenize_str(message["content"])) for message in messages)

    assert estimate_prompt_tokens(messages) == expected


def test_build_completion_usage_prefers_completion_usage_and_output_tokens_fallback():
    usage = build_completion_usage(
        {"prompt_tokens": 3, "output_tokens": 5},
        messages=[{"role": "user", "content": "hello"}],
        text="hello",
        model="default",
    )

    assert usage.prompt_tokens == 3
    assert usage.completion_tokens == 5
    assert usage.total_tokens == 8


def test_build_completion_usage_estimates_missing_usage_with_tokenizers():
    messages = [{"role": "user", "content": "Count these tokens."}]
    text = "Response text."

    usage = build_completion_usage(None, messages=messages, text=text, model="default")

    assert usage.prompt_tokens == estimate_prompt_tokens(messages, model="default")
    assert usage.completion_tokens == estimate_tokens_from_text(text, model="default")
    assert usage.total_tokens == usage.prompt_tokens + usage.completion_tokens
