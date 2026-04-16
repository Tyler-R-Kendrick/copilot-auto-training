## Student Candidate

The student candidate is the optimized prompt from the manual_followup pass with teacher-guided verification applied.

**Verified additions over original:**
1. Explicit evidence reading order in approach step 1.
2. Elicitation step (approach step 2) that stops before search when constraints are missing.
3. Fallback to loaded skill instructions in BOTH the MCP contract section and approach step 3.
4. Compact source approval bar section directly in the agent (no new placeholders introduced).
5. Blocker-report format named and described in the output format section.
6. `argument-hint` now distinguishes required from recommended from optional inputs.

**Reasoning:**
- Fallback appears in both MCP contract (bullet 3) and approach (step 3), satisfying teacher requirement.
- Approval bar uses no placeholder syntax — only prose bullets.
- Output format section includes parenthetical guidance for the blocker-report shape.
- The candidate predicts teacher approval on all three verification points.
