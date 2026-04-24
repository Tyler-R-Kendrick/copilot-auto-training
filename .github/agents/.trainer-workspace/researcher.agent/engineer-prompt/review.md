## Goal

Assess the current `researcher.agent.md` as an optimization target for grounded public-source research workflows, with emphasis on evidence discipline, source-triage rigor, and research-brief completeness.

The optimization target is research reliability, not role expansion. A strong researcher agent should activate the `researcher-research` skill correctly, produce structured research briefs that ground later eval authoring, and stop cleanly when no acceptable public source exists rather than forcing weak recommendations.

## Current Strengths

- Role is correctly scoped to source discovery, triage, licensing checks, and provenance review.
- Constraints correctly prohibit other agents and fabrication of source quality.
- MCP execution contract is clearly stated: `find_agent_skill` → `load_agent_skill` → `run_agent_skill`.
- Output format names the six required sections of a research brief.

## Main Risks

1. **No evidence reading order.** The approach says "read the target prompt or skill file, task description, scoring rule, and source constraints first," but does not specify what to do when those inputs are absent or partial.

2. **Weak skill-activation guidance.** The MCP contract says to call `run_agent_skill` "only when the `researcher-research` skill exposes a deterministic helper under `scripts/`," but does not instruct the agent to fall back to the loaded skill instructions as the operating contract when no script is available — the fallback is implicit rather than explicit.

3. **Approval bar is undefined.** The constraints prohibit fabrication of "source authority, licensing, annotation quality, or benchmark support," but the agent has no stated approval bar for when a source crosses from acceptable to unacceptable. The loaded `researcher-research` skill defines the approval bar, but the agent itself carries no summary of it.

4. **No stopping condition for missing constraints.** The approach step 5 says to "build a primary-source-first research plan that names the approval bar, missing constraints, and the evidence required for a usable source," but there is no instruction to elicit missing constraints from the caller before starting the search.

5. **Output format omits blocker-report shape.** The output format lists approved sources, rejected candidates, and mapping notes, but does not name what a blocker report should look like when no source clears the approval bar — a research-critical output is missing from the contract.

6. **`argument-hint` is under-informative.** The hint says "target prompt or skill file, task description, scoring rule, constraints, and desired research artifact location" but does not say which of those are required versus optional, potentially causing the agent to start searching without enough context.

## Rewrite Hypotheses

- Add an explicit evidence reading order: target file first, task description second, scoring rule third, caller-supplied source constraints last.
- Promote the fallback-to-skill-instructions contract to an explicit step when no `scripts/` helper exists.
- Add a compact version of the `researcher-research` approval bar directly in the agent so it can gate source candidates without always loading the full skill.
- Add an explicit step to elicit missing constraints before searching when domain, language, or licensing details are absent.
- Add a blocker-report section to the output format contract that describes what a no-source recommendation looks like.
- Make the `argument-hint` distinguish required from optional inputs.
- Keep the rewrite minimal: evidence order, explicit fallback, approval bar summary, elicitation step, and blocker-report shape are the highest-value additions.

## Suggested Metrics

- Skill activation rate: percent of runs that correctly call `find_agent_skill` and `load_agent_skill` before producing output.
- Brief completeness: percent of briefs that contain all six named sections.
- Approval bar adherence: percent of approved sources that pass all stated criteria (accountable maintainer, traceable origin, license, version stability).
- Blocker report rate: percent of runs where no acceptable source exists that produce a clean blocker report rather than a forced recommendation.
- Elicitation rate: percent of runs with missing constraints that ask for them before searching.
- Research-to-synthesis handoff quality: percent of research briefs that downstream synthesize workflows can consume without additional clarification.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions in existing tests. Verify that representative research brief outputs contain all six required sections and that at least one blocker-report scenario is correctly handled in the eval cases.

## Recommendation

This is a worthwhile optimization target because research brief quality is a prerequisite for eval synthesis and downstream prompt optimization. The current agent has the right role scoping but lacks structured evidence reading, an explicit fallback contract, a compact approval bar, and a complete blocker-report format.

Prioritize a rewrite that adds a fixed evidence reading order, an explicit skill-instructions fallback, a compact source approval bar, and a named blocker-report format. Measure on brief completeness and skill activation rate first. Only add examples if the first structured rewrite still produces incomplete or low-quality briefs.
