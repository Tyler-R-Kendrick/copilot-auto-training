# Adversary Steering Summary — Iteration 1

## Active Iteration
`iterations/iteration-1`

## Turn 1 — Credible Exploit Found and Resolved

**Exploit 1 (Strongest)**: Partial MCP Failure → Graceful Degradation Bypass
- Targets the "all calls fail" guard clause which leaves partial failure undefined
- Predicted score 0.93 (exploit) vs 0.88 (student) — outranks student
- **Resolved**: Student candidate updated to cover any individual call failure and explicitly prohibit local skill copy fallback

**Exploit 2**: Approval Bar "Provisional Approval" — weaker, no test coverage gap
**Exploit 3**: Blocker Template Minimalism — exploits the teacher's identified gap; slightly weaker than Exploit 1

## Blocking Pattern for Future Judge Turns
Any candidate introducing multi-state MCP failure handling where partial failure allows continued research (via graceful degradation, local skill copy, or best-effort mode) violates the MCP contract. Correct behavior: report a blocker for any MCP call failure.
