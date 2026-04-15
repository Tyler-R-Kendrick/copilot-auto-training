## Student Candidate Description

This candidate addresses all five engineer-review priorities from the manual-followup optimization pass:

1. **`run_agent_skill` threshold**: added explicit check — if `scripts/run_research.py` exists in the skill directory, call `run_agent_skill`; otherwise use loaded skill instructions as the operating contract.
2. **Constraint resolution**: added a dedicated "Constraint Resolution" section distinguishing required inputs (task boundary, scoring rule, placeholders) from elicitable ones (domain, language, recency), with prescriptive elicitation rules.
3. **Approval bar**: embedded five key criteria directly in the agent under a "Source Approval Bar" section, removing dependence on the loaded skill contract for gating decisions.
4. **Blocker-report template**: added to the output format with content specification (failed criterion, missing evidence, stop recommendation).
5. **Minimum output scope**: six required output sections are now explicitly mandated.

**Structural change**: minimal — additions only, no section removals, role and scope unchanged.
