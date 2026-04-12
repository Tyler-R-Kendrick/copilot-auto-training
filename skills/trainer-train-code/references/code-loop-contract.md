# Code Loop Contract

This reference defines the routing table, Trace-specific patterns, feedback-signal rules, and validation constraints for the trainer-train-code skill.

## Target type

- Python files (`.py`) intended for optimization through Microsoft Trace.
- Trainable boundaries include: functions, methods, module-level callables, and small agent components.

## Workspace derivation

- Strip the final extension from the target filename to derive `<code-name>`.
- Use `<target-dir>/.trainer-workspace/<code-name>/` as the workspace root.

## Required checkpoint

Require `engineer-prompt/review.md` before any optimization pass. If absent, set `workflow_state: pending_engineer_prompt` and report a blocker.

## Trainable surface selection guide

| Use case | Trace pattern |
|----------|--------------|
| Mutable value (prompt string, threshold, template) | `trace.node(trainable=True)` |
| Callable whose behavior should be optimized as a unit | `@trace.bundle(trainable=True)` |
| Multiple related trainable nodes/bundles in one object | `@trace.model` |
| Orchestration, I/O, stable business logic | Plain Python — not trainable |

## Judge-mode routing table

| Row shape | Inferred mode |
|-----------|--------------|
| Explicit `scoring: custom` | `custom` |
| Explicit `scoring: exact_match` | `deterministic` |
| Explicit `scoring: llm_judge` | `llm_judge` |
| Executable test suite exists | Default to `custom` |
| No explicit scoring, no test suite | Blocker — require a feedback signal |

## Feedback signal discipline

- Reset feedback each iteration before the next backward pass.
- Preserve failed executions via `ExecutionError` when the failure is informative.
- Prefer deterministic, repeatable checks over subjective critiques.
- If no feedback signal can be deterministically rerun, stop and report a blocker.

## Blocker conditions

Stop optimization and report a blocker when:
- No repeatable feedback signal exists.
- The trainable surface is undefined or covers the entire file without a scoped boundary.
- Hidden dependencies inside a candidate bundle would break tracing assumptions.
- Tracked artifact pointers are missing or inconsistent.

## Write-back gate

Write back only when all of the following are true:
1. Test suite (or deterministic evaluator) passes.
2. Trace imports are explicit and local to the trainable surface.
3. No hidden dependencies were introduced in the candidate.
4. The feedback signal can still be rerun deterministically against the candidate.
5. Decision summary written at `<workspace-root>/decision.md`.
