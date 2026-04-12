# Delegation: trainer-train-agent

## When to delegate

Route to `trainer-train-agent` when the selected target is:

- A `*.agent.md` file (custom agent definition or agent instruction document)
- An agent contract that configures tool routing, MCP skill invocation, agent personas, or handoff behavior

## What it handles

- Agent-specific workspace initialization (strips final extension from agent filename)
- Engineering review checkpoint enforcement
- MCP skill routing audit: compares agent routing instructions against available skill descriptions
- Three-concern separation: tool routing, persona/scope, handoff behavior
- Prompt bloat control: removes instructions that duplicate tool enforcement or list excessive prohibitions
- Handoff bounding: ensures all handoffs name specific, real workspace agents with no recursive self-invocation
- Judge-mode defaulting to `llm_judge` for open-ended agent behavior quality tasks

## How to invoke

Tell the caller: "The selected target is an agent contract. Use `trainer-train-agent` for this run." Pass the agent contract path, workspace root, validation command, the agent's tool list and MCP skill configuration, any known failure modes (wrong routing, over-broad persona, bad handoffs), and the stage capability map.

## What it does not handle

- Prompt files → use `trainer-train-prompt`
- Python code targets → use `trainer-train-code`
- SKILL.md files → use `trainer-train-skill`
- Agent contracts where the tool list and MCP configuration cannot be determined (blocker — resolve before routing here)
