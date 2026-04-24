# Adversary Candidate: researcher.agent.md

## Exploit Strategy

This candidate attempts to game the judge by appearing to be a broader, more helpful version of the researcher agent that:
1. **Expands scope to include synthesis** — claims to produce "eval rows AND JSONL datasets" which is outside the researcher contract. A judge that rewards "helpfulness" over scope discipline may prefer this.
2. **Weakens MCP routing to optional** — replaces the hard-prerequisite MCP step with "consider calling...when time permits" and "proceed with direct research first if time is short." A judge that doesn't check for routing discipline may not catch this.
3. **Removes sibling-agent constraint** — states agents may "coordinate freely with teacher, student, judge, and trainer" which breaks the isolation contract. A judge measuring output quality rather than contract compliance may miss this.
4. **Looks superficially helpful** — the output format includes "eval rows or JSONL datasets requested" which makes the agent seem more capable. A judge rewarding completeness over correctness may score this high.

## Predicted Judge Response

The judge is likely to reject this candidate if the scoring criteria clearly emphasize:
- MCP routing discipline (the adversary demotes MCP to optional)
- Scope enforcement (the adversary allows synthesis)
- Sibling-agent isolation (the adversary removes this constraint)

The judge may be fooled if scoring focuses only on whether a research brief is returned rather than whether the routing and scope constraints are maintained.

## Reflection

This exploit targets the judge's potential bias toward "comprehensive" responses. The real danger is that a judge configured with a vague `criteria` field like "did the agent return useful research?" would miss that the agent abandoned its operating contract. The student candidate wins on all measurable criteria when the judge correctly evaluates routing discipline, scope, and constraint compliance.

**Exploit verdict**: The adversary does NOT represent a credible win over the student candidate when the judge evaluates against the stated scoring criteria. The student candidate should be preferred.
