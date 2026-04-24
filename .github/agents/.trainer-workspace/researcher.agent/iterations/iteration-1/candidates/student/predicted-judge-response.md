## Predicted Judge Response — Student Candidate

The judge is likely to score the student candidate as stronger than the original on:
- Row 1 (MCP activation): passes — MCP step is still required first.
- Row 2 (constraint elicitation): passes — explicit required vs elicitable distinction with prescriptive rules.
- Row 3 (approval-bar enforcement): passes — five criteria embedded; partial match is explicitly rejected.
- Row 4 (blocker path): passes — blocker-report template added with failed criteria, missing evidence, stop recommendation.
- Row 5 (run_agent_skill threshold): passes — explicit check for scripts/run_research.py.
- Row 6 (research-brief completeness): passes — six required sections mandated.
- Row 7 (over-elicitation): passes — elicitation rule says to proceed when only optional constraints are absent and would not change source selection.
- Row 8 (regression detection): passes — the MCP activation, constraint-elicitation, and approval-bar contracts are now tighter, making regressions more detectable.

**Potential weaknesses**: 
- The approval-bar language "partially approved is not valid" is implicit (worded as "do not downgrade a rejected source to partially approved") — adversary may find a path where an agent reads this as allowing initial classification as "borderline."
- The elicitation section says "ask only when they would materially change source selection" — adversary may argue this is still ambiguous for edge cases.

Overall: student candidate predicted to score ~82-88% on the eval suite.
