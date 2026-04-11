---
name: trainer-train
description: Own the end-to-end trainer loop contract for a prompt-like file, skill contract, or agent contract after the caller has already chosen the concrete stage capabilities. Use this whenever the current agent must set up the local trainer workspace, coordinate stage sequencing, maintain workflow state, manage steering and candidates, recover from manual follow-up mode, and decide whether a trained candidate is safe to write back.
argument-hint: Describe the target file, workspace root, validation command, available stage capabilities, agent roster, and any current blocker such as missing review artifacts, missing datasets, or manual follow-up recovery.
license: MIT
compatibility: Python 3.11+. Works in repositories that keep trainer artifacts in a local `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.3.0"
---

# Trainer Train

Use this skill as the orchestration contract for one trainer run against one selected target. Treat the concrete research, synthesis, optimization, and election capabilities as caller-supplied stage implementations. This skill owns the loop behavior, workspace state, steering, validation, and write-back rules around those stages.

## Before you start

- Read `references/workspace-contract.md`, `references/stage-orchestration.md`, and `references/collaboration-contract.md` before broad changes or stage execution.
- Consult those references whenever stage sequencing, artifact paths, scoring behavior, or ownership boundaries are uncertain.
- Do not improvise artifact paths or stage order from memory.

## When to use this skill

Use it when the current agent needs to:

- run the repository trainer loop for one selected prompt-like file
- initialize or resume a local `.trainer-workspace/` for that target
- coordinate missing-data recovery before optimization starts
- choose stage order and judge mode from the available artifacts
- manage steering, candidate staging, and validation across one or more iterations
- recover when optimization returns a manual follow-up payload instead of a finished candidate
- decide whether to apply the winning candidate back to the source file

Do not use this skill for isolated research, isolated dataset authoring, single-shot optimization without workspace coordination, or standalone winner selection with no loop orchestration around it.

## Required inputs

- one selected target file
- the repository root or enough path context to derive the local trainer workspace
- the validation command for the repository
- the concrete stage capability map supplied by the caller
- the currently available specialist-agent roster
- any existing workspace artifacts that should be reused

## Blocker-first rule

**Stop and report a clear blocker before attempting any optimization, rewrite, or stage execution when:**

- the prerequisite engineering review artifact is absent
- train, validation, or authored eval assets are missing and the caller has not supplied them
- `workflow-status.json` is in `training` state from a prior session (resume instead of re-initializing)

Prefer a justified blocker or no-op report over any speculative rewrite. A blocker report must name the missing artifact, explain why the loop cannot advance without it, and leave `workflow-status.json` in a resumable checkpoint state. Do not describe the loop as complete when a blocker is active.

## Core workflow

Follow this order. At each step, read the relevant reference file if the correct path, scoring mode, or artifact name is uncertain.

1. **Resolve and initialize.** Derive the local trainer workspace from the selected target. Check `workflow-status.json`. If `workflow_state` is `training`, treat this as a resumption: read `required_artifacts.latest_iteration_dir`, audit which stages already produced artifacts in that iteration directory, and skip completed stages. Do not create a new iteration directory for a resumed run.
2. **Confirm the prerequisite.** Verify that `engineer-prompt/review.md` exists. If it is absent, apply the blocker-first rule and stop.
3. **Check for reusable assets.** Inspect existing train, validation, and authored eval assets. Prefer reuse over regeneration when they fit the selected target and scoring shape. Record which assets are reused in `workflow-status.json`.
4. **Run the missing-data path if needed.** If any required dataset or eval asset is missing and the caller has not supplied it, pause optimization and gather inputs through the caller-supplied stage capabilities before continuing.
5. **Infer judge mode.** Inspect representative dataset rows before calling the optimization stage. See the judge-mode inference section below. Pass the selected mode explicitly — do not rely on a default.
6. **Run at least one optimization pass.** Execute the optimization stage for the selected target using the train dataset, validation dataset, and authored evals. Store outputs under `iterations/iteration-N/optimize/`.
7. **Handle manual follow-up.** If optimization returns `mode=manual_followup`, follow the manual follow-up branch (see below) rather than stopping. Continue the loop after the branch completes.
8. **Run separate selection if needed.** If optimization produces multiple defensible candidates that require comparison, run the selection stage as a separate step. Do not assume the optimizer chose a winner internally.
9. **Stage candidates and steering.** Publish candidate bundles and steering artifacts before any write-back decision.
10. **Validate.** Run the repository validation command after every meaningful candidate revision.
11. **Write back.** Apply the winning candidate to the source file only when validation passes **and** the decision summary is written.

## Loop rules

### Workspace ownership

- Keep every trainer artifact inside the selected target's local workspace.
- Treat `workflow-status.json` and required-artifact pointers as checkpoint data that must reflect actual file existence, not intended paths.
- Preserve prior iteration artifacts unless the caller explicitly asks to discard them.
- Read `references/workspace-contract.md` when artifact paths, directory names, or `workflow-status.json` field names are in doubt.

### Missing-data path

- If train, validation, or authored eval assets are missing, stop optimization and gather them first through the caller-supplied stage capabilities.
- Prefer reuse over regeneration when existing assets already fit the target and scoring shape.
- Keep the validation split as a genuine holdout rather than a paraphrase-only copy of training rows.
- Keep authored evals, train data, and validation data as separate artifacts in separate files.

### Judge-mode inference

Infer the scoring mode from representative dataset rows before passing it to the optimization stage. Use exactly one of these three modes:

- **Exact-match:** rows expose an `expected` field and the task genuinely has one correct answer with no normalization or partial-credit logic needed. Use only when this is truly the case.
- **Structured / normalization-aware:** rows expose `expected_json`, row-level scoring fields such as `normalized_match` or `json_schema`, or `custom_python` functions. Use this mode when outputs must be parsed or normalized before comparison.
- **Open-ended / LLM judge:** rows expose a `reference` answer plus `criteria` fields, or explicitly declare `scoring: "llm_judge"`. Use this mode when grading depends on subjective quality or multi-criterion judgment.

When a row declares `scoring`, treat that as authoritative. Only infer from fields such as `expected`, `expected_json`, `reference`, or `criteria` when `scoring` is absent. If train and validation rows imply different scoring modes, stop and report dataset inconsistency instead of guessing. Do not collapse richer scoring cases into exact-match. Pass the inferred mode explicitly to the optimization stage.

### Manual follow-up recovery

When optimization returns `mode=manual_followup`:

1. Save the returned payload as `manual-followup-report.json` under `iterations/iteration-N/optimize/`.
2. Answer the returned model-facing prompt using the current orchestrating agent.
3. Save the answer as `optimized-prompt.md` under the same optimize directory.
4. Save `operator-followup.md` with the blocker reason, handoff summary, and the optional rerun command.
5. Treat `optimized-prompt.md` as the optimize-stage candidate for the rest of the workflow.
6. Continue with steering, validation, and decision-making. Do not stop at the handoff artifact.

Treat manual follow-up mode as a supported branch, not an optimization failure.

### Validation and write-back

- Validate after every meaningful candidate revision, not only at the end of the loop.
- Never describe a candidate as accepted until **both** validation passes **and** the decision summary is written under the workspace root.
- Prefer a justified no-op or blocker report over speculative rewrites when prerequisites are missing or the current contract is already fit for purpose.

## Collaboration rules

- The orchestration layer owns sequencing, workspace coordination, and candidate application decisions.
- Research specialists own grounded-source discovery and blocker reporting when source truth is missing.
- Review specialists should critique supplied artifacts and recommend the next steering turn without taking over orchestration.
- Revision specialists should produce bounded candidate changes and explain the reasoning behind them.
- Evaluation specialists should score candidates or trajectories from the supplied artifacts instead of inventing new workflow steps.
- Stress-test specialists should try distinct exploit candidates before finalization when robustness matters.

Read `references/collaboration-contract.md` when agent ownership boundaries or candidate bundle structure is uncertain.

## Steering and candidate rules

- Publish one steering artifact per specialist turn plus rolling summaries for each specialist in the active iteration.
- Stage original, revised, and adversarial candidates as explicit candidate bundles before review or selection.
- Keep cross-run rollups at the workspace root only when they summarize the active best result.

## Output contract

Return:

1. workspace status and any active blockers
2. current-turn stage decisions: reuse choice, judge mode, selected branch, and any blockers encountered this turn
3. optimization or manual-follow-up status with artifact paths
4. validation status
5. write-back decision and its justification
6. next required action: what must happen next to resume or continue the loop, and what is waiting on it
