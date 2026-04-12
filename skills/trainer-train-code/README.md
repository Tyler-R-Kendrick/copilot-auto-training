# trainer-train-code

Specialization of the trainer-train orchestration loop for **Python code targets** optimized with Microsoft Trace.

## When to use

Use this skill when the selected training target is a Python file, function, or agent component that benefits from test-based or benchmark-based feedback through Microsoft Trace nodes, bundles, or models.

## Key references

- `references/code-loop-contract.md` — Trace pattern routing, feedback-signal rules, write-back gate

## Datasets

- `datasets/train.jsonl` — training cases
- `datasets/val.jsonl` — holdout validation cases

## Evals

- `evals/evals.json` — eval manifest for the skill
