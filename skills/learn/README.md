# Learn

Capture user corrections and reusable lessons from the active conversation, then update the most relevant instructions, skills, docs, evals, or tests so the same mistake is less likely to happen again.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- The user corrects your workflow and wants the correction applied going forward.
- The user says a mistake should not happen again.
- The user introduces a new requirement that should be reflected in durable guidance.
- The user points out a recurring failure pattern across prompts, instructions, docs, or tests.
- The user wants repository guidance updated to match what was learned in the active conversation.

Do not use this skill for one-off stylistic preferences, ephemeral debugging notes, or corrections that are too narrow to generalize safely. In those cases, apply the correction locally without hard-coding it into durable repository guidance.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
