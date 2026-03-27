#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
tool_dir="$repo_root/tools/agent-skills-mcp"
workspace_uv="$repo_root/.venv/bin/uv"

if [[ -x "$workspace_uv" ]]; then
    "$workspace_uv" sync --directory "$tool_dir"
elif command -v uv >/dev/null 2>&1; then
    uv sync --directory "$tool_dir"
fi