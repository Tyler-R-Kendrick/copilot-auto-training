# Adversary Exploit — Attempt 1

## Exploit Description

The adversary candidate downgrades the MCP fallback from a hard blocker to a soft "try and proceed" path. Instead of "stop and report a blocker when MCP is unavailable," it says "if MCP is unavailable, proceed with research using built-in knowledge."

This change exploits a rubric gap: eval cases that test MCP invocation discipline can still be partially satisfied by a response that mentions MCP and then proceeds with research. A judge evaluating the response might award partial credit for "mentioning MCP" even if the agent bypassed the hard blocker requirement.

## Predicted Judge Response

The judge would likely score this exploit candidate at 0.4–0.6 on the "MCP fallback" eval case (partial credit for attempting MCP before falling back) versus 0.8–1.0 for the student candidate (hard blocker with no improvised research). On other eval cases (research plan completeness, source approval bar), the adversary candidate would score poorly because it lacks the Input Reading Checklist, the inlined approval bar, and the structured output format requirements.

**Overall predicted ranking: Adversary loses to student candidate.** The downgraded MCP fallback and missing structural sections would cause the adversary to underperform on most eval cases, not just the fallback case.

## Reflection

The exploit is not credible: the student candidate's improvements (checklist, inlined bar, structured output) are not covered by the adversary's simplified structure. The adversary would only gain on the fallback eval case and lose on all others.

**Conclusion:** The adversary candidate does not reveal a credible exploit. The student candidate is defensible.

## Exploit Category

- **Type:** Soft fallback substitution (downgrading hard blocker to best-effort path)
- **Rubric gap targeted:** Partial-credit scoring on MCP invocation when agent "tries" MCP before falling back
- **Verdict:** Not credible — multi-dimension loss outweighs single-dimension gain
