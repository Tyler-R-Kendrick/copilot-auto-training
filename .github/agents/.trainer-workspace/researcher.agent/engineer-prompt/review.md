## Goal

Assess the current researcher agent as an optimization target for public-source discovery and research artifact workflows, with emphasis on triggering clarity, MCP routing discipline, and constraint-elicitation behavior before searching.

The optimization target is research workflow discipline rather than a broader role rewrite. A strong researcher agent should route every public-source discovery task through the `researcher-research` skill via MCP, derive the target eval layout before searching, apply the approval bar strictly, and stop with a blocker report when no source clears that bar — rather than forcing a recommendation.

## Current Strengths

- The description is already strong for discovery. It covers public-source discovery, dataset triage, benchmark selection, licensing review, provenance checks, and source-quality gating with a clear triggering phrase.
- The MCP routing contract is explicit: `find_agent_skill` → `load_agent_skill` → conditional `run_agent_skill` for `researcher-research`.
- The scope boundary is well-stated: research artifacts only, not eval row authoring.
- The constraint-elicitation section correctly lists the inputs that must be resolved before searching.
- The output format is well-structured with six named sections.

## Main Risks

1. **Constraint elicitation is conditional, not mandatory.** The current prompt says "If any of these materially affect source selection and are missing, ask first." The conditional wording leaves room to skip elicitation when the agent incorrectly judges a constraint as non-material.

2. **No explicit stop path when constraints are unresolvable.** The constraints section ends at elicitation but never says to halt research if the caller cannot or does not provide required inputs. The skill itself says "stop with a blocker report" but the agent prompt is silent on this path.

3. **MCP routing contract lacks a fallback prohibition.** The current wording says to call `find_agent_skill` first but does not explicitly prohibit improvised free-form research when MCP is available. A strict prohibition would reduce scope drift.

4. **No explicit no-change path.** The prompt has no clause for preserving the target file when it is already fit for purpose, though this agent is not a file editor. However, it also lacks an explicit path for returning to the caller when the research task is fully satisfied by existing artifacts.

5. **Approach steps blend task setup and skill execution.** Steps 1 and 2 overlap with the MCP contract. Clearer separation of pre-search setup, MCP activation, and search execution would improve repeatability.

6. **Scope constraint is implicit.** "DO NOT involve any other agents" is present but "DO NOT fabricate" and "DO NOT guess" are in separate bullet groups. A consolidated constraint list would be easier to audit.

## Rewrite Hypotheses

- Add an explicit stop path when required constraints cannot be resolved: if elicitation produces no answer and the missing input materially changes source selection, stop and name the missing input.
- Replace the conditional constraint-elicitation phrasing with a mandatory resolve-before-search gate that enumerates the specific inputs from the Scope section.
- Add an explicit prohibition against free-form research when MCP is available, making the routing contract harder to skip.
- Consolidate `DO NOT` constraints into a single numbered list to reduce scanning overhead and make them easier to audit.
- Tighten the Approach steps so task setup, MCP activation, and search are clearly separated phases.
- Keep frontmatter and discovery surface essentially unchanged to preserve triggering accuracy.

## Suggested Metrics

- **Constraint elicitation rate**: percent of cases where the agent asks for missing inputs before searching rather than proceeding with guessed constraints.
- **MCP routing compliance**: percent of research tasks where `find_agent_skill` and `load_agent_skill` are called before any source recommendation.
- **Stop-report accuracy**: percent of cases where no acceptable source exists and the agent stops with a blocker report rather than forcing a weak recommendation.
- **Approval bar adherence**: percent of approved sources that include authority, provenance, licensing, and version notes.
- **Scope stability**: percent of runs that remain in research and mapping mode without attempting to author eval rows or hand off to other agents.

## Recommendation

The agent already has a solid base contract. The highest-value optimization is a small discipline-focused rewrite: make constraint elicitation mandatory, add an explicit stop path when inputs are unresolvable, and strengthen the MCP routing prohibition. Avoid a broader structural rewrite because the discovery text, output format, and scope boundary are already strong.
