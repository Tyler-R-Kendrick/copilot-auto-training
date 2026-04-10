---
name: trainer-train
description: Own the end-to-end trainer loop contract for a prompt-like file, skill contract, or agent contract after the caller has already chosen the concrete stage capabilities. Use this whenever the current agent must set up the local trainer workspace, coordinate stage sequencing, maintain workflow state, manage steering and candidates, recover from manual follow-up mode, and decide whether a trained candidate is safe to write back.
argument-hint: Describe the target file, workspace root, validation command, available stage capabilities, agent roster, and any current blocker such as missing review artifacts, missing datasets, or manual follow-up recovery.
license: MIT
compatibility: Python 3.11+. Works in repositories that keep trainer artifacts in a local `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Trainer Train

Use this skill as the orchestration contract for one trainer run against one selected target. Treat the concrete research, synthesis, optimization, and election capabilities as caller-supplied stage implementations. This skill owns the loop behavior, workspace state, steering, validation, and write-back rules around those stages.

Read `references/workspace-contract.md`, `references/stage-orchestration.md`, and `references/collaboration-contract.md` before making broad changes.

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

## Core workflow

Follow this order:

1. Resolve the selected target and derive its local trainer workspace.
2. Confirm the prerequisite engineering review artifact exists before training starts.
3. Create or refresh workspace state, source snapshots, required subdirectories, and checkpoint metadata.
4. Reuse existing datasets and eval assets when they fit; otherwise run the missing-data path before optimization.
5. Inspect representative dataset rows before optimization and infer the scoring mode the optimization stage should use.
6. Run at least one optimization pass for the selected target.
7. If optimization produces multiple defensible candidates, run the separate selection stage instead of assuming the optimizer chose a winner.
8. If optimization returns manual follow-up mode, answer the returned model prompt yourself, save the candidate artifact, and continue the loop.
9. Publish steering, candidate bundles, validation logs, and decision summaries under the active iteration.
10. Write the winning candidate back to the source file only when the candidate is defensible and validation passes.

## Loop rules

### Workspace ownership

- Keep every trainer artifact inside the selected target's local workspace.
- Treat workflow state and required-artifact pointers as checkpoint data, not optional notes.
- Preserve prior iteration artifacts unless the caller explicitly asks to discard them.

### Missing-data path

- If train, validation, or authored eval assets are missing, stop optimization and gather them first through the caller-supplied stage capabilities.
- Prefer reuse over regeneration when existing assets already fit the target and scoring shape.
- Keep validation rows as a genuine holdout rather than a paraphrase-only copy of training rows.

### Judge-mode inference

- Infer the scoring mode from the row shape before optimization begins.
- Use exact-match scoring only when the rows truly support exact-match grading.
- Use richer scoring whenever the rows depend on structured outputs, normalization, or open-ended judgment criteria.

### Manual follow-up recovery

- Treat manual follow-up mode as a supported branch, not as an optimization failure.
- Save the returned report, answer the model-facing prompt, persist the candidate artifact, and continue with steering, validation, and decision-making.

### Validation and write-back

- Validate after every meaningful candidate revision.
- Prefer a justified no-op or blocker report over speculative rewrites when prerequisites are missing or the current contract is already fit for purpose.
- Never describe a candidate as accepted until validation passes and the decision summary is written.

## Collaboration rules

- The orchestration layer owns sequencing, workspace coordination, and candidate application decisions.
- Research specialists own grounded-source discovery and blocker reporting when source truth is missing.
- Review specialists should critique supplied artifacts and recommend the next steering turn without taking over orchestration.
- Revision specialists should produce bounded candidate changes and explain the reasoning behind them.
- Evaluation specialists should score candidates or trajectories from the supplied artifacts instead of inventing new workflow steps.
- Stress-test specialists should try distinct exploit candidates before finalization when robustness matters.

## Steering and candidate rules

- Publish one steering artifact per specialist turn plus rolling summaries for each specialist in the active iteration.
- Stage original, revised, and adversarial candidates as explicit candidate bundles before review or selection.
- Keep cross-run rollups at the workspace root only when they summarize the active best result.

## Output contract

Return:

1. workspace status
2. stage decision and any blockers
3. optimization or manual-follow-up status
4. validation status
5. write-back decision
6. next-step guidance when the loop should continue
