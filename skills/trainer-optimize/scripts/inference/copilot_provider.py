from __future__ import annotations

import asyncio
from asyncio.subprocess import PIPE
from datetime import UTC, datetime
import json
import os
import shlex
import shutil
from time import perf_counter
from typing import Any
from uuid import uuid4

from inference.config import InferenceConfig
from inference.contract import InferenceRequest, InferenceResult
from training.trace_logger import log_inference


API_KEY_ENV_VARS = (
    "OPENAI_API_KEY",
    "GITHUB_MODELS_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
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
                "content": _stringify_message_content(message.get("content", "")),
            }
        )
    return normalized


def _extract_text_from_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, dict):
        for key in ("text", "output_text", "content", "message"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            content = message.get("content") if isinstance(message, dict) else None
            if isinstance(content, str) and content.strip():
                return content.strip()
    raise CopilotInferenceError("Copilot runtime response did not include any text.")


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
        self._sessions: dict[str, list[dict[str, str]]] = {}
        self._reject_provider_keys()
        self._command = self._resolve_command()

    def _reject_provider_keys(self) -> None:
        detected = sorted(name for name in API_KEY_ENV_VARS if os.getenv(name) not in (None, ""))
        if detected:
            raise ValueError(
                "github_copilot inference refuses provider API keys. Remove these variables before using Copilot mode: "
                + ", ".join(detected)
            )

    def _resolve_command(self) -> tuple[str, ...]:
        if self.config.cli_command:
            return self.config.cli_command
        if self.config.mode == "bundled_cli":
            if not self.config.bundled_cli_path:
                raise CopilotInferenceError("bundled_cli mode requires bundled_cli_path.")
            return (self.config.bundled_cli_path, "chat", "--json", "--stdio")
        override = os.getenv("COPILOT_INFERENCE_COMMAND", "").strip()
        if override:
            return tuple(shlex.split(override))
        executable = shutil.which("copilot")
        if executable:
            return (executable, "chat", "--json", "--stdio")
        raise CopilotInferenceError(
            "No signed-in Copilot CLI runtime was found. Install the Copilot CLI or set COPILOT_INFERENCE_COMMAND."
        )

    def reset_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def _session_id_for(self, request: InferenceRequest) -> str | None:
        metadata = request.metadata or {}
        for key in ("session_id", "episode_id"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    def _conversation_for(self, request: InferenceRequest) -> tuple[str | None, list[dict[str, str]]]:
        messages = _normalize_messages(request.messages)
        session_id = self._session_id_for(request)
        if not session_id:
            return None, messages
        history = list(self._sessions.get(session_id, []))
        preserve_history = bool((request.metadata or {}).get("preserve_history", True))
        return session_id, history + messages if preserve_history else messages

    async def _invoke_cli(self, payload: dict[str, Any]) -> dict[str, Any]:
        process = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(json.dumps(payload).encode("utf-8")),
            timeout=self.config.timeout_seconds,
        )
        if process.returncode != 0:
            message = stderr.decode("utf-8", errors="replace").strip() or stdout.decode("utf-8", errors="replace").strip()
            lowered = message.lower()
            if any(token in lowered for token in ("auth", "sign in", "login", "oauth", "unauthorized")):
                raise CopilotAuthenticationError(message or "Copilot CLI authentication failed.")
            raise CopilotInferenceError(message or f"Copilot CLI exited with code {process.returncode}.")
        raw_text = stdout.decode("utf-8", errors="replace").strip()
        if not raw_text:
            raise CopilotInferenceError("Copilot CLI returned an empty response.")
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            parsed = {"text": raw_text}
        return parsed if isinstance(parsed, dict) else {"text": raw_text, "raw": parsed}

    async def generate(self, request: InferenceRequest) -> InferenceResult:
        attempts = max(1, int(self.config.retries) + 1)
        session_id, messages = self._conversation_for(request)
        payload = {
            "model": request.model or self.config.model,
            "messages": messages,
            "temperature": self.config.temperature if request.temperature is None else request.temperature,
            "max_tokens": self.config.max_tokens if request.max_tokens is None else request.max_tokens,
            "tools": request.tools,
            "metadata": request.metadata or {},
        }
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            started = perf_counter()
            try:
                raw = await self._invoke_cli(payload)
                text = _extract_text_from_payload(raw)
                finish_reason = raw.get("finish_reason") if isinstance(raw, dict) else None
                usage = raw.get("usage") if isinstance(raw, dict) and isinstance(raw.get("usage"), dict) else None
                latency_ms = int((perf_counter() - started) * 1000)
                if session_id:
                    self._sessions[session_id] = messages + [{"role": "assistant", "content": text}]
                self._logger(
                    {
                        "training_run_id": (request.metadata or {}).get("training_run_id"),
                        "episode_id": session_id,
                        "step_id": (request.metadata or {}).get("step_id", f"attempt-{attempt}"),
                        "latency_ms": latency_ms,
                        "model_name": payload["model"],
                        "response_length": len(text),
                        "timestamp": datetime.now(UTC).isoformat(),
                        "provider": self.config.provider,
                        "status": "ok",
                    }
                )
                return InferenceResult(
                    text=text,
                    model=str(payload["model"]),
                    finish_reason=finish_reason if isinstance(finish_reason, str) else None,
                    usage=usage,
                    raw=raw,
                )
            except Exception as exc:
                last_error = exc
                latency_ms = int((perf_counter() - started) * 1000)
                self._logger(
                    {
                        "training_run_id": (request.metadata or {}).get("training_run_id"),
                        "episode_id": session_id,
                        "step_id": (request.metadata or {}).get("step_id", f"attempt-{attempt}"),
                        "latency_ms": latency_ms,
                        "model_name": payload["model"],
                        "response_length": 0,
                        "timestamp": datetime.now(UTC).isoformat(),
                        "provider": self.config.provider,
                        "status": "error",
                        "error_type": type(exc).__name__,
                    }
                )
                if isinstance(exc, CopilotAuthenticationError) or attempt >= attempts:
                    raise
                await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
        raise CopilotInferenceError(str(last_error) if last_error else "Copilot inference failed.")
