---
description: "Use when editing prompt and instruction files such as *.prompt.md, *.prompty, *.instructions.md, SKILL.md, AGENTS.md, or *.agent.md. Covers prompt-optimization workflow, dataset expectations, and validation habits."
applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"
---
# Prompt Optimization Guidance

- Preserve prompt placeholders unless the task explicitly changes the prompt interface.
- Keep authored skill eval cases under `evals/evals.json` and supporting assets under `evals/files/`.
- Pass explicit `train.jsonl` and `val.jsonl` paths to `trainer-optimize`; do not rely on hidden runtime conventions or auto-discovery.
- When datasets are missing, run `researcher` first, then `trainer-synthesize` to create the datasets, then `trainer-optimize`. Use `trainer-election` only to compare multiple optimize outputs — not after a single run.
- Infer `judge_mode` from the dataset row shape before calling `trainer-optimize`: use `llm_judge` when rows expose `reference` and `criteria`; use `custom` when rows expose `expected_json` or a row-level scoring key; keep `deterministic` only for exact-match `expected` rows.
- Keep evaluator-only fields — `expected`, `expected_json`, `reference`, `criteria`, `scoring` — out of prompt-visible render paths.
- Keep baseline comparisons explicit and external to `trainer-optimize` when a workflow chooses to compare multiple revisions.
- Apply the eval-manifest guidance when editing `evals/evals.json` files.
- Re-run `python -m pytest -q` from the repository root after meaningful edits to prompt-like files.
