from __future__ import annotations

import asyncio
import json
from pathlib import Path
import types

import pytest

import config as optimize_config
from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotAuthenticationError, CopilotInferenceProvider
from inference.local_adapter_service import _response_body
from training.lightning_integration import ProviderBackedOpenAIClient


def _write_repo_env(tmp_path: Path, *lines: str) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
    (repo_root / ".env").write_text("\n".join([*lines, ""]), encoding="utf-8")
    prompt_path = repo_root / "prompts" / "prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text("Prompt body\n", encoding="utf-8")
    return prompt_path


class TestCopilotConfig:
    def test_resolve_model_settings_supports_copilot_provider(self, tmp_path):
        prompt_path = _write_repo_env(
            tmp_path,
            "INFERENCE_PROVIDER=github_copilot",
            "COPILOT_INFERENCE_MODE=local_cli",
            "COPILOT_MODEL=default",
        )

        settings = optimize_config.resolve_model_settings(str(prompt_path))

        assert settings["provider"] == "github_copilot"
        assert settings["base_url"] == "copilot://local_cli"
        assert settings["inference_model"] == "default"
        assert settings["gradient_model"] == "default"
        assert settings["apply_edit_model"] == "default"

    def test_create_openai_client_returns_provider_backed_client_for_copilot(self, tmp_path, monkeypatch):
        prompt_path = _write_repo_env(
            tmp_path,
            "INFERENCE_PROVIDER=github_copilot",
            "COPILOT_INFERENCE_MODE=local_cli",
            "COPILOT_MODEL=default",
            "COPILOT_INFERENCE_COMMAND=fake-copilot --json",
        )
        monkeypatch.setattr(
            "inference.copilot_provider.CopilotInferenceProvider._resolve_command",
            lambda self: ("fake-copilot", "--json"),
        )

        client, settings = optimize_config.create_openai_client(str(prompt_path))

        assert isinstance(client, ProviderBackedOpenAIClient)
        assert settings["provider"] == "github_copilot"


class TestCopilotProvider:
    @pytest.mark.asyncio
    async def test_generate_uses_cli_json_and_preserves_session_history(self, monkeypatch):
        events: list[dict[str, object]] = []

        class FakeProcess:
            returncode = 0

            async def communicate(self, payload: bytes):
                body = json.loads(payload.decode("utf-8"))
                content = [message["content"] for message in body["messages"]]
                return json.dumps({"text": " | ".join(content), "usage": {"prompt_tokens": len(content)}}).encode(
                    "utf-8"
                ), b""

        async def fake_exec(*args, **kwargs):
            return FakeProcess()

        monkeypatch.setattr("inference.copilot_provider.asyncio.create_subprocess_exec", fake_exec)

        provider = CopilotInferenceProvider(
            InferenceConfig(cli_command=("fake-copilot", "--json")),
            logger=events.append,
        )

        first = await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "hello"}],
                model="default",
                metadata={"episode_id": "episode-1", "step_id": "step-1"},
            )
        )
        second = await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "again"}],
                model="default",
                metadata={"episode_id": "episode-1", "step_id": "step-2"},
            )
        )

        assert first.text == "hello"
        assert second.text == "hello | hello | again"
        assert events[-1]["status"] == "ok"
        assert events[-1]["episode_id"] == "episode-1"

    @pytest.mark.asyncio
    async def test_generate_surfaces_authentication_errors_without_retry(self, monkeypatch):
        attempts = {"count": 0}

        class FakeProcess:
            returncode = 1

            async def communicate(self, payload: bytes):
                attempts["count"] += 1
                return b"", b"Please sign in to Copilot"

        async def fake_exec(*args, **kwargs):
            return FakeProcess()

        monkeypatch.setattr("inference.copilot_provider.asyncio.create_subprocess_exec", fake_exec)

        provider = CopilotInferenceProvider(InferenceConfig(cli_command=("fake-copilot",)))

        with pytest.raises(CopilotAuthenticationError):
            await provider.generate(
                InferenceRequest(messages=[{"role": "user", "content": "hi"}], model="default")
            )

        assert attempts["count"] == 1


def test_local_adapter_response_shape_matches_chat_completions():
    result = types.SimpleNamespace(model="default", text="hello", finish_reason="stop", usage={"total_tokens": 3})

    body = _response_body(result)

    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"] == "hello"
    assert body["usage"] == {"total_tokens": 3}
