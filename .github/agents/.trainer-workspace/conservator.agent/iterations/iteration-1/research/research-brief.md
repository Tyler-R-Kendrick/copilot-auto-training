# Conservator Agent Research Brief

## Target Layout

- Target file: `.github/agents/conservator.agent.md`
- Local trainer workspace: `.github/agents/.trainer-workspace/conservator.agent`
- Local run artifacts for this iteration:
  - `iterations/iteration-1/research/research-brief.md`
  - `iterations/iteration-1/research/source-shortlist.json`
  - `iterations/iteration-1/synthesize/evals/evals.json`
  - `iterations/iteration-1/synthesize/datasets/train.jsonl`
  - `iterations/iteration-1/synthesize/datasets/val.jsonl`
  - `iterations/iteration-1/optimize/optimize-stage.json`

Canonical eval and dataset paths derived from the prompt would normally live next to the target file, but this workflow persists authored artifacts under the local `.trainer-workspace` tree as required by the repo trainer contract.

## Observed Interface

- The target is a review-only subagent instruction file, not a user-facing prompt template.
- The prompt currently has no task-input placeholders, so `trainer-optimize` cannot inject row-specific task content into the rendered prompt text.
- The stable contract that must be preserved is narrow and repo-specific: review prompt, dataset, evaluator, and validation changes for likely regressions without editing files or rerunning the full workflow.
- The engineer review identifies four rewrite priorities: stronger regression-detection reliability, a fixed evidence order, broader evaluator and validation coverage, and more stable output structure with an explicit no-finding path.

## Research Questions

1. Which sources best define the conservator agent's non-negotiable repo contract?
2. Which artifacts most directly justify stronger coverage for evaluator assumptions, authored eval compatibility, and validation adequacy?
3. Which source material supports a fixed audit sequence and output package without turning the prompt into a long-form judge?
4. Which evidence best explains whether the raw `.agent.md` target can be optimized meaningfully by the current runtime?

## Approval Bar

- The source must be authoritative for the conservator task or the optimizer runtime.
- The source must map directly to one of the user-requested optimization goals.
- The source must support objective eval authoring or blocker detection, not generic prompt-writing advice.
- The source must not require hidden benchmark notes to understand the repo behavior being tested.

## Approved Sources

1. The conservator engineer review.
   - Why approved: it is the clearest repo-owned statement of the prompt weaknesses and the desired rewrite direction.
   - What it supports: fixed evidence order, explicit evaluator and validation coverage, stable output structure, and an explicit no-finding path.

2. The current conservator agent prompt.
   - Why approved: it defines the current scope, required workflow checks, and the exact phrases that tests pin.
   - What it supports: preserving the review-only role while tightening the audit sequence and output contract.

3. `tests/test_customizations.py`.
   - Why approved: it encodes the repo's hard requirements for conservator language and workflow assumptions.
   - What it supports: seeded regression cases around MCP routing, hidden leader-election behavior, authored eval separation, and validation expectations.

4. Prompt-optimization and eval-manifest instructions.
   - Why approved: they define the repository's canonical distinction between prompt files, authored evals, and explicit train or validation datasets.
   - What it supports: dataset and manifest mismatch cases, plus output expectations for eval authoring.

5. `trainer-optimize` dataset and runtime references.
   - Why approved: they describe the actual scoring modes and the placeholder-driven render path used during optimization.
   - What it supports: choosing `judge_mode`, building realistic `llm_judge` rows, and flagging the raw target as non-optimizer-native.

6. The existing judge-agent trainer-workspace decision.
   - Why approved: it demonstrates an established repo pattern for prompt-like `.agent.md` files that cannot yet be optimized meaningfully by the runtime.
   - What it supports: writing a local optimize blocker artifact rather than claiming a successful APO pass when task input never reaches the prompt.

7. `RULERS`.
   - Why approved: it is the most relevant external methodology source for locked, evidence-anchored review structure.
   - What it supports: a small fixed taxonomy such as breaking regression, silent contract drift, missing proof, and a stable decision package.

## Rejected Candidates

- Generic code-review checklists.
  - Reason: they miss repo-specific regressions such as dropped `find_agent_skill` or `load_agent_skill` routing, or the blur between authored eval manifests and explicit runtime datasets.

- External benchmark summaries without the repo runtime contract.
  - Reason: they cannot explain the `.agent.md` placeholder mismatch or where this workflow must persist artifacts.

- Blog-style LLM review tips.
  - Reason: they are derivative and do not provide a trustworthy basis for authored eval rows or blocker decisions.

## Mapping Notes

- Use repo-local workflow contracts to seed cases for missing MCP routing, reintroduced internal election behavior, authored eval or dataset blur, evaluator undercoverage, and weak validation claims.
- Use the engineer review to seed cases that reward fixed evidence order, a stable output package, and explicit no-finding or missing-proof behavior.
- Use the optimizer runtime contract to author a blocker note explaining why a raw `.agent.md` file without placeholders cannot receive row-specific task input during optimization.
- Use the `RULERS` methodology only as support for structure and evidence anchoring, not as the primary content source.

## Unresolved Gaps

- The raw target prompt is not optimizer-native because it has no task-input placeholders. The current runtime can execute against it, but it cannot render per-row task content into the prompt.
- That mismatch means a full APO run against the raw prompt would not be operationally reliable even if the environment is healthy.
- No additional user input is required for synthesis because the repo-local sources and engineer review are sufficient to author conservator-specific eval and dataset cases for this iteration.