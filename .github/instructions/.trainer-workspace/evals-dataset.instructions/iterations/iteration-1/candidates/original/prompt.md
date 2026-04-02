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