# Judging Techniques Reference

Use this brief when optimizing judge prompts, rubric-heavy evaluators, or `llm_judge` scoring workflows for the judge agent. It lives next to `judge.agent.md` inside the judge agent's local trainer workspace so benchmark guidance stays with the prompt being optimized rather than drifting into a generic skill directory.

## Citation lookup notes

When an exact stable identifier is available, this file includes an arXiv ID and title for fast lookup. When a named system or benchmark does not have one canonical identifier in this brief, use the quoted title or system name as the lookup key.

## Current synthesis

The modern judge frontier is rubricized, evidence-anchored, trajectory-aware, tool-verifying, and bias-aware. The practical implication for this repo is simple: a strong judge prompt should behave more like a small audit system than a generic grader.

## Canonical benchmark pressure

### JudgeBench

- Source: JudgeBench, 2024.
- Citation lookup: "JudgeBench: A Benchmark for Evaluating LLM-based Judges" (`arXiv:2410.12784`, `https://arxiv.org/abs/2410.12784`).
- Why it matters: strong judges often perform only slightly above random on difficult response pairs.
- What it should change in prompt design: do not assume that a generally capable model becomes a reliable judge with a minimal "score this answer" prompt. Use explicit rubrics, observable evidence, and narrow confidence claims.

### ContextualJudgeBench

- Source: reported in the judge-benchmark literature and related benchmarking discussions.
- Citation lookup: use the benchmark name `ContextualJudgeBench` together with the JudgeBench and LLM-as-a-Judge benchmarking literature when tracing contextual judge-consistency results.
- Why it matters: contextual evaluation remains brittle even for strong judge models, with consistency only modestly above chance on hard settings.
- What it should change in prompt design: force the judge to ground decisions in provided context, references, and task-specific criteria instead of rewarding fluent but weakly grounded explanations.

### RewardBench 2

- Source: RewardBench 2, 2025.
- Citation lookup: use the benchmark name `RewardBench 2` and the project paper or benchmark release notes for the current version being referenced.
- Why it matters: it is materially harder than the original RewardBench and exposes weaknesses in shallow preference scoring.
- What it should change in prompt design: treat hard preference or ranking judgments as high-risk. Require stronger comparison structure, explicit failure modes, and tie-break logic.

## Locked-rubric and rubric-generation techniques

### RULERS

- Source: RULERS, 2026.
- Citation lookup: "RULERS: Locked Rubrics and Evidence-Anchored Scoring for Robust LLM Evaluation" (`arXiv:2601.08654`, `https://arxiv.org/abs/2601.08654`).
- Core idea: compile natural-language rubrics into locked criteria with explicit score boundaries, structured decoding, deterministic evidence checks, and post-hoc calibration.
- Practical takeaway: judge prompts should name immutable dimensions, required evidence, and score boundaries. Avoid free-form holistic scoring when a dimensioned rubric is possible.

### Autorubric

- Source: Autorubric.
- Citation lookup: use the system name `Autorubric` together with terms such as `behavioral anchors`, `locked rubrics`, and `multi-round sampling`.
- Core idea: use behavioral anchors, locked rubric structure, and inference-time aggregation rather than a single unstructured grade.
- Practical takeaway: when optimizing a judge prompt, encode what a high, medium, or low score means. If the workflow samples multiple judgments later, the rubric should still be stable under repeated runs.

### AdaRubric

- Source: AdaRubric, 2026.
- Citation lookup: "AdaRubric: Task-Adaptive Rubrics for LLM Agent Evaluation" (`arXiv:2603.21362`, `https://arxiv.org/abs/2603.21362`).
- Core idea: synthesize rubric dimensions per task and score step-by-step with confidence-aware aggregation.
- Practical takeaway: use fixed rubric shells only when the task family is stable. For new tasks, adapt dimensions to the actual task contract, tool use, and artifact expectations.

### RubricRAG

- Source: RubricRAG.
- Citation lookup: use the system name `RubricRAG` with `retrieval-grounded rubric generation`.
- Core idea: retrieve related rubrics and examples before generating a task-specific rubric.
- Practical takeaway: keep benchmark and rubric references in this judge-local trainer workspace so prompt-optimization workflows can reuse them without moving the source of truth away from the judge agent.

## Agent and trajectory judging

### Agent-as-a-Judge survey

- Source: Agent-as-a-Judge survey, 2026.
- Citation lookup: "A Survey on Agent-as-a-Judge" (`arXiv:2601.05111`, `https://arxiv.org/abs/2601.05111`).
- Core idea: judging is shifting from endpoint-only grading to planned workflows that inspect trajectories, tool calls, environment effects, and gathered evidence.
- Practical takeaway: when workspace artifacts include intermediate steps, evaluate process quality, verifier usage, and side effects, not just polished final prose.

### VerifiAgent and related verifier-backed systems

- Source: verifier-backed judge systems summarized by the survey.
- Citation lookup: use the system name `VerifiAgent` together with `verifiable correctness` and `reasoning task verification`.
- Core idea: the judge should gather or verify evidence before scoring.
- Practical takeaway: in this repo, prioritize concrete artifacts such as `optimize-report.json`, validation logs, benchmark summaries, and dataset criteria. Do not reward unsupported claims when the artifacts disagree.

## Inference and aggregation techniques

### Judgment distribution

- Source: Improving LLM-as-a-Judge Inference with the Judgment Distribution, 2025.
- Citation lookup: "Improving LLM-as-a-Judge Inference with the Judgment Distribution" (`arXiv:2503.03064`, `https://arxiv.org/abs/2503.03064`).
- Core idea: using the distribution over judgment outcomes can outperform a single greedy decoded verdict.
- Practical takeaway: even if the runtime currently emits one summary, the prompt should preserve calibrated uncertainty. Avoid forcing fake certainty when the evidence is thin or conflicting.

### Multi-agent or panel judging

- Source: Agent-as-a-Judge survey and CollabEval.
- Citation lookup: use `CollabEval` and `multi-agent judging` together with the Agent-as-a-Judge survey for the broader method family.
- Core idea: role-specialized or debate-style judging can outperform single-pass judging.
- Practical takeaway: this repo's current judge subagent is single-agent, so emulate the benefit by making the prompt compare candidates across multiple explicit dimensions rather than collapsing immediately to one verdict.

## Bias and robustness guidance

### Order and presentation bias

- Sources: position-bias work in rubric-based judging and PCFJudge.
- Citation lookup: "Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge" (`arXiv:2602.02219`, `https://arxiv.org/abs/2602.02219`) and the system name `PCFJudge` for listwise order-robust factuality judging.
- Why it matters: candidate order and presentation details can change verdicts.
- What it should change in prompt design: ask for order-robust comparison language, require explicit evidence for differences, and note when the result is close enough that order effects may matter.

### Bias-bounded evaluation

- Source: Bias-Bounded Evaluation.
- Citation lookup: use the system name `Bias-Bounded Evaluation` together with `judge sensitivity` and `bias-bounded scoring`.
- Why it matters: a judge can look accurate while still being highly sensitive to chosen framing biases.
- What it should change in prompt design: call out potential sensitivity and avoid overstating confidence when the comparison is narrow or the rubric is under-specified.

## Chain-of-thought caution

### Gaming the Judge

- Source: Gaming the Judge, 2026.
- Citation lookup: "Gaming the Judge: Unfaithful Chain-of-Thought Can Undermine Agent Evaluation" (`arXiv:2601.14691`, `https://arxiv.org/abs/2601.14691`).
- Why it matters: exposing chain-of-thought can bias verdicts if the judge trusts narration more than observable state or actions.
- What it should change in prompt design: prefer evidence from artifacts, tool traces, and verifiable outputs over the candidate's self-explanation.

### CoT and uncertainty collapse

- Source: judgment-distribution work and related judge-analysis papers.
- Citation lookup: start with "Improving LLM-as-a-Judge Inference with the Judgment Distribution" (`arXiv:2503.03064`) and then expand to related chain-of-thought calibration papers if needed.
- Why it matters: explicit chain-of-thought can collapse useful uncertainty and worsen judgments.
- What it should change in prompt design: do not require long explanatory reasoning from the judge when a concise evidence table or rubric summary is enough.

## Repo usage rules

- Use this file to inform prompt optimization, trainer guidance, and rubric authoring for the judge agent.
- Keep evaluator-only benchmark notes out of dataset `input` fields and out of prompt-visible task content unless the benchmark itself is the object of the task.
- Keep runtime scoring prompts concise. Put durable benchmark summaries here, then point prompts or trainer workflows at this file when they need current judging guidance.
- When creating or tuning `llm_judge` datasets, pair `reference` and `criteria` with a judge prompt that can justify its score from observable evidence.

## Suggested reading order

1. JudgeBench or equivalent benchmark summary for general judge weakness.
2. RewardBench 2 for hard preference and ranking pressure.
3. RULERS for locked-rubric design.
4. AdaRubric and RubricRAG for task-adaptive rubric generation.
5. Agent-as-a-Judge survey for trajectory, planning, tool use, and multi-agent patterns.
6. Judgment-distribution and order-bias papers for calibration and robustness.
7. Gaming the Judge for chain-of-thought skepticism.