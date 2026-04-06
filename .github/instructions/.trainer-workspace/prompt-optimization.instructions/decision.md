# Decision Summary — prompt-optimization.instructions.md

## Selected Candidate

`iterations/iteration-1/candidates/student/candidate.md` — the gap-filling 9-bullet revision.

## What Changed

The original 8-bullet instruction file was updated to a 9-bullet version. Changes:

1. **Bullet 3 (dataset paths)**: Replaced "use explicit dataset paths and avoid hidden runtime conventions" with "Pass explicit `train.jsonl` and `val.jsonl` paths to `trainer-optimize`; do not rely on hidden runtime conventions or auto-discovery." — more concrete and actionable.

2. **Bullet 4 (skill routing)**: Replaced the long list-of-skills bullet with an ordered workflow: "When datasets are missing, run `trainer-research` first, then `trainer-synthesize`…then `trainer-optimize`. Use `trainer-election` only to compare multiple optimize outputs — not after a single run." — explicit ordering and election scope.

3. **Bullet 5 (NEW — judge_mode)**: Added "Infer `judge_mode` from the dataset row shape before calling `trainer-optimize`: use `llm_judge` when rows expose `reference` and `criteria`; use `custom` when rows expose `expected_json` or a row-level scoring key; keep `deterministic` only for exact-match `expected` rows."

4. **Bullet 9 (validation)**: Replaced "Re-run the relevant validation command" with "Re-run `python -m pytest -q` from the repository root" — names the command explicitly.

## Gaps Closed

- ✅ Skill routing order (research → synthesize → optimize)
- ✅ `trainer-election` scope limited to multiple outputs
- ✅ `judge_mode` selection rule from row shape (new bullet)
- ✅ Named validation command (`python -m pytest -q`)
- ✅ Explicit dataset paths + no auto-discovery

## Validation

7 pre-existing failures unchanged. 579 tests passed. No regressions introduced.

## Iteration

- Workspace: `.github/instructions/.trainer-workspace/prompt-optimization.instructions/`
- Iteration: `iteration-1`
- Optimize mode: `manual_followup` (no model configured)
- Teacher verdict: STOP after Turn 1 — all 8 training scenarios pass, all 5 gaps closed
- Adversary exploit blocked: H2 section headers (violates flat-bullet convention)
