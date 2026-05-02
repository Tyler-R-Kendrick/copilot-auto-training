# Decision: student.agent.md — iteration-1

## Outcome: Apply Student Candidate

**Date**: 2026-05-02  
**Target**: `.github/agents/student.agent.md`  
**Workspace**: `.github/agents/.trainer-workspace/student.agent/`  
**Iteration**: iteration-1

## Selection Rationale

The student candidate from the manual_followup optimize pass was selected. The adversary candidate's exploit (replacing the contradiction exit and precedence rule with "synthesize both perspectives") was credible but did not outrank the student candidate on the full evaluation dataset, particularly training case 6 (contradiction handling).

## Changes Applied

Seven improvements from the engineering review were applied:

1. **Explicit evidence reading order**: Five-step priority sequence (iteration goal → STEERING.md → summary.md → candidate → validation evidence)
2. **Artifact precedence rule**: Turn-scoped STEERING.md takes priority over rolling summary.md
3. **Sharpened engineer handoff trigger**: Three specific conditions replace the vague original
4. **Defined smallest defensible revision**: One change per iteration goal, verifiable against current steering, narrow enough for single-pass review
5. **Teacher-approval criteria**: Four explicit approval conditions
6. **Revision scope boundary**: Fix only what the iteration goal and critique address; note adjacent issues but do not fix them
7. **Contradiction exit**: Two consecutive unresolved teacher turns → blocker report

## Validation

- `python -m pytest -q`: **856 passed, 0 failed**
- All pre-existing tests pass including `test_student_agent_contract_structure`

## Artifacts

- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Optimize mode: `manual_followup` (no model credentials in CI)
- Blocker report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Teacher steering: `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
- Adversary analysis: `iterations/iteration-1/candidates/adversary/`
- Candidate manifest: `iterations/iteration-1/candidates/candidates.json`
