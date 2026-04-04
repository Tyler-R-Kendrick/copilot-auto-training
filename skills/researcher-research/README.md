# Research

Research public datasets, benchmarks, documentation, and source material for official skill eval cases. Use this skill whenever a prompt or skill needs grounded public examples, authoritative dataset references, or a primary-source brief before synthesis or optimization.

## Canonical files

- [SKILL.md](SKILL.md): canonical researcher-owned skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details.

## When to use

- The optimizer or evaluation workflow needs grounded eval cases, but no suitable local source material exists yet.
- The user wants grounded public examples instead of purely simulated rows.
- The agent needs a ranked shortlist of public datasets, benchmarks, or documentation sources that match a prompt task.
- The user needs explicit judgment about source quality, data reliability, annotation quality, licensing, provenance, or leakage risk before authoring eval data.
- The workflow needs to know whether no acceptable public source exists, so synthesis should stop instead of guessing.

If the source material is already known and the job is to convert it into eval rows, use a synthesis workflow instead.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional constraints such as domain, language, geography or jurisdiction, recency, licensing, privacy, label taxonomy, or excluded source types

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
