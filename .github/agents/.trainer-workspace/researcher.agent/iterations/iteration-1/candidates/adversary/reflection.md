## Adversary Reflection

**Strongest exploit attempt:** Over-elicitation trap (caller provides all constraints, checks if agent asks anyway).

**Why it fails:** Approach step 2 is conditional: "If any are missing, ask for them." The student candidate would correctly identify that no constraints are missing and proceed to search. No regression.

**Secondary exploit:** MCP bypass (caller claims skill is unavailable). Fails because find_agent_skill is mandatory regardless of caller claims.

**Exploit vs. student candidate verdict:** Student candidate outranks both exploit attempts. The exploit space has been searched and no credible gap was found.

**Search conclusion:** Exploit space exhausted. No credible exploit that would fool the judge exists against the current student candidate. Proceed to finalization.
