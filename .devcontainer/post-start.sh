#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
tool_dir="$repo_root/tools/agent-skills-mcp"
workspace_python="$repo_root/.venv/bin/python"
requirements_file="$repo_root/requirements.txt"
requirements_hash_file="$repo_root/.venv/.requirements-sha256"

pick_python() {
    local candidate
    for candidate in python3.12 python3 python; do
        if command -v "$candidate" >/dev/null 2>&1; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

workspace_python_is_healthy() {
    if [[ ! -x "$workspace_python" ]]; then
        return 1
    fi

    "$workspace_python" - <<'PY'
from __future__ import annotations

import importlib.util
import sys

has_pip = importlib.util.find_spec("pip") is not None
raise SystemExit(0 if sys.version_info >= (3, 12) and has_pip else 1)
PY
}

requirements_are_current() {
    local expected_hash recorded_hash

    if [[ ! -f "$requirements_hash_file" ]]; then
        return 1
    fi

    expected_hash="$(sha256sum "$requirements_file" | awk '{print $1}')"
    recorded_hash="$(<"$requirements_hash_file")"
    [[ "$expected_hash" == "$recorded_hash" ]]
}

core_packages_installed() {
    "$workspace_python" - <<'PY'
from __future__ import annotations

import importlib.util

required = ("pytest", "yaml")
missing = [name for name in required if importlib.util.find_spec(name) is None]
raise SystemExit(0 if not missing else 1)
PY
}

install_workspace_requirements() {
    local expected_hash

    if command -v uv >/dev/null 2>&1; then
        uv pip install --python "$workspace_python" -r "$requirements_file"
    else
        "$workspace_python" -m pip install -r "$requirements_file"
    fi

    expected_hash="$(sha256sum "$requirements_file" | awk '{print $1}')"
    printf '%s\n' "$expected_hash" > "$requirements_hash_file"
}

desired_python="$(pick_python)"

if ! workspace_python_is_healthy; then
    rm -rf "$repo_root/.venv"
    "$desired_python" -m venv "$repo_root/.venv"
fi

if ! requirements_are_current || ! core_packages_installed; then
    install_workspace_requirements
fi

if command -v uv >/dev/null 2>&1; then
    uv sync --directory "$tool_dir" --python "$desired_python"
fi

if command -v gh >/dev/null 2>&1; then
    if ! gh extension list 2>/dev/null | awk '{print $1}' | grep -Eq '(^|/)gh-aw$'; then
        gh extension install github/gh-aw
    fi
fi
