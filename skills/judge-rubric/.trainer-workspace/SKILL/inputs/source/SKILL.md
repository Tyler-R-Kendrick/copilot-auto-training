---
name: judge-rubric
description: 'Generate a formalized rubric for scoring, grading, or evaluation in the current domain. Use when a judging task needs locked dimensions, pass-partial-fail boundaries, evidence requirements, tie-breakers, or confidence guidance before candidate comparison.'
argument-hint: 'Domain, task contract, artifacts, scoring mode, and any existing evaluation criteria.'
---

# Rubric Authoring

Use this skill to build a formal judging rubric before scoring responses, candidates, trajectories, benchmark outputs, or other evaluation artifacts.

Read `references/rubric-techniques.md` when you need current judging guidance on locked rubrics, task-adaptive rubric design, verifier-backed evidence, robustness checks, calibration, and chain-of-thought skepticism.

When the judging inputs are already available as a structured contract, use `scripts/render_rubric.py` to render the rubric package deterministically instead of drafting it manually.

## When to use this skill

- The judging task is missing a stable rubric and needs one before scoring starts.
- The user asks for a grading rubric, scoring rubric, evaluation rubric, or formal scorecard.
- The domain has specific failure modes, policy constraints, or artifact requirements that must become explicit judging dimensions.
- The evaluation needs pass, partial, and fail boundaries instead of holistic free-form grading.
- The comparison is high-risk enough that tie-break rules, robustness checks, and confidence guidance must be defined in advance.

## Required inputs

- The task contract or judging objective.
- The domain context, expected outputs, and any non-negotiable constraints.
- The artifacts that will later be judged, such as final outputs, process traces, validation logs, or benchmark summaries.
- Any scoring mode, reference answer, criteria list, benchmark notes, or existing rubric fragments already available.

## Rubric authoring workflow

1. Clarify the judging target first. State what is being judged, what success looks like, what evidence is allowed, and what the ruling must decide.
2. Classify the evidence shape. Decide whether the upcoming judgment is outcome-focused, process-aware, or hybrid so the rubric fits the actual artifacts rather than a generic template.
3. Lock 3 to 7 rubric dimensions before scoring starts. Prefer concrete dimensions such as correctness, constraint compliance, evidence quality, tool reliability, completeness, safety, format fidelity, or domain-specific policy adherence.
4. Define explicit pass, partial, and fail boundaries for each dimension. Behavioral anchors should say what observable evidence earns each band and what failure modes force a downgrade.
5. State the evidence ledger requirements for every dimension. Name which artifacts may support a score, what counts as corroboration, and what evidence is too weak to rely on.
6. Add aggregation and tie-break rules. Specify whether dimensions are equal-weighted or prioritized, then lock tie-breakers such as stronger rubric compliance, clearer evidence anchoring, lower evaluator risk, better benchmark fit, or clearer writing.
7. Add robustness controls before the rubric is used. Include order-bias checks, benchmark-overfitting skepticism, confidence guidance, and a rule that unsupported chain-of-thought or self-explanations are low-trust evidence unless confirmed by artifacts.
8. Return a decision-ready rubric package that another judge can apply without reinterpreting the task halfway through scoring.

## Output package

- Judging target and evidence mode.
- Locked rubric table with dimensions, rationale, pass-partial-fail boundaries, and allowed evidence.
- Aggregation and tie-break rules.
- Robustness checks and confidence guidance.
- Missing inputs or blockers that must be resolved before the rubric is safe to use.

## Structured helper

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
