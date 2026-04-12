# Prompt Loop Contract

This reference defines the routing table, judge-mode rules, and prompt-specific validation constraints for the trainer-train-prompt skill.

## Target type

- `*.prompt.md` — markdown prompt files
- `*.prompty` — prompty artifacts (strip the extension entirely to derive `<prompt-name>`)
- `*.instructions.md` — instruction files
- System prompts embedded in skill or agent files when extracted as standalone targets

## Workspace derivation

Use `.github/hooks/trainer-workspace.py` (`prompt_name_for`) as the canonical source:
- Strip `.prompty` entirely (e.g., `draft.prompty` → `draft`).
- Strip only `.md` for all other `.md` files (e.g., `summarize.prompt.md` → `summarize.prompt`; `triage.instructions.md` → `triage.instructions`).
- For any other extension, use `Path.stem` (strip only the final extension).
- Use `<target-dir>/.trainer-workspace/<prompt-name>/` as the workspace root.

## Required checkpoint

Require `engineer-prompt/review.md` before any optimization pass. If absent, set `workflow_state: pending_engineer_prompt` and report a blocker.

## Judge-mode routing table

| Row shape | Inferred mode |
|-----------|--------------|
| Explicit `scoring: exact_match` | `deterministic` |
| Explicit `scoring: llm_judge` | `llm_judge` |
| Explicit `scoring` (any other value) | Use that value as authoritative |
| `reference` + `criteria` fields, no explicit `scoring` | `llm_judge` |
| `expected` field only, task has one correct answer | Consider `deterministic`; default to `llm_judge` if ambiguous |
| No scoring fields | Default to `llm_judge` for prompt targets |

When train and validation splits imply different modes, stop and report dataset inconsistency.

## Prompt-specific validation rules

### Placeholder preservation

Before write-back:
1. Extract all template placeholders from the original source (e.g., `{{variable}}`, `{input}`, `<PLACEHOLDER>`).
2. Confirm every placeholder appears in the candidate with the same name and in a compatible position.
3. Reject any candidate that removes, renames, or reorders template placeholders.

### Evaluator field isolation

Confirm these fields do not appear in the optimized prompt text:
- `expected`
- `reference`
- `criteria`
- `scoring`

These are evaluator-only fields and must never appear in the prompt-visible render path.

### Few-shot and chain-of-thought preservation

When the original prompt contains example pairs or step-by-step reasoning traces:
- Preserve the structural pattern (not necessarily the exact examples).
- Do not flatten multi-turn or chain-of-thought structures into a single instruction block.

## Write-back gate

Write back only when all of the following are true:
1. Validation passes (e.g., `python -m pytest -q` exits 0).
2. Placeholder preservation confirmed.
3. Evaluator fields absent from candidate text.
4. Decision summary written at `<workspace-root>/decision.md`.
