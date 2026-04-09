# Frontmatter Optimization for Agent Skills

Read this file when improving a skill's YAML frontmatter fields. Frontmatter is the primary mechanism that determines whether an agent discovers and triggers a skill, so optimizing it has outsized impact on skill effectiveness.

## Specification constraints

These are hard limits from the agentskills.io specification:

| Field         | Type   | Limit         | Required |
|---------------|--------|---------------|----------|
| name          | string | 1–64 chars    | yes      |
| description   | string | 1–1024 chars  | yes      |
| license       | string | —             | no       |
| compatibility | string | ≤ 500 chars   | no       |
| metadata      | object | arbitrary k/v | no       |
| allowed-tools | string | space-delimited | no    |

No other top-level keys are permitted.

## Name field

- Must be kebab-case: lowercase letters, digits, hyphens only.
- Must match the directory name exactly.
- No leading, trailing, or consecutive hyphens.
- Keep names short and descriptive. Prefer `verb-noun` or `domain-action` patterns.

## Description field

The description is the single most important field for skill triggering. Agents see only name + description when deciding whether to consult a skill.

### Writing effective descriptions

1. **Lead with the action.** Start with what the skill does, not what it is.
2. **Include trigger phrases.** Add explicit "Use this whenever..." clauses covering the realistic user intents that should activate this skill.
3. **Be slightly pushy.** Agents tend to under-trigger. Include adjacent use cases and near-miss phrasings.
4. **Avoid jargon walls.** The description should be parseable by a general-purpose agent, not only by a domain expert.
5. **Stay under 1024 characters.** Shorter is better if coverage is preserved.

### Common failure modes

- Too narrow: only describes the happy path, misses edge cases.
- Too broad: triggers on unrelated tasks, wastes context.
- Too abstract: uses meta-language ("A skill for...") instead of concrete actions.
- Missing negative boundaries: does not say when *not* to trigger.

### Evaluation approach

Generate a mix of 10 should-trigger and 10 should-not-trigger queries. The should-not-trigger set is most valuable when it includes near-misses that share keywords with the skill. Run the trigger evaluation to measure precision and recall, then iterate.

## Compatibility field

Use compatibility to declare hard requirements: Python version, required packages, environment constraints. Keep it factual and under 500 characters.

## Metadata field

Use metadata for author, version, and any custom key-value pairs that help with cataloging or deployment. Metadata does not affect triggering.
