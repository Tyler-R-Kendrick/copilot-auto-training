---
description: "Use when editing prompt and instruction files such as *.prompt.md, *.prompty, *.instructions.md, SKILL.md, AGENTS.md, or *.agent.md. Covers prompt-optimization workflow, dataset expectations, and validation habits."
applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"
---
# Prompt Optimization Guidance

- Preserve prompt placeholders unless the task explicitly changes the prompt interface.
- Keep authored skill eval cases under `evals/evals.json` and supporting assets under `evals/files/`.
- When the optimizer runtime needs JSONL data, use explicit dataset paths and avoid hidden runtime conventions.
- Use the `trainer-optimize` skill for single-shot optimization, `trainer-election` only for external leader selection when a workflow explicitly compares multiple optimize outputs, `trainer-research` for public-source discovery, and `trainer-synthesize` for conversion or simulated dataset generation.
- Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` out of prompt-visible render paths.
- Keep baseline comparisons explicit and external to `trainer-optimize` when a workflow chooses to compare multiple revisions.
- Apply the eval-manifest guidance when editing `evals/evals.json` files.
- Re-run the relevant validation command after meaningful edits to prompt-like files.