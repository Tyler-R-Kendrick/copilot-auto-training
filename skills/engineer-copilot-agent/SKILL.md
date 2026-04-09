---
name: engineer-copilot-agent
description: Improve GitHub Copilot custom agents by validating agent contracts, tightening tool and MCP skill routing, and minimizing prompt bloat while keeping handoffs bounded to real workspace agents. Use this whenever the user wants to create, debug, or refine a custom agent.
argument-hint: Describe the target custom agent, whether the concern is triggering, routing, handoffs, structure, evals, or all, and any observed failures such as stale tool names, bad handoffs, or bloated instructions.
license: MIT
compatibility: Python 3.11+. Works in repositories that store GitHub Copilot custom agents as `.agent.md` files alongside reusable skills.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Engineer Copilot Agent

Use this skill to create or improve GitHub Copilot custom agents. Treat triggering, routing, handoffs, and prompt size as separate concerns. Keep the top-level agent contract lean.

Read `references/copilot-agent-standard.md` for the baseline contract and `references/context-minimization-loop.md` before editing.

## When to use this skill

Use it when the user wants to:

- create a new Copilot custom agent
- improve an existing `.agent.md` file
- remove stale tool, skill, or agent names
- tighten tool-calling or MCP skill routing
- clarify subagent handoffs and ownership
- trim a bloated agent prompt
- add eval coverage for routing regressions

Do not use this skill for prompt-only or skill-only work unless the target artifact is a Copilot custom agent contract or the user explicitly wants to design one.

## Required inputs

- Target `.agent.md` path, or a description of the agent to create
- Repo root when runtime surface discovery matters
- Improvement focus: triggering, routing, handoffs, structure, evals, or all
- Known failure modes such as under-triggering, over-triggering, stale names, bad handoffs, or prompt bloat

## Core workflow

Follow this order:

1. Run `python scripts/discover_runtime_surface.py --repo-root <repo-root> --json`.
2. Reconcile discovered repo surfaces against the live session inventory. If they differ, trust the live session.
3. Run `python scripts/validate_agent.py <agent-path> --repo-root <repo-root> --json`.
4. Run `python scripts/analyze_agent_body.py <agent-path> --repo-root <repo-root> --json`.
5. Fix validation errors before rewriting for style.
6. Fix stale or invented routing next.
7. Trim prompt body last by moving standards to `references/` and mechanical checks to `scripts/`.
8. Re-run discovery, validation, and analysis after each meaningful revision.

## Four concern separation

### Frontmatter

Optimize discoverability and fit:

- keep `name`, `description`, and hints specific
- expose only real tools and handoff surfaces
- avoid body-level execution detail in frontmatter

### Routing

Name only tools, skills, helpers, and agents that actually exist in the workspace or live session.

- Discover before naming helpers.
- When names drift, live inventory overrides stale repo text.
- Do not invent MCP routing, helper names, or handoff targets.

### Handoffs

Make ownership explicit:

- state what the agent should do directly
- state what should be handed off
- avoid overlapping ownership across agents
- avoid handoffs that are wasteful, circular, or unsupported

### Minimization

Keep the `.agent.md` file as a routing layer.

- put standards and examples in `references/`
- put deterministic checks and repeated summaries in `scripts/`
- remove prose that only duplicates deeper assets

## Recursive minimization loop

Use a recursive pass until the prompt is only as large as needed:

1. Draft or repair the routing layer.
2. Move standards, examples, and extended guidance into focused references.
3. Move mechanical checks and inventory logic into scripts.
4. Delete duplicated prose from the agent body.
5. Re-read the remaining prompt and trim again.

Stop when each remaining section is necessary for triggering, routing, handoffs, or bounded execution.

## Evals guidance

When the user asks for evals, prefer coverage that catches:

- invented tools, skills, or handoff targets
- stale helper names
- missing discovery before concrete helper naming
- missing discovery-to-load-to-run ordering for MCP skill usage
- prompt bloat that should have been pushed into references or scripts

## Output contract

When improving a custom agent, return:

1. Runtime surface summary
2. Validation results
3. Analysis results
4. Improvement plan
5. Changes made
6. Re-validation status and remaining risks
