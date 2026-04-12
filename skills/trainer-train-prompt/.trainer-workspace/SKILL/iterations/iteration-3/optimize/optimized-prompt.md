---
name: trainer-train-prompt
description: Own the end-to-end trainer loop for prompt-like files (*.prompt.md, *.prompty, *.instructions.md, system prompts, and other natural-language instruction artifacts). Use this whenever the caller needs to research, synthesize datasets, optimize, validate, and write back a trained candidate for a prompt-type target. Prefer this specialized loop for any file whose primary content is natural-language instructions rather than code, skill configuration, or agent contracts.
argument-hint: Describe the target prompt file, the repository root, the validation command, the available stage capabilities (researcher, synthesizer, optimizer, elector), and any existing dataset or workspace artifacts.
license: MIT
compatibility: Python 3.11+. Works in any repository that keeps trainer artifacts in `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Trainer Train - Prompt

Use this skill as the orchestration contract for one trainer run against a **prompt-like target**: any `*.prompt.md`, `*.prompty`, `*.instructions.md`, system prompt, or natural-language instruction file.

Read `references/prompt-loop-contract.md` for the full routing table, judge-mode rules, and prompt-specific validation constraints before any stage execution.

## When to use this skill

- The selected target is a prompt file, instruction file, or prompty artifact.
- The caller needs to initialize or resume a trainer workspace for a prompt target.
- Missing datasets or eval manifests need to be synthesized before optimization.
- The optimization stage returns a manual follow-up payload and the loop must continue.
- A winning candidate needs to be validated and written back to the source prompt file.

Do not use this skill for code files, skill files, or agent contract files. Read the parent trainer skill's `references/target-routing.md` to identify the appropriate specialist for those target types.

## Required inputs

- One selected prompt-like target file.
- Repository root or enough path context to derive the local trainer workspace.
- The validation command for the repository (e.g., `python -m pytest -q`).
- The concrete stage capability map: researcher, synthesizer, optimizer, elector.
- The currently available specialist-agent roster.
- Any existing workspace artifacts to reuse.

## Prompt-specific loop rules

### Judge mode

Use the following routing table (sourced verbatim from `references/prompt-loop-contract.md`) to infer scoring mode from dataset row shape:

| Row shape | Inferred mode |
|-----------|---------------|
| Explicit `scoring: exact_match` | `deterministic` |
| Explicit `scoring: llm_judge` | `llm_judge` |
| Explicit `scoring` (any other value) | Use that value as authoritative |
| `reference` + `criteria` fields, no explicit `scoring` | `llm_judge` |
| `expected` field only, task has one correct answer | Consider `deterministic`; default to `llm_judge` if ambiguous |
| No scoring fields | Default to `llm_judge` for prompt targets |

If the caller explicitly supplies a `scoring_mode` override at invocation time, treat that value as authoritative and skip per-row mode inference. Even with a caller-supplied override, still validate that the train and validation splits are internally consistent (i.e., do not imply conflicting modes) before proceeding; report a blocker if they are inconsistent.

### Placeholder preservation

Never remove, rename, or reorder template placeholders (e.g., `{{variable}}`, `{input}`, `<PLACEHOLDER>`) during optimization or write-back. Confirm placeholder set is unchanged before any candidate write-back. Any rename is a failure — for example, changing `{{user_query}}` to `{{query}}` in a candidate is not an acceptable optimization and must be rejected.

### Evaluator field isolation

Keep `expected`, `reference`, `criteria`, and `scoring` fields out of the prompt-visible render path. These are evaluator-only fields and must not appear in the optimized prompt text. See the write-back gate checklist in Step 11 for the corresponding pre-commit confirmation requirement.

### Few-shot and chain-of-thought patterns

When the dataset rows expose example pairs or step-by-step reasoning traces, preserve those structural patterns in the optimized candidate. Do not flatten multi-turn or chain-of-thought structures into a single instruction block.

## Core workflow

Follow this order. Consult `references/prompt-loop-contract.md` when artifact paths, scoring mode, or stage boundaries are uncertain.

1. **Resolve target and workspace.** Derive `<prompt-name>` by stripping `.prompty` entirely or stripping the final extension. Use `<target-dir>/.trainer-workspace/<prompt-name>/` as workspace root. If state indicates a resumed run, audit tracked artifact pointers and skip only stages that already produced valid outputs. The review checkpoint (Step 2) is exempt from this skip rule and must be re-confirmed on every run regardless of workflow state or tracked artifact pointers.
2. **Require the workspace review checkpoint.** Confirm the engineering review artifact exists before optimization starts. Report a blocker if it is absent.
3. **Initialize or refresh workspace.** Create or update `workflow-status.json` with an initial `workflow_state` value of `pending_engineer_prompt`. Create the review artifacts subdirectory, `inputs/source/`, and `iterations/` directories. The exact review path is defined in `references/prompt-loop-contract.md`. Copy the target file as the source snapshot to `inputs/source/<basename>` (e.g., `inputs/source/my-prompt.prompt.md`).
4. **Inspect existing datasets and evals.** Prefer reuse when train, validation, and authored eval assets already fit the prompt target and scoring shape. Keep authored evals, train data, and validation data as separate artifacts in separate files.
5. **Run missing-data path if needed.** If any required dataset or eval is absent or the validation split is not a genuine holdout, pause optimization and gather them via the caller-supplied researcher and synthesizer before continuing.
6. **Infer judge mode.** Inspect representative dataset rows and apply the routing table in the Judge mode section above. Default to `llm_judge` for prompt targets. Treat an explicit row-level `scoring` declaration as authoritative. Stop and report inconsistency if train and validation splits imply different modes (see Blocker-first rule for resolution path).
7. **Run at least one optimization pass.** Pass the inferred judge mode and the prompt-specific constraints (placeholder preservation, evaluator field isolation) to the optimizer.
8. **Handle manual follow-up if returned.** Save the optimizer report as `manual-followup-report.json`, answer the model-facing prompt, persist the revised candidate as `optimized-prompt.md`, and continue the loop. After persisting `optimized-prompt.md`, confirm placeholder preservation (full set unchanged, no renames) before proceeding to election or write-back.
9. **Run election if multiple candidates exist.** Use the caller-supplied elector when optimization produces more than one defensible candidate. A candidate is defensible when it: (a) passes the repository validation command with exit code 0, (b) achieves a judge score strictly above the current baseline score, and (c) falls within the elector's acceptable margin relative to the top-ranked candidate. If election produces no defensible candidate, report a blocker — set `workflow_state: pending_iteration_review`, explain why no candidate passed the defensibility gate, and recommend a new optimization pass or caller override before continuing.
10. **Publish iteration artifacts.** Stage steering, candidate bundles, validation logs, and a decision summary under the active iteration directory.
11. **Write back only when all gate conditions are satisfied.** Confirm each of the following before writing the winning candidate back to the source prompt file:
    1. Validation passes — the repository validation command (e.g., `python -m pytest -q`) exits with code 0.
    2. Placeholder preservation confirmed — the full placeholder set is identical between the original and the candidate; no placeholder was added, removed, renamed, or reordered.
    3. Evaluator fields absent — `expected`, `reference`, `criteria`, and `scoring` fields do not appear in the candidate prompt text.
    4. Decision summary written — `<workspace-root>/decision.md` exists and records the winning candidate, scores, and justification.
    5. Baseline score gate — if a prior baseline score exists in the workspace, the candidate's judge score must be at or above that baseline. Record the candidate score in `decision.md` whether or not a prior baseline score exists.

## Blocker-first rule

Stop and report a clear blocker before any optimization or rewrite when:

- The workspace review artifact is absent.
- Required datasets or authored evals are missing.
- Tracked artifact pointers from a resumed run are missing or inconsistent.
- Train and validation splits imply different judge modes — set `workflow_state: pending_dataset_repair` in `workflow-status.json` and choose one of two resolution paths: (1) repair or resplit the dataset so both splits share a consistent scoring shape, or (2) obtain an explicit caller-supplied `scoring_mode` override that supersedes row-shape inference.

A blocker report must name the missing artifact, explain why the loop cannot advance, and leave `workflow-status.json` in a resumable checkpoint state.

## Output contract

Return:

1. Workspace status and any active blockers.
2. Current-turn decisions: reuse choice, judge mode, selected branch, blockers.
3. Optimization or manual follow-up status with artifact paths — `manual-followup-report.json` and `optimized-prompt.md` for manual follow-up branches, or `optimize-report.json` for direct optimization branches.
4. Placeholder preservation confirmation.
5. Validation status.
6. Write-back decision and justification.
7. Next required action to resume or continue the loop.
