# Student Candidate

The `@trainer`-authored optimized candidate, produced in response to the `manual_followup` handoff.

## Changes from Original

1. **No-op path added**: New "No-Op Path" section tells the agent to confirm sufficiency and recommend the next step when source material and datasets already exist, rather than repeating research.

2. **Approach reordered**: Step 2 now checks for existing material first (no-op path). Steps 3+ clarify missing-constraint handling: ask when the caller can answer, proceed with documented assumptions for small gaps, stop for large gaps.

3. **MCP fallback added**: Both the intro paragraph and the MCP Execution Contract section now state that if the MCP server is unreachable, the agent should apply the skill guidance directly and document the fallback in the brief.

4. **"Other agents" constraint clarified**: Changed from "DO NOT involve any other agents" to "DO NOT involve other workflow agents (student, teacher, judge, adversary, trainer). Agent-skills MCP tool calls (`agent-skills/*`) are permitted and required." This removes the ambiguity about whether MCP tool calls violate the constraint.

5. **Output format extended**: Added guidance that if the caller supplied a desired artifact location, save the brief there; otherwise return it inline.

## Quality Prediction

The judge should prefer this candidate because it addresses all five identified gaps from the engineer-prompt review while keeping the existing MCP routing contract and stop condition intact. The changes are additive and minimal; no existing behavior is removed.
