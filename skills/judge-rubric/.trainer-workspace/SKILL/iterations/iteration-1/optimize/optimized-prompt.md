---
name: judge-rubric
description: 'Generate a formalized rubric for scoring, grading, or evaluation in the current domain. Use when a judging task needs locked dimensions, pass-partial-fail boundaries, evidence requirements, tie-breakers, or confidence guidance before candidate comparison.'
argument-hint: 'Domain, task contract, artifacts, scoring mode, and any existing evaluation criteria.'
---

# Rubric Authoring

Use this skill to build a formal judging rubric before scoring responses, candidates, trajectories, benchmark outputs, or other evaluation artifacts.

Read `references/rubric-techniques.md` when you need current judging guidance on locked rubrics, task-adaptive rubric design, verifier-backed evidence, robustness checks, calibration, and chain-of-thought skepticism.

## Default Branch

- If the judging inputs already include a structured rubric contract, prefer `scripts/render_rubric.py` instead of drafting free-form prose.
- If the structured contract might be incomplete, run `scripts/render_rubric.py --validate-only` first and return blockers before rendering.
- Draft manually only when the needed rubric fields are not yet structured.

## Required Inputs

- The task contract or judging objective.
- The domain context, expected outputs, and any non-negotiable constraints.
- The artifacts that will later be judged, such as final outputs, process traces, validation logs, or benchmark summaries.
- Any scoring mode, reference answer, criteria list, benchmark notes, or existing rubric fragments already available.

## Non-Negotiables

- Lock the rubric before scoring begins.
- Keep 3 to 7 dimensions.
- For every dimension, include: why it matters, pass boundary, partial boundary, fail boundary, and allowed evidence.
- Freeze aggregation rules and tie-breakers before judging starts.
- Include robustness checks and confidence guidance.
- Treat unsupported chain-of-thought or self-explanations as low-trust evidence unless corroborated by artifacts.
- If key domain constraints, evidence rules, or decision criteria are missing, return blockers instead of inventing provisional thresholds.

## Evidence Mode Mapping

- Outcome-focused: prioritize final outputs, references, criteria, schemas, and other end-state artifacts.
- Process-aware: prioritize traces, tool calls, intermediate artifacts, logs, validation output, and runtime behavior.
- Hybrid: split evidence expectations explicitly across both process and final-answer artifacts so the same evidence is not double-counted.

## Workflow

1. Decide the branch first. Use the structured helper path when contract fields are already available; otherwise draft the rubric manually from the supplied task inputs.
2. Clarify the judging target. State what is being judged, what success looks like, what evidence is allowed, and what the ruling must decide.
3. Classify the evidence mode as outcome-focused, process-aware, or hybrid based on the actual artifacts that will be judged.
4. Lock 3 to 7 task-adaptive dimensions. Prefer concrete dimensions such as correctness, constraint compliance, evidence quality, tool reliability, completeness, safety, format fidelity, or domain-specific policy adherence.
5. Define pass, partial, and fail boundaries for each dimension using observable behavioral anchors rather than vague quality labels.
6. Name the allowed evidence for each dimension. State what artifacts support a score, what counts as corroboration, and what evidence is too weak to trust alone.
7. Add aggregation rules and tie-breakers. Specify weighting or priority, non-negotiable failures, and the tie-break order before scoring begins.
8. Add robustness checks. Include order-bias checks, evidence-quality checks, benchmark-overfitting skepticism, and explicit confidence guidance for narrow or under-evidenced margins.
9. Return a decision-ready rubric package that another judge can apply without reinterpreting the task midway through scoring.

## Final Response Format

Return the rubric package with these sections in this order:

1. `## Judging Target`
2. `## Locked Rubric`
3. `## Aggregation Rules`
4. `## Robustness Checks`
5. `## Blockers`

In `## Locked Rubric`, use a table or equally structured list that covers every locked dimension and all required fields.

## Structured Helper

Use `scripts/render_rubric.py` when the rubric inputs are already structured and you want a deterministic first draft.

Use `scripts/render_rubric.py --validate-only` when you need to verify that a structured contract is complete and consistent before rendering or handing it to another judging workflow.

Accepted contract fields:

- `domain`
- `task`
- `evidence_mode`
- `decision`
- `dimensions`: array of objects with `name`, `why_it_matters`, `pass_boundary`, `partial_boundary`, `fail_boundary`, and `allowed_evidence`
- `aggregation_rules`: object with `weighting_or_priority`, `non_negotiable_failures`, and `tie_breakers`
- `robustness_checks`: object with `order_bias_check`, `evidence_quality_check`, `benchmark_overfitting_check`, and `confidence_guidance`
- `blockers`: object with `missing_inputs`, `weak_evidence_areas`, and `clarifications_needed`

Example:

```bash
python scripts/render_rubric.py --input-file contract.json --output-file rubric.md
```

Validation example:

```bash
python scripts/render_rubric.py --input-file contract.json --validate-only
```

## Assets

- `assets/rubric-template.md` provides a reusable template for the final rubric package.

## Notes

- Keep the rubric task-adaptive, but only adapt it before scoring begins.
- Prefer observable evidence over polished narration.
- If the domain is under-specified, stop and list the missing inputs instead of improvising score boundaries.