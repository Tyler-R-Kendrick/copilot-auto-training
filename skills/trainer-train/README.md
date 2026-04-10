# Trainer Train

Own the end-to-end trainer loop contract for a selected prompt-like file, skill contract, or agent contract after the caller has already chosen the concrete stage capabilities.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and orchestration guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [datasets/](datasets/): explicit train and validation fixtures for prompt optimization.
- [references/](references/): deeper workspace, stage, and collaboration guidance.
- [assets/](assets/): reserved for templates or supporting artifacts.
- [scripts/](scripts/): reserved for deterministic helpers if this skill later needs them.

## When to use

- The current agent already knows which concrete stage capabilities implement research, synthesis, optimization, and election.
- The task is to coordinate one or more trainer iterations for one selected target.
- The workflow must manage local workspace state, steering, validation, and write-back safely.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
