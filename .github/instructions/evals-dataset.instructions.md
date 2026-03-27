---
description: "Use when editing prompt-adjacent dataset files under .evals directories. Covers JSONL shape, split discipline, and evaluator metadata hygiene for train.jsonl and val.jsonl."
applyTo: "**/.evals/**/*.jsonl"
---
# Evals Dataset Guidance

- Keep each line as a standalone JSON object.
- Treat `train.jsonl` and `val.jsonl` as separate roles and avoid copying the same examples into both splits.
- Preserve the input fields the prompt expects to render; do not rename or drop keys without updating the prompt and evaluator logic together.
- Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` explicit and out of prompt-visible text payloads.
- Prefer realistic edge cases, representative class balance, and stable IDs when the dataset already uses them.