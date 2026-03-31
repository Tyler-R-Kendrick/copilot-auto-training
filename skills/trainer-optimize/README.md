# Prompt Optimization with Agent Lightning

Improve a markdown prompt file using Agent Lightning APO (Automatic Prompt Optimization). Use when the user asks to optimize or improve a markdown prompt, or starts a message with /trainer-optimize.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [datasets/](datasets/): explicit datasets used by local runs or optimization workflows.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts.
- [scripts/](scripts/): runtime helpers or implementation details.

## When to use

- The user says "optimize my prompt", "improve this prompt", or starts with `/trainer-optimize`
- The target artifact is a single `.md` (markdown) prompt template file
- The user provides, or can provide, train and validation JSONL datasets with expected outputs

Do not use this skill for general code optimization or non-markdown prompts.

## Inputs

The skill always needs a prompt path. It also needs train and validation datasets. In this repository, authored eval cases live under `evals/evals.json`, while APO datasets are passed explicitly.

- `prompt`: path to the markdown prompt file to optimize
- `train`: path to the JSONL training dataset
- `val`: path to the JSONL validation dataset

If those files do not exist, stop and report the missing path instead of guessing.
Do not synthesize missing datasets inside `trainer-optimize`. Any dataset creation or conversion must happen before this skill runs.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
