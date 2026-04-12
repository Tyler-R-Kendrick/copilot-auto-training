# trainer-train-agent

Specialization of the trainer-train orchestration loop for **agent contract targets**: `*.agent.md` files.

## When to use

Use this skill when the selected training target is an agent contract or agent instruction document. It enforces agent-specific rules: MCP skill routing audit, handoff bounding, prompt bloat control, and `llm_judge` mode as the default scoring strategy.

## Key references

- `references/agent-loop-contract.md` — three-concern routing, MCP audit rules, handoff bounding, write-back gate

## Datasets

- `datasets/train.jsonl` — training cases
- `datasets/val.jsonl` — holdout validation cases

## Evals

- `evals/evals.json` — eval manifest for the skill
