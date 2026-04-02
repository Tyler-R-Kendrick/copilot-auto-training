from __future__ import annotations

from datetime import UTC, datetime
import json
from typing import Any


def log_inference(event: dict[str, Any]) -> None:
    payload = {
        "training_run_id": event.get("training_run_id"),
        "episode_id": event.get("episode_id"),
        "step_id": event.get("step_id"),
        "latency_ms": event.get("latency_ms"),
        "model_name": event.get("model_name"),
        "response_length": event.get("response_length"),
        "timestamp": event.get("timestamp") or datetime.now(UTC).isoformat(),
        "provider": event.get("provider"),
        "status": event.get("status"),
        "error_type": event.get("error_type"),
    }
    print(json.dumps(payload, sort_keys=True))
