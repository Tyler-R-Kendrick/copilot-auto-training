# Engineering Review: trainer-train-agent

## Overview

`trainer-train-agent` is a specialization of the trainer-train orchestration loop targeting `*.agent.md` files — agent contracts that configure tool routing, MCP skill invocation, personas, and handoff behavior. It owns workspace initialization, MCP routing audit, three-concern separation (routing, persona, handoffs), prompt bloat control, and write-back gating for agent-type targets.

## Strengths

1. **Three-concern separation.** Separating tool routing, persona/scope, and handoff behavior into distinct optimization concerns prevents mixing symptoms with causes.
2. **MCP routing audit before optimization.** Running the routing audit before any optimization pass ensures the optimizer has accurate context about mismatches rather than discovering them during write-back.
3. **Handoff bounding rule.** Requiring all handoffs to name specific, real workspace agents (no recursive self-invocation) is a strong, testable constraint.
4. **Prompt bloat control.** Actively removing redundant or over-broad instructions as part of optimization, not just as a post-hoc cleanup, is architecturally sound.

## Gaps and recommendations

1. **MCP routing audit artifact.** Step 4 says to "record mismatches as steering context" but does not specify the artifact path. Define a concrete artifact path (e.g., `optimize/mcp-routing-audit.md`) so later iterations can track drift.
2. **Tool list source.** The skill says "identify all MCP skills available to the agent" but does not say where to find this list. Add a lookup order: (1) the agent contract's tool/skills frontmatter, (2) the repository's plugin or MCP config, (3) prompt the caller for the list if neither is found.
3. **Election criteria for agent targets.** Define a preference rule: prefer the candidate with the highest llm_judge score on routing correctness; break ties by fewest open-ended instructions.
4. **Persona scope definition.** "Bounded and consistent" is the goal but the skill does not define what counts as bounded. Add a heuristic: a persona is bounded when it can be described in one sentence without the word "any" or "all".

## Verdict

Ready for optimization loop. Priority improvements: (1) MCP routing audit artifact path, (2) tool list lookup order, (3) bounded persona heuristic, (4) election preference rule for agent targets.
