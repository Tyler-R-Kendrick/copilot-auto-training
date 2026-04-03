from __future__ import annotations

import asyncio
from http import HTTPStatus
import json
from pathlib import Path
import types

import pytest

import config as optimize_config
from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotAuthenticationError, CopilotInferenceProvider, _retry_delay_seconds
from inference.local_adapter_service import MAX_REQUEST_BYTES, _build_handler, _response_body
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
            self.create_session_kwargs: list[dict[str, object]] = []

        async def start(self):
            self.started = True

        async def create_session(self, **kwargs):
            self.create_session_kwargs.append(dict(kwargs))
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

    @pytest.mark.asyncio
    async def test_generate_passes_working_directory_and_session_id_to_sdk(self, monkeypatch):
        fake_client = self._patch_sdk(monkeypatch)

        provider = CopilotInferenceProvider(
            InferenceConfig(),
            model_settings={"repo_root": "/tmp/repo-root"},
        )

        await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "hello"}],
                model="default",
                metadata={"episode_id": "episode-7"},
            )
        )

        created_session = fake_client.created_sessions[0]
        session_kwargs = fake_client.create_session_kwargs[0]
        assert created_session.session_id == "episode-7"
        assert session_kwargs["working_directory"] == "/tmp/repo-root"
        assert session_kwargs["model"] == "default"

    @pytest.mark.asyncio
    async def test_generate_with_preserve_history_false_restarts_sdk_session(self, monkeypatch):
        fake_client = self._patch_sdk(monkeypatch)

        provider = CopilotInferenceProvider(InferenceConfig())
        await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "first"}],
                model="default",
                metadata={"episode_id": "episode-9"},
            )
        )

        result = await provider.generate(
            InferenceRequest(
                messages=[{"role": "user", "content": "second"}],
                model="default",
                metadata={"episode_id": "episode-9", "preserve_history": False},
            )
        )

        assert result.text == "second"
        assert len(fake_client.created_sessions) == 2
        assert fake_client.created_sessions[0].disconnected is True

    def test_retry_delay_seconds_rejects_non_positive_attempts(self):
        with pytest.raises(ValueError, match="attempt must be >= 1"):
            _retry_delay_seconds(0.5, 0)


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


def test_local_adapter_ignores_unsupported_provider_kwargs(monkeypatch):
    captured = {}

    class StubProvider:
        config = types.SimpleNamespace(model="default")

        async def generate(self, request):
            captured["request"] = request
            return types.SimpleNamespace(model="default", text="ok", finish_reason="stop", usage={})

    handler_cls = _build_handler(StubProvider())

    def send_error(self, code, message=None, explain=None):
        raise AssertionError(f"unexpected send_error({code})")

    monkeypatch.setattr(handler_cls, "send_error", send_error)

    handler = handler_cls.__new__(handler_cls)
    payload = {
        "messages": [{"role": "user", "content": "hi"}],
        "model": "custom-model",
        "temperature": 0.7,
        "max_tokens": 42,
        "tools": [{"type": "function", "function": {"name": "demo"}}],
        "metadata": {"episode_id": "ep"},
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    handler.path = "/v1/chat/completions"
    handler.headers = {"Content-Length": str(len(body_bytes))}
    handler.rfile = types.SimpleNamespace(read=lambda _: body_bytes)
    handler.wfile = types.SimpleNamespace(write=lambda data: captured.setdefault("response", data))
    handler.send_response = lambda status: captured.setdefault("status", status)
    handler.send_header = lambda name, value: None
    handler.end_headers = lambda: None

    handler.do_POST()

    request = captured["request"]
    assert request.model == "custom-model"
    assert request.messages == payload["messages"]
    assert request.metadata == payload["metadata"]
    assert not hasattr(request, "temperature")
    assert not hasattr(request, "max_tokens")
    assert not hasattr(request, "tools")
    assert captured["status"] == HTTPStatus.OK


def test_local_adapter_rejects_oversized_payloads(monkeypatch):
    captured = {}

    class StubProvider:
        config = types.SimpleNamespace(model="default")

        async def generate(self, request):
            raise AssertionError("oversized requests should be rejected before provider.generate")

    handler_cls = _build_handler(StubProvider())
    monkeypatch.setattr(
        handler_cls,
        "send_error",
        lambda self, code, message=None, explain=None: captured.setdefault("error", code),
    )

    handler = handler_cls.__new__(handler_cls)
    handler.path = "/v1/chat/completions"
    handler.headers = {"Content-Length": str(MAX_REQUEST_BYTES + 1)}
    handler.rfile = types.SimpleNamespace(
        read=lambda _: (_ for _ in ()).throw(AssertionError("oversized requests should not be read"))
    )

    handler.do_POST()

    assert captured["error"] == HTTPStatus.REQUEST_ENTITY_TOO_LARGE


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


@pytest.mark.asyncio
async def test_provider_backed_client_chat_completions_ignores_unsupported_kwargs():
    captured = {}

    class StubProvider:
        async def generate(self, request):
            captured["request"] = request
            return types.SimpleNamespace(
                text="hello",
                model=request.model,
                finish_reason="stop",
                usage={"prompt_tokens": 1, "output_tokens": 2},
                raw={"ok": True},
            )

    client = ProviderBackedOpenAIClient(StubProvider(), default_model="default")

    response = await client.chat.completions.create(
        model="default",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.2,
        max_tokens=25,
        tools=[{"type": "function", "function": {"name": "demo"}}],
        metadata={"episode_id": "episode-sdk"},
    )

    request = captured["request"]
    assert request.model == "default"
    assert request.messages == [{"role": "user", "content": "hello"}]
    assert request.metadata == {"interaction": "chat.completions.create", "episode_id": "episode-sdk"}
    assert not hasattr(request, "temperature")
    assert not hasattr(request, "max_tokens")
    assert not hasattr(request, "tools")
    assert response.choices[0].message.content == "hello"
