---
description: "Use when editing official skill eval manifests under evals/evals.json. Covers eval case shape, file references, assertions, and workspace-result expectations."
applyTo: "**/evals/evals.json"
---
# Skill Eval Guidance

- Keep the manifest root as a JSON object with `skill_name` and an `evals` array.
- Keep each eval case realistic: `prompt` should read like an actual user request, not a label or shorthand.
- Use `expected_output` for a human-readable success description, not brittle exact-match text unless exact wording is the real requirement.
- Keep `files` paths relative and prefer assets under `evals/files/`.
- Add `assertions` only when they are objective and observable; leave subjective qualities for later human review.
- Start with a small, varied set of cases and expand coverage only after the first evaluation loop exposes real gaps.

## Required and Optional Fields

Every eval row must include:
- `prompt` — a realistic user request string (never a label like "Test case 1")
- `expected_output` — a human-readable description of a successful response

Optional fields follow these rules when present:
- `assertions` — a list of string predicates that are objectively checkable (e.g., "Response contains a category label", "Response is valid JSON"); do not add subjective assertions
- `files` — a list of paths relative to the eval manifest directory; always store supporting assets under `evals/files/`
- `scoring` — one of `deterministic`, `custom`, or `llm_judge`; use `deterministic` when the check is rule-based, `llm_judge` for open-ended quality, and `custom` for schema or normalization checks
- `criteria` — a string describing the evaluation criteria when `scoring` is `llm_judge`

## Example: Correct Eval Row

```json
{
  "prompt": "Categorize this support ticket: My invoice shows an incorrect charge.",
  "expected_output": "The skill should classify the ticket as billing and return a category label.",
  "assertions": ["Response contains a category label", "Category is one of: billing, technical, general"],
  "scoring": "llm_judge",
  "criteria": "The response must identify the correct ticket category with a clear label."
}
```

## Forbidden Patterns

- Do not write label-style prompts: `"Test case 3: billing classification"` is wrong; write a real user request instead.
- Do not use absolute file paths in `files`; paths must be relative to the manifest directory.
- Do not write brittle exact-match `expected_output` strings for open-ended tasks; describe the quality characteristics instead.
- Do not add assertions that require subjective judgment; keep assertions to objectively verifiable predicates.
