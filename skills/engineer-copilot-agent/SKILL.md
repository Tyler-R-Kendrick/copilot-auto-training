---
name: engineer-copilot-agent
description: Improve GitHub Copilot custom agents by validating agent contracts, tightening tool and MCP skill routing, and optimizing bounded handoffs to real workspace agents. Use this whenever the user wants to create, debug, or refine a custom agent, fix tool-calling or skill-usage guidance, reduce prompt bloat, or tune subagent handoffs for Copilot workflows.
argument-hint: Describe the target custom agent, whether the concern is triggering, tool or skill routing, handoffs, structure, evals, or all, and any observed failures such as stale tool names, bad handoffs, or bloated instructions.
license: MIT
compatibility: Python 3.11+. Works in repositories that store GitHub Copilot custom agents as `.agent.md` files alongside reusable skills.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Engineer Copilot Agent

Use this skill to improve GitHub Copilot custom agents by treating frontmatter, tool and skill routing, handoff design, and context minimization as separate but composable concerns.

Read `references/copilot-agent-standard.md` for the baseline contract and `references/context-minimization-loop.md` before editing.

## When to use this skill

- The user wants to create a new Copilot custom agent.
- The user wants to improve an existing `.agent.md` file.
- The user reports stale tool names, stale agent names, or invented MCP routing.
- The user wants tighter tool-calling guidance or better bounded skill usage.
- The user wants clearer subagent handoffs and ownership boundaries.
- The user wants to trim a bloated custom-agent prompt with progressive disclosure.
- The user wants evals or training data for a custom-agent contract.

Do not use this skill for prompt-only or skill-only work unless the target artifact is a Copilot custom agent contract or the user explicitly wants to design one.

## Required inputs

- The path to an existing `.agent.md` file, or a description of the custom agent to create.
- The repository root when runtime surface discovery matters.
- The improvement focus: frontmatter, routing, handoffs, structure, evals, or all.
- Any observed failure modes: under-triggering, over-triggering, stale tools, bad handoffs, bloated context, or weak ownership boundaries.

## Core workflow

Follow this order:

1. Run `python scripts/discover_runtime_surface.py --repo-root <repo-root> --json` to list repo-owned agents, skills, and observed tool surfaces.
2. Compare that discovery output against the current session's live tool and agent inventory. Treat the live session as the source of truth when names drift.
3. Run `python scripts/validate_agent.py <agent-path> --repo-root <repo-root> --json` to catch contract mismatches, stale names, and missing fields.
4. Run `python scripts/analyze_agent_body.py <agent-path> --repo-root <repo-root> --json` to find oversized sections, deterministic instructions, and routing guidance that should move deeper.
5. Fix validation errors first, then routing mismatches, then body clarity and context size.
6. Read `references/frontmatter-optimization.md` when triggering or discoverability is the concern.
7. Read `references/tool-skill-usage-optimization.md` when tool calls, MCP skill routing, or tool-usage evals are the concern.
8. Read `references/handoff-optimization.md` when subagent sequencing or ownership boundaries are the concern.
9. Extract deterministic checks and inventory summarization to scripts instead of repeating them in prose.
10. Re-run discovery, validation, and analysis after each meaningful revision.

## Four concern separation

### Frontmatter

The frontmatter controls whether Copilot discovers the custom agent. Optimize the name, description, tool declarations, and exposed handoff surfaces without mixing in execution detail.

### Tool and skill routing

The body should name only tools, MCP helpers, and skills that actually exist in the current workspace or live session. Prefer discovery and validation before editing so the contract does not fossilize stale names.

### Handoffs and ownership

The body should make it obvious which tasks the agent owns directly, which tasks should hand off, and when a handoff would be wasteful or unsafe. Keep boundaries crisp so multiple agents do not compete for the same responsibility.

### Context minimization

The `.agent.md` body should stay lean. Put standards, optimization heuristics, eval guidance, and large examples in `references/`. Put fixed analyses in `scripts/`.

## Recursive minimization loop

1. Draft the routing layer in the `.agent.md` file first.
2. Move standards, examples, and optimization heuristics into reference docs.
3. Move mechanical checks, inventory discovery, and repeated summaries into scripts.
4. Re-read the `.agent.md` file and delete anything that merely duplicates deeper assets.
5. Re-read each reference file and move any repeated checklist or parser logic into scripts or smaller references.
6. Stop only when each layer contains information that cannot be stored more cheaply at a deeper layer.

## Output contract

When improving a custom agent, structure the response as:

1. `Runtime surface summary`: what agents, skills, and tool surfaces are actually available
2. `Validation results`: output from the validator
3. `Analysis results`: output from the analyzer
4. `Improvement plan`: prioritized list of changes
5. `Changes made`: specific edits with rationale
6. `Re-validation`: confirmation of the final contract plus any remaining risks
