# Researcher Agent Research Brief

## Target Layout

- Target file: `.github/agents/researcher.agent.md`
- Local trainer workspace: `.github/agents/.trainer-workspace/researcher.agent`
- Local run artifacts for this iteration:
  - `iterations/iteration-1/research/research-brief.md`
  - `iterations/iteration-1/research/source-shortlist.json`
  - `iterations/iteration-1/synthesize/evals/evals.json`
  - `iterations/iteration-1/synthesize/datasets/train.jsonl`
  - `iterations/iteration-1/synthesize/datasets/val.jsonl`
  - `iterations/iteration-1/optimize/`

Canonical eval and dataset paths for this workflow live under the local `.trainer-workspace` tree per the repo trainer contract.

## Observed Interface

- The target is a specialist agent instruction file for grounded source research in prompt/skill evaluation workflows.
- The prompt has no task-input placeholders, so `trainer-optimize` cannot inject per-row task content into the rendered prompt. This is the same pattern as the conservator agent workspace.
- The stable contract that must be preserved is narrow and repo-specific: activate `researcher-research` via MCP before any free-form searching, resolve constraints before source selection, approve or reject sources against an explicit bar, and stop with a blocker report when no source clears the bar.
- The engineer review identifies five rewrite priorities: explicit constraint-resolution contract, embedded approval bar criteria, clear blocker-report template in the output format, clearer `run_agent_skill` threshold, and tighter elicitation scope.

## Research Questions

1. Which sources best define the researcher agent's non-negotiable repo contract (MCP activation, constraint elicitation, approval bar)?
2. Which artifacts most directly justify the rewrite hypotheses in the engineer review?
3. Which source material supports objective eval authoring for source-approval, blocker, and constraint-elicitation behaviors?
4. Which evidence explains whether the raw `.agent.md` target can be optimized meaningfully by the current runtime?

## Approval Bar

- The source must be authoritative for the researcher agent task or the optimizer runtime.
- The source must map directly to one of the five engineer-review rewrite priorities.
- The source must support objective eval authoring or blocker detection, not generic research advice.
- The source must not require hidden benchmark notes to understand the repo behavior being tested.

## Approved Sources

1. The researcher agent engineer review (`engineer-prompt/review.md`).
   - Why approved: it is the clearest repo-owned statement of prompt weaknesses and the desired rewrite direction.
   - What it supports: seeding eval cases around constraint resolution, approval-bar embedding, blocker-report template, and `run_agent_skill` threshold clarity.

2. The current researcher agent prompt (`.github/agents/researcher.agent.md`).
   - Why approved: it defines the current scope, MCP execution contract, and the exact phrases tests may pin.
   - What it supports: preserving the research-only scope while tightening the constraint-resolution and approval-bar contracts.

3. The `researcher-research` skill (`skills/researcher-research/SKILL.md`).
   - Why approved: it is the primary skill the researcher agent must activate and correctly determines when `run_agent_skill` applies.
   - What it supports: defining the deterministic-helper threshold, the approval bar content to embed, and elicitation scope.

4. `tests/test_customizations.py`.
   - Why approved: it encodes hard requirements for workflow language and assumptions.
   - What it supports: seeded cases around MCP routing, single-shot optimizer boundaries, and authored eval separation.

5. Prompt-optimization and eval-manifest instructions (`.github/instructions/`).
   - Why approved: they define the repository's canonical distinction between prompt files, authored evals, and explicit train/val datasets.
   - What it supports: dataset/manifest mismatch cases and output expectations for research brief completeness.

6. The conservator agent workspace (`.github/agents/.trainer-workspace/conservator.agent/`).
   - Why approved: it demonstrates the established repo pattern for `.agent.md` files that cannot be directly optimized by the APO runtime.
   - What it supports: writing a local optimize-blocker artifact rather than claiming an unsuccessful APO pass.

## Rejected Candidates

- Generic information-retrieval benchmark datasets (MSMARCO, TREC, NQ, TriviaQA).
  - Reason: they test retrieval quality, not whether an agent activates an MCP skill, elicits constraints, or enforces a source approval bar. They cannot produce authentic eval rows for this task.

- Academic source-evaluation rubrics (e.g., CRAAP test, SIFT).
  - Reason: they are public but do not align with the repo-specific approval bar criteria, MCP execution contract, or blocker-report format. Their format does not map to `llm_judge` rows that test agent behavior.

- Generic prompt-quality datasets.
  - Reason: they are derivative and unmoored from the specific researcher-agent behaviors (MCP activation, constraint elicitation, blocker path) the evals must cover.

- Web search and SEO blog posts on "research agent" prompts.
  - Reason: they are tertiary sources without accountable maintainers or traceable schema definitions.

## Mapping Notes

- Use repo-local workflow contracts to seed eval cases for:
  - MCP activation: the agent must call `find_agent_skill` and `load_agent_skill` before proposing any sources.
  - Constraint elicitation: the agent must identify and elicit required constraints (task boundary, scoring rule, placeholders) before searching.
  - Approval-bar enforcement: the agent must reject sources that fail authority, provenance, or licensing checks with explicit reasons.
  - Blocker path: when no source clears the bar, the agent must stop with a blocker report rather than forcing a recommendation.
  - Research-brief completeness: the output must include approved sources, rejected candidates, mapping notes, and unresolved gaps.
- Use the `researcher-research` skill contract to ground the `run_agent_skill` threshold case.
- Use `llm_judge` rows throughout since the task requires open-ended reasoning with `reference` + `criteria` assertions.

## Unresolved Gaps

- The raw target prompt has no task-input placeholders, matching the conservator pattern. A full APO run against the raw agent file would return `mode=manual_followup` because per-row task content cannot be injected.
- No external public dataset directly tests researcher-agent MCP activation or approval-bar enforcement. Synthesis from repo-local workflow contracts and simulated cases is the correct path.
- No additional user input is required; the repo-local sources and engineer review are sufficient to author this iteration's eval and dataset cases.
