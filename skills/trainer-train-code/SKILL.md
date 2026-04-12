---
name: trainer-train-code
description: Own the end-to-end trainer loop for Python code targets optimized with Microsoft Trace (nodes, bundles, models, and trainable agent components). Use this whenever the caller needs to research, synthesize test-based datasets, optimize, validate, and write back a trained candidate for a code-type target. Prefer this specialized loop for any Python file or callable that benefits from deterministic, test-based or benchmark-based feedback rather than open-ended language instruction quality.
argument-hint: Describe the target Python file or component, the repository root, the test or benchmark command used as the feedback signal, the available stage capabilities, and any existing trace nodes, bundles, or models already in scope.
license: MIT
compatibility: Python 3.11+. Requires Microsoft Trace (trace-opt package). Works in repositories that keep trainer artifacts in `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Trainer Train - Code

Use this skill as the orchestration contract for one trainer run against a **Python code target** optimized through Microsoft Trace. The target is a Python file, function, helper, or agent component that benefits from test-based or benchmark-based feedback.

Read `references/code-loop-contract.md` for the full routing table, Trace-specific patterns, feedback-signal rules, and validation constraints before any stage execution.

## When to use this skill

- The selected target is a Python file or callable that should be improved with Microsoft Trace.
- The caller needs to initialize or resume a trainer workspace for a code target.
- Feedback signals exist as test results, benchmark scores, compiler errors, or deterministic evaluators.
- The optimization stage returns a manual follow-up payload and the loop must continue.
- A winning candidate needs to be validated against the test suite and written back.

Do not use this skill for prompt-only targets, skill files, or agent contracts. Read the parent trainer skill's `references/target-routing.md` to identify the appropriate specialist for those target types.

## Required inputs

- One selected Python target file or component boundary.
- Repository root or enough path context to derive the local trainer workspace.
- The feedback command: test suite, benchmark script, or deterministic evaluator (e.g., `python -m pytest -q`).
- The concrete stage capability map: researcher, synthesizer, optimizer, elector.
- The candidate trainable surface: which parts should become Trace nodes, bundles, or models.
- Any existing workspace artifacts, test results, or Trace configurations to reuse.

## Code-specific loop rules

### Trace surface selection

Choose the smallest trainable surface that Trace should control:

- Use `trace.node(trainable=True)` for mutable values: prompts, instruction strings, thresholds, templates, routing labels.
- Use `@trace.bundle(trainable=True)` for a callable whose behavior should be optimized as a unit: formatters, extractors, classifiers, repair functions.
- Use `@trace.model` when several trainable nodes and bundles belong to one coherent object.
- Leave orchestration, I/O, and stable business logic as plain Python outside the trainable surface.

### Judge mode

Code targets use **custom** scoring mode by default. Executable feedback (test pass/fail, benchmark scores, compiler errors) is authoritative. Use `llm_judge` only as a secondary signal when tests explain *what* failed but not *how* to improve it. Treat an explicit row-level `scoring` declaration as authoritative.

### Feedback signal discipline

- Reset feedback each iteration before the next backward pass.
- Preserve failed executions and feed them back through `ExecutionError` when the failure itself is informative.
- Prefer deterministic, repeatable checks over subjective critiques whenever possible.
- If no feedback signal can be deterministically rerun, stop and report a blocker.

### Import and dependency hygiene

- Keep Trace imports explicit and local to the trainable surface.
- Call out hidden dependencies inside trainable bundles before optimization begins.
- Warn when a trainable surface is too broad to produce attributable feedback.

## Core workflow

Follow this order. Consult `references/code-loop-contract.md` when artifact paths, Trace patterns, or feedback-signal choices are uncertain.

1. **Resolve target and workspace.** Derive `<code-name>` from the selected file using the canonical rule: strip only `.md` for `.md` files; for `.prompty` strip entirely; otherwise use `Path.stem`. For a typical Python file (`config.py`), strip `.py` to get `config`. Use `<target-dir>/.trainer-workspace/<code-name>/` as workspace root. If state indicates a resumed run, audit tracked artifact pointers and skip only stages that already produced valid outputs.
2. **Require the workspace review checkpoint.** Confirm the engineering review artifact exists before optimization starts. Report a blocker if it is absent.
3. **Initialize or refresh workspace.** Create or update `workflow-status.json`, source snapshot, the review subdirectory, `inputs/source/`, and `iterations/` directories.
4. **Identify the trainable surface.** Confirm which code boundaries should become Trace nodes, bundles, or models. Record the trainable surface in the workspace before optimization.
5. **Inspect existing datasets and evals.** Prefer reuse when train, validation, and authored eval assets already fit the code target and feedback signal. Keep authored evals, train data, and validation data as separate artifacts.
6. **Run missing-data path if needed.** If any required dataset or feedback-signal script is absent, pause optimization and gather them via the caller-supplied researcher and synthesizer.
7. **Infer judge mode.** Default to `custom` scoring for code targets. Treat explicit row-level `scoring` as authoritative. Stop and report inconsistency if train and validation splits imply different modes.
8. **Run at least one optimization pass.** Pass the inferred judge mode, the trainable surface description, and the feedback command to the optimizer.
9. **Handle manual follow-up if returned.** Save the report as `manual-followup-report.json`, answer the model-facing prompt, persist the candidate artifact, and continue the loop.
10. **Run election if multiple candidates exist.** Use the caller-supplied elector when optimization produces more than one defensible candidate.
11. **Publish iteration artifacts.** Stage steering, candidate bundles, validation logs, and a decision summary under the active iteration directory.
12. **Write back only when validation passes.** Confirm the test suite passes and the decision summary justifies write-back before persisting the winning candidate.

## Blocker-first rule

Stop and report a clear blocker before any optimization or rewrite when:

- The workspace review artifact is absent.
- No repeatable feedback signal exists (tests, benchmarks, or evaluator script).
- The trainable surface is undefined or too broad to produce attributable feedback.
- Tracked artifact pointers from a resumed run are missing or inconsistent.

A blocker report must name the missing artifact or undefined boundary, explain why the loop cannot advance, and leave `workflow-status.json` in a resumable checkpoint state.

## Output contract

Return:

1. Workspace status and any active blockers.
2. Current-turn decisions: trainable surface, judge mode, selected branch, blockers.
3. Optimization or manual follow-up status with artifact paths.
4. Feedback signal confirmation (test command and expected signal shape).
5. Validation status (test suite pass/fail).
6. Write-back decision and justification.
7. Next required action to resume or continue the loop.
