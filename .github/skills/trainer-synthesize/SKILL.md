---
name: trainer-synthesize
description: Simulate, convert, and generate high-quality official skill eval cases. Use when a prompt or skill needs `evals/evals.json` content from known source material, user examples, or a prior research pass.
license: MIT
compatibility: Requires Python 3.11+. Works with the trainer-optimize skill in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Synthesize

Use this skill to create official skill eval manifests for optimization and review workflows.

## When to use this skill

- The workflow needs `evals/evals.json` for a markdown prompt or skill.
- The user has examples, a CSV file, or source notes from the `trainer-research` skill.
- The agent should convert known source material into high-quality eval cases.
- The agent should simulate representative examples when the known source material is incomplete.