# Decision Summary: student.agent.md — Iteration 1

## Target File
`.github/agents/student.agent.md`

## Decision
**Student candidate accepted.** Written back to source file. Validated with `python -m pytest -q`: 856 tests pass.

## What Changed

The original student agent had 7 gaps identified by the engineer-prompt review, plus 3 additional definition gaps surfaced by the adversary.

### Changes Applied (10 improvements, one targeted rewrite)

1. **Evidence priority order** (step 1): Added numbered 1–5 list with explicit tiebreaker — most recent STEERING.md wins.
2. **No-op check** (step 3): New explicit gate — if STEERING.md contains no critique items, declare no-op rather than drafting speculatively.
3. **Structural self-check** (step 7): Replaced subjective exit criteria ("unsupported/incomplete/misaligned") with three checkable gates: (a) all STEERING.md items addressed, (b) no new scope, (c) positive approval prediction.
4. **Validation definition** (step 8): Three concrete checks — placeholder tokens preserved, no constraints removed without justification, no syntax errors; noted as minimum floor, not replacement for teacher review.
5. **Engineer handoff trigger**: Sharpened to two concrete conditions; explicit exclusion for minor wording changes.
6. **Deferral constraint**: Added parenthetical defining "explicitly re-raises" as direct naming in STEERING.md — thematic proximity alone does not qualify.
7. **Step numbering**: Promoted step 2b to full step 3; all subsequent steps renumbered 3–8.
8. **Constraint scope rule**: Added "address only current STEERING.md items; defer older-summary items unless re-raised."
9. **"New scope" definition** (step 7 self-check): Added one-line definition — capability or constraint category not cited in STEERING.md and not already in source prompt.
10. **No-op condition precision** (step 3): Clarified "no critique items" as the trigger (qualitative, no false-precision threshold).

## Validation

`python -m pytest -q` → **856 passed, 0 failed**

Test `test_student_agent_contract_structure` updated to match improved engineer handoff text.

## Iteration Artifacts

- `engineer-prompt/review.md` — 7-gap analysis
- `iterations/iteration-1/research/research-brief.md` — 5 approved sources (Self-Refine, ProTeGi, OPRO, PRM800K, DSPy)
- `iterations/iteration-1/synthesize/evals/evals.json` — 6 eval cases
- `iterations/iteration-1/synthesize/datasets/train.jsonl` — 4 rows
- `iterations/iteration-1/synthesize/datasets/val.jsonl` — 2 rows
- `iterations/iteration-1/optimize/manual-followup-report.json`
- `iterations/iteration-1/optimize/optimized-prompt.md` — final candidate
- `iterations/iteration-1/steering/teacher/turn-1/STEERING.md` — all 7 gaps confirmed
- `iterations/iteration-1/steering/adversary/turn-1/STEERING.md` — 3 exploit surfaces blocked
- `iterations/iteration-1/candidates/candidates.json`
- `iterations/iteration-1/validation/pytest.txt` — 856 passed
