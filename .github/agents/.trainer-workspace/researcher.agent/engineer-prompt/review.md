## Goal

Assess the current researcher agent as an optimization target for grounded source research work in prompt-optimization workflows, with emphasis on MCP execution discipline, evidence ordering, blocker reporting, and research brief completeness.

The optimization target is execution reliability, not role expansion. A strong researcher agent should activate the researcher-research skill before any free-form search, resolve missing constraints before proposing sources, surface a clear approval bar, and return a structured brief that a downstream synthesizer can consume without ambiguity.

## Current Strengths

- The role is narrowly scoped: grounded source discovery, triage, and brief authoring only.
- The MCP execution contract is explicit: find → load → run before any research.
- The constraints correctly prohibit guessing, involving other agents, and fabricating source authority.
- The approach section lists the right six steps in the right order.
- The output format names all six required sections.

## Main Risks

1. **No evidence-order for incoming artifacts.** The approach says "Read the target prompt or skill file, task description, scoring rule, and any source constraints first," but does not specify what to do when some of these inputs are missing before the MCP activation step, leaving the agent to improvise.

2. **`run_agent_skill` guard clause is ambiguous.** The MCP contract says to call `run_agent_skill` "only when the researcher-research skill exposes a deterministic helper under `scripts/`; otherwise use the loaded skill instructions as the active operating contract." This is ambiguous: an agent new to the repo cannot easily determine whether a scripts/ helper exists without reading the skill content, but the contract implies they should decide this before loading. In practice the agent may skip the load step or call run_agent_skill anyway.

3. **No explicit blocker-report path.** The constraints say "DO NOT guess missing constraints that materially change source selection; ask for them or report the gap." But the approach does not name a step for surfacing missing constraints before the MCP load, which means a partially-specified task may proceed into research rather than pausing for clarification.

4. **Output format is flat.** The six output sections are named but not described in terms of required content, leaving the agent to vary depth significantly across runs. In particular, "Unresolved gaps or stop recommendation" is vague: the agent may produce a thin note or a full stop recommendation without guidance on when each is appropriate.

5. **No artifact path guidance.** The agent description says to "return a concise research brief unless the caller explicitly asks for a saved artifact path," but there is no instruction for where to save the brief or how to name the file when the caller does ask. Other agents in the same repo (adversary, teacher) have more explicit artifact naming.

6. **Scope section does not mention eval authoring limits.** The scope says "Separate research from synthesis" implicitly through constraints, but the scope section itself does not call out that the researcher should stop at mapping notes, which could cause scope creep in edge cases.

## Rewrite Hypotheses

- Add a pre-MCP checklist: read inputs in a fixed order (prompt file → task description → scoring rule → constraints), confirm which are present, and surface a blocker note before calling `find_agent_skill` if any materially affect source selection.
- Clarify the `run_agent_skill` guard clause: after loading the skill, check whether `scripts/run_research.py` is mentioned in the loaded contract; if yes, call `run_agent_skill`; if the helper is not mentioned or not available, use the loaded instructions as the operating contract directly.
- Add an explicit blocker-report step to the approach: if required inputs are missing after reading the target file, surface the gap immediately and wait for clarification before proceeding.
- Expand the output format descriptions: for each of the six sections, add one sentence describing the minimum required content and the depth expected.
- Add artifact path guidance: when the caller requests a saved artifact, save the research brief under the iteration research directory (`iterations/iteration-N/research/`) and return the path.
- Add an explicit synthesis boundary to the scope section: note that the researcher stops at mapping notes and does not author eval rows.

## Suggested Metrics

- MCP activation rate: percent of runs where `find_agent_skill` and `load_agent_skill` are called before any research begins.
- Blocker-report accuracy: percent of runs where missing-constraint gaps are surfaced before proceeding rather than guessed.
- Brief completeness: percent of runs where all six output sections are present and non-trivial.
- Stop-recommendation precision: percent of runs where a stop recommendation is issued when no source clears the approval bar.
- Approval-bar explicitness: percent of runs where the approval bar is stated before sources are evaluated.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions in existing tests. Review representative research brief outputs against the evals.json cases in `skills/researcher-research/evals/` for section completeness and source-triage discipline.

## Recommendation

This is a worthwhile optimization target because research brief quality directly gates downstream synthesize and optimize quality. The current agent has correct role scoping and a clean MCP contract, but is underspecified on constraint resolution, blocker reporting, and output section depth.

Prioritize a rewrite that adds a pre-MCP constraint check, clarifies the `run_agent_skill` guard, and expands output section descriptions. Measure on brief completeness and blocker-report rate. Only expand examples if the first structured rewrite still produces incomplete section content.
