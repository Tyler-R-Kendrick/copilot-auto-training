# Engineer-Prompt Review: researcher.agent.md

**Target file:** `.github/agents/researcher.agent.md`
**Review date:** 2026-04-13

## Target Goal

The `researcher.agent.md` agent contract defines a specialist agent for grounded source research to support prompt evaluation workflows. It must:
1. Route public-source discovery through the `researcher-research` skill via the `agent-skills` MCP server
2. Produce concise, evidence-based research briefs
3. Enforce primary-source discipline and reject weak/derivative sources
4. Stop with a blocker report when no acceptable source exists

## Current Prompt Analysis

### Strengths
- Clear MCP execution contract with ordered `find_agent_skill` → `load_agent_skill` → `run_agent_skill` steps
- Explicit scope definition that separates research from synthesis
- "Stop with a blocker report" safety valve is present
- Output format is structured and mirrors the researcher-research skill layout

### Likely Failure Modes

1. **Ambiguous `run_agent_skill` condition**: The condition "only when the researcher-research skill exposes a deterministic helper under `scripts/`" is easy to misread — agents may skip the MCP tool call entirely and default to free-form research when scripts are absent, defeating the MCP-first rule.

2. **Constraint contradiction**: "DO NOT involve any other agents" conflicts with the `agent-skills/*` tool allowance. The intent (no collaborative handoff to sibling agents like teacher/student) is valid but poorly stated — it could block legitimate MCP skill calls.

3. **Approach step 2 is too passive**: "Use `find_agent_skill` and `load_agent_skill` to activate `researcher-research` before **proposing** sources or a search plan" — the emphasis should be on *discovering and loading* before any research action, not just before proposing. Agents can interpret "proposing" narrowly.

4. **Output format lacks artifact path guidance**: The format tells the agent *what* to include but not *where to save* the research brief when called from a trainer workflow. The `argument-hint` mentions a desired artifact location, but the prompt body doesn't reinforce saving behavior.

5. **Missing: explicit guidance on the `load_agent_skill` fallback when scripts are absent**: When `researcher-research` has no runnable scripts, agents should use the loaded skill contract as the operating guide rather than improvising. This is implicit but not stated clearly enough.

6. **Scope ambiguity**: "Source material" in the constraints could be interpreted as including code, documentation, or internal files — not just public datasets. Clarifying "external public-source material" reduces this ambiguity.

## Dataset Gaps

The `skills/researcher-research/evals/` directory contains 3 eval cases covering:
- Support ticket intent classification research
- Bug entity extraction research
- Grounded QA research

These test the *skill*, not the *agent contract*. For agent-level optimization, we need:
- Cases that test MCP routing behavior (was `find_agent_skill` used?)
- Cases that test blocker-report behavior (no acceptable source → stop signal)
- Cases that test scope enforcement (synthesis request → redirect, not execution)

## Validation Plan

1. Run `python -m pytest -q` to confirm no regressions
2. Evaluate the optimized agent against the 3 researcher-research eval cases (the skill's existing evals serve as proxy tests for the agent)
3. Validate that the optimized contract preserves all required frontmatter fields

## Optimization Hypothesis

The highest-value rewrites are:
1. **Clarify `run_agent_skill` usage**: Replace the scripts-conditional with a positive instruction to use the loaded contract as the primary operating guide when no deterministic helper exists.
2. **Fix constraint wording**: Change "DO NOT involve any other agents" to "DO NOT hand off to other agents or coordinate collaborative loops" to avoid blocking MCP skill calls.
3. **Strengthen approach step 2**: Make the MCP discovery and load a hard prerequisite before *any* research action, not just before *proposing*.
4. **Add artifact-saving guidance**: Reference the `argument-hint` location in the approach and output sections so agent knows to persist the brief at the caller-supplied path.

## Next Step

Proceed with synthesis of train/val datasets, then optimize with `judge_mode=llm_judge` (output quality requires open-ended scoring).
