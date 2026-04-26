# Decision: student.agent.md — iteration-1

**Date**: 2026-04-26
**Target**: `.github/agents/student.agent.md`
**Iteration**: iteration-1
**Workspace**: `.github/agents/.trainer-workspace/student.agent/`

## Outcome

**Winner: Student candidate** (optimized via manual_followup)
**Validation**: 856 passed, 0 failed

## Changes Applied

Six targeted improvements from the engineer-prompt review were applied to `.github/agents/student.agent.md`:

1. **Evidence reading order** (Approach step 1): Numbered order with two-level STEERING.md fallback.
2. **Unclear target criteria** (Approach step 2): Three enumerable failure modes replace implicit "if unclear."
3. **No-op conditions** (Constraints): Four specific conditions replace vague "evidence does not support."
4. **Engineer handoff threshold** (body + step 4): "More than two sentences" threshold replaces permissive condition.
5. **Section-scoping constraint** (Constraints): Single-critique rule + section-scoping added.
6. **Validation step** (step 7): `python -m pytest -q` with concrete reporting replaces vague "measurement step."

## Teacher Review

All 6 gaps closed. No further student revision needed. Residual watch items: implicit-threshold no-op condition; "two sentences" engineer heuristic.

## Adversary Review

Credible 3-surface exploit found (predicted score 0.85 vs student 0.75 under `judge-default.md`). Exploit surfaces:
- Teacher handoff bypass via "unambiguous workspace evidence" escape
- "Shared root cause" scope-creep loophole  
- Silent removal of engineer skill ban + conditional pytest gate

**Student candidate is defensible**: its existing protections (unconditional handoff, explicit engineer ban, unconditional pytest gate) correctly block all three exploit surfaces. Anti-exploit steering added to workspace.

## Key Artifacts

- Optimized source: `.github/agents/student.agent.md`
- Manual-followup report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Teacher steering: `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
- Candidates manifest: `iterations/iteration-1/candidates/candidates.json`
- Validation log: `iterations/iteration-1/validation/pytest.txt`
