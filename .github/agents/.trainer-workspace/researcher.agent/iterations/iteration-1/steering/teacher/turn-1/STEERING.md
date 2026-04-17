# Teacher Steering — Turn 1

## Evidence Reviewed

- **Target file**: `.github/agents/researcher.agent.md` (baseline)
- **Engineer-prompt review**: `.github/agents/.trainer-workspace/researcher.agent/engineer-prompt/review.md`
- **Training dataset**: 8 rows, all `llm_judge` scoring with `reference` and `criteria`
- **Validation dataset**: 3 rows, same scoring shape
- **Optimized candidate**: `iterations/iteration-1/optimize/optimized-prompt.md`

## Predicted Student Mistakes

Before reviewing the candidate, expected student failure modes:
1. Losing the blocker-report step by folding it into a generic constraint paragraph.
2. Overly verbose output format descriptions that bloat the prompt without adding precision.
3. Keeping the `run_agent_skill` guard ambiguous ("check the loaded contract" without naming what to look for).

## Candidate Review

The optimized candidate addresses all six main risks from the engineer-prompt review:

- **Pre-Research Constraint Check**: Added correctly. The fixed reading order (prompt → task → scoring rule → constraints) is explicit and the blocker condition is clear.
- **`run_agent_skill` guard**: Clarified successfully. The candidate names `scripts/run_research.py` as the specific helper to look for, which is concrete and actionable.
- **Blocker-report step in Approach**: Added as step 1, before `find_agent_skill` is called. Correct position.
- **Synthesis boundary in Scope**: Added clearly. "Stop at mapping notes" is unambiguous.
- **Artifact path guidance**: Added in Approach step 8. Correct.
- **Output format descriptions**: Each section now has minimum content guidance. Depth is appropriate — not too verbose.

## Stop-or-Continue Decision

**Stop**. The candidate applies all six targeted improvements from the engineer-prompt review without introducing regressions. The changes are minimal and surgical. No evidence of student mistakes predicted above was found in the final candidate. Further iteration is not supported by the current evidence.

## Judge Notes

The candidate should score higher on:
- MCP activation rate (explicit pre-MCP constraint check)
- Blocker-report accuracy (step 1 forces gap surfacing)
- Brief completeness (output section descriptions require non-trivial content)

The adversary should check whether the pre-research constraint check could be gamed by an agent that calls find_agent_skill before completing the constraint check.

## Verdict

Accept candidate as the optimized result for this iteration. Proceed to adversary review and validation.
