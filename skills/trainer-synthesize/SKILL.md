---
name: trainer-synthesize
description: Build official `evals/evals.json` cases and explicit APO datasets from grounded or computed source data. Use whenever a prompt or skill needs eval rows, `train.jsonl`, or `val.jsonl`, especially when correct outputs must be derived from raw fields, business rules, or verifier-backed synthetic examples.
license: MIT
compatibility: Requires Python 3.11+. Produces official eval manifests plus explicit APO datasets for this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Synthesize

Use this skill to turn source material into official skill eval manifests and explicit APO datasets.

In this repository, authored eval cases live in `evals/evals.json`, optional eval assets live in `evals/files/`, and APO training data lives in explicit `datasets/train.jsonl` and `datasets/val.jsonl` files. Work compute-first. If labels, expected outputs, assertions, or JSONL rows depend on derived values, plan the computation before writing them. Synthesize only after the ground truth is provided or derived.

## When to use this skill

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

## Resolve Before Writing

Resolve these inputs before authoring eval cases:

- raw source fields
- derived target values
- transformation logic
- output schema or answer format
- dataset row shape and split boundary
- constraints, edge cases, and disallowed shortcuts

If any of these are missing, ask for them before synthesizing. Do not invent hidden rules, thresholds, or labels.

## Output

Return, in order:

1. A synthesis plan
2. Missing-input questions, if any
3. The final `evals/evals.json` content and any `evals/files/` assets
4. The final `train.jsonl` and `val.jsonl` content when APO datasets are required
5. A brief provenance and split note that explains which rows are grounded, which rows are synthetic, and how validation rows were held out

If the needed inputs are already present, state that the plan is fully satisfied and proceed. In this repository, producing only `evals/evals.json` is the exception; when the output is meant to feed an optimizer, treat `train.jsonl` and `val.jsonl` as part of done state.

## Synthesis Plan

Before writing any eval rows, build a short plan with these sections:

1. `Target layout`: derived `evals/evals.json` path, `evals/files/` assets, explicit `datasets/train.jsonl` and `datasets/val.jsonl` paths, and any workspace directory implied by the prompt file.
2. `Observed inputs`: the fields directly present in the source data or prompt placeholders.
3. `Derived outputs`: the labels, scores, extracted facts, summaries, or structured answers that must be computed.
4. `Computation recipe`: the exact operations required to go from observed inputs to derived outputs. Use concrete language such as map, filter, reduce, group, join, normalize, rank, or rule-match.
5. `Verification path`: how each computed value will be checked independently.
6. `Dataset split`: how grounded rows, boundary cases, and verifier-backed synthetic rows will be distributed between train and validation without leakage.
7. `Missing inputs`: fields, rules, thresholds, label definitions, or source files that still need to be elicited.

For repeated or error-prone computation, prefer a script or deterministic transformation over manual mental arithmetic.

Use `scripts/run_synthesize.py` to derive the canonical target paths and prompt placeholders before writing files. If the source rows already exist in CSV form, use the repository JSONL generator utility to bootstrap explicit `train.jsonl` and `val.jsonl` files under the modern `datasets/` layout.

## Dataset contract

Keep authored eval cases and APO datasets separate:

- `evals/evals.json` should contain realistic user prompts, human-readable `expected_output`, optional `files`, and objective `assertions`.
- `train.jsonl` and `val.jsonl` should contain evaluator-facing rows such as `input`, `expected`, `expected_json`, `reference`, `criteria`, and `scoring` as needed by the task.
- Do not leak evaluator-only fields into the prompt-visible input path.
- Preserve prompt placeholders exactly. If the template uses multiple placeholders, emit structured JSONL input that satisfies those names.
- Keep at least one grounded or independently verified row in both train and validation splits.

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
4. Start from grounded source material such as user rows, CSV input, tables, or an approved research brief.
5. Compute target values with explicit transforms such as map, filter, reduce, grouping, joins, normalization, and rule evaluation.
6. Keep grounded examples first; add synthetic rows only after the task pattern is established.
7. Verify every synthetic candidate independently and discard failures.
8. Fill coverage deliberately: edge cases, class balance, hard near-misses, null or missing inputs, malformed inputs, and realistic long-tail cases.
9. Convert the resulting tasks into official eval cases with realistic `prompt`, `expected_output`, optional `files`, and objective `assertions`.
10. Convert the same grounded task set into explicit `train.jsonl` and `val.jsonl` rows, keeping evaluator-only fields out of the prompt-visible path.
11. Split rows so validation remains a genuine holdout. Explain the split if the source set is small or skewed.
12. Produce `evals/evals.json`, any required `evals/files/` assets, and explicit dataset files under the canonical layout next to the prompt or skill.

## Quality Rules

- Keep eval prompts realistic and user-like, not schematic labels.
- Keep JSONL rows faithful to the prompt interface and scoring mode.
- Prefer small, diverse eval sets over large repetitive sets.
- Make synthetic rows distributionally plausible for the task domain.
- Include hard negatives and boundary cases, not just easy canonical examples.
- Avoid leakage from the prompt wording into the expected answer when the real task would not provide that shortcut.
- Keep assertions objective and observable. If a property is subjective, leave it for later human review.
- Keep validation rows meaningfully different from training rows; do not create a split that only differs by superficial wording.
- Never blur authored `evals/evals.json` fixtures together with `train.jsonl` or `val.jsonl` datasets.
- Never hide unresolved ambiguity by writing overconfident expected outputs.

## Elicit If Missing

Ask for the missing items that block correct computation, such as:

- field definitions and units
- aggregation windows or grouping keys
- label taxonomy and tie-breaking rules
- normalization rules and text-cleaning rules
- required scoring mode and dataset row fields
- train or validation split constraints when the caller already has a benchmark plan
- allowed reference files or lookup tables
- examples of tricky failures or borderline cases

If none are missing, say so explicitly and continue.

## Guardrails

- Do not claim a downstream optimizer will infer or synthesize missing datasets later.
- Do not route around missing rules by inventing labels, thresholds, or tie-breakers.
- Do not add benchmark, leader-election, or optimizer-runtime behavior to this skill.
- Do not emit empty dataset splits. If there is not enough trustworthy data for both train and validation, say so.

## Naming rationale

`synthesize` is the best public name here because it focuses on conversion and example generation after source material has already been gathered.