---
name: trainer-research
description: Research public datasets, benchmarks, and source material for prompt-adjacent evaluations. Use when a prompt needs grounded public-source discovery before dataset synthesis or conversion.
license: MIT
compatibility: Requires Python 3.11+. Works with the trainer-optimize and trainer-synthesize skills in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Research

Use this skill to research source material before generating prompt-adjacent datasets.

## When to use this skill

- The optimizer needs `train.jsonl` and `val.jsonl`, but no suitable local dataset exists yet.
- The user wants grounded public examples instead of purely simulated rows.
- The agent needs a shortlist of public datasets, benchmarks, or documentation sources that match a prompt task.
- The trainer-synthesize stage needs research queries, source notes, or schema guidance before generating JSONL.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule

## Process

1. Inspect the prompt placeholders and derive the prompt-adjacent `.evals/<prompt-name>/` target paths.
2. Build research queries that match the task, answer format, and prompt-visible fields.
3. Shortlist public datasets, benchmarks, or documentation sources that fit the task.
4. Summarize source constraints, likely field mappings, and any licensing concerns.
5. Hand the resulting source shortlist and schema notes to the `trainer-synthesize` skill for JSONL generation.

## Naming rationale

`research` is explicit, standard, and narrow enough to separate source discovery from later synthesis and conversion.