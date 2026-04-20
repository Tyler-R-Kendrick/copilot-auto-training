## Goal

Assess the current `researcher` agent as an optimization target for grounded source research workflows in the trainer-loop ecosystem, with emphasis on MCP execution discipline, research plan completeness, and source-triage quality.

The optimization target is operational reliability and research rigor, not role expansion. A strong researcher agent should consistently invoke `researcher-research` through the MCP server before doing any free-form research, build a full research plan before searching, apply the source approval bar strictly, and return a structured brief rather than improvised summaries.

## Current Strengths

- The role is precisely scoped: grounded source research only, no inference or synthesis.
- The MCP execution contract is clearly stated: `find_agent_skill` → `load_agent_skill` → `run_agent_skill`.
- The constraints correctly block involvement of other agents, guessing missing constraints, and fabricating source authority.
- The output format captures the necessary brief components: target, plan, approved sources, rejected candidates, mapping notes, and gaps.
- The approach steps reference the correct skill (`researcher-research`) and preserve a plan-before-search discipline.

## Main Risks

1. **No evidence order for reading inputs.** The approach says "Read the target prompt or skill file, task description, scoring rule, and any source constraints first," but does not specify what to extract from each or what state the agent must reach before proceeding to the MCP call.

2. **No fallback path when `researcher-research` is unavailable.** The current prompt says "do not improvise generic research advice when the MCP tools are available," but does not state what the agent should do if the MCP server is unreachable or the skill is missing: stop and report a blocker, or proceed differently.

3. **Approval bar not restated in agent prompt.** The skill SKILL.md defines the full source approval bar, but the agent's own prompt does not include it. If the MCP server fails to load the skill, the agent has no local approval bar to apply and may silently lower standards.

4. **No stopping rule for missing constraints.** The constraints say "DO NOT guess missing constraints that materially change source selection; ask for them or report the gap." But the approach does not name which inputs are most likely to be missing or give the agent a threshold for when to stop and ask versus proceed with what is known.

5. **Output format is underspecified.** The output format names six components but does not describe the expected depth or structure of each, especially "Mapping notes" and "Unresolved gaps." An agent receiving this prompt may produce shallow notes that do not give the downstream synthesizer enough to work with.

6. **No guidance on run_agent_skill conditions.** The MCP contract says "Call `run_agent_skill` only when the `researcher-research` skill exposes a deterministic helper under `scripts/`." But the agent has no instruction for what to do when that condition is false—e.g., when the skill provides guidance only rather than a deterministic helper.

## Rewrite Hypotheses

- Add an explicit input-reading checklist: what to extract from the target prompt file, task description, scoring rule, and source constraints before calling MCP.
- Add a clear fallback path: if `researcher-research` is not discoverable or not loadable, stop with a blocker report that names the missing skill and suggests re-running after the MCP server is available.
- Inline the key elements of the source approval bar so the agent can apply minimum standards even without the MCP contract.
- Expand the stopping rule for missing constraints: name the most likely missing inputs (domain terminology, licensing, scoring rule) and give explicit stop-or-continue criteria.
- Expand the output format with minimal structure notes for mapping notes and unresolved gaps so downstream synthesizers know what level of detail to expect.
- Clarify the `run_agent_skill` path: when the skill provides guidance only, use the loaded skill instructions as the active operating contract for the research task instead of calling `run_agent_skill`.

## Suggested Metrics

- MCP invocation rate: percent of runs where `find_agent_skill` + `load_agent_skill` is called before any source recommendation.
- Research plan completeness: percent of runs where the output includes all six required components with non-trivial content.
- Source approval bar adherence: percent of approved sources that include authority, provenance, licensing, and task-fit notes.
- Rejected-candidate rate: percent of runs where at least one rejected candidate is recorded with an explicit rejection reason.
- Blocker report quality: percent of blocked runs where the blocker report names the specific missing input and explains why it blocks source selection.
- Mapping note depth: percent of runs where mapping notes include at least one specific field-to-eval-row mapping rather than a generic note.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions in existing tests. Review representative researcher outputs against staged evals.json cases for research plan completeness, source approval bar adherence, and mapping note depth.

## Recommendation

This is a valuable optimization target because research quality directly affects eval authoring and downstream prompt optimization quality. The current agent has the right MCP execution contract and output format but lacks a complete approval bar, an explicit fallback path, and structured guidance on mapping notes and unresolved gaps.

Prioritize a rewrite that adds the fallback path for unavailable MCP skills, inlines the key source approval bar elements, and expands the output format with minimum structure for mapping notes. Measure on MCP invocation rate and research plan completeness first.
