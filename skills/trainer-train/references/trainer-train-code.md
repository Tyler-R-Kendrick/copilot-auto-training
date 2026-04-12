# Delegation: trainer-train-code

## When to delegate

Route to `trainer-train-code` when the selected target is:

- A Python file (`*.py`) intended for optimization through Microsoft Trace
- A trainable function, method, or agent component with a deterministic feedback signal (test suite, benchmark, or evaluator script)

## What it handles

- Code-specific workspace initialization
- Engineering review checkpoint enforcement
- Trainable surface identification: recommends `trace.node`, `@trace.bundle`, or `@trace.model` based on the target shape
- Judge-mode defaulting to `custom` for executable feedback signals
- Feedback signal validation (requires repeatable, deterministic evaluation)
- Trace import hygiene and hidden-dependency warnings
- Test suite pass requirement before write-back

## How to invoke

Tell the caller: "The selected target is a Python code file. Use `trainer-train-code` for this run." Pass the target path, workspace root, the test/benchmark command as the feedback signal, the trainable surface description, and the stage capability map.

## What it does not handle

- Prompt files → use `trainer-train-prompt`
- SKILL.md files → use `trainer-train-skill`
- Agent contracts → use `trainer-train-agent`
- Code files with no repeatable feedback signal (blocker — resolve before routing here)
