#!/usr/bin/env bash
set -euo pipefail

payload="$(cat || true)"

if [[ "$payload" != *".prompt.md"* ]] && [[ "$payload" != *".prompty"* ]] && [[ "$payload" != *".instructions.md"* ]] && [[ "$payload" != *"SKILL.md"* ]] && [[ "$payload" != *"AGENTS.md"* ]] && [[ "$payload" != *".agent.md"* ]] && [[ "$payload" != *".evals/"* ]] && [[ "$payload" != *".jsonl"* ]]; then
  printf '%s\n' '{"continue": true}'
  exit 0
fi

if [[ -x ./.venv/bin/python ]]; then
  ./.venv/bin/python -m pytest -q
else
  python -m pytest -q
fi

printf '%s\n' '{"continue": true, "systemMessage": "Prompt-optimization validation passed via python -m pytest -q."}'