# Judge Agent Research Brief

## Target Layout

- Target file: `.github/agents/judge.agent.md`
- Local trainer workspace: `.github/agents/.trainer-workspace/judge.agent`
- Local run artifacts for this iteration:
  - `iterations/iteration-1/research/research-brief.md`
  - `iterations/iteration-1/research/source-shortlist.json`
  - `iterations/iteration-1/synthesize/evals/evals.json`
  - `iterations/iteration-1/synthesize/datasets/train.jsonl`
  - `iterations/iteration-1/synthesize/datasets/val.jsonl`

Canonical eval and dataset paths derived from the prompt would live next to the prompt file, but this workflow persists the authored artifacts under the local `.trainer-workspace` tree as required by the repo-level trainer contract.

## Observed Interface

- The target is a subagent instruction file, not a user-facing task template.
- The prompt has no task-injection placeholders, so the optimizer cannot feed per-row task input into the rendered prompt text without a wrapper harness.
- The stable behavioral contract already present in the file is evidence-first judging with MCP routing into `judge-trajectory` and `judge-outcome`.
- The engineer review identifies four optimization priorities: operational reliability, routing clarity, rubric stability, and output structure.

## Research Questions

1. Which primary sources best justify a locked-rubric, evidence-anchored judging style for a judge subagent?
2. Which sources most directly support the boundary between process-heavy trajectory judging and outcome-only judging?
3. Which sources justify explicit missing-evidence handling, confidence calibration, and order-bias checks?
4. Which sources should shape eval rows for routing, runtime-failure separation, and concise decision packages without leaking benchmark notes into runtime task inputs?

## Approval Bar

- Accountable maintainer, publisher, or cited paper title with stable lookup identifier.
- Clear connection to one of the optimization goals: routing, rubric stability, evidence discipline, confidence calibration, or bias robustness.
- Enough methodological detail to justify eval assertions and rewrite hypotheses.
- Explicit fit for judge or evaluator behavior, not generic prompt-writing advice.

## Approved Sources

1. `RULERS: Locked Rubrics and Evidence-Anchored Scoring for Robust LLM Evaluation` (`arXiv:2601.08654`)
   - Fit: strongest source for immutable dimensions, explicit score boundaries, and evidence-anchored scoring.
   - Use in this run: supports a stable rubric shell and a fixed decision package.

2. `A Survey on Agent-as-a-Judge` (`arXiv:2601.05111`)
   - Fit: strongest source for process-aware judging, trajectories, tool calls, and verifier-backed evidence gathering.
   - Use in this run: supports clearer routing into `judge-trajectory` when traces, failures, or side effects matter.

3. `JudgeBench: A Benchmark for Evaluating LLM-based Judges` (`arXiv:2410.12784`)
   - Fit: strongest pressure source for judge brittleness and overconfidence on hard pairwise tasks.
   - Use in this run: justifies evidence-first scoring, fixed rubrics, and skepticism toward fluent but weakly grounded summaries.

4. `AdaRubric: Task-Adaptive Rubrics for LLM Agent Evaluation` (`arXiv:2603.21362`)
   - Fit: best source for adaptive dimensions that still respond to task shape.
   - Use in this run: supports a stable default rubric shell with limited pre-scoring adaptation rather than ad hoc dimension drift.

5. `Improving LLM-as-a-Judge Inference with the Judgment Distribution` (`arXiv:2503.03064`)
   - Fit: best calibration source in the local reference set.
   - Use in this run: supports explicit low-confidence handling when evidence is thin, conflicting, or order-sensitive.

6. `Gaming the Judge: Unfaithful Chain-of-Thought Can Undermine Agent Evaluation` (`arXiv:2601.14691`)
   - Fit: strongest caution against trusting narrated reasoning over artifacts.
   - Use in this run: supports low-trust treatment of self-explanations and stronger missing-evidence behavior.

7. Position-bias work and `PCFJudge`
   - Fit: strongest source family for order effects and presentation bias.
   - Use in this run: supports explicit order-robustness checks and confidence reduction on close calls.

## Rejected Candidates

- `ContextualJudgeBench` as a direct synthesis source.
  - Reason: the local reference explicitly treats it as a lookup key rather than a single pinned primary artifact, so it is useful benchmark pressure but not a clean direct basis for eval authoring in this workspace.

- Generic blog-style “LLM judge best practices” summaries.
  - Reason: derivative guidance without stable protocol details does not clear the approval bar for eval authoring.

- RewardBench 2 as the primary routing source.
  - Reason: useful background pressure for hard preference tasks, but less direct than trajectory and rubric papers for the specific routing boundary between `judge-trajectory` and `judge-outcome`.

## Mapping Notes

- `RULERS` maps to eval cases that require a locked rubric, explicit pass or partial or fail boundaries, and a rigid decision package.
- `Agent-as-a-Judge` maps to mixed-evidence and runtime-failure cases where trajectory evidence must outrank polished final prose.
- `JudgeBench` maps to cases that penalize unsupported claims and reward observable evidence over generic persuasion.
- `AdaRubric` maps to cases that allow limited rubric adaptation while preserving a stable shell.
- `Judgment Distribution` and order-bias work map to close-call cases that require lower confidence and explicit order-robustness notes.
- `Gaming the Judge` maps to cases that reject unsupported chain-of-thought and require missing-evidence callouts.

## Unresolved Gaps

- The current target prompt is not optimizer-native because it has no task-input placeholder. The `trainer-optimize` runtime can validate it, but it cannot inject per-row task input into the rendered prompt text.
- Because of that mismatch, a full APO run against the raw target file would not be operationally reliable. This workflow should treat optimize as a debug-only or blocked preflight unless a temporary wrapper harness is introduced.
- The local research reference is sufficient for grounded synthesis, so no additional user input is required for this iteration.