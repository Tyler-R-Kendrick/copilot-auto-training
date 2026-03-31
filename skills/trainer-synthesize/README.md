# Synthesize

Build official `evals/evals.json` cases and explicit APO datasets from grounded or computed source data. Use whenever a prompt or skill needs eval rows, `train.jsonl`, or `val.jsonl`, especially when correct outputs must be derived from raw fields, business rules, or verifier-backed synthetic examples.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details.

## When to use

- The workflow needs `evals/evals.json` for a markdown prompt or skill.
- The workflow also needs explicit `train.jsonl` and `val.jsonl` files before handing off to a downstream optimizer.
- The user has examples, CSV or JSON data, tables, schemas, business rules, or source notes from an approved research brief.
- The agent should convert known source material into high-quality eval cases.
- The agent should convert grounded source rows into explicit APO datasets without blurring them together with authored eval manifests.
- The expected outputs are not directly written down and must be derived from raw fields.
- The agent needs explicit transforms such as map, filter, reduce, grouping, joins, sorting, normalization, or rule evaluation before authoring eval rows.
- The agent should add synthetic rows only after grounded or computed rows establish the target task pattern.

If no credible source material exists yet, use a primary-source research workflow first instead of guessing.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional `split_strategy`: how to divide grounded rows into train and validation sets when APO datasets are required
- Optional source material such as `csv_file`, JSON, tables, schemas, rule definitions, lookup tables, existing examples, or structured notes from an approved research brief

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
