#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$repo_root"

python_bin="/workspaces/copilot-apo/.venv/bin/python"
scan_all=0
if [[ "${1:-}" == "--all" ]]; then
  scan_all=1
  shift
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

should_validate() {
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue

    case "$line" in
      */skills/*/SKILL.md|skills/*/SKILL.md)
        return 0
        ;;
    esac
  done

  return 1
}

inputs="$(collect_candidates "$@")"

if [[ "$scan_all" -eq 0 ]]; then
  if [[ -z "$inputs" ]]; then
    exit 0
  fi

  if ! printf '%s\n' "$inputs" | should_validate; then
    exit 0
  fi
fi

"$python_bin" -c '
import json
import re
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
skills_root = repo_root / "skills"
skill_files = sorted(path for path in skills_root.glob("*/SKILL.md") if path.is_file())
skill_names = sorted(path.parent.name for path in skill_files)
patterns = {
    name: re.compile(rf"(?<![A-Za-z0-9-]){re.escape(name)}(?![A-Za-z0-9-])")
    for name in skill_names
}

violations = []
for skill_file in skill_files:
    current_name = skill_file.parent.name
    text = skill_file.read_text(encoding="utf-8")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for other_name in skill_names:
            if other_name == current_name:
                continue
            if patterns[other_name].search(line):
                rel_path = skill_file.relative_to(repo_root).as_posix()
                violations.append((rel_path, line_number, other_name, line.strip()))

if not violations:
    raise SystemExit(0)

lines = [
    f"- {path}:{line_number} references `{other_name}` -> {source}"
    for path, line_number, other_name, source in violations
]
message = (
    "Agent skill isolation policy violated in canonical skill contracts:\n"
    + "\n".join(lines)
    + "\n\nCanonical skills/*/SKILL.md files may describe prerequisites, upstream inputs, or downstream workflows generically, but they must not name other agent skills."
)
print(json.dumps({"continue": False, "stopReason": message, "systemMessage": message}))
' "$repo_root"
