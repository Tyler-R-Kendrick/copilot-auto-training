## Goal

Assess the current `researcher.agent.md` as an optimization target for public-source discovery work in prompt-evaluation workflows, with emphasis on research rigor, MCP execution discipline, blocker reporting, and output completeness.

The optimization target is research reliability and output fidelity. A strong researcher agent should discover and load the `researcher-research` skill first, build a primary-source-first query plan before searching, apply the source approval bar before recommending anything, and deliver a self-contained research brief rather than free-form suggestions.

## Current Strengths

- The role is clearly scoped: produce grounded research briefs, not eval rows or optimization artifacts.
- The constraints correctly prohibit involving other agents and fabricating source authority.
- The MCP execution contract names the right operations (`find_agent_skill`, `load_agent_skill`, `run_agent_skill`) in the correct order.
- The approach section distinguishes reading the target from building a query plan, which is a good structural discipline.
- The output format lists distinct sections (sources, rejections, mapping notes, gaps), which supports downstream synthesis.

## Main Risks

1. **No evidence reading order.** The approach says "Read the target prompt or skill file … first," but does not specify what to read next, how many artifacts to read before building a plan, or when to stop gathering context. An agent with partial context may start searching prematurely.

2. **MCP fallback is silent.** The contract says "Call `run_agent_skill` only when the `researcher-research` skill exposes a deterministic helper under `scripts/`; otherwise use the loaded skill instructions as the active operating contract." But there is no guidance on what the agent should do when MCP tools are unavailable entirely — should it fall back to free-form research, or report a blocker?

3. **No convergence or stopping rule.** The approach ends with "gather candidate sources, rank approved options," but does not say how many rounds of source triage are appropriate, when the agent should stop searching and deliver a brief, or what constitutes a "complete enough" brief for downstream use.

4. **No explicit source approval bar in the agent contract.** The body references the `researcher-research` skill contract for the approval bar, but an agent loading that skill at runtime could miss this dependency if the skill contract is long and the agent reads only the summary. A brief inline restatement of the core approval criteria (accountable maintainer, traceable origin, explicit license) would make the contract self-contained.

5. **Blocker reporting is underspecified.** The constraint "DO NOT guess missing constraints that materially change source selection; ask for them or report the gap" is correct in principle, but does not say whether to ask the user, report to the caller, or write a blocker artifact — which leads to inconsistent output formats across runs.

6. **Scope of `execute` tool is ambiguous.** The frontmatter lists `execute` as an available tool, but the body never mentions when it is appropriate to execute a script versus use `search`. This can lead to agents running `scripts/run_research.py` unpredictably or skipping it when it would save time.

## Rewrite Hypotheses

- Add an explicit evidence reading order as a numbered list: target file → task description → scoring rule → existing evals → optional constraints → then stop and plan.
- Add a clear MCP fallback rule: if MCP tools are unavailable, report a blocker rather than conducting free-form research as the primary path.
- Add a stopping rule: deliver the brief once the approved-source list is stable and the mapping notes can support downstream synthesis, rather than continuing to search for additional sources.
- Add an inline summary of the core source approval bar (3–5 bullet points) so the agent does not depend entirely on the loaded skill contract being fully read.
- Replace "ask for them or report the gap" with a concrete instruction: if missing constraints materially affect source selection, write a blocker report and stop rather than proceeding with assumptions.
- Add a single sentence on `execute` tool usage: use `run_agent_skill` for the `researcher-research` skill runtime; use `execute` only to run `scripts/run_research.py` for deterministic scaffold setup, not for general web search.

## Suggested Metrics

- MCP call compliance: percent of runs that call `find_agent_skill` and `load_agent_skill` before proposing sources.
- Source approval rate: percent of recommended sources that pass all approval bar criteria.
- Blocker report quality: percent of runs with missing constraints that produce a structured blocker artifact rather than a guess.
- Brief completeness: percent of runs that include all six output sections (target layout, query plan, approved sources, rejected candidates, mapping notes, unresolved gaps).
- Downstream synthesis compatibility: percent of research briefs that include enough field-mapping notes to allow a synthesis agent to author at least three eval rows without further clarification.
- Stopping discipline: percent of runs that deliver a brief rather than continuing research indefinitely or returning mid-brief.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions. Review representative researcher outputs against the `skills/researcher-research/evals/evals.json` cases for compliance with the output format and source approval discipline.

## Next Optimization Hypothesis

Focus the first pass on: (1) adding an explicit evidence reading order, (2) adding a concise inline approval bar summary, (3) specifying the MCP fallback behavior when tools are unavailable, and (4) adding a brief stopping condition. Keep the rewrite minimal — structural improvements only, without expanding scope or adding new constraints.
