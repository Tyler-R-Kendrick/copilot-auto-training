# Engineer Code

Improve Python implementations with Microsoft Trace by turning prompts, helper functions, or small agent components into trainable code. Use this whenever the user wants to apply Trace or trace-opt, optimize Python behavior from tests or feedback, make a method trainable with nodes, bundles, or models, or decide how to structure a Trace training loop for code-focused work.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- The user wants to optimize Python behavior with Microsoft Trace or `trace-opt`.
- The user wants to convert a prompt, helper function, or small agent method into a trainable Trace component.
- The user asks how to use `trace.node`, `@trace.bundle`, `@trace.model`, `ExecutionError`, or `OptoPrime`.
- The user wants to train code from unit-test results, benchmark scores, natural-language critiques, compiler errors, or other non-scalar feedback.
- The user wants help deciding what should stay plain Python and what should become a Trace parameter.

Do not use this skill as the primary fix for generic Python runtime performance tuning, missing Trace installation, infrastructure or tooling failures, or tasks with no repeatable feedback signal. In those cases, say Trace is a bad fit or only a secondary lever.

## Inputs

- The Python behavior or component to improve.
- The candidate trainable surface, or the code boundary under consideration.
- The feedback signal available today: tests, benchmark scores, compiler or runtime errors, or concise natural-language critiques.
- Any repo or runtime constraints, including whether Microsoft Trace is installed and what validation can be rerun deterministically.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
