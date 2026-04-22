# Decision: researcher.agent.md Optimization

## Target
`.github/agents/researcher.agent.md`

## Selection Reason
First `.agent.md` file without an existing trainer workspace, selected per deterministic priority ordering (`.agent.md` before `SKILL.md`) with path-ascending tiebreaker.

## Optimization Summary

**Iteration 1** applied a `manual_followup` optimize run (no model credentials available) in which the `@trainer` agent authored the candidate directly.

### Changes Applied

1. **MCP fallback added**: Both the intro paragraph and the MCP Execution Contract section now note that if the MCP server is unreachable, the agent should apply the skill guidance directly and document the fallback.

2. **No-Op Path section added**: Explicit new section tells the agent to confirm sufficiency and recommend the next step when source material and datasets already exist, rather than repeating research.

3. **Approach reordered**: Step 2 now checks for existing material (no-op path). Step 3 clarifies missing-constraint handling: ask when the caller can answer, proceed with documented assumptions for small gaps, stop for large gaps. Original step 3 became step 5, etc.

4. **"Other agents" constraint clarified**: Added parenthetical `(Agent-skills MCP tool calls via agent-skills/* are permitted and required; they are not "other agents.")` to remove ambiguity while preserving the exact test-required string.

5. **Output format extended**: Added inline vs. saved artifact guidance tied to whether the caller supplied a desired artifact location.

## Validation Result
✅ `python -m pytest -q` — **856 passed**, 0 failed.

## Artifacts
- Workspace: `.github/agents/.trainer-workspace/researcher.agent/`
- Iteration: `iterations/iteration-1/`
- Optimize report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Validation log: `iterations/iteration-1/validation/pytest.txt`
- Candidates: `iterations/iteration-1/candidates/`
- Steering: `iterations/iteration-1/steering/`
