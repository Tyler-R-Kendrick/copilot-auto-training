## Goal

Assess the current researcher agent as an optimization target for grounded public-source discovery in prompt-optimization and eval-authoring workflows. The optimization goal is operational reliability: the researcher agent should read evidence in a fixed order, activate the `researcher-research` skill via MCP before free-form searching, produce a structured research brief with explicit approved-source mapping, and stop cleanly when no grounded source clears the approval bar.

## Current Strengths

- The role is sharply scoped: grounded source research, not synthesis or optimization.
- The MCP Execution Contract correctly mandates `find_agent_skill` → `load_agent_skill` → `run_agent_skill` order before ad-hoc research.
- The constraints correctly prohibit guessing missing constraints that materially change source selection.
- The Scope section covers the right research surface: datasets, benchmarks, documentation, provenance, licensing.
- The Approach step 6 includes a blocker-report stopping condition when no source clears the bar.

## Main Risks

1. **No fixed evidence reading order.** The Approach says "Read the target prompt or skill file, task description, scoring rule, and any source constraints first" but gives no numbered order for how to process those inputs, how to handle conflicts between them, or when to stop reading before searching.

2. **No explicit workspace artifact path guidance.** When operating inside a trainer loop, the agent has no instruction about where to save the research brief — whether to write to the active iteration's `research/` directory or to an ad-hoc location. Other agents in this repo (adversary, teacher) use iteration-scoped paths.

3. **MCP unavailability not handled.** If `find_agent_skill` fails or the MCP server is unavailable, the prompt gives no fallback instruction. The agent may silently fall back to free-form research or freeze.

4. **No explicit stopping criteria for partial approval.** Step 6 stops when no source clears the bar, but gives no guidance on what to do when some sources partially clear (e.g., correct domain but wrong license), or when the research brief is "good enough" versus requiring another search pass.

5. **Output format is narrative rather than structured.** The six output items (target summary, research plan, approved sources, rejected candidates, mapping notes, unresolved gaps) are not named as artifact files with expected structure, making it harder for downstream synthesizers to parse the output reliably.

6. **Missing field-mapping concreteness.** The Approach says to "derive the target eval layout, prompt-visible placeholders, and field-mapping notes needed for later use" but does not describe what a complete field-mapping note looks like or what downstream fields it must cover (`input`, `reference`, `criteria`, `scoring`).

## Rewrite Hypotheses

- Add an explicit numbered evidence order (prompt interface → task boundary → scoring rule → domain constraints → licensing → missing constraints to resolve) before the Approach section.
- Add workspace artifact path guidance: when a trainer workspace exists, save the research brief as `research/research-brief.json` under the active iteration directory.
- Add an MCP fallback instruction: if `find_agent_skill` fails, report the MCP unavailability and proceed with free-form research only for tasks that do not require researcher-research skill execution.
- Clarify the partial-approval case: sources that partially clear the bar should be listed as "conditional" with explicit conditions required before use.
- Restructure the output format as a named JSON-compatible artifact (`research-brief.json`) with defined top-level keys: `target`, `research_plan`, `approved_sources`, `rejected_candidates`, `field_mapping`, `unresolved_gaps`.
- Expand the field-mapping note description to include the four downstream eval fields: `input`, `reference`, `criteria`, `scoring`.

## Suggested Metrics

- MCP activation rate: percent of research runs that call `find_agent_skill` before free-form search.
- Approved-source precision: percent of approved sources that downstream synthesis can directly use without requiring clarification.
- Blocker-report accuracy: percent of runs that correctly issue a blocker report when no source clears the approval bar.
- Field-mapping completeness: percent of research briefs that include a complete field mapping for all four eval fields.
- Partial-approval classification rate: percent of runs that correctly classify partial-approval sources as "conditional" rather than approved or rejected.
- Workspace path compliance: percent of trainer-loop runs that save research-brief.json to the correct iteration-scoped path.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite. Review a representative set of research-brief outputs against staged evals.json cases for field-mapping completeness and blocker-report accuracy. Check that the MCP activation instruction appears before any free-form search step.

## Recommendation

This is a moderate-priority optimization target. The current agent has the right scoping and constraints but is missing structured evidence order, explicit workspace artifact paths, MCP fallback handling, and a machine-readable output format. A first-pass rewrite that adds an evidence order, workspace path guidance, and a structured output format should measurably improve downstream usability without expanding scope. Keep the MCP execution contract and constraints unchanged. Measure on field-mapping completeness and blocker-report accuracy first.
