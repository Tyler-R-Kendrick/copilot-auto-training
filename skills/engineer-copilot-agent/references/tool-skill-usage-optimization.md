# Tool Calling And Skill Usage Optimization

Read this file when a custom agent is inventing tools, misusing MCP skill helpers, or routing work to the wrong capability.

## Source-of-truth order

Use this order before editing tool or skill guidance:

1. Current session tool list and available-agent list
2. `python scripts/discover_runtime_surface.py --repo-root <repo-root> --json`
3. Public repo docs and tests

If the first two disagree, optimize for the live session and leave the body resilient to future renames.

## Tool routing patterns

- Use direct file and search tools for local reading, editing, and repo inspection.
- Use MCP skill surfaces only when the repo actually exposes them.
- Use subagent handoffs only when another named agent has a better ownership boundary than the current agent.
- Do not mention tools the target does not declare or that the live session cannot see.

## Repo-observed MCP skill-routing pattern

Public repo tests currently show a recurring order for skill-routed agents:

1. discover the exact skill
2. load the skill before first use
3. run a deterministic helper only when the skill actually exposes a runnable script

Keep that order explicit whenever a custom agent owns MCP skill routing. If the live session exposes different helper names, update the prose to name the real helpers instead of the stale repo snapshot.

## Repo-observed skill and agent boundaries

The repository currently documents these patterns in tests and README material:

- research work routes through `researcher` and `researcher-research`
- prompt and context engineering work routes through `engineer`, `engineer-prompt`, and `engineer-code`
- judging work routes through `judge`, `judge-rubric`, `judge-trajectory`, and `judge-outcome`
- training orchestration routes through `trainer` plus the `trainer-*` skills

Keep those as examples, not hard requirements. The discovery script and live inventory still win.

## Tool-usage eval ideas

Add evals that verify the agent:

- refuses to invent tools or agents
- uses discovery before load, and load before run, for skill helpers
- avoids unnecessary handoffs when direct tools are enough
- treats deterministic validation as script work instead of prose work
