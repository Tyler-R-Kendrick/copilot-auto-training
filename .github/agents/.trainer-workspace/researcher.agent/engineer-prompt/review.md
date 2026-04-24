## Goal

Assess the current `researcher.agent.md` as an optimization target, focusing on grounded-source discipline, MCP skill routing accuracy, artifact completeness, and research-brief quality for downstream prompt-optimization workflows.

The optimization objective is **operational clarity and routing reliability**: a strong researcher agent should activate `researcher-research` consistently via MCP before doing any free-form discovery, produce structured research briefs with explicit approval/rejection evidence, surface licensing and provenance risks, and stop rather than guess when no candidate clears the approval bar.

## Current Strengths

- Role scope is well-defined: source discovery, licensing review, provenance checks, brief production.
- MCP execution contract is present: `find_agent_skill` → `load_agent_skill` → `run_agent_skill` sequence is documented.
- Constraints correctly prohibit fabricating source authority or guessing missing constraints.
- Output format enumerates the right sections: approved sources, rejected candidates, mapping notes, gaps.

## Main Risks

1. **No evidence order.** The approach says "read the target prompt first" but does not specify which artifacts to read in which order, or what to do when the target or scoring rule is ambiguous. Missing a fixed evidence priority can lead to inconsistent source selection.

2. **Skill routing is conditional but under-specified.** The prompt says to use `researcher-research` "whenever the task is about public-source discovery," but does not define what qualifies. When the boundary is unclear, the agent may improvise instead of delegating to the skill.

3. **No approval bar definition.** The approach mentions building a research plan that "names the approval bar," but the agent contract never defines what the minimum approval bar looks like for a source to be usable. Without a concrete threshold, the agent may approve low-quality sources or under-reject weak candidates.

4. **No structured rejection evidence.** The output format lists "rejected candidates with rejection reasons," but the prompt does not require the agent to record the rejection evidence, distinguish weak evidence from licensing failure from provenance risk, or explain what would make a rejected source approvable.

5. **Stop condition is underspecified.** The constraint says "if no candidate clears the approval bar, stop with a blocker report," but does not specify what a blocker report must contain or when to issue a partial brief versus a full stop.

6. **No minimum artifact completeness contract.** The prompt does not require the agent to produce structured output fields (source URL, license, annotation quality, benchmark support, mapping notes) in a machine-readable or predictable format that downstream synthesis can consume without guessing.

7. **MCP `run_agent_skill` gate is ambiguous.** The prompt says to run the skill "only when the skill exposes a deterministic helper under `scripts/`," but this is inconsistent with how other agents handle the non-scriptable case. When `scripts/` has no helper, the agent should still use the loaded skill contract as the operating guide, not fall back to improvisation.

## Rewrite Hypotheses

- Add an explicit evidence order: target prompt file → task description → scoring rule → constraints → existing workspace artifacts → prior research briefs.
- Define the MCP routing condition more precisely: any task that involves identifying, evaluating, or approving public-source material activates `researcher-research` via MCP.
- Add a concrete approval bar: at minimum, a source must provide public accessibility (URL or DOI), an acceptable license (permissive or academic), known annotation quality (paper or leaderboard reference), and a clear field mapping to the eval schema.
- Require structured rejection evidence: for each rejected source, record the specific failure mode (license, quality, coverage, leakage) and the bar that would need to be met for approval.
- Define the blocker report format: target, approved count, rejection reasons, unresolved gaps, recommended next step.
- Add a minimum artifact completeness requirement: each approved source entry must include URL, license, annotation quality note, field-mapping plan, and downstream synthesis notes.
- Clarify the `run_agent_skill` gate: when `scripts/` has no deterministic helper, use the loaded skill contract as the operating guide for the entire research task, not just as a fallback hint.

## Suggested Metrics

- Routing accuracy: percent of eligible tasks where `researcher-research` is activated via MCP before any free-form source proposal.
- Approval bar clarity: percent of briefs where each approved source explicitly passes all four bar criteria (accessibility, license, annotation quality, field mapping).
- Rejection evidence completeness: percent of rejected candidates where the specific failure mode is recorded.
- Blocker report quality: percent of stopped briefs that include all required fields (target, approved count, rejection reasons, gaps, next step).
- Artifact completeness: percent of approved source entries with all five required fields present.

## Validation Plan

Run `python -m pytest -q` from the repository root after any rewrite to confirm no regressions. Review representative research briefs from `skills/researcher-research/evals/` to check approval-bar coverage and artifact completeness against the rewritten contract.

## Recommendation

This is a good optimization target because `researcher.agent.md` drives the first stage of the trainer loop; routing and brief-quality failures here cascade into bad datasets and weak optimization. The current agent is reasonably scoped but lacks structured approval gates, concrete artifact completeness requirements, and an unambiguous MCP routing condition.

Prioritize a rewrite that adds a fixed evidence order, a concrete approval bar definition, structured rejection evidence, and a complete artifact completeness requirement. Keep the rewrite minimal and validate against `researcher-research` eval cases before finalizing.
