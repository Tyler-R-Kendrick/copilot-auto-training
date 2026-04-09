---
name: engineer-skill
description: Improve agent skills by validating structure, optimizing YAML frontmatter for triggering accuracy, and refining SKILL.md prompt content for reliable agent behavior. Use this whenever the user wants to create, improve, debug, or optimize an agent skill, fix skill triggering issues, extract deterministic instructions into scripts, restructure a skill for progressive disclosure, or reduce a bloated SKILL.md body.
argument-hint: Describe the skill to improve, the specific concern (frontmatter triggering, body content, structure, or all), and any observed failure modes.
license: MIT
compatibility: Requires Python 3.11+. Works in any environment that supports the agentskills.io specification.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Engineer Skill

Use this skill to systematically improve agent skills by treating frontmatter optimization and prompt content optimization as two separate, composable concerns.

Read `references/skill-structure-spec.md` for the complete directory layout and file conventions before starting.

## When to use this skill

- The user wants to create a new agent skill from scratch.
- The user wants to improve an existing skill's triggering accuracy (frontmatter).
- The user wants to improve an existing skill's execution reliability (body content).
- The user has a bloated SKILL.md and wants to restructure it with progressive disclosure.
- The user wants to extract deterministic instructions from prose into executable scripts.
- The user wants to validate a skill against the agentskills.io specification.
- The user asks about skill best practices, structure, or conventions.

Do not use this skill for general prompt engineering that is not tied to agent skill files. Use this skill only when the target artifact is a skill directory with a SKILL.md file or the user is creating one.

## Required inputs

- The path to an existing skill directory, or a description of the skill to create.
- The improvement focus: frontmatter (triggering), body (execution), structure, or all.
- Any observed failure modes: under-triggering, over-triggering, inconsistent agent behavior, bloated context.

## Core workflow

Follow this order:

1. **Validate** the skill structure and spec compliance by running `python scripts/validate_skill.py <skill-path>`.
2. **Analyze** the body for extraction opportunities by running `python scripts/analyze_skill_body.py <skill-path> --json`.
3. **Prioritize** improvements based on validation errors first, then analysis recommendations.
4. **Improve frontmatter** if triggering is the concern. Read `references/frontmatter-optimization.md` for guidance.
5. **Improve body content** if execution reliability is the concern. Read `references/prompt-content-optimization.md` for guidance.
6. **Extract deterministic work** to scripts when the analysis identifies sequential or mechanical instructions.
7. **Re-validate** after changes to confirm spec compliance.

## Two-concern separation

### Frontmatter (triggering concern)

The frontmatter controls when agents discover and invoke the skill. Optimization targets:

- Description wording and coverage of user intents.
- Explicit trigger phrases and negative boundaries.
- Name clarity and discoverability.

Read `references/frontmatter-optimization.md` before making frontmatter changes.

### Body content (execution concern)

The body controls what agents do after triggering. Optimization targets:

- Instruction clarity and ordering.
- Progressive disclosure through referenced files.
- Extraction of deterministic logic to scripts.
- Section sizing under recommended thresholds.

Read `references/prompt-content-optimization.md` before making body changes.

## Output contract

When improving a skill, structure the response as:

1. `Validation results`: output from the validation script
2. `Analysis results`: output from the analysis script
3. `Improvement plan`: prioritized list of changes
4. `Changes made`: specific edits with rationale
5. `Re-validation`: confirmation of spec compliance after changes
