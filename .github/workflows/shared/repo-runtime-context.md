# Repository Runtime Context

Use the checked-in repository assets as the source of truth for trainer execution instead of inventing parallel copies inside the workflow.

- Agents: `.github/agents/` contains the imported `trainer.agent.md` orchestrator plus sibling handoff agents such as `engineer.agent.md`, `judge.agent.md`, and `conservator.agent.md`.
- MCP servers: `shared/agent-skills-runtime.md` configures the `agent-skills` MCP server, and its implementation lives under `tools/agent-skills-mcp/`.
- Skills: canonical skill content lives under `.agents/skills/` and `skills/`.
- Hooks: repository helper scripts and workflow support hooks live under `.github/hooks/`.
- Supporting material: prefer checked-in examples and documentation under `examples/` and `docs/` when they are directly relevant to the selected target.

Treat the current repository checkout as the execution environment for these assets. Reuse the existing agents, MCP server configuration, skills, and hooks from the repository instead of creating substitute workflow-local versions.
