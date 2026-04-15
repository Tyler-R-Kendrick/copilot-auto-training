## Goal

Assess the current researcher agent as an optimization target for grounded source research in prompt and skill evaluation workflows, with emphasis on reliable MCP skill activation, blocker discipline, and research-brief quality.

The optimization target is operational consistency, not role expansion. A strong researcher agent should activate `researcher-research` via MCP before any free-form searching, resolve prompt interface and scoring rule constraints before source selection, correctly produce source-approved briefs, and stop with a clear blocker report when no source clears the approval bar.

## Current Strengths

- Role is sharply scoped: grounded source discovery only, no synthesis or eval authoring.
- MCP execution contract is explicit: `find_agent_skill`, `load_agent_skill`, `run_agent_skill` steps are named in order.
- The constraints correctly prohibit fabricating authority, licensing, or annotation quality.
- The approach correctly calls for resolving prompt placeholders and task boundary before searching.
- The output format lists the right sections: approved sources, rejected candidates, mapping notes, and unresolved gaps.
- The scope section correctly restricts involvement to other agents.

## Main Risks

1. **No evidence order for the MCP skill activation.** The approach says "use `find_agent_skill` and `load_agent_skill` before proposing sources," but does not specify what to inspect from the loaded skill contract or when the loaded instructions become the active operating contract versus when `run_agent_skill` applies.

2. **Constraint resolution is implicit.** The prompt notes constraints such as domain, language, jurisdiction, and recency, but does not specify which of those are required to resolve before source selection begins versus which are optional. This can lead to incomplete elicitation before searching.

3. **Approval bar is absent from the agent.** The agent prompt does not include the source approval bar criteria (authority, provenance, licensing, recency, contamination risk), relying on the loaded `researcher-research` skill contract to carry that logic. If the skill contract is not consulted, the agent may approve weak sources.

4. **No explicit blocker path in the output format.** The approach mentions stopping with a blocker report, but the output format section does not include a blocker-report template, making it easy for the model to force a recommendation when no source clears the bar.

5. **MCP `run_agent_skill` threshold is vague.** The contract says to call `run_agent_skill` only when the skill "exposes a deterministic helper under `scripts/`," but does not explain how to determine that or what to do when the helper is absent.

6. **No minimum output scope.** The output format lists sections but does not specify how many approved sources constitute a usable brief, when to declare the brief complete, or what the minimum evidence a rejected candidate must document.

## Rewrite Hypotheses

- Add an explicit step: after loading `researcher-research`, check whether `scripts/run_research.py` exists and use it if present; otherwise apply the loaded skill instructions as the operating contract.
- Make the constraint resolution step explicit: list which constraints are required (task boundary, scoring rule, prompt placeholders) versus elicitable (domain, language, recency), and require resolution of required ones before searching.
- Embed the source approval bar criteria directly in the agent so the model does not depend solely on the loaded skill contract for gating logic.
- Add an explicit blocker-report template to the output format section.
- Keep the rewrite minimal: targeted constraint-resolution and approval-bar additions plus a blocker template should be enough for a first improvement pass.

## Suggested Metrics

- MCP activation rate: percent of runs where `find_agent_skill` and `load_agent_skill` precede any source proposal.
- Constraint elicitation completeness: percent of runs that resolve required constraints before searching.
- Approval bar enforcement: percent of runs where rejected sources include explicit rejection reasons tied to the bar.
- Blocker recall: percent of runs where the agent correctly stops with a blocker report when no source clears the bar.
- Research-brief completeness: percent of briefs that include all required sections (approved sources, rejected candidates, mapping notes, unresolved gaps).
- False approval rate: percent of runs where a source that fails the bar is approved.
- MCP `run_agent_skill` accuracy: percent of runs that correctly determine whether the deterministic helper applies.

## Validation Plan

Run `python -m pytest -q` from the repository root after any rewrite to confirm no regressions in existing tests. Validate the optimized prompt against synthesized eval cases covering MCP activation, constraint resolution, blocker paths, and source approval.

## Recommendation

This is a good optimization target because research reliability directly gates dataset quality and eval safety for the entire trainer loop. The current agent has the right structural scope but leaves the constraint-resolution contract, approval bar, and blocker path implicit.

Prioritize a rewrite that makes constraint-resolution required before searching, embeds the approval bar in the agent, and adds a clear blocker template. Measure on blocker recall and approval bar enforcement first. Only expand with few-shot examples if the first structured rewrite still lets weak sources through.
