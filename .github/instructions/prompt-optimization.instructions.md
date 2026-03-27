---
description: "Use when editing prompt and instruction files such as *.prompt.md, *.prompty, *.instructions.md, SKILL.md, AGENTS.md, or *.agent.md. Covers prompt-optimization workflow, dataset expectations, and validation habits."
applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"
---
# Prompt Optimization Guidance

- Preserve prompt placeholders unless the task explicitly changes the prompt interface.
- Keep prompt-adjacent datasets under `.evals/<prompt-name>/` and prefer `train.jsonl` plus `val.jsonl` over ad hoc formats.
- Use the `trainer-optimize` skill for optimization, `trainer-election` for leader selection, `trainer-research` for public-source discovery, and `trainer-synthesize` for conversion or simulated dataset generation.
- Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` out of prompt-visible render paths.
- Treat the original prompt as a baseline candidate when comparing revisions.
- Apply the dataset-specific `.evals` guidance when editing prompt-adjacent JSONL files.
- Re-run the relevant validation command after meaningful edits to prompt-like files.