---
name: trainer-train-skill
description: Own the end-to-end trainer loop for agent skill targets (SKILL.md files and their supporting references, scripts, and evals). Use this whenever the caller needs to research, synthesize datasets, optimize, validate, and write back a trained candidate for a skill-type target. Prefer this specialized loop whenever the selected target is a SKILL.md file or the user wants to improve skill triggering accuracy, body content quality, or progressive-disclosure structure.
argument-hint: Describe the skill directory, the repository root, the validation command, the available stage capabilities, the improvement focus (frontmatter, body, structure, or all), and any existing workspace artifacts.
license: MIT
compatibility: Python 3.11+. Designed for repositories following the agentskills.io specification. Works with skills that keep trainer artifacts in `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Trainer Train - Skill

Use this skill as the orchestration contract for one trainer run against an **agent skill target**: a `SKILL.md` file and its associated directory of references, scripts, assets, and evals.

Read `references/skill-loop-contract.md` for the full routing table, spec-compliance rules, frontmatter optimization constraints, and body-content validation requirements before any stage execution.

## When to use this skill

- The selected target is a `SKILL.md` file or a full skill directory.
- The caller needs to initialize or resume a trainer workspace for a skill target.
- The improvement focus is triggering accuracy (frontmatter), execution reliability (body), structure, or all three.
- Missing datasets or eval manifests need to be synthesized before optimization.
- A winning candidate needs to be validated against spec compliance and written back.

Do not use this skill for raw prompt files, Python code targets, or agent contracts. Read the parent trainer skill's `references/target-routing.md` to identify the appropriate specialist for those target types.

## Required inputs

- One selected skill directory containing a `SKILL.md` file.
- Repository root or enough path context to derive the local trainer workspace.
- The validation command for the repository (e.g., `python -m pytest -q`).
- The concrete stage capability map: researcher, synthesizer, optimizer, elector.
- The improvement focus: frontmatter triggering, body content, structure, or all.
- Any observed failure modes: under-triggering, over-triggering, inconsistent agent behavior, bloated context.

## Skill-specific loop rules

### Two-concern separation

Treat frontmatter optimization and body content optimization as two separate, composable concerns:

- **Frontmatter (triggering concern):** The `description` field is the primary triggering mechanism. Optimize it when the skill under-triggers (agents ignore it) or over-triggers (agents invoke it for unrelated requests). The `name` field must remain unchanged.
- **Body content (execution concern):** Improve instructions, examples, workflow steps, and progressive-disclosure structure when agent behavior during skill execution is inconsistent or unreliable.

Always validate both concerns after a revision round, even when only one was the primary focus.

### Judge mode

Skill targets use **llm_judge** mode by default because skill quality is open-ended. Use `deterministic` mode only when the dataset has `expected` rows representing exact spec-compliance checks (e.g., required YAML fields present). Treat an explicit row-level `scoring` declaration as authoritative.

### Spec compliance

Before any write-back, confirm the candidate SKILL.md satisfies the agentskills.io specification:
- YAML frontmatter includes required fields (`name`, `description`).
- Body is under 500 lines or uses progressive disclosure with clear reference pointers.
- No evaluator-only fields (`expected`, `reference`, `criteria`, `scoring`) appear in the prompt-visible body.

### Progressive disclosure rules

- Keep the SKILL.md body under 500 lines.
- If the body approaches this limit, extract content into `references/` files with explicit pointers from the body.
- For large reference files (>300 lines), include a table of contents.

## Core workflow

Follow this order. Consult `references/skill-loop-contract.md` when artifact paths, scoring mode, or spec-compliance constraints are uncertain.

1. **Resolve target and workspace.** The selected target is the `SKILL.md` file itself. Derive `<prompt-name>` from the filename using the canonical rule: strip `.md` from `SKILL.md` to get `SKILL`. Use `<skill-dir>/.trainer-workspace/SKILL/` as workspace root (the directory name is not used). If state indicates a resumed run, audit tracked artifact pointers and skip only stages that already produced valid outputs.
2. **Require the workspace review checkpoint.** Confirm the engineering review artifact exists before optimization starts. Report a blocker if it is absent.
3. **Initialize or refresh workspace.** Create or update `workflow-status.json`, source snapshot of `SKILL.md`, the review subdirectory, `inputs/source/`, and `iterations/` directories.
4. **Run spec validation.** Before optimization, confirm the current `SKILL.md` is spec-compliant. Record any violations as steering context for the optimizer.
5. **Inspect existing datasets and evals.** Prefer reuse when train, validation, and authored eval assets already fit the skill target and scoring shape. Check that `evals/evals.json` exists and has realistic prompts.
6. **Run missing-data path if needed.** If any required dataset or eval is absent, pause optimization and gather them via the caller-supplied researcher and synthesizer.
7. **Infer judge mode.** Default to `llm_judge` for skill targets. Treat explicit row-level `scoring` as authoritative. Stop and report inconsistency if splits imply different modes.
8. **Run at least one optimization pass.** Pass the inferred judge mode, the improvement focus, and spec-compliance constraints to the optimizer.
9. **Handle manual follow-up if returned.** Save the report as `manual-followup-report.json`, answer the model-facing prompt, persist the candidate artifact, and continue the loop.
10. **Run election if multiple candidates exist.** Use the caller-supplied elector when optimization produces more than one defensible candidate.
11. **Publish iteration artifacts.** Stage steering, candidate bundles, validation logs, and a decision summary under the active iteration directory.
12. **Write back only when validation passes.** Confirm spec compliance and validation success before writing the winning candidate back to `SKILL.md`.

## Blocker-first rule

Stop and report a clear blocker before any optimization or rewrite when:

- The workspace review artifact is absent.
- Required datasets or authored evals are missing.
- The current `SKILL.md` violates spec in a way that would invalidate optimization results.
- Tracked artifact pointers from a resumed run are missing or inconsistent.

A blocker report must name the missing artifact or violation, explain why the loop cannot advance, and leave `workflow-status.json` in a resumable checkpoint state.

## Output contract

Return:

1. Workspace status and any active blockers.
2. Current-turn decisions: improvement focus, judge mode, spec-compliance status, selected branch, blockers.
3. Optimization or manual follow-up status with artifact paths.
4. Spec-compliance confirmation for the winning candidate.
5. Validation status.
6. Write-back decision and justification.
7. Next required action to resume or continue the loop.
