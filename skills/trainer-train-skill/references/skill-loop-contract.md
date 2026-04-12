# Skill Loop Contract

This reference defines the routing table, spec-compliance rules, frontmatter optimization constraints, and body-content validation requirements for the trainer-train-skill skill.

## Target type

- `SKILL.md` files in any skill directory following the agentskills.io specification.
- The skill directory name is used as `<skill-name>` for workspace derivation.

## Workspace derivation

- Use the skill directory name as `<skill-name>`.
- Use `<skill-dir>/.trainer-workspace/<skill-name>/` as the workspace root.

## Required checkpoint

Require `engineer-prompt/review.md` before any optimization pass. If absent, set `workflow_state: pending_engineer_prompt` and report a blocker.

## Two-concern routing

| Observed failure mode | Primary concern | Secondary concern |
|----------------------|-----------------|-------------------|
| Agents ignore the skill | Frontmatter (description) | Body (if execution is also broken) |
| Agents invoke for wrong tasks | Frontmatter (description) | None |
| Inconsistent agent behavior | Body (instructions) | Frontmatter (if also misrouting) |
| Bloated context | Body (structure / progressive disclosure) | None |
| All concerns | Both, in order: frontmatter → body | — |

## Judge-mode routing table

| Row shape | Inferred mode |
|-----------|--------------|
| Explicit `scoring: deterministic` | `deterministic` (spec-compliance checks) |
| Explicit `scoring: llm_judge` | `llm_judge` |
| `expected` fields only | `llm_judge` (default — skill quality is open-ended) |
| `reference` + `criteria` fields | `llm_judge` |
| No scoring fields | Default to `llm_judge` |

## Spec-compliance checklist

Before write-back, confirm all of the following:

1. **Required YAML fields present:** `name` and `description` in frontmatter.
2. **Name unchanged:** The `name` field must match the original exactly.
3. **Body length:** Under 500 lines. If ≥500 lines, content must be extracted into `references/` files with explicit body pointers.
4. **Large reference files:** Files >300 lines must include a table of contents.
5. **Evaluator field isolation:** `expected`, `reference`, `criteria`, and `scoring` must not appear in the prompt-visible body.
6. **No malware or exploits:** Skill contents must not contain executable exploit patterns.

## Frontmatter optimization rules

- The `description` field is the primary triggering mechanism. All "when to use" information belongs here, not in the body.
- Descriptions should be "pushy" — lean toward including contexts where the skill would be useful rather than being conservative.
- The `name` field must not change.
- Optional fields (`argument-hint`, `compatibility`, `license`, `metadata`) may be added or updated.

## Write-back gate

Write back only when all of the following are true:
1. All spec-compliance checks pass.
2. No evaluator-only fields appear in the prompt-visible body.
3. `name` field is unchanged.
4. Validation passes (e.g., `python -m pytest -q` exits 0).
5. Decision summary written at `<workspace-root>/decision.md`.
