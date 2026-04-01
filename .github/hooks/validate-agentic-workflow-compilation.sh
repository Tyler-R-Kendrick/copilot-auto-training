#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

state_dir="$repo_root/.git"
state_file="$repo_root/.git/copilot-agentic-workflows.txt"
python_bin="$repo_root/.venv/bin/python"
enforce=0
if [[ "${1:-}" == "--enforce" ]]; then
  enforce=1
  shift
fi

if [[ ! -x "$python_bin" ]]; then
  echo "Error: expected repository Python at $python_bin so the hook can emit JSON responses." >&2
  exit 1
fi

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

is_agentic_workflow() {
  local path="$1"

  case "$path" in
    .github/workflows/*.md)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

normalize_targets() {
  local input

  while IFS= read -r input; do
    [[ -z "$input" ]] && continue

    local abs_path="$input"
    if [[ "$abs_path" != /* ]]; then
      abs_path="$repo_root/$abs_path"
    fi

    [[ -e "$abs_path" ]] || continue

    local rel_path
    rel_path="$(realpath --relative-to="$repo_root" "$abs_path")"
    [[ "$rel_path" != ..* ]] || continue

    if is_agentic_workflow "$rel_path"; then
      printf '%s\n' "$rel_path"
    fi
  done | sort -u
}

load_recorded_targets() {
  if [[ -f "$state_file" ]]; then
    cat "$state_file"
  fi
}

record_targets() {
  local targets="$1"
  mkdir -p "$state_dir"

  {
    load_recorded_targets
    printf '%s\n' "$targets"
  } | sed '/^$/d' | sort -u > "$state_file"
}

render_json_message() {
  local continue_value="$1"
  local message="$2"

  REPO_HOOK_MESSAGE="$message" REPO_HOOK_CONTINUE="$continue_value" "$python_bin" - <<'PY'
import json
import os

message = os.environ["REPO_HOOK_MESSAGE"]
payload = {"continue": os.environ["REPO_HOOK_CONTINUE"] == "true", "systemMessage": message}
if not payload["continue"]:
    payload["stopReason"] = message
print(json.dumps(payload))
PY
}

recorded_targets="$(load_recorded_targets | normalize_targets)"

if [[ "$enforce" -eq 0 ]]; then
  current_targets="$(collect_candidates "$@" | normalize_targets)"
  if [[ -z "$current_targets" ]]; then
    exit 0
  fi

  record_targets "$current_targets"

  message="Agentic workflow source file(s) changed:
$(printf '%s\n' "$current_targets" | sed 's/^/- /')

Before finishing, run \`gh aw compile <workflow-name>\` for each changed workflow. The stop hook will enforce compilation before the session can end."
  render_json_message true "$message"
  exit 0
fi

if [[ -z "$recorded_targets" ]]; then
  rm -f "$state_file"
  exit 0
fi

missing_gh_message="Agentic workflow compilation enforcement could not run because \`gh aw\` is unavailable. Install or refresh the gh-aw extension, then run \`gh aw compile\` for the changed workflow files."
if ! command -v gh >/dev/null 2>&1 || ! gh aw --help >/dev/null 2>&1; then
  render_json_message false "$missing_gh_message"
  exit 0
fi

compile_failures=()
lockfile_updates=()
while IFS= read -r workflow_path; do
  [[ -z "$workflow_path" ]] && continue

  workflow_name="$(basename "${workflow_path%.md}")"
  if ! compile_output="$(gh aw compile "$workflow_name" 2>&1)"; then
    compile_failures+=("- $workflow_path -> ${compile_output//$'\n'/ }")
    continue
  fi

  lock_path="${workflow_path%.md}.lock.yml"
  if [[ ! -f "$lock_path" ]]; then
    lockfile_updates+=("- $workflow_path -> missing $lock_path after compile")
    continue
  fi

  if ! git diff --quiet -- "$lock_path" || ! git diff --cached --quiet -- "$lock_path"; then
    lockfile_updates+=("- $workflow_path -> $lock_path")
  fi
done <<< "$recorded_targets"

if [[ "${#compile_failures[@]}" -gt 0 ]]; then
  message="Agentic workflow compilation failed:
$(printf '%s\n' "${compile_failures[@]}")

Fix the workflow source and rerun \`gh aw compile\` until it succeeds."
  render_json_message false "$message"
  exit 0
fi

if [[ "${#lockfile_updates[@]}" -gt 0 ]]; then
  message="Agentic workflow source file(s) required recompilation:
$(printf '%s\n' "${lockfile_updates[@]}")

The stop hook ran \`gh aw compile\` for these workflows and updated their lock files. Review those generated changes and include them before finishing."
  render_json_message false "$message"
  exit 0
fi

rm -f "$state_file"
