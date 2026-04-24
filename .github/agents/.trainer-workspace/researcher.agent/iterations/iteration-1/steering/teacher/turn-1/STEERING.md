# Teacher Steering: Turn 1

**Agent:** teacher
**Iteration:** iteration-1
**Turn:** 1

## Evidence Reviewed

1. `engineer-prompt/review.md` — 5 failure modes identified in the baseline researcher.agent.md
2. `iterations/iteration-1/optimize/optimized-prompt.md` — trainer agent's manual_followup candidate
3. `iterations/iteration-1/candidates/adversary/reflection.md` — adversary analysis confirms no credible exploit
4. Training dataset (5 rows) and validation dataset (3 rows) — all use `scoring: "llm_judge"` with `reference` + `criteria`

## Assessment

The student candidate addresses all 5 identified failure modes:
1. ✅ `run_agent_skill` condition clarified
2. ✅ Constraint wording fixed (MCP vs. sibling agents distinguished)
3. ✅ Approach step 2 is now a hard prerequisite
4. ✅ Scope exclusion for eval authoring added
5. ✅ Artifact-saving guidance added to approach and output format

The changes are minimal and surgical — no interface changes, no new placeholders, no evaluator-only fields exposed.

## Predicted Student Mistakes

None credible at this stage. The student candidate is the output of the trainer agent's model_prompt handoff response, which directly addressed each identified failure mode.

## Stop-or-Continue Decision

**STOP** — the student candidate is defensible. The adversary did not reveal a credible exploit. Another iteration would risk over-engineering the contract without measurable improvement against the eval criteria.

## Requested Revision

None. Persist the student candidate to the target file.

## Judge Notes

The student candidate should score 0.7–0.9 against the llm_judge criteria when the judge evaluates MCP routing discipline, scope enforcement, and artifact-saving behavior. The adversary scores 0.1–0.2 and the original scores 0.4–0.5 (MCP routing is present but weaker).
