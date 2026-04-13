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
  echo "Error: expected the repository virtualenv Python at $python_bin so the hook can emit JSON responses. Recreate the repo environment if needed (for example: python3.12 -m venv .venv && source .venv/bin/activate && python -m pip install -r requirements.txt)." >&2
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

default_branch_ref() {
  if git show-ref --verify --quiet refs/remotes/origin/HEAD; then
    git symbolic-ref --quiet --short refs/remotes/origin/HEAD
    return
  fi

  if git show-ref --verify --quiet refs/remotes/origin/main; then
    echo "origin/main"
    return
  fi

  if git show-ref --verify --quiet refs/remotes/origin/master; then
    echo "origin/master"
    return
  fi

  return 1
}

collect_git_changed_targets() {
  git diff --name-only -- '.github/workflows/*.md' 2>/dev/null || true
  git diff --name-only --cached -- '.github/workflows/*.md' 2>/dev/null || true
  git ls-files --others --exclude-standard -- '.github/workflows/*.md' 2>/dev/null || true

  local base_ref
  if base_ref="$(default_branch_ref 2>/dev/null)"; then
    local merge_base
    if merge_base="$(git merge-base HEAD "$base_ref" 2>/dev/null)"; then
      git diff --name-only "$merge_base...HEAD" -- '.github/workflows/*.md' 2>/dev/null || true
    fi
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

normalize_lockfile_writeback_tokens() {
  local workflow_path="$1"
  local lock_path="$2"

  "$python_bin" - "$repo_root/$workflow_path" "$lock_path" <<'PY'
from pathlib import Path
import sys

import yaml

workflow_path = Path(sys.argv[1])
lock_path = Path(sys.argv[2])

workflow_text = workflow_path.read_text(encoding="utf-8")
if not workflow_text.startswith("---\n"):
    raise SystemExit(0)

try:
    _, frontmatter, _ = workflow_text.split("---", 2)
except ValueError:
    raise SystemExit(
        f"{workflow_path}: expected exactly one frontmatter block delimited by leading and closing --- lines"
    )

parsed = yaml.safe_load(frontmatter) or {}
token_fallback = (
    ((parsed.get("safe-outputs") or {}).get("create-pull-request") or {}).get("github-token")
)
# Only workflows that explicitly opt into the COPILOT_GITHUB_TOKEN fallback need
# post-compile normalization; leave all other lockfiles untouched.
if not token_fallback or "COPILOT_GITHUB_TOKEN" not in token_fallback:
    raise SystemExit(0)

lock_text = lock_path.read_text(encoding="utf-8")
compiler_default = "${{ secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}"
normalized = lock_text.replace(compiler_default, token_fallback)
if normalized != lock_text:
    lock_path.write_text(normalized, encoding="utf-8")
PY
}

recorded_targets="$(load_recorded_targets | normalize_targets)"
if [[ -z "$recorded_targets" ]]; then
  recorded_targets="$(collect_git_changed_targets | normalize_targets)"
fi

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

missing_gh_message="Agentic workflow compilation enforcement could not run because \`gh aw\` is unavailable. Install or refresh the extension with \`gh extension install github/gh-aw\` or \`gh extension upgrade gh-aw\`, then run \`gh aw compile\` for the changed workflow files."
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

  normalize_lockfile_writeback_tokens "$workflow_path" "$lock_path"

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
