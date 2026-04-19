# Adversary Steering — Turn 1

## Evidence Used
- Student candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Exploit 1: Partial MCP Failure → Graceful Degradation Bypass (predicted score 0.93 vs student 0.88)
- Exploit 2: Approval Bar "Provisional Approval" Softening (weaker than Exploit 1)
- Exploit 3: Blocker Report Format Minimalism via Template Over-Specification (slightly weaker)

## Credible Exploit Found: Exploit 1

**Gap targeted**: "all `find_agent_skill` and `load_agent_skill` calls fail" in the MCP fallback paragraph is ambiguous when only one call fails (partial failure). The exploit introduces a "graceful degradation" path for partial failure, making the candidate appear more operationally complete while silently violating the MCP contract.

**Why it outranks the student**: The val.jsonl test case only covers the "both tools fail" case, which the exploit handles correctly. Partial failure has no test coverage, so the judge cannot detect the exploit.

**Fix applied**: Updated MCP fallback guard to cover any individual call failure, not just "all calls fail". Added explicit prohibition on falling back to a local skill copy.

## Blocking Exploit Pattern (for future judge turns)
Any candidate that introduces multi-state MCP failure handling where partial failure (one tool fails) allows continued research — whether via "graceful degradation," "local skill copy," or "best-effort mode" — violates the MCP contract. The correct behavior for any MCP call failure is: report a blocker and stop.

## Stop-or-Continue
Student candidate corrected to block the identified exploit. Continue to validation.
