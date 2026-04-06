# Research Brief: prompt-optimization.instructions.md

## Target Layout

- **Prompt file**: `.github/instructions/prompt-optimization.instructions.md`
- **Eval manifest**: `.github/instructions/evals/evals.json`
- **Files dir**: `.github/instructions/evals/files/`
- **Workspace root**: `.github/instructions/.trainer-workspace/prompt-optimization.instructions/`
- **Placeholders**: none (instruction file only)

## Task Description

Improve `prompt-optimization.instructions.md` so agents editing prompt-like files follow actionable, non-ambiguous guidance: correct skill routing, dataset handling, judge-mode selection, evaluator-field isolation, validation commands, and workspace conventions.

## Scoring Rule

`llm_judge` — eval rows test agent understanding and correct behavior when following the instruction guidelines. Expected outputs describe what a compliant response looks like; objective assertions check observable properties.

## Research Plan

### Research Questions
1. Are there public benchmarks or datasets for testing instruction-following behavior for prompt-editing workflows?
2. Are there official guidelines or documentation on prompt-optimization instruction authoring?
3. Can the repo's own `engineer-prompt/review.md` and existing `evals.json` for related skills serve as grounded source material?

### Approval Bar
- Traceable origin with accountable maintainer.
- Clear label/annotation definitions suitable for eval authoring.
- Stable version or date.
- Acceptable contamination/leakage risk for this use case.

### Missing Inputs
- None — the target file is complete and self-contained.

## Source Evaluation

### Approved Sources

**1. Existing repo skill evals (primary source)**
- **Authority**: Tyler Kendrick / copilot-auto-training repository
- **Provenance**: hand-authored evals for closely related skills: `skills/engineer-prompt/evals/evals.json`, `skills/trainer-optimize/evals/evals.json`, `skills/trainer-synthesize/evals/evals.json`, `skills/trainer-research/evals/evals.json`
- **Task fit**: Directly adjacent to the target (prompt editing workflow, trainer skill routing)
- **Licensing**: MIT (repo license)
- **Risk**: Very low — same repo, no contamination concerns
- **Notes**: These provide the schema, eval row style, and assertion format for synthesis

**2. Engineer-prompt review.md for this target (primary source)**
- **Authority**: `.github/instructions/.trainer-workspace/prompt-optimization.instructions/engineer-prompt/review.md`
- **Provenance**: Handcrafted review identifying gaps, failure modes, and optimization hypotheses
- **Task fit**: Direct — this review defines what the optimized instruction file should achieve
- **Licensing**: Part of same repo
- **Risk**: None
- **Notes**: Defines failure modes that should become eval scenarios

**3. Existing instructions files and their workspaces (primary source)**
- **Authority**: `.github/instructions/agentic-workflow-editing.instructions.md` + its workspace
- **Provenance**: Same repo, sibling instruction files
- **Task fit**: Shows the pattern and scope of high-quality instruction files
- **Licensing**: MIT
- **Risk**: None

### Rejected Candidates

**Public benchmark datasets for instruction-following (IFEval, etc.)**
- **Reason**: IFEval and similar benchmarks test atomic constraint-following on arbitrary text, not domain-specific prompt-editing instructions. The task here is not measurable by a generic instruction-following benchmark.

**OpenAI prompt engineering guide**
- **Reason**: Tertiary summary/guide, not a labelled dataset. Cannot be converted to eval rows with ground truth.

**Anthropic prompt design documentation**
- **Reason**: Same — guidance documentation, not a grounded eval dataset.

## Mapping Notes

From the approved sources, eval rows should cover:
1. **Skill routing**: agent asks which skill to use when datasets are missing → should say `trainer-research` first, not `trainer-synthesize` directly
2. **Judge-mode selection**: agent is shown a dataset row with `reference`+`criteria` → should select `judge_mode=llm_judge`
3. **Evaluator field isolation**: agent editing a prompt template accidentally includes `expected` → should be flagged as wrong
4. **Placeholder preservation**: agent editing a prompt file should not silently remove/rename placeholders
5. **Validation command**: agent asks which command to run after editing → `python -m pytest -q`
6. **Dataset path explicitness**: agent should use explicit `train.jsonl` / `val.jsonl` paths, not auto-discover
7. **Election scope**: agent asks when to use `trainer-election` → only for comparing multiple optimize outputs, not single runs

## Unresolved Gaps

None — synthesis can proceed from repo-internal sources. No public dataset is needed; simulated eval rows grounded in the failure modes from the review.md are the appropriate path.

## Recommendation

Proceed directly to `trainer-synthesize` using:
- Failure modes from `engineer-prompt/review.md`
- Eval row style from `skills/engineer-prompt/evals/evals.json`
- No external source material needed
- `judge_mode=llm_judge` for all eval rows (open-ended instruction-following quality)
