from __future__ import annotations

import asyncio
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
    class _StubSDKClient:
        async def start(self):
            return None

    def test_resolve_model_settings_uses_copilot_model(self, tmp_path):
        prompt_path = _write_repo_env(
            tmp_path,
            "COPILOT_MODEL=default",
        )

        settings = optimize_config.resolve_model_settings(str(prompt_path))

        assert settings["model"] == "default"

    def test_create_openai_client_returns_provider_backed_client_for_copilot(self, tmp_path, monkeypatch):
        prompt_path = _write_repo_env(
            tmp_path,
            "COPILOT_MODEL=default",
        )
        monkeypatch.setattr(
            "inference.copilot_provider.CopilotInferenceProvider._init_client",
            lambda self: TestCopilotConfig._StubSDKClient(),
        )

        client, settings = optimize_config.create_openai_client(str(prompt_path))

        assert isinstance(client, ProviderBackedOpenAIClient)
        assert settings["model"] == "default"


class TestCopilotProvider:
    class _FakeSDKSession:
        def __init__(self, session_id: str | None = None):
            self.session_id = session_id
            self.prompts: list[str] = []
            self.disconnected = False

        async def send_and_wait(self, prompt: str, *, timeout: float):
            self.prompts.append(prompt)
            return types.SimpleNamespace(
                data=types.SimpleNamespace(
                    content=" | ".join(self.prompts),
                    finish_reason="stop",
                    usage={"prompt_tokens": len(self.prompts), "output_tokens": len(self.prompts) + 1},
                )
            )

        async def disconnect(self):
            self.disconnected = True

    class _FakeSDKClient:
        def __init__(self):
            self.started = False
            self.created_sessions: list[object] = []

        async def start(self):
            self.started = True

        async def create_session(self, **kwargs):
            session = TestCopilotProvider._FakeSDKSession(kwargs.get("session_id"))
            self.created_sessions.append(session)
            return session

    @staticmethod
    def _patch_sdk(monkeypatch, client: _FakeSDKClient | None = None):
        fake_client = client or TestCopilotProvider._FakeSDKClient()
        monkeypatch.setattr("inference.copilot_provider.CopilotClient", lambda *args, **kwargs: fake_client)
        monkeypatch.setattr("inference.copilot_provider.PermissionHandler", types.SimpleNamespace(approve_all=object()))
        monkeypatch.setattr("inference.copilot_provider.SubprocessConfig", lambda **kwargs: types.SimpleNamespace(**kwargs))
        return fake_client

    @pytest.mark.asyncio
    async def test_generate_uses_sdk_session_and_preserves_session_history(self, monkeypatch):
        events: list[dict[str, object]] = []
        fake_client = self._patch_sdk(monkeypatch)

        provider = CopilotInferenceProvider(
            InferenceConfig(),
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
        assert second.text == "hello | again"
        assert events[-1]["status"] == "ok"
        assert events[-1]["episode_id"] == "episode-1"
        assert fake_client.started is True
        assert len(fake_client.created_sessions) == 1

    @pytest.mark.asyncio
    async def test_generate_surfaces_authentication_errors_without_retry(self, monkeypatch):
        attempts = {"count": 0}

        class AuthFailSession(self._FakeSDKSession):
            async def send_and_wait(self, prompt: str, *, timeout: float):
                attempts["count"] += 1
                raise RuntimeError("please sign in to copilot")

        class AuthFailClient(self._FakeSDKClient):
            async def create_session(self, **kwargs):
                session = AuthFailSession(kwargs.get("session_id"))
                self.created_sessions.append(session)
                return session

        self._patch_sdk(monkeypatch, AuthFailClient())

        provider = CopilotInferenceProvider(InferenceConfig())

        with pytest.raises(CopilotAuthenticationError):
            await provider.generate(
                InferenceRequest(messages=[{"role": "user", "content": "hi"}], model="default")
            )

        assert attempts["count"] == 1

    @pytest.mark.asyncio
    async def test_reset_session_clears_episode_history(self, monkeypatch):
        fake_client = self._patch_sdk(monkeypatch)

        provider = CopilotInferenceProvider(InferenceConfig())
        await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "first"}],
                model="default",
                metadata={"episode_id": "episode-2"},
            )
        )
        provider.reset_session("episode-2")
        await asyncio.sleep(0)

        result = await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "second"}],
                model="default",
                metadata={"episode_id": "episode-2"},
            )
        )

        assert result.text == "second"
        assert len(fake_client.created_sessions) == 2
        assert fake_client.created_sessions[0].disconnected is True

    @pytest.mark.asyncio
    async def test_ephemeral_requests_disconnect_sdk_session(self, monkeypatch):
        fake_client = self._patch_sdk(monkeypatch)

        provider = CopilotInferenceProvider(InferenceConfig())
        result = await provider.generate(
            InferenceRequest(messages=[{"role": "user", "content": "hi"}], model="default")
        )

        assert result.text == "hi"
        assert fake_client.created_sessions[0].disconnected is True


def test_local_adapter_response_shape_matches_chat_completions():
    result = types.SimpleNamespace(model="default", text="hello", finish_reason="stop", usage={"total_tokens": 3})

    body = _response_body(result)

    assert body["object"] == "chat.completion"
    assert body["choices"][0]["message"]["content"] == "hello"
    assert body["usage"] == {"total_tokens": 3}


def test_local_adapter_response_shape_defaults_usage_and_finish_reason():
    result = types.SimpleNamespace(model="default", text="", finish_reason=None, usage=None)

    body = _response_body(result)

    assert body["choices"][0]["finish_reason"] == "stop"
    assert body["usage"] == {}


@pytest.mark.asyncio
async def test_provider_backed_client_maps_output_token_usage(monkeypatch):
    class StubProvider:
        async def generate(self, request):
            return types.SimpleNamespace(
                text="hello",
                model=request.model,
                finish_reason="stop",
                usage={"prompt_tokens": 3, "output_tokens": 5},
                raw={"ok": True},
            )

    client = ProviderBackedOpenAIClient(StubProvider(), default_model="default")

    response = await client.chat.completions.create(
        model="default",
        messages=[{"role": "user", "content": "hello"}],
    )

    assert response.usage.prompt_tokens == 3
    assert response.usage.completion_tokens == 5
    assert response.usage.total_tokens == 8
