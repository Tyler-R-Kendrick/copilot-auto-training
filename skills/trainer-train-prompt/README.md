# trainer-train-prompt

Specialization of the trainer-train orchestration loop for **prompt-like targets**: `*.prompt.md`, `*.prompty`, `*.instructions.md`, and system prompt files.

## When to use

Use this skill when the selected training target is a natural-language instruction or prompt file. It enforces prompt-specific rules: placeholder preservation, evaluator field isolation, and `llm_judge` mode as the default scoring strategy.

## Key references

- `references/prompt-loop-contract.md` — routing table, judge-mode rules, write-back gate

## Datasets

- `datasets/train.jsonl` — training cases
- `datasets/val.jsonl` — holdout validation cases

## Evals

- `evals/evals.json` — eval manifest for the skill
