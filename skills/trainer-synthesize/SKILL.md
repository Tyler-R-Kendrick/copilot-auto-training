---
name: trainer-synthesize
description: Convert grounded source material into official `evals/evals.json` cases for prompts and skills. Use whenever a prompt or skill needs eval data, especially when labels or expected outputs must be computed from raw inputs, derived with map/filter/reduce style transforms, or synthesized through verifier-backed examples after a research pass or user-provided examples.
license: MIT
compatibility: Requires Python 3.11+. Works with the trainer-optimize skill in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Synthesize

Use this skill to create official skill eval manifests for optimization and review workflows.

This skill is compute-first, not prose-first. When the desired labels, expected outputs, or assertions depend on derived values, statistics, rule application, or normalization, plan that computation before writing any eval cases. Synthesis happens only after the ground truth is either provided or derived.

## When to use this skill

- The workflow needs `evals/evals.json` for a markdown prompt or skill.
- The user has examples, a CSV file, tables, schemas, business rules, or source notes from the `trainer-research` skill.
- The agent should convert known source material into high-quality eval cases.
- The expected outputs are not directly written down and must be derived from raw fields.
- The agent needs to compute actual values through transformations such as map, filter, reduce, grouping, joins, sorting, normalization, or rule evaluation before authoring eval rows.
- The agent should simulate representative examples only after grounded or computed examples establish the target task shape.

If no credible source material exists yet, use `trainer-research` first instead of guessing.

## Inputs

- `prompt_file`: target markdown prompt
- `task_description`: short description of the real task the prompt should solve
- `scoring_rule`: expected answer format or evaluation rule
- Optional source material such as `csv_file`, JSON, tables, schemas, rule definitions, existing examples, or structured notes from the `trainer-research` skill

## Required working inputs

Before authoring eval cases, resolve these inputs explicitly:

- raw source fields available to the prompt author or end user
- hidden derived values that must be computed to obtain the correct answer
- transformation logic needed to compute those values
- output schema or answer format required by the scoring rule
- constraints, edge cases, and disallowed shortcuts

If any of these are missing, ask the user for them before synthesizing. Do not invent hidden business rules, thresholds, or labels when they are required to compute the correct answer.

## Output

Produce the work in this order:

1. A synthesis plan that identifies the target files, the computation required, and any missing inputs.
2. A concise elicitation list for any missing fields, rules, or assets that must be supplied.
3. The final `evals/evals.json` content and any `evals/files/` assets once the computation path is fully specified.

If the needed inputs are already present, state that the plan is fully satisfied and proceed.

## Compute-first synthesis plan

Before writing any eval rows, build a short plan with these sections:

1. `Target layout`: derived `evals/evals.json` path, `evals/files/` assets, and any workspace directory implied by the prompt file.
2. `Observed inputs`: the fields directly present in the source data or prompt placeholders.
3. `Derived outputs`: the labels, scores, extracted facts, summaries, or structured answers that must be computed.
4. `Computation recipe`: the exact operations required to go from observed inputs to derived outputs. Use concrete language such as map, filter, reduce, group, join, normalize, rank, or rule-match.
5. `Verification path`: how each computed value will be checked independently.
6. `Missing inputs`: fields, rules, thresholds, label definitions, or source files that still need to be elicited.

For repeated or error-prone computation, prefer a script or deterministic transformation over manual mental arithmetic.

## Synthetic-data standard

Synthetic data is only useful here when it is grounded and verified. The recent improvement that makes synthetic data far more valuable than naive hand-written examples is verifier-backed generation: use a capable model or source material to draft candidates, then independently check them with deterministic rules, derived ground truth, or a stricter verifier before keeping them.

Apply that standard here:

- Prefer real or research-grounded source rows first.
- Compute or verify the target answers independently from the generator whenever possible.
- Use synthetic generation to expand coverage, not to replace missing truth conditions.
- Reject candidate rows that cannot be traced back to a clear rule, source, or verification result.
- Keep generator and verifier roles conceptually separate. A candidate example is not valid just because it sounds plausible.

This is the core best practice: generate, verify, filter, then keep only high-confidence rows. Unverified synthetic data is not acceptable for official eval authoring.

## Process

1. Inspect the prompt placeholders and derive the official `evals/evals.json` target path and any `evals/files/` assets.
2. Build the synthesis plan before authoring any rows. Identify observed fields, derived targets, the computation recipe, and the verification method.
3. If the computation depends on missing inputs, ask for them directly. Elicit missing schemas, field meanings, thresholds, label definitions, or source files before continuing.
4. Start from known source material such as user rows, CSV input, tables, or a source shortlist from the `trainer-research` skill.
5. Compute actual target values from the source material. Use explicit transformations such as map, filter, reduce, grouping, joins, normalization, and rule evaluation where needed.
6. Prefer grounded examples when they fit the task and licensing allows reuse.
7. Synthesize additional examples only after the grounded or computed cases establish the correct task pattern.
8. Apply verifier-backed generation: draft candidate synthetic rows, independently verify the target outputs, and discard anything that does not pass verification.
9. Fill gaps in coverage deliberately: edge cases, class balance, difficult near-misses, null or missing inputs, malformed inputs, and realistic long-tail cases.
10. Convert the resulting tasks into official eval cases with realistic `prompt`, `expected_output`, optional `files`, and objective `assertions`.
11. Produce `evals/evals.json` and any required `evals/files/` assets next to the prompt or skill.

## Coverage and quality rules

- Keep eval prompts realistic and user-like, not schematic labels.
- Prefer small, diverse eval sets over large repetitive sets.
- Make synthetic rows distributionally plausible for the task domain.
- Include hard negatives and boundary cases, not just easy canonical examples.
- Avoid leakage from the prompt wording into the expected answer when the real task would not provide that shortcut.
- Keep assertions objective and observable. If a property is subjective, leave it for later human review.
- Never hide unresolved ambiguity by writing overconfident expected outputs.

## Elicitation checklist

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