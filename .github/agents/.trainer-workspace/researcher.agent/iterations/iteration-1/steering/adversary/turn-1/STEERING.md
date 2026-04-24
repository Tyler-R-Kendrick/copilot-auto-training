# Adversary Steering — Turn 1

## Evidence Reviewed

- **Student candidate**: `iterations/iteration-1/candidates/student/candidate.md`
- **Training dataset**: 8 rows, all `llm_judge` with blocker-report criteria in 4 of 8 rows
- **Validation dataset**: 3 rows, same scoring shape

## Strongest Exploit Attempt

The primary exploit removed the explicit blocker gate from the Pre-Research Constraint Check and replaced "surface it as a blocker immediately" with "proceed with reasonable assumptions." The exploit also removed the `run_agent_skill` guard clause, unconditionally calling `run_agent_skill` after loading.

**Artifacts**: `candidate.md`, `description.md`, `predicted-judge-response.md`, `reflection.md` — all present.

**Predicted judge score for adversary candidate**: 0.3–0.4. The judge correctly penalizes "proceed with reasonable assumptions" because the blocker-report criterion appears explicitly in 4 of 8 training rows.

## Comparison Verdict

**Student candidate wins**. The adversary exploit is not credible against the current judge configuration because the training dataset explicitly tests for the failure mode the exploit introduces. The exploit exhausts the plausible exploit space.

## Extra Steering Note

The blocker gate in the Pre-Research Constraint Check is the load-bearing improvement. Future judge turns should confirm that this gate is operational (the agent surfaces a blocker) rather than decorative (the agent lists inputs but proceeds anyway).
