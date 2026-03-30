---
on:
  workflow_dispatch:

permissions:
  contents: read

engine: copilot

tools:
  github:
    toolsets: [default]

network:
  allowed:
    - defaults
---

# Workflow Title

State the workflow goal in one sentence.

## Context

Describe the repository context, constraints, and any important background.

## Procedure

1. Describe the first action.
2. Describe how to inspect inputs or repository state.
3. Describe the main analysis or generation step.
4. Describe any branching logic or escalation conditions.

## Decision Rules

If condition A, do X.

If condition B, do Y.

Otherwise, do Z.

## Output Format

## Summary

## Key Findings

## Recommended Actions

## Guardrails

- Do not guess when repository evidence is missing.
- Use configured tools deliberately.
- Keep outputs concise and specific.