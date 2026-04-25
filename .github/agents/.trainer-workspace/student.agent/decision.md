# Decision: student.agent.md — Iteration 1

## Outcome: APPLY

**Target file**: `.github/agents/student.agent.md`
**Workspace**: `.github/agents/.trainer-workspace/student.agent/`
**Iteration**: `iteration-1`
**Date**: 2026-04-25

## Winning Candidate

**Source**: `iterations/iteration-1/candidates/student/candidate.md`
**Origin**: Agent-authored in `manual_followup` mode (no external model API available)

## Changes Applied

Seven targeted improvements were applied to the source file:

| # | Failure Mode | Change |
|---|---|---|
| 1 | Revision scope undefined | Added "one section, one critique dimension, one behavioral adjustment" to constraint |
| 2 | No reasoning format guidance | Added CoT/ToT/CoUoT decision criteria to step 3 |
| 3 | Vague approval prediction | Added 3-criteria check (a)(b)(c) to step 6 and constraint |
| 4 | Missing no-critique path | Added explicit teacher handoff when critique is absent |
| 5 | Engineer handoff over-permissive | Added threshold (multi-section OR cross-domain) |
| 6 | No steering artifact priority | Added explicit order to step 1 (turn-scoped > summary > goal) |
| 7 | Output lacks evidence requirement | Output format now cites criteria (a)(b)(c) for approval |

## Adversary Assessment

The adversary candidate used front-loaded quality claims and redundant constraints to inflate perceived
quality. This exploit was not credible against criterion-anchored scoring — it failed criterion (b)
(bounded revision) because it added content outside the named critique dimension. No extra judge
steering is needed to block this exploit.

## Validation Result

`python -m pytest -q`: **856 passed, 0 failed**

## Optimize Mode

`manual_followup` — external model API unavailable. The `@trainer` agent answered the `model_prompt`
directly. Rerun command available in `iterations/iteration-1/optimize/operator-followup.md`.
