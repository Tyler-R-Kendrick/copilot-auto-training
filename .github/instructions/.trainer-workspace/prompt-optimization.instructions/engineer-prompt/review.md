# Engineer-Prompt Review: prompt-optimization.instructions.md

## Target Goal

Improve `prompt-optimization.instructions.md` so that agents editing prompt-like files follow consistent, actionable practices for optimization: preserving placeholders, routing skill calls correctly, keeping evaluator-only fields out of prompt-visible paths, and re-running validation after changes.

## Current State Analysis

The current file contains 8 bullet rules:

1. Preserve prompt placeholders unless the task explicitly changes the prompt interface.
2. Keep authored skill eval cases under `evals/evals.json` and supporting assets under `evals/files/`.
3. When the optimizer runtime needs JSONL data, use explicit dataset paths and avoid hidden runtime conventions.
4. Use the correct trainer-skill for each stage (optimize, election, research, synthesize).
5. Keep evaluator-only fields (`expected`, `expected_json`, `reference`, `criteria`, `scoring`) out of prompt-visible render paths.
6. Keep baseline comparisons explicit and external to `trainer-optimize`.
7. Apply the eval-manifest guidance when editing `evals/evals.json` files.
8. Re-run the relevant validation command after meaningful edits to prompt-like files.

**Gaps identified:**
- No explicit ordering of when to use `trainer-research` vs. `trainer-synthesize` vs. `trainer-optimize` (the default loop order is not stated).
- No guidance on how to choose `judge_mode` from dataset row shape — this is critical to avoid silent mismatch failures.
- No explanation of what "evaluator-only fields out of prompt-visible render paths" means in practice — agents struggle with this abstraction without a concrete example.
- No mention of the workspace contract or where generated artifacts belong.
- No guidance on what validation command to run and where (e.g., `python -m pytest -q` from repo root).
- The skill routing rule (bullet 4) lists skills but gives no trigger condition — an agent cannot determine when each skill is needed without additional context.
- No guidance on what to do when `trainer-optimize` returns `mode=manual_followup`.
- No clarification that `trainer-election` is only for *external* leader selection across multiple optimize outputs, not for single-run optimization.

## Likely Failure Modes

1. **Wrong skill for stage**: Agent calls `trainer-synthesize` when research is still missing, or calls `trainer-election` after a single optimize run.
2. **Judge-mode mismatch**: Agent runs `trainer-optimize` with `judge_mode=deterministic` on `llm_judge`-shaped rows, producing misleading scores.
3. **Evaluator field leak**: Agent includes `expected`, `criteria`, or `scoring` fields in a prompt template or render context, polluting the model's view.
4. **Hidden JSONL convention**: Agent relies on auto-discovered datasets instead of passing explicit `train.jsonl` / `val.jsonl` paths.
5. **Placeholder mutation**: Agent silently strips or renames a placeholder while editing a prompt, breaking the prompt interface.
6. **Stale validation**: Agent edits a prompt file but forgets to rerun `python -m pytest -q` before committing.
7. **Workspace scatter**: Agent saves optimizer artifacts outside the designated local `.trainer-workspace/<prompt-name>/` tree.
8. **Manual-followup not handled**: Agent treats `mode=manual_followup` as a failure and stops instead of answering the returned `model_prompt`.

## Dataset Gaps

- No concrete example illustrating the difference between evaluator-only fields and prompt-visible fields.
- No worked example of the correct `judge_mode` selection from a sample dataset row.
- No example of an explicit `train.jsonl` / `val.jsonl` path reference vs. an implicit convention.
- No example showing a placeholder that should be preserved vs. one that can be legitimately changed.

## Optimization Hypothesis

The instruction file can be improved by:
1. Adding a concise trigger table or ordered checklist mapping dataset state → correct skill stage.
2. Adding an explicit `judge_mode` selection rule (llm_judge for `reference`+`criteria`, custom for `expected_json`, deterministic for exact-match `expected`).
3. Clarifying "evaluator-only fields out of prompt-visible render paths" with a one-line concrete example.
4. Naming the default validation command explicitly: `python -m pytest -q` from the repository root.
5. Adding a one-liner note that `trainer-election` is for comparing *multiple* optimize outputs, not for a single run.
6. Adding a one-liner on `manual_followup`: treat it as a deterministic fallback, answer `model_prompt`, save as `optimized-prompt.md`.
7. Keeping the file concise — these are tightly scoped coding instructions, not a full workflow narrative.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying changes. The instruction file itself is not directly tested, but the test suite confirms no regressions in supporting Python code. Validate that the frontmatter `applyTo` glob and `description` remain intact after edits.

## Next Optimization Iteration

- Narrow each rule to one concrete, actionable statement.
- Add judge_mode selection guidance.
- Add explicit skill-stage trigger conditions.
- Clarify validation command.
- Keep total line count comparable to current file (conciseness is a design constraint for instruction files).
