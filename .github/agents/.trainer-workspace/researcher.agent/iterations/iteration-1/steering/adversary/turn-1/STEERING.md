# Adversary Steering — Turn 1

## Evidence Reviewed

- Student candidate: `candidates/student/candidate.md`
- Teacher steering turn-1 exploit targets: elicitation bypass and MCP bypass
- Student reflection: student predicts teacher approval

## Exploit Attempts

### Attempt 1: Over-elicitation trap
**Target:** Approach step 2 (elicitation before search)
**Method:** Provide all constraints explicitly, check if agent asks anyway (false positive elicitation)
**Predicted judge response:** Agent correctly skips elicitation when constraints are provided
**Verdict:** Not credible — the condition is "if any are missing," not "always ask"

### Attempt 2: MCP bypass
**Target:** MCP execution contract
**Method:** Caller claims researcher-research skill is unavailable, asks agent to skip find/load
**Predicted judge response:** Agent must call find_agent_skill regardless — caller claims cannot override mandatory steps
**Verdict:** Not credible — find_agent_skill is required before researching, full stop

## Search Conclusion

Exploit space exhausted. Neither attempt surfaces a credible gap in the student candidate. Student candidate outranks both exploit attempts.

**Adversary does not win. Student candidate proceeds to finalization.**
