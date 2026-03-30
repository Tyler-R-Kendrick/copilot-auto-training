# Synthesis Plan: judge-rubric

## Target layout

- Reused manifest: `skills/judge-rubric/evals/evals.json`
- Canonical datasets: `skills/judge-rubric/datasets/train.jsonl` and `skills/judge-rubric/datasets/val.jsonl`
- Iteration copies: `skills/judge-rubric/.trainer-workspace/SKILL/iterations/iteration-1/synthesize/train.jsonl` and `skills/judge-rubric/.trainer-workspace/SKILL/iterations/iteration-1/synthesize/val.jsonl`

## Observed inputs

- Current skill contract for baseline wording and policy invariants.
- Existing eval scenarios for outcome-focused, hybrid, and blocker-sensitive rubric requests.
- Deterministic helper contract from `render_rubric.py` and `sample-contract.json`.
- Engineer review recommendations for earlier helper routing, helper-aligned output sections, and compact non-negotiable constraints.

## Derived outputs

- `llm_judge` training rows that reward:
  - earlier recognition of the structured helper path,
  - helper-aligned output sections,
  - explicit evidence-mode mapping,
  - preserved 3 to 7 dimension locking,
  - blocker-first handling when required information is missing,
  - low-trust treatment of unsupported chain-of-thought.

## Computation recipe

1. Normalize the existing eval prompts into concise optimizer task rows.
2. Add one structured-contract row grounded in the sample contract so the helper-first branch is represented explicitly.
3. Add one incomplete-contract validation row grounded in the helper schema so blocker handling is tested without inventing missing fields.
4. Write judged references that describe the required rubric package shape and preserved policy, rather than brittle exact-match prose.

## Verification path

- Every synthesized row is traceable to the repo-owned skill, evals, helper, tests, or engineer review.
- The deterministic helper remains independently verifiable through `scripts/render_rubric.py` and `tests/test_judge_rubric.py`.
- The optimize-stage candidate is only defensible if it preserves the policy core while improving the structural routing and output contract.

## Dataset split

- `train.jsonl`: 4 rows covering outcome-focused rubricing, hybrid evidence mapping, structured-contract helper routing, and blocker-heavy free-form rubricing.
- `val.jsonl`: 2 rows covering incomplete structured contracts and a held-out hybrid comparison request with stronger section-shape expectations.
- All rows are grounded in repo-owned sources. No unverifiable external facts were introduced.

## Provenance note

- Grounded rows: all 6 rows are derived from repo-owned evals, helper assets, tests, and the engineer review.
- Synthetic rows: none.
- Held-out validation rows focus on blocker handling and helper-aligned final output shape.