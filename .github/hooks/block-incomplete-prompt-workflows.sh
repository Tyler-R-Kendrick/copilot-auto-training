#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

/workspaces/copilot-apo/.venv/bin/python -c '
import json
from pathlib import Path

repo_root = Path(".").resolve()
pending = []
for status_path in repo_root.glob("**/.trainer-workspace/*/workflow-status.json"):
    try:
        payload = json.loads(status_path.read_text(encoding="utf-8"))
    except Exception:
        continue

    state = payload.get("workflow_state")
    if state == "complete":
        continue

    target = payload.get("target_file", str(status_path))
    workspace = payload.get("workspace_root", str(status_path.parent))
    pending.append((target, workspace, state or "pending_engineer_prompt"))

if not pending:
    raise SystemExit(0)

lines = [f"- {target} -> {workspace} ({state})" for target, workspace, state in pending]
message = (
    "Prompt optimization workflow is still incomplete for:\n"
    + "\n".join(lines)
    + "\n\nFinish the required /engineer-prompt review and @trainer run, then update each workflow-status.json to complete before ending the session."
)
print(json.dumps({"continue": False, "stopReason": message, "systemMessage": message}))
'