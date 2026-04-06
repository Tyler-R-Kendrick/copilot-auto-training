---
description: "Use when editing prompt and instruction files such as *.prompt.md, *.prompty, *.instructions.md, SKILL.md, AGENTS.md, or *.agent.md. Covers prompt-optimization workflow, dataset expectations, and validation habits."
applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"
---
# Prompt Optimization Guidance

## Interface Rules
- Preserve ALL prompt placeholders exactly as written unless the task explicitly and unambiguously authorizes a prompt interface change — renaming a placeholder such as `{user_query}` to `{query}` breaks the interface contract for all callers.

## Eval Asset Rules
- Keep all authored skill eval cases in the official `evals/evals.json` manifest and supporting input files under `evals/files/`.
- Never include evaluator-only fields — `expected`, `expected_json`, `reference`, `criteria`, or `scoring` — in the prompt body, template, or any prompt-visible render path.
- Apply the eval-manifest authoring guidance whenever editing `evals/evals.json`.
- Keep baseline comparisons and leader-election steps explicit and external to `trainer-optimize`.

## Dataset and Skill Routing Rules
- Always pass explicit `--train-file` and `--val-file` paths to `trainer-optimize`. Never rely on automatic dataset discovery or hidden runtime path conventions.
- When explicit `train.jsonl` and `val.jsonl` files do not yet exist: run `trainer-research` first to identify sources, then run `trainer-synthesize` to convert sources into datasets, then run `trainer-optimize`.
- Use `trainer-election` ONLY to compare multiple externally generated `trainer-optimize` outputs. Do NOT run `trainer-election` after a single optimize pass.

## Judge Mode Selection
- Inspect each dataset row shape before calling `trainer-optimize` and pass `--judge-mode` explicitly:
  - `llm_judge` — row has `reference` and `criteria` fields
  - `custom` — row has `expected_json` or a row-level scoring key such as `normalized_match`, `json_schema`, or `custom_python`
  - `deterministic` — row has only an `expected` field with no richer scoring contract

## Validation
- After every meaningful edit to a prompt-like file, run `python -m pytest -q` from the repository root to confirm no regressions.
