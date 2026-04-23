# Engineer-Prompt Review: researcher.agent.md

## Goal

Assess the current researcher agent as an optimization target for grounded source-discovery workflows, with emphasis on triggering clarity, MCP routing discipline, and output consistency for research briefs that support eval authoring and prompt optimization.

The optimization target is operational discipline and clarity: the researcher agent should load the `researcher-research` skill before acting, stay anchored to primary-source evidence, surface genuine stop conditions rather than forcing weak recommendations, and avoid generic web browsing when the skill contract covers the task.

## Current Strengths

- The description is strongly worded and covers the full discovery surface: datasets, benchmarks, documentation, source material, and licensing.
- The `argument-hint` gives concrete guidance for callers about what context to supply.
- The MCP routing contract is explicit about the three-step `find_agent_skill` → `load_agent_skill` → `run_agent_skill` sequence.
- The output format is structured and covers approved sources, rejected candidates, mapping notes, and unresolved gaps.
- The stop-recommendation path ("if no candidate clears the approval bar") is present.

## Main Risks

- The `tools` list includes `agent-skills/*` but does not mention `search` at the top level. The frontmatter says `tools: [read, edit, search, execute, 'agent-skills/*']`, which is inconsistent with the constraint "DO NOT involve any other agents" — `search` here is fine but the constraint needs to clarify it means no sub-agents, not no search.
- The approach steps mention "use `find_agent_skill` and `load_agent_skill` to activate `researcher-research` before proposing sources" (step 2), but the skill activation should be step 1 or at least mandatory before any search planning, not listed after "read the target prompt" as if it can be deferred.
- There is no explicit path for when the caller supplies materials that are sufficient without external research (i.e., no defensible no-op path for the research stage itself). The agent always tries to find sources even when the caller already supplies them.
- The constraint "DO NOT guess missing constraints" is correct but paired with "ask for them or report the gap" — in a non-interactive context the agent should prefer reporting the gap rather than asking.
- The output format lists items but does not specify the artifact save location or format when the caller asks for a saved output rather than inline text.

## Rewrite Hypotheses

- Keep the frontmatter and description essentially unchanged; the discovery language is already well-calibrated.
- Reorder the approach so skill activation (find + load) is the first action after reading the target, not step 2 after a read.
- Add a short no-op path: if the caller supplies sufficient source material already, surface that fact and defer to the caller rather than re-running a search.
- Clarify the "DO NOT involve any other agents" constraint to explicitly mean sub-agent invocation, not research tools like `search`.
- Add a clear "non-interactive gap reporting" note so the agent defaults to gap reports instead of interactive clarifying questions.
- Keep the rewrite minimal. The existing structure and MCP routing contract are sound.

## Suggested Metrics

- Skill-activation compliance: percentage of runs where `find_agent_skill` and `load_agent_skill` are called before any source is proposed.
- Stop-condition precision: percentage of cases with no viable sources where the agent correctly surfaces a blocker report rather than a weak recommendation.
- No-op accuracy: percentage of cases where pre-supplied source material is correctly recognized as sufficient.
- Output completeness: percentage of runs that include approved sources, rejected candidates, mapping notes, and gap notes in the brief.
- Non-interactive compliance: percentage of runs in non-interactive contexts where gaps are reported rather than asked as open questions.

## Recommendation

This agent file has a solid base. The best optimization is a small discipline-focused rewrite: enforce skill activation as the first action, clarify constraint wording, and add a no-op and non-interactive gap-reporting path. Avoid broadening the scope or restructuring the output format, since those are already well-defined.

## Validation Plan

- Run `python -m pytest -q` after any file change to confirm no regressions.
- Use the `researcher-research` skill evals (`skills/researcher-research/evals/evals.json`) as the ground-truth behavioral check for the researcherr workflow.
- Judge mode: `llm_judge` (evaluation relies on qualitative research-brief quality, not exact match).
