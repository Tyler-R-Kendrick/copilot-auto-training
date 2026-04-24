# Adversary Exploit: Missing Constraint → Proceed Anyway

## Exploit Description

The strongest exploit targets the **Pre-Research Input Collection** section in the student candidate. The student candidate's improvement correctly adds a fixed reading order and a blocker condition. However, the exploit demonstrates that an agent following the student prompt could bypass the blocker by "proceeding with reasonable assumptions" — which the adversary candidate demonstrates by removing the explicit blocker condition and replacing it with "proceed with reasonable assumptions."

This exploit directly negates the primary improvement in the student candidate. The adversary candidate looks superficially similar: it has the same reading order list and activates `researcher-research` via MCP. But it removes the critical blocker gate ("surface it as a blocker immediately, ask for clarification, do not proceed") and substitutes "proceed with reasonable assumptions," which is exactly the behavior the student candidate was designed to prevent.

**Exploit surface**: The `run_agent_skill` call in the adversary candidate also removes the guard clause check (whether the loaded skill contract mentions a scripts/ helper). It unconditionally calls `run_agent_skill`, which could fail or behave incorrectly if the helper is not present.
