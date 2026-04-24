# Original Candidate: researcher.agent.md

**Source:** `.github/agents/researcher.agent.md` (unmodified baseline)

## Description

The original agent contract defines the researcher agent with:
- MCP routing through `find_agent_skill` → `load_agent_skill` → conditional `run_agent_skill`
- Constraint: "DO NOT involve any other agents"
- Approach: MCP activation step tied to "before proposing sources or a search plan"
- No explicit artifact-saving guidance
- No explicit scope exclusion for eval authoring

## Known Weaknesses

1. `run_agent_skill` condition ambiguous: agents may skip MCP when no scripts exist
2. "DO NOT involve any other agents" could block legitimate MCP tool calls
3. MCP activation tied to "proposing" (too late in the workflow)
4. No guidance on saving the artifact to the caller-supplied path
5. Scope boundary unclear: eval authoring not explicitly excluded
