from __future__ import annotations

import argparse
import asyncio
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any
from uuid import uuid4

from inference.config import InferenceConfig
from inference.contract import InferenceRequest
from inference.copilot_provider import CopilotInferenceProvider


def _response_body(result: Any) -> dict[str, Any]:
    return {
        "id": f"chatcmpl-{uuid4().hex[:12]}",
        "object": "chat.completion",
        "model": result.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": result.text},
                "finish_reason": result.finish_reason or "stop",
            }
        ],
        "usage": result.usage or {},
    }


def _build_handler(provider: CopilotInferenceProvider):
    class AdapterHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/v1/chat/completions":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            request = InferenceRequest(
                messages=payload.get("messages") or [],
                model=str(payload.get("model") or provider.config.model),
                temperature=payload.get("temperature"),
                max_tokens=payload.get("max_tokens"),
                tools=payload.get("tools"),
                metadata=payload.get("metadata"),
            )
            try:
                result = asyncio.run(provider.generate(request))
                body = _response_body(result)
                self.send_response(HTTPStatus.OK)
            except Exception as exc:  # pragma: no cover - exercised through callers
                body = {"error": {"message": str(exc), "type": type(exc).__name__}}
                self.send_response(HTTPStatus.BAD_GATEWAY)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return AdapterHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Expose Copilot inference as a local OpenAI-compatible endpoint.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--model", default="default")
    args = parser.parse_args(argv)
    provider = CopilotInferenceProvider(InferenceConfig(model=args.model))
    server = ThreadingHTTPServer((args.host, args.port), _build_handler(provider))
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
