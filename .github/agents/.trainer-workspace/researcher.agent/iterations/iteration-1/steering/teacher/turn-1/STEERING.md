# Teacher Steering — Turn 1

## Evidence Reviewed

- Baseline: `.github/agents/researcher.agent.md`
- Engineer review: `engineer-prompt/review.md`
- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Dataset rows: 8 eval cases (6 train, 2 val)
- Original candidate reflection: `candidates/original/reflection.md`

## Predicted Response of Optimized Candidate

The optimized candidate adds:
1. Explicit evidence reading order (target → task description → scoring rule → constraints)
2. Elicitation step before searching when constraints are missing
3. Explicit fallback: "use loaded skill instructions as the active operating contract"
4. Compact source approval bar section
5. Blocker-report named in the output format

**Predicted scores:**
- Case 1 (elicitation-first): 0.9 — elicitation is now an explicit approach step
- Case 2 (MCP activation + 6-section brief): 0.9 — unchanged from baseline
- Case 3 (fallback when script unavailable): 0.9 — fallback is now explicit in both MCP contract and approach
- Case 4 (blocker report shape): 0.9 — blocker report format is now named in output section
- Case 5 (prompt interface first): 0.9 — evidence reading order now explicit
- Case 6 (bias/contamination constraints): 0.85 — approval bar now includes contamination risk
- Case 7 (HIPAA compliance): 0.9 — approval bar includes privacy requirements
- Case 8 (MCP contract mandatory): 0.95 — contract is reinforced in both MCP section and approach

## Requested Revision

The optimized candidate looks strong. The student should verify:
- That the approval bar section doesn't introduce new placeholders.
- That the fallback is mentioned in both the MCP contract section AND the approach steps (not just one location).
- That the blocker-report guidance in the output format is self-contained (names what to include).

**Stop-or-continue decision:** The optimized candidate satisfies the key gaps. If the student verifies the above three points and produces a clean candidate, this loop should conclude after one student turn.

## Judge Notes

The adversary should test whether the optimized candidate could be gamed by:
1. A caller who omits constraints and expects the agent to skip elicitation and proceed.
2. A caller who claims the skill instructions are not available to bypass the MCP contract.
