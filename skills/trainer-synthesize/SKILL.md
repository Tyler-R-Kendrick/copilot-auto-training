---
name: trainer-synthesize
description: Simulate, convert, and generate high-quality prompt-adjacent JSONL datasets. Use when a prompt needs train and validation data from known source material, user examples, or a prior research pass.
license: MIT
compatibility: Requires Python 3.11+. Works with the trainer-optimize skill in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Synthesize

Use this skill to create prompt-adjacent datasets for optimization.

## When to use this skill

- The optimizer needs `train.jsonl` and `val.jsonl` for a markdown prompt.
- The user has examples, a CSV file, or source notes from the `trainer-research` skill.
- The agent should convert known source material into high-quality prompt-local JSONL.
- The agent should simulate representative examples when the known source material is incomplete.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional source material such as `csv_file`, existing examples, or structured notes from the `trainer-research` skill

## Process

1. Inspect the prompt placeholders and derive the prompt-adjacent `.evals/<prompt-name>/` target paths.
2. Start from known source material such as user rows, CSV input, or a source shortlist from the `trainer-research` skill.
3. Prefer grounded examples when they fit the task and licensing allows reuse.
4. Synthesize additional examples to fill gaps in coverage, edge cases, or label balance.
5. Convert the resulting tasks into JSONL with prompt-visible inputs and evaluator-only scoring fields.
6. Produce `train.jsonl` and `val.jsonl` next to the prompt.

## Naming rationale

`synthesize` is the best public name here because it focuses on conversion and example generation after source material has already been gathered.