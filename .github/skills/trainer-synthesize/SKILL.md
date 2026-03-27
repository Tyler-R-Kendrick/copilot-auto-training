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