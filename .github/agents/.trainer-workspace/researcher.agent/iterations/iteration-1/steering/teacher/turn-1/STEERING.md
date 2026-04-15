# Teacher Steering — Iteration 1, Turn 1

## Evidence Inspected

1. **Engineer review** (`engineer-prompt/review.md`): identified five rewrite priorities — vague `run_agent_skill` threshold, implicit constraint resolution, absent approval bar, missing blocker-report template, and no minimum output scope.
2. **Original prompt** (`.github/agents/researcher.agent.md`): the current agent has the correct role scoping and MCP contract structure but leaves the constraint-resolution contract, approval bar, and blocker path implicit.
3. **Dataset rows** (train.jsonl, val.jsonl): all 8 rows test MCP activation, constraint elicitation, approval-bar enforcement, blocker recall, `run_agent_skill` threshold, research-brief completeness, over-elicitation, and conservator-style regression detection. All use `llm_judge` scoring.
4. **Manual-followup report**: confirms the target has no task-input placeholders; APO cannot inject per-row task content. The candidate must be authored manually.

## Predicted Student Mistakes

- Expanding scope beyond research (e.g., adding synthesis steps to the agent)
- Rewriting the entire structure rather than making targeted additions
- Using hedging language ("may", "might") instead of prescriptive rules
- Omitting the distinction between required and elicitable constraints
- Forgetting the blocker-report template in the output format section

## Requested Revision

The optimized candidate draft addresses all five engineer-review priorities:
1. **`run_agent_skill` threshold** — made explicit: check for `scripts/run_research.py`, call `run_agent_skill` if present, otherwise use loaded instructions.
2. **Constraint resolution** — added a dedicated section distinguishing required (task boundary, scoring rule, placeholders) from elicitable (domain, language, recency) inputs with clear elicitation rules.
3. **Approval bar** — embedded five key criteria directly in the agent so the model does not depend solely on the loaded skill contract for gating decisions.
4. **Blocker-report template** — added to the output format section with content specification (failed criterion, missing evidence, recommendation to stop).
5. **Minimum output scope** — all six required sections are now named explicitly in the output format.

## Assessment

The draft candidate addresses all five rewrite priorities with minimal structural change. The role and scope remain unchanged. The additions are prescriptive rather than advisory, which is the right tone for an agent instruction file.

## Stop or Continue

**Continue to adversary turn.** The candidate is defensible but should be stress-tested before finalizing: specifically, whether the approval bar language could be gamed by an agent that approves weak sources using partial criteria, and whether the elicitation section could cause over-elicitation when the task is already well-specified.

## Judge Notes

- If the adversary produces a credible exploit against the approval-bar section (e.g., approving sources with partial criteria), add explicit guidance that "partially approved" is not a valid classification.
- If the adversary exploits the elicitation section (e.g., asking for optional constraints even when the task is clear), tighten the elicitation rule to say "proceed if only optional constraints are absent and they would not change source selection."
