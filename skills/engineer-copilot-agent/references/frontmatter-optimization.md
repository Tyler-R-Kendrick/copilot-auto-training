# Frontmatter Optimization For Copilot Custom Agents

Read this file when the custom agent under-triggers, over-triggers, or advertises the wrong tools or child agents.

## Name

- Match the filename stem exactly.
- Prefer short kebab-case names that describe the ownership boundary, not the implementation detail.
- Rename only when the role itself is wrong; do not rename just to chase style.

## Description

The description is the primary trigger contract. Improve it by:

1. Leading with the owned task.
2. Adding explicit “Use when …” trigger guidance.
3. Naming the kinds of artifacts, workflows, or failure modes the agent owns.
4. Adding negative boundaries when another agent or direct tool use should win.

## Tools

- Keep the tool list minimal but sufficient.
- Match the declared tools against `discover_runtime_surface.py` output and the live session inventory.
- If the repo still mentions an old tool alias, update the contract and the surrounding prose together.

## Child agents and handoffs

- Declare only agents that the target should truly orchestrate.
- Mirror every exposed handoff in the body with a clear ownership explanation.
- If a child agent is repo-real but not session-real, tell the live agent to verify before shipping rather than silently hardcoding the stale name.

## Frontmatter eval ideas

Add eval cases that check whether the optimized agent:

- routes only to real agents
- declares only real tools
- explains when not to invoke the agent
- keeps the description focused on ownership, not implementation trivia
