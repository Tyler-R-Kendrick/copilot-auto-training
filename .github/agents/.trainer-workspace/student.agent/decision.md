# Decision: student.agent.md Optimization — Iteration 1

**Date:** 2026-04-24

## Target

`.github/agents/student.agent.md`

## Winner

The optimized candidate from `iterations/iteration-1/candidates/student/candidate.md` is applied.

## Changes applied

1. **Evidence reading order** — Added explicit 4-step numbered reading order (STEERING.md → summary.md → candidate → critique) with a stop-reading condition. (Approach Step 1)
2. **Teacher-handoff trigger** — Replaced vague "whenever critique is incomplete/contradictory/stale" with three observable workspace conditions: no active STEERING.md, ambiguous STEERING.md, or conflicting artifacts. Added "do not use for general uncertainty" guard.
3. **Three-outcome self-check** — Added concrete (a/b/c) stopping rule to both Constraints and Approach Step 6. Eliminates infinite-loop and premature-stop failure modes.
4. **Scope boundary definition** — Added inline definition of "smallest defensible revision": phrasing, section order, constraint wording, output structure only — not new sections, removed fields, new handoffs, or task framing changes.
5. **Engineer-handoff deduplication** — Consolidated condition into Constraints only; Approach Step 5 now cross-references Constraints instead of repeating the condition.
6. **Fixed output template** — Replaced unstructured "State the..." list with six labeled sections: Steering followed, Reasoning trajectory, Revision, Engineer handoff (if used), Predicted teacher approval, Validation result.
7. **Missing-steering fallback** — Added Approach Step 2: when no active-iteration STEERING.md exists, summarize candidate state and request trainer initialization. Do not invent a revision target.

## Teacher review outcome

- Issues 1, 2, 3, 4, 6, 7: ✅ Correctly fixed in first pass
- Issue 5 (engineer-handoff duplication): ⚠️ Partially fixed — one targeted student turn applied to remove the self-contradictory meta-sentence and replace the Approach Step 5 duplicate with a cross-reference

## Adversary review

Pending at time of validation pass. Results to be recorded in `iterations/iteration-1/steering/adversary/` once available.

## Validation

`python -m pytest -q`: **856 passed**, 0 failed

## Artifact paths

- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Optimize report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Operator followup: `iterations/iteration-1/optimize/operator-followup.md`
- Teacher steering: `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
- Student steering: `iterations/iteration-1/steering/student/turn-1/STEERING.md`
- Validation log: `iterations/iteration-1/validation/pytest.txt`
