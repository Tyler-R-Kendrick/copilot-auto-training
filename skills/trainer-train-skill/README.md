# trainer-train-skill

Specialization of the trainer-train orchestration loop for **agent skill targets**: `SKILL.md` files.

## When to use

Use this skill when the selected training target is a `SKILL.md` file. It enforces skill-specific rules: spec compliance, progressive disclosure limits, frontmatter vs. body concern separation, and `llm_judge` mode as the default scoring strategy.

## Key references

- `references/skill-loop-contract.md` — two-concern routing, spec-compliance checklist, write-back gate

## Datasets

- `datasets/train.jsonl` — training cases
- `datasets/val.jsonl` — holdout validation cases

## Evals

- `evals/evals.json` — eval manifest for the skill
