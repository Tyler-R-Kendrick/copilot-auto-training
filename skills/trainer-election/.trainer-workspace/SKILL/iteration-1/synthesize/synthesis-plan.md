# Synthesis Plan: trainer-election

## Target layout

- Reused manifest: `skills/trainer-election/evals/evals.json`
- Canonical datasets: `skills/trainer-election/datasets/train.jsonl` and `skills/trainer-election/datasets/val.jsonl`
- Iteration copies: `skills/trainer-election/.trainer-workspace/SKILL/iteration-1/synthesize/train.jsonl` and `skills/trainer-election/.trainer-workspace/SKILL/iteration-1/synthesize/val.jsonl`

## Observed inputs

- Current skill contract for operator-facing wording.
- Runtime behavior from `scripts/run_election.py`.
- Behavioral edge cases from `tests/test_election.py`.
- Existing authored eval scenarios from `evals/evals.json`.
- Engineering review findings about prerequisite clarity and section overlap.

## Derived outputs

- APO rows that test whether the skill instructions reliably surface:
  - scored-artifact preconditions,
  - accepted workspace layouts,
  - manifest discovery behavior,
  - coverage penalties,
  - baseline visibility,
  - benchmark fallback,
  - tie-breakers,
  - persisted winner metadata.

## Computation recipe

1. Normalize the repo-owned runtime and tests into concise operator tasks.
2. Group tasks by prerequisite handling, workspace discovery, scoring and tie-break logic, and output contract.
3. Write judged reference answers that preserve runtime semantics without changing the output schema.
4. Split broader operator-clarity scenarios into train and hold out the highest-risk contract checks for validation.

## Verification path

- The content of every reference answer is traceable to the current runtime, tests, eval manifest, or engineer review.
- The optimize-stage candidate will be treated as justified only if it preserves the same contract while improving clarity.

## Dataset split

- `train.jsonl`: 4 rows covering prerequisites, benchmark fallback, nested `runs/` layouts, and tie-breaks.
- `val.jsonl`: 2 rows covering accepted workspace shapes plus explicit output schema expectations.
- All rows are grounded in repo-owned sources; no unverifiable synthetic domain facts were introduced.

## Provenance note

- Grounded rows: all 6 rows are derived from repo-owned runtime/tests/evals/review artifacts.
- Synthetic rows: none.
- Held out validation rows focus on contract summary and output-field fidelity.