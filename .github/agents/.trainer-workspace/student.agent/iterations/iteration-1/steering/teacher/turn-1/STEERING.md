# Teacher Steering — Turn 1

## Artifacts Consulted

- `engineer-prompt/review.md` — 7 failure modes identified
- `iterations/iteration-1/synthesize/datasets/train.jsonl` — 8 training examples
- `iterations/iteration-1/synthesize/datasets/val.jsonl` — 4 validation holdout examples
- `iterations/iteration-1/optimize/optimize-report.json` — manual_followup mode
- `iterations/iteration-1/optimize/optimized-prompt.md` — agent-authored candidate

## Evidence

The training data shows consistent failure patterns in the baseline student.agent.md:
1. Revision scope undefined → students over-revise
2. No reasoning format guidance → inconsistent trajectory quality
3. Approval prediction criteria absent → false positives based on "looks good"
4. Missing no-critique path → students speculate without steering
5. Engineer handoff over-permissive → unnecessary delegation
6. No artifact priority order → stale steering applied
7. Output format lacks evidence requirement → vague approval claims

## Recommendation

The student candidate addresses all 7 failure modes with surgical, bounded changes. Each change is
anchored to a specific training criterion. The adversary exploit is not credible against criterion-
anchored scoring.

**Decision**: Apply the student candidate to the source file and proceed to validation.

## Forecasted Student Mistake

The main risk in future iterations: a student might interpret "one section per revision" so strictly
that it refuses to apply obvious minor follow-up corrections in the same session. The guidance should
clarify that the "one section" rule applies per revision action, not per optimization loop run.

## Stop/Continue Decision

**Stop** — the candidate is defensible, addresses all documented failure modes, and validation with
`python -m pytest -q` is the next required step.

## Steering Note

> Student candidate wins iteration-1. All 7 failure modes from engineer-prompt review are addressed.
> Adversary exploit failed criterion (b) — bounded revision. Apply candidate to source file and run
> pytest validation. If validation passes, set workflow_state to complete and open PR.
