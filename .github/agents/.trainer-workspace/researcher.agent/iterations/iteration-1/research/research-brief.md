# Research Brief: researcher.agent.md Optimization

## Target and Task Summary

**Target:** `.github/agents/researcher.agent.md`
**Task:** Identify grounded sources and patterns for evaluating the researcher agent's ability to perform MCP-backed source discovery and produce complete research briefs.

**Optimization Goal:** Improve the agent's MCP execution discipline, research plan completeness, source approval bar adherence, and structured brief output quality.

## Research Plan

**Target layout:**
- Eval manifest: `skills/researcher-research/evals/evals.json` (reference only)
- Workspace evals: `iterations/iteration-1/synthesize/evals/evals.json`
- APO datasets: `iterations/iteration-1/synthesize/datasets/train.jsonl` and `val.jsonl`

**Approval bar:**
Each source must provide:
- Accountable maintainer or standards body
- Traceable data origin and schema
- Stable version or date
- Acceptable licensing for eval use

## Source Evaluation

### Research Question

What constitutes correct researcher agent behavior for each major behavioral dimension?

### Primary Authoritative Sources

1. **The researcher agent itself** (`researcher.agent.md`) — defines expected behaviors, MCP contract, output format.
   - Authority: repository-owned canonical contract
   - License: project-internal, freely reusable for eval authoring
   - Fit: exact match; forms the ground truth for correct/incorrect behavior

2. **The `researcher-research` skill** (`skills/researcher-research/SKILL.md`) — defines the source approval bar, output structure, and process steps the agent must follow.
   - Authority: repository-owned skill contract
   - License: project-internal
   - Fit: defines the expected execution path the agent must demonstrate

3. **The `trainer-synthesize` skill** (`skills/trainer-synthesize/SKILL.md`) — defines what the downstream consumer (synthesizer) needs from the research brief.
   - Authority: repository-owned skill contract
   - License: project-internal
   - Fit: defines minimum viable mapping note depth for the synthesizer to proceed

4. **Existing adversary.agent workspace** — provides structural reference for the expected workspace layout, eval case format, and judge-mode selection.
   - Authority: repository-internal prior run
   - License: project-internal
   - Fit: provides concrete examples of the eval shape

## Approved Sources

| Source | Fit | Risk | Notes |
|--------|-----|------|-------|
| researcher.agent.md | Direct | None | Primary behavioral contract |
| researcher-research/SKILL.md | Direct | None | Execution path and approval bar |
| trainer-synthesize/SKILL.md | Indirect | None | Downstream consumer expectations |
| adversary.agent workspace | Structural | None | Format reference only |

## Rejected Candidates

- **Public ML benchmark datasets (e.g., SQuAD, MS-MARCO):** These are reading-comprehension/retrieval tasks, not researcher-agent behavioral evaluation tasks. They would test the *subject* of research, not the agent's execution discipline. Rejected.
- **Generic agent eval benchmarks (e.g., AgentBench, WebArena):** Too broad; no specific coverage of MCP invocation discipline or structured brief output quality. Rejected.
- **Blog posts / tutorials on research methodology:** No accountable maintainer, unstable, not traceable to a standard. Rejected.

## Mapping Notes

The researcher agent should be evaluated on six behavioral dimensions mapped to the engineer-prompt review:

1. **MCP invocation** — Did the agent call `find_agent_skill` + `load_agent_skill` before any source recommendation?
   - Eval type: behavioral process check (llm_judge with criteria)

2. **Research plan completeness** — Does the output contain all six required components (target layout, query plan, approved sources, rejected candidates, mapping notes, unresolved gaps)?
   - Eval type: structural completeness (llm_judge with criteria)

3. **Source approval bar adherence** — Does each approved source include authority, provenance, licensing, and task-fit notes?
   - Eval type: quality check (llm_judge with criteria)

4. **Rejected-candidate documentation** — Does at least one rejected candidate appear with an explicit rejection reason?
   - Eval type: structural presence (llm_judge with criteria)

5. **Fallback / blocker behavior** — When MCP is unavailable or a required input is missing, does the agent stop with a clear blocker report?
   - Eval type: conditional behavior (llm_judge with criteria)

6. **Mapping note depth** — Do mapping notes include at least one specific field-to-eval-row mapping?
   - Eval type: quality check (llm_judge with criteria)

## Judge Mode

All eval cases use `llm_judge` because they evaluate open-ended agent behavior against qualitative criteria, not exact-match outputs.

## Unresolved Gaps

None. All required source material is available from repository-internal files. The eval cases will be synthesized from the agent's own behavioral contract.

## Recommendation

Proceed to synthesis. All required source material exists. Use `llm_judge` for all eval cases with specific criteria per behavioral dimension.
