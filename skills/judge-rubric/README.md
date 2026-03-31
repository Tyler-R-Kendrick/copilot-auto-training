# Rubric Authoring

Generate a formalized rubric for scoring, grading, or evaluation in the current domain. Use when a judging task needs locked dimensions, pass-partial-fail boundaries, evidence requirements, tie-breakers, or confidence guidance before candidate comparison.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [datasets/](datasets/): explicit datasets used by local runs or optimization workflows.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts.
- [scripts/](scripts/): runtime helpers or implementation details.

## When to use

- The judging task is missing a stable rubric and needs one before scoring starts.
- The user asks for a grading rubric, scoring rubric, evaluation rubric, or formal scorecard.
- The domain has specific failure modes, policy constraints, or artifact requirements that must become explicit judging dimensions.
- The evaluation needs pass, partial, and fail boundaries instead of holistic free-form grading.
- The comparison is high-risk enough that tie-break rules, robustness checks, and confidence guidance must be defined in advance.

## Inputs

- The task contract or judging objective.
- The domain context, expected outputs, and any non-negotiable constraints.
- The artifacts that will later be judged, such as final outputs, process traces, validation logs, or benchmark summaries.
- Any scoring mode, reference answer, criteria list, benchmark notes, or existing rubric fragments already available.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
