## Goal

Assess the current researcher agent as an optimization target for grounded source research work, with emphasis on triggering clarity, MCP routing discipline, and blocker handling when sources are missing or constraints are underspecified.

The optimization target is operational discipline rather than a role rewrite. A strong researcher agent should route discovery work through the `researcher-research` skill via the `agent-skills` MCP server, stop with a clear blocker report when no public source clears the approval bar, and remain silent on tasks where the source material is already known and the job is synthesis rather than discovery.

## Current Strengths

- The description is well-tuned for triggering. It names the right task types (public-source discovery, dataset triage, licensing review, provenance checks).
- The MCP routing contract is explicit: `find_agent_skill` → `load_agent_skill` → conditional `run_agent_skill`. This is testable and mirrors the engineer agent pattern.
- The scope is tightly bounded around grounded discovery rather than generic advice.
- The constraints explicitly forbid fabricating source authority or licensing, which is a high-risk failure mode for this task.
- The approach is ordered and ends with a clear stop condition when no source clears the bar.

## Main Risks

- **No explicit no-op path.** The prompt says to stop with a blocker report when no candidate clears the bar, but it does not say what to do when the task is already satisfied — for example, when the caller already has sufficient source material and only needs a brief confirmation. That gap could lead to unnecessary searching or fabrication.
- **Missing constraint handling is underspecified.** Step 4 says to name "missing constraints" in the plan, but the earlier constraints section only says "ask for them or report the gap" without clarifying when to ask vs. when to proceed with documented assumptions.
- **No fallback for MCP unavailability.** The MCP contract says to "discover and load the relevant skill contract first" but does not specify what to do when the agent-skills MCP server is not reachable. A brief fallback clarification would prevent silent failure.
- **Output format has no size or verbosity guidance.** The prompt says to return a "concise research brief," but it does not distinguish inline vs. saved artifact output. The argument-hint mentions a "desired research artifact location," but the output format section ignores this.
- **The "DO NOT involve any other agents" constraint** is absolute, but the agent uses agent-skills MCP tools. The constraint should clarify that `agent-skills/*` tool calls are permitted since they're listed in the `tools` frontmatter — this is a potential triggering confusion.

## Rewrite Hypotheses

- Add an explicit no-op path: when source material is already present or the task is clearly synthesis-only, say so and stop without initiating a full search plan.
- Clarify missing-constraint handling: specify that the agent asks when constraints materially change source selection AND the caller can answer, but proceeds with documented assumptions otherwise.
- Add a short MCP fallback note: if the MCP server is unavailable, apply the loaded skill's guidance directly using the agent's own research capability.
- Add inline vs. artifact output guidance tied to whether the caller supplies a desired artifact location.
- Tighten the "DO NOT involve any other agents" constraint so it explicitly refers to other workflow agents (student, teacher, judge) while keeping agent-skills MCP tool calls permitted.

## Suggested Metrics

- **No-op precision**: share of already-satisfied tasks where the agent correctly halts without unnecessary searching.
- **MCP routing compliance**: share of discovery tasks that invoke `find_agent_skill` and `load_agent_skill` before proposing sources.
- **Blocker accuracy**: share of underspecified tasks where the agent stops with a clear gap report rather than guessing sources.
- **Fabrication resistance**: share of runs where no source authority, licensing, or benchmark support is invented.
- **Output completeness**: share of research briefs that include approved sources, rejected candidates, mapping notes, and an unresolved-gap or stop recommendation.

## Validation Plan

Run `python -m pytest -q` after optimization to confirm no regressions. The research brief structure can be validated by checking that optimized outputs continue to include all required sections (target summary, approved sources, rejected candidates, mapping notes, gaps). Reviewer spot-checking on 3–5 diverse task inputs is the primary quality gate given the LLM-judge nature of the task.

## Recommendation

This agent has a strong base. The optimization should be minimal and focused: add an explicit no-op path, clarify missing-constraint behavior, note the MCP fallback, and tighten the "other agents" constraint. Avoid structural rewrites because the discovery framing, MCP routing contract, and stop condition are already well-formed.
