#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

python_bin="$repo_root/.venv/bin/python"

collect_candidates() {
  if [[ "$#" -gt 0 ]]; then
    printf '%s\n' "$@"
    return
  fi

  if [[ -n "${COPILOT_TOOL_USE_FILE_PATHS:-}" ]]; then
    printf '%s\n' "$COPILOT_TOOL_USE_FILE_PATHS"
    return
  fi

  if [[ ! -t 0 ]]; then
    cat
  fi
}

should_validate() {
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue

    if [[ "$line" == *"/evals/"* ]]; then
      return 0
    fi

    case "$line" in
      *.prompt.md|*.prompty|*.instructions.md|*.agent.md|*/SKILL.md|*/AGENTS.md)
        return 0
        ;;
    esac
  done

  return 1
}

inputs="$(collect_candidates "$@")"

if [[ -z "$inputs" ]]; then
  exit 0
fi

if ! printf '%s\n' "$inputs" | should_validate; then
  exit 0
fi

"$python_bin" -m pytest -q tests/test_customizations.py
