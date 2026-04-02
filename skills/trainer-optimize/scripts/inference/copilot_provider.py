from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import inspect
import os
from time import perf_counter
from typing import Any

from inference.config import InferenceConfig
from inference.contract import InferenceRequest, InferenceResult
from training.trace_logger import log_inference

try:
    from copilot import CopilotClient, ExternalServerConfig, PermissionHandler, SubprocessConfig
except ImportError:  # pragma: no cover - exercised only when dependency is missing at runtime
    CopilotClient = None
    ExternalServerConfig = None
    PermissionHandler = None
    SubprocessConfig = None


API_KEY_ENV_VARS = (
    "OPENAI_API_KEY",
    "GITHUB_MODELS_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)
AUTHENTICATION_ERROR_MARKERS = (
    "please sign in to copilot",
    "copilot authentication failed",
    "oauth token",
    "not authenticated",
    "login required",
)


class CopilotInferenceError(RuntimeError):
    pass


class CopilotAuthenticationError(CopilotInferenceError):
    pass


def _stringify_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text)
        return "\n".join(chunks)
    return str(content)


def _normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        normalized.append(
            {
                "role": str(message.get("role", "user")),
                "content": _stringify_message_content(message.get("content", "")).strip(),
            }
        )
    return [message for message in normalized if message["content"]]


def _extract_data_value(data: Any, *names: str) -> Any:
    for name in names:
        if isinstance(data, dict) and name in data:
            return data[name]
        value = getattr(data, name, None)
        if value is not None:
            return value
    return None


def _extract_text_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()
    data = getattr(payload, "data", payload)
    value = _extract_data_value(
        data,
        "content",
        "text",
        "delta_content",
        "deltaContent",
        "output_text",
        "message",
    )
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list):
        parts = [part.strip() for part in value if isinstance(part, str) and part.strip()]
        if parts:
            return "\n".join(parts)
    raise CopilotInferenceError("Copilot SDK response did not include any text.")


class CopilotInferenceProvider:
    def __init__(
        self,
        config: InferenceConfig,
        *,
        model_settings: dict[str, Any] | None = None,
        logger: Any = log_inference,
    ):
        self.config = config
        self.model_settings = model_settings or {}
        self._logger = logger
        self._client_lock = asyncio.Lock()
        self._session_lock = asyncio.Lock()
        self._sessions: dict[str, Any] = {}
        self._session_models: dict[str, str] = {}
        self._client_started = False
        self._reject_provider_keys()
        self.client = self._init_client()

    def _reject_provider_keys(self) -> None:
        detected = sorted(name for name in API_KEY_ENV_VARS if os.getenv(name) not in (None, ""))
        if detected:
            raise ValueError(
                "github_copilot inference refuses provider API keys. Remove these variables before using Copilot mode: "
                + ", ".join(detected)
            )

    def _init_client(self) -> Any:
        if CopilotClient is None or PermissionHandler is None or SubprocessConfig is None:
            raise CopilotInferenceError(
                "github-copilot-sdk is required for github_copilot inference. Install repository dependencies first."
            )
        client_config: Any | None = None
        if self.config.mode == "bundled_cli":
            if not self.config.bundled_cli_path:
                raise CopilotInferenceError("bundled_cli mode requires bundled_cli_path.")
            client_config = SubprocessConfig(cli_path=self.config.bundled_cli_path, use_logged_in_user=True)
        elif self.config.mode in {"local_cli", "oauth"}:
            client_config = SubprocessConfig(use_logged_in_user=True)
        else:
            raise CopilotInferenceError(f"Unsupported Copilot SDK mode: {self.config.mode!r}")
        return CopilotClient(client_config, auto_start=False)

    async def _ensure_client_started(self) -> Any:
        async with self._client_lock:
            if not self._client_started:
                await self.client.start()
                self._client_started = True
        return self.client

    def _session_id_for(self, request: InferenceRequest) -> str | None:
        metadata = request.metadata or {}
        for key in ("session_id", "episode_id"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    async def _disconnect_session(self, session: Any) -> None:
        disconnect = getattr(session, "disconnect", None)
        if not callable(disconnect):
            return
        result = disconnect()
        if inspect.isawaitable(result):
            await result

    async def _create_session(self, *, session_id: str | None, model: str) -> Any:
        client = await self._ensure_client_started()
        session_kwargs: dict[str, Any] = {
            "on_permission_request": PermissionHandler.approve_all,
            "model": model,
            "working_directory": self.model_settings.get("repo_root"),
        }
        if session_id:
            session_kwargs["session_id"] = session_id
        return await client.create_session(**session_kwargs)

    async def _start_session(self, request: InferenceRequest) -> tuple[str | None, Any, bool]:
        model_name = str(request.model or self.config.model)
        session_id = self._session_id_for(request)
        if not session_id:
            session = await self._create_session(session_id=None, model=model_name)
            return None, session, True

        async with self._session_lock:
            existing = self._sessions.get(session_id)
            existing_model = self._session_models.get(session_id)
            if existing is not None and existing_model == model_name and (request.metadata or {}).get("preserve_history", True):
                return session_id, existing, False
            if existing is not None:
                await self._disconnect_session(existing)
            session = await self._create_session(session_id=session_id, model=model_name)
            self._sessions[session_id] = session
            self._session_models[session_id] = model_name
            return session_id, session, False

    def reset_session(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        self._session_models.pop(session_id, None)
        if session is None:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(self._disconnect_session(session))

    def _build_prompt(self, request: InferenceRequest, *, session_is_new: bool) -> str:
        messages = _normalize_messages(request.messages)
        if not messages:
            raise CopilotInferenceError("InferenceRequest.messages must include at least one non-empty message.")
        if not session_is_new:
            for message in reversed(messages):
                if message["role"] == "user":
                    return message["content"]
            return messages[-1]["content"]
        if len(messages) == 1 and messages[0]["role"] == "user":
            return messages[0]["content"]
        return "\n\n".join(f"{message['role'].capitalize()}: {message['content']}" for message in messages)

    async def _send_request(self, session: Any, request: InferenceRequest, *, session_is_new: bool) -> Any:
        prompt = self._build_prompt(request, session_is_new=session_is_new)
        try:
            return await session.send_and_wait(prompt, timeout=float(self.config.timeout_seconds))
        except Exception as exc:
            raise self._normalize_sdk_error(exc) from exc

    def _normalize_sdk_error(self, exc: Exception) -> Exception:
        message = str(exc).strip()
        lowered = message.lower()
        if any(marker in lowered for marker in AUTHENTICATION_ERROR_MARKERS):
            return CopilotAuthenticationError(message or "Copilot SDK authentication failed.")
        if isinstance(exc, TimeoutError):
            return CopilotInferenceError(f"Copilot SDK timed out after {self.config.timeout_seconds}s.")
        return CopilotInferenceError(message or type(exc).__name__)

    def _extract_finish_reason(self, response: Any) -> str | None:
        data = getattr(response, "data", response)
        finish_reason = _extract_data_value(data, "finish_reason", "finishReason", "stop_reason", "stopReason")
        return str(finish_reason) if finish_reason is not None else None

    def _extract_usage(self, response: Any) -> dict[str, Any] | None:
        data = getattr(response, "data", response)
        usage = _extract_data_value(data, "usage", "token_usage", "tokenUsage")
        if isinstance(usage, dict):
            return usage
        if usage is None:
            return None
        return {
            key: value
            for key in ("prompt_tokens", "completion_tokens", "output_tokens", "total_tokens")
            if (value := getattr(usage, key, None)) is not None
        } or None

    async def generate(self, request: InferenceRequest) -> InferenceResult:
        attempts = max(1, int(self.config.retries) + 1)
        session_id, session, ephemeral = await self._start_session(request)
        last_error: Exception | None = None
        try:
            for attempt in range(1, attempts + 1):
                started = perf_counter()
                try:
                    raw = await self._send_request(session, request, session_is_new=ephemeral and attempt == 1)
                    text = _extract_text_from_payload(raw)
                    latency_ms = int((perf_counter() - started) * 1000)
                    usage = self._extract_usage(raw)
                    self._logger(
                        {
                            "training_run_id": (request.metadata or {}).get("training_run_id"),
                            "episode_id": session_id,
                            "step_id": (request.metadata or {}).get("step_id", f"attempt-{attempt}"),
                            "latency_ms": latency_ms,
                            "model_name": request.model or self.config.model,
                            "response_length": len(text),
                            "timestamp": datetime.now(UTC).isoformat(),
                            "provider": self.config.provider,
                            "status": "ok",
                        }
                    )
                    return InferenceResult(
                        text=text,
                        model=str(request.model or self.config.model),
                        finish_reason=self._extract_finish_reason(raw),
                        usage=usage,
                        raw=raw,
                    )
                except Exception as exc:
                    normalized = exc if isinstance(exc, CopilotInferenceError) else self._normalize_sdk_error(exc)
                    last_error = normalized
                    latency_ms = int((perf_counter() - started) * 1000)
                    self._logger(
                        {
                            "training_run_id": (request.metadata or {}).get("training_run_id"),
                            "episode_id": session_id,
                            "step_id": (request.metadata or {}).get("step_id", f"attempt-{attempt}"),
                            "latency_ms": latency_ms,
                            "model_name": request.model or self.config.model,
                            "response_length": 0,
                            "timestamp": datetime.now(UTC).isoformat(),
                            "provider": self.config.provider,
                            "status": "error",
                            "error_type": type(normalized).__name__,
                        }
                    )
                    if isinstance(normalized, CopilotAuthenticationError) or attempt >= attempts:
                        raise normalized
                    await asyncio.sleep(self.config.retry_backoff_seconds * (2 ** max(0, attempt - 1)))
            raise CopilotInferenceError(str(last_error) if last_error else "Copilot inference failed.")
        finally:
            if ephemeral:
                await self._disconnect_session(session)
