# Agent Loop Contract

This reference defines the routing table, agent-contract constraints, tool-routing rules, and validation requirements for the trainer-train-agent skill.

## Target type

- `*.agent.md` files — custom agent definitions and agent instruction documents.
- Agent contracts that configure tool routing, MCP skill invocation, agent personas, or handoff behavior.

## Workspace derivation

- Strip only `.md` from the target filename to derive `<agent-name>` (e.g., `researcher.agent.md` → `researcher.agent`).
- Use `<target-dir>/.trainer-workspace/<agent-name>/` as the workspace root.

## Required checkpoint

Require `engineer-prompt/review.md` before any optimization pass. If absent, set `workflow_state: pending_engineer_prompt` and report a blocker.

## Three-concern routing

| Observed failure mode | Primary concern | Secondary concern |
|----------------------|-----------------|-------------------|
| Wrong tool or skill invoked | Tool routing | Persona (if scope too broad) |
| Tasks outside intended scope | Persona / scope | Tool routing |
| Incorrect or unbounded handoffs | Handoff behavior | Tool routing |
| Duplicate or redundant instructions | Prompt bloat | All concerns |
| All concerns | In order: routing → persona → handoff | — |

## Judge-mode routing table

| Row shape | Inferred mode |
|-----------|--------------|
| Explicit `scoring: deterministic` | `deterministic` (rule-checkable: field presence, non-empty tool list) |
| Explicit `scoring: llm_judge` | `llm_judge` |
| `reference` + `criteria` fields | `llm_judge` |
| No scoring fields | Default to `llm_judge` |

## MCP skill routing audit

Before optimization, for each MCP skill available to the agent:
1. Read the skill's `description` field.
2. Compare it to the agent's routing instructions for that skill.
3. Flag any mismatch as steering context: "Agent routes X but skill description says Y."
4. If the agent's tool list cannot be determined, report a blocker.

## Prompt bloat rules

During optimization, remove instructions that:
- Duplicate what the available tools already enforce.
- List prohibitions exhaustively rather than providing positive routing rules.
- Are broad enough to make the agent attempt tasks outside its intended scope.

Prefer explicit, positive routing rules over long negative lists.

## Handoff bounding rules

All handoff instructions must:
- Name a specific, real workspace agent (not "the best available agent" or "another agent").
- Be bounded — no open-ended chains or recursive self-invocation.
- Be documented in the decision summary when changed.

Flag any open-ended or recursive handoff instructions as write-back blockers.

## Write-back gate

Write back only when all of the following are true:
1. Tool routing audit passes (each invocation matches available tools and MCP skill descriptions).
2. All handoffs are bounded to named, real agents with no recursive self-invocation.
3. Persona scope is explicit and bounded.
4. Validation passes (e.g., `python -m pytest -q` exits 0).
5. Decision summary written at `<workspace-root>/decision.md`.
