# Teacher Steering — Turn 1

## Evidence Reviewed

- **Target file**: `.github/agents/student.agent.md`
- **Engineer-prompt review**: `engineer-prompt/review.md` (5 risk areas, 7 rewrite hypotheses)
- **Training dataset**: 6 cases covering: evidence reading order, teacher handoff on missing steering, scope check, reasoning trajectory, insertion point selection, STEERING.md priority over summary.md
- **Validation dataset**: 2 cases covering: self-check termination, STEERING.md verification overriding prose approval
- **Optimized candidate**: `iterations/iteration-1/optimize/optimized-prompt.md`
- **Optimize mode**: `manual_followup` (no inference model configured)

## Predicted Response

The optimized candidate resolves all 5 risk areas identified in the engineer review:
1. **Evidence reading order** — added explicit prioritized steps (STEERING.md → summary.md → candidate → workspace)
2. **Scope check** — added pre-edit scope confirmation with blocker reporting for out-of-scope files
3. **Stale critique signal** — replaced vague "stale" with a concrete timestamp comparison rule
4. **Self-check termination** — added explicit cap: after one self-check, hand off unconditionally
5. **Validation step** — added `python -m pytest -q` plus diff review as the default validation
6. **Candidate persistence** — added explicit instruction to save to `candidates/student/` and record the path

The revision is minimal: it adds 7 concrete improvements without changing the agent's interface, frontmatter, or overall scope. No new tools, agents, or handoffs are introduced.

## Requested Revision

No further revision needed at this turn. The candidate addresses all engineer-review gaps. Teacher approves with one observation:

- The scope check in Approach step 3 duplicates the constraint bullet. This is acceptable — the constraint states the rule, the approach step makes it operational. No change needed.

## Stop-or-Continue Decision

**Stop.** The candidate is defensible and ready for adversarial review and validation. No additional student revision turn is warranted.

## Judge Notes

- The candidate should score higher than baseline on evidence reading order compliance, scope discipline, teacher handoff correctness, and self-check termination adherence.
- The no-op justification behavior (constraint: "Report a justified no-op when the supplied evidence does not support a better candidate") is unchanged and correct.
