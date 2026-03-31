# Election

Elect the strongest prompt or skill candidate from an existing evaluation workspace. Use this skill whenever a workflow already has multiple scored configurations and needs a separate leader-selection pass over grading, timing, or benchmark artifacts, especially when comparing optimizer outputs without pushing that selection logic back into the optimization runtime.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [datasets/](datasets/): explicit datasets used by local runs or optimization workflows.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details.

## When to use

- A workflow already produced multiple candidate configurations and now needs a winner chosen from scored artifacts.
- Multiple candidate configurations already exist as `with_skill`, `without_skill`, `old_skill`, or other config directories inside a skill-eval workspace.
- Each candidate has already been run against authored evals and saved `grading.json` and optional `timing.json` artifacts.
- You need a separate election pass that picks the strongest configuration from workspace results instead of generating new candidates.
- The workflow explicitly needs comparison across multiple optimizer outputs, prompt rewrites, or skill revisions without folding that comparison into the optimization runtime.

Do not use this skill to gather datasets, synthesize evals, optimize prompts, or run missing evaluations from scratch. Those remain separate skills.

## Inputs

- `workspace_dir`: root workspace path, a specific iteration directory, or a direct eval directory
- `iteration`: optional iteration selector when the workspace contains multiple iterations
- `manifest_file`: optional authored `evals/evals.json` path for expected eval coverage

If `manifest_file` is omitted, the runtime searches `evals/evals.json` next to the iteration directory, then one level higher.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
