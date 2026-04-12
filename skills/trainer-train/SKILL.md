---
name: trainer-train
description: Own the end-to-end trainer loop contract for a prompt-like file, skill contract, or agent contract after the caller has already chosen the concrete stage capabilities. Use this whenever the current agent must set up the local trainer workspace, coordinate stage sequencing, maintain workflow state, manage steering and candidates, recover from manual follow-up mode, and decide whether a trained candidate is safe to write back.
argument-hint: Describe the target file, workspace root, validation command, available stage capabilities, agent roster, and any current blocker such as missing review artifacts, missing datasets, or manual follow-up recovery.
license: MIT
compatibility: Python 3.11+. Works in repositories that keep trainer artifacts in a local `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.4.0"
---

# Trainer Train

Use this skill as the orchestration contract for one trainer run against one selected target. Treat the concrete research, synthesis, optimization, and election capabilities as caller-supplied stage implementations. This skill owns the loop behavior, workspace state, steering, validation, and write-back rules around those stages.

## Before you start

- Read `references/workspace-contract.md`, `references/stage-orchestration.md`, and `references/collaboration-contract.md` before broad changes or stage execution.
- Consult those references whenever stage sequencing, artifact paths, scoring behavior, or ownership boundaries are uncertain.
- Do not improvise artifact paths, stage order, or write-back gates from memory.

## Target-type delegation

Before running the loop, identify the selected target type and read `references/target-routing.md` to determine whether a specialist trainer should handle this target instead. Specialists own target-specific workspace rules, judge-mode defaults, and write-back constraints for their domain.

Use this generic skill only when the target does not match any specialist category, the caller explicitly bypasses delegation, or the relevant specialist is unavailable.

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

Stop and report a clear blocker before attempting any optimization, rewrite, or stage execution when:

- the prerequisite workspace review artifact is absent
- train, validation, or authored eval assets are missing and the caller has not supplied them
- workflow state indicates a resumed run, but the tracked artifact pointers are missing, unreadable, or inconsistent with the active iteration

Prefer a justified blocker or no-op report over speculative rewriting. A blocker report must name the missing or inconsistent artifact, explain why the loop cannot advance safely, and leave workflow state in a resumable checkpoint shape. Do not describe the loop as complete while a blocker is active.

## Core workflow

Follow this order. At each step, read the relevant reference file if the correct path, scoring mode, or artifact name is uncertain.

1. Resolve the selected target and derive its local trainer workspace. If workflow state already indicates an in-progress run, treat this as a resume path: audit the tracked iteration, confirm the tracked artifact pointers still exist, and skip only the stages that already produced valid artifacts. Do not create a fresh iteration for a resumed run unless the active iteration is invalidated by a blocker.
2. Confirm the prerequisite workspace review artifact exists before training starts. Use the workspace reference when the exact path is uncertain.
3. Create or refresh workspace state, source snapshots, required subdirectories, and checkpoint metadata.
4. Inspect existing train, validation, and authored eval assets. Prefer reuse over regeneration when they fit the target, the scoring shape, and holdout expectations.
5. If any required dataset or eval asset is missing, or the validation split is not a genuine holdout, stop optimization and run the missing-data path before continuing.
6. Inspect representative dataset rows before optimization and infer the scoring mode the optimization stage should use. Treat an explicit row-level scoring declaration as authoritative.
7. Run at least one optimization pass for the selected target. The "fit for purpose" rule can guide later write-back decisions, but it must not be used to skip the first required optimization pass.
8. If optimization returns manual follow-up mode, answer the returned model prompt yourself, save the candidate artifact, and continue the loop.
9. If optimization produces multiple defensible candidates, run the separate selection stage instead of assuming the optimizer chose a winner.
10. Publish steering, candidate bundles, validation logs, and decision summaries under the active iteration.
11. Write the winning candidate back to the source file only when validation passes and the decision summary is written.

## Loop rules

### Workspace ownership

- Keep every trainer artifact inside the selected target's local workspace.
- Treat workflow state and required-artifact pointers as checkpoint data that must correspond to real files, not optional notes or future intentions.
- Preserve prior iteration artifacts unless the caller explicitly asks to discard them.
- Read `references/workspace-contract.md` when artifact paths, directory names, or status-file field names are in doubt.

### Missing-data path

- If train, validation, or authored eval assets are missing, stop optimization and gather them first through the caller-supplied stage capabilities.
- Prefer reuse over regeneration when existing assets already fit the target and scoring shape.
- Keep validation rows as a genuine holdout rather than a paraphrase-only copy of training rows.
- Treat an invalid or laundered holdout as a blocker, not as a soft preference.
- Keep authored evals, train data, and validation data as separate artifacts in separate files.

### Judge-mode inference

Infer the scoring mode from representative dataset rows before optimization begins. Use exactly one of these three modes:

- **Exact-match:** rows expose an `expected` field and the task truly has one correct answer with no normalization or partial-credit logic.
- **Structured or normalization-aware:** rows expose structured expectations or normalization-sensitive scoring such as schema checks, normalized matching, or custom comparison logic.
- **Open-ended judge:** rows expose a reference answer plus grading criteria, or explicitly declare an open-ended scoring path.

When a row declares `scoring`, treat that as authoritative. Only infer from other fields when `scoring` is absent. If train and validation rows imply different modes, or rows inside one split disagree materially, stop and report dataset inconsistency instead of guessing. Do not collapse richer scoring cases into exact-match.

### Manual follow-up recovery

- Treat manual follow-up mode as a supported branch, not as an optimization failure.
- Save the returned report, answer the model-facing prompt, persist the candidate artifact, and continue with steering, validation, and decision-making.
- Record the blocker reason, handoff summary, and any rerun guidance alongside the candidate so later turns can audit what happened.

### Validation and write-back

- Validate after every meaningful candidate revision.
- Prefer a justified no-op or blocker report over speculative rewrites when prerequisites are missing.
- Treat "already fit for purpose" as a write-back decision only after at least one optimization pass has completed.
- Never describe a candidate as accepted until validation passes and the decision summary is written.

## Collaboration rules

- The orchestration layer owns sequencing, workspace coordination, and candidate application decisions.
- Research specialists own grounded-source discovery and blocker reporting when source truth is missing.
- Review specialists should critique supplied artifacts and recommend the next steering turn without taking over orchestration.
- Revision specialists should produce bounded candidate changes and explain the reasoning behind them.
- Evaluation specialists should score candidates or trajectories from the supplied artifacts instead of inventing new workflow steps.
- Stress-test specialists should try distinct exploit candidates before finalization when robustness matters.

Read `references/collaboration-contract.md` when ownership boundaries, steering bundle contents, or candidate manifest structure are uncertain.

## Steering and candidate rules

- Publish one steering artifact per specialist turn plus rolling summaries for each specialist in the active iteration.
- Stage original, revised, and adversarial candidates as explicit candidate bundles before review or selection.
- Keep cross-run rollups at the workspace root only when they summarize the active best result.

## Output contract

Return:

1. workspace status and any active blockers
2. current-turn stage decisions: reuse choice, scoring mode, selected branch, and any blockers encountered this turn
3. optimization or manual-follow-up status with artifact paths
4. validation status
5. write-back decision and its justification
6. next required action to resume or continue the loop
