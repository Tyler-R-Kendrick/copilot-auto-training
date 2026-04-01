#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

python_bin="$repo_root/.venv/bin/python"
workspace_helper="$repo_root/.github/hooks/trainer-workspace.py"

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

is_prompt_like() {
  local path="$1"

  case "$path" in
    *.prompt.md|*.prompty|*.instructions.md|*.agent.md|*/SKILL.md|*/AGENTS.md|*/copilot-instructions.md)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

prompt_name_for() {
  local path="$1"
  local base
  base="$(basename "$path")"

  case "$base" in
    *.md)
      printf '%s\n' "${base%.md}"
      ;;
    *.prompty)
      printf '%s\n' "${base%.prompty}"
      ;;
    *)
      printf '%s\n' "${base%.*}"
      ;;
  esac
}

workspace_root_for() {
  local rel_path="$1"
  local parent_dir
  parent_dir="$(dirname "$rel_path")"

  if [[ "$parent_dir" == "." ]]; then
    printf '%s\n' ".trainer-workspace/$(prompt_name_for "$rel_path")"
    return
  fi

  printf '%s\n' "$parent_dir/.trainer-workspace/$(prompt_name_for "$rel_path")"
}

read_status_state() {
  local status_path="$1"

  if [[ ! -f "$status_path" ]]; then
    return 0
  fi

  "$python_bin" -c 'import json, pathlib, sys; path = pathlib.Path(sys.argv[1]); data = json.loads(path.read_text(encoding="utf-8")); print(data.get("workflow_state", ""))' "$status_path"
}

inputs="$(collect_candidates "$@")"

if [[ -z "$inputs" ]]; then
  exit 0
fi

targets=()
messages=()
while IFS= read -r raw_path; do
  [[ -z "$raw_path" ]] && continue

  abs_path="$raw_path"
  if [[ "$abs_path" != /* ]]; then
    abs_path="$repo_root/$abs_path"
  fi

  [[ -e "$abs_path" ]] || continue

  rel_path="$(realpath --relative-to="$repo_root" "$abs_path")"
  [[ "$rel_path" != ..* ]] || continue

  if ! is_prompt_like "$rel_path"; then
    continue
  fi

  workspace_rel="$(workspace_root_for "$rel_path")"
  workspace_abs="$repo_root/$workspace_rel"
  status_path="$workspace_abs/workflow-status.json"
  current_state="$(read_status_state "$status_path")"

  if [[ "$current_state" == "training" ]]; then
    continue
  fi

  next_state="pending_engineer_prompt"
  next_step="Run /engineer-prompt, save its review to $workspace_rel/engineer-prompt/review.md, update workflow-status.json to pending_training, then run @trainer."
  if [[ "$current_state" == "pending_training" ]]; then
    next_state="pending_training"
    next_step="Run @trainer and have it use $workspace_rel for iterations/iteration-N artifacts, per-turn steering/turn-N/STEERING.md files, the rolling STEERING.md summary, benchmarks, and workflow-status.json updates."
  fi

  "$python_bin" "$workspace_helper" init \
    --repo-root "$repo_root" \
    --target-file "$rel_path" \
    --state "$next_state" >/dev/null

  targets+=("$rel_path")
  messages+=("- $rel_path -> $workspace_rel ($next_state)\n  $next_step")
done <<< "$inputs"

if [[ "${#targets[@]}" -eq 0 ]]; then
  exit 0
fi

printf '%s\0' "${messages[@]}" | "$python_bin" -c '
import json
import sys

entries = [item for item in sys.stdin.read().split("\0") if item]
bullet_list = "\n".join(entries)
message = (
    "Prompt-like file(s) were created or updated:\n"
    f"{bullet_list}\n\n"
    "Required follow-up workflow:\n"
  "1. Run /engineer-prompt against each changed prompt-like file and save the review under engineer-prompt/review.md inside the local .trainer-workspace folder.\n"
  "2. Keep stable prompt snapshots and any reused dataset references under inputs/, including the copied source snapshot under inputs/source/, and update workflow-status.json to pending_training once the review artifact is saved.\n"
  "3. Then run @trainer, which must reuse that same .trainer-workspace tree for repo-specific iterations/iteration-N artifacts: research notes, synthesized evals/datasets, optimize reports, per-turn steering/turn-N/STEERING.md files, the rolling STEERING.md summary, validation logs, and the final decision summary in decision.md.\n\n"
    "This hook injects the workflow and local workspace path because hooks can run shell commands and system messages, but cannot directly launch slash skills or @agents on their own."
)
print(json.dumps({"continue": True, "systemMessage": message}))
'
