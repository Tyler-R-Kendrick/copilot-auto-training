---
name: trainer-synthesize
description: Build official `evals/evals.json` cases from grounded or computed source data. Use whenever a prompt or skill needs eval data, especially when correct outputs must be derived from raw fields, business rules, or verifier-backed synthetic examples.
license: MIT
compatibility: Requires Python 3.11+. Works with the trainer-optimize skill in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Synthesize

Use this skill to turn source material into official skill eval manifests.

Work compute-first. If labels, expected outputs, or assertions depend on derived values, plan the computation before writing rows. Synthesize only after the ground truth is provided or derived.

## When to use this skill

- The workflow needs `evals/evals.json` for a markdown prompt or skill.
- The user has examples, CSV or JSON data, tables, schemas, business rules, or source notes from the `trainer-research` skill.
- The agent should convert known source material into high-quality eval cases.
- The expected outputs are not directly written down and must be derived from raw fields.
- The agent needs explicit transforms such as map, filter, reduce, grouping, joins, sorting, normalization, or rule evaluation before authoring eval rows.
- The agent should add synthetic rows only after grounded or computed rows establish the target task pattern.

If no credible source material exists yet, use `trainer-research` first instead of guessing.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional source material such as `csv_file`, JSON, tables, schemas, rule definitions, lookup tables, existing examples, or structured notes from the `trainer-research` skill

## Resolve Before Writing

Resolve these inputs before authoring eval cases:

- raw source fields
- derived target values
- transformation logic
- output schema or answer format
- constraints, edge cases, and disallowed shortcuts

If any of these are missing, ask for them before synthesizing. Do not invent hidden rules, thresholds, or labels.

## Output

Return, in order:

1. A synthesis plan
2. Missing-input questions, if any
3. The final `evals/evals.json` content and any `evals/files/` assets

If the needed inputs are already present, state that the plan is fully satisfied and proceed.

## Synthesis Plan

Before writing any eval rows, build a short plan with these sections:

1. `Target layout`: derived `evals/evals.json` path, `evals/files/` assets, and any workspace directory implied by the prompt file.
2. `Observed inputs`: the fields directly present in the source data or prompt placeholders.
3. `Derived outputs`: the labels, scores, extracted facts, summaries, or structured answers that must be computed.
4. `Computation recipe`: the exact operations required to go from observed inputs to derived outputs. Use concrete language such as map, filter, reduce, group, join, normalize, rank, or rule-match.
5. `Verification path`: how each computed value will be checked independently.
6. `Missing inputs`: fields, rules, thresholds, label definitions, or source files that still need to be elicited.

For repeated or error-prone computation, prefer a script or deterministic transformation over manual mental arithmetic.

## Synthetic-data standard

Synthetic data is only acceptable here when it is grounded and verified. Use verifier-backed generation: draft candidate rows, then independently check them with deterministic rules, derived ground truth, or a stricter verifier before keeping them.

Apply that standard like this:

- Prefer real or research-grounded source rows first.
- Compute or verify the target answers independently from the generator whenever possible.
- Use synthetic generation to expand coverage, not to replace missing truth conditions.
- Reject candidate rows that cannot be traced back to a clear rule, source, or verification result.
- Keep generator and verifier roles conceptually separate. A candidate example is not valid just because it sounds plausible.

Core rule: generate, verify, filter, then keep only high-confidence rows.

## Process

1. Inspect the prompt placeholders and derive the official `evals/evals.json` target path and any `evals/files/` assets.
2. Build the synthesis plan before authoring any rows. Identify observed fields, derived targets, the computation recipe, and the verification method.
3. If the computation depends on missing inputs, ask for them before continuing.
4. Start from grounded source material such as user rows, CSV input, tables, or an approved shortlist from `trainer-research`.
5. Compute target values with explicit transforms such as map, filter, reduce, grouping, joins, normalization, and rule evaluation.
6. Keep grounded examples first; add synthetic rows only after the task pattern is established.
7. Verify every synthetic candidate independently and discard failures.
8. Fill coverage deliberately: edge cases, class balance, hard near-misses, null or missing inputs, malformed inputs, and realistic long-tail cases.
9. Convert the resulting tasks into official eval cases with realistic `prompt`, `expected_output`, optional `files`, and objective `assertions`.
10. Produce `evals/evals.json` and any required `evals/files/` assets next to the prompt or skill.

## Quality Rules

- Keep eval prompts realistic and user-like, not schematic labels.
- Prefer small, diverse eval sets over large repetitive sets.
- Make synthetic rows distributionally plausible for the task domain.
- Include hard negatives and boundary cases, not just easy canonical examples.
- Avoid leakage from the prompt wording into the expected answer when the real task would not provide that shortcut.
- Keep assertions objective and observable. If a property is subjective, leave it for later human review.
- Never hide unresolved ambiguity by writing overconfident expected outputs.

## Elicit If Missing

Ask for the missing items that block correct computation, such as:

- field definitions and units
- aggregation windows or grouping keys
- label taxonomy and tie-breaking rules
- normalization rules and text-cleaning rules
- allowed reference files or lookup tables
- examples of tricky failures or borderline cases

If none are missing, say so explicitly and continue.

## Naming rationale

`synthesize` is the best public name here because it focuses on conversion and example generation after source material has already been gathered.