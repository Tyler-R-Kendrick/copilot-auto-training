# Dataset Format Reference

The `trainer-optimize` skill uses JSONL (JSON Lines) files for training and validation datasets, while authored skill eval cases live in `evals/evals.json`.

Authored skill eval cases follow the official Agent Skills structure:

```text
<prompt-dir>/evals/evals.json
<prompt-dir>/evals/files/
```

The optimizer itself works with explicit JSONL datasets such as:

```text
<prompt-dir>/datasets/train.jsonl
<prompt-dir>/datasets/val.jsonl
```

Use `evals/evals.json` to author realistic prompts, expected outputs, optional file inputs, and assertions. Use explicit JSONL files only when you need APO training and validation splits.

## Model configuration

The repository root `.env` may define `COPILOT_MODEL` to select the single Copilot model used by the optimizer.

`trainer-optimize` does not infer dataset locations and does not synthesize missing JSONL files at runtime. Provide explicit `train.jsonl` and `val.jsonl` paths before starting optimization.

Single-shot optimize does not write steering files, iteration summaries, candidate workspaces, or dataset-collection artifacts unless a higher-level workflow adds them externally.

## File format

Each line in a `.jsonl` file must be a valid JSON object. Blank lines are skipped.

## Required fields

| Field | Type | Description |
|---|---|---|
| `input` | string or object | The input passed to the prompt. Must satisfy all template placeholders. |
| `expected` | string | The ideal output. Used by `deterministic`, `exact_match`, and `normalized_match`. |
| `scoring` | string | Recommended. Declares the intended scoring mode for the row, such as `exact_match`, `normalized_match`, `json_schema`, or `llm_judge`. |

## Shapes

### Simple string input

Use when your prompt template has a single `{input}` placeholder:

```json
{"input": "How do I reset my password?", "expected": "Visit account settings and click 'Forgot password'.", "scoring": "exact_match"}
```

### Structured input

Use when your prompt template has multiple named placeholders like `{question}` and `{context}`:

```json
{"input": {"question": "What is the capital of France?", "context": "European geography."}, "expected": "Paris", "scoring": "normalized_match"}
```

Each key in the `input` object must match a placeholder in the markdown template.

### Structured output

Use when the evaluator should compare structured JSON output against an expected schema or object:

```json
{"input": "Extract the order details from this email", "expected_json": {"order_id": "12345", "priority": "high"}, "scoring": "json_schema"}
```

### Open-ended judged response

Use when exact matching is not appropriate and an LLM judge must score the answer:

```json
{"input": "Draft a support reply for a delayed shipment", "reference": "Reference answer here", "criteria": ["correctness", "policy compliance", "resolution completeness"], "scoring": "llm_judge"}
```

Keep the runtime judge prompt, rubric text, and external benchmark notes separate:
- Put row-level scoring evidence in dataset fields such as `reference`, `criteria`, and `scoring`.
- Put reusable benchmark and rubric-design guidance next to the judge agent, such as [.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md](../../../.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md).
- Keep canonical benchmark summaries out of prompt-visible render paths and out of the raw `input` payload unless the task explicitly requires them.

## Placeholder matching rules

Given a template like:

```markdown
Context: {context}
Question: {question}
```

The dataset must have either:
- A top-level key that matches the placeholder name directly, **or**
- A nested path reachable via dot notation (e.g., `input.question` satisfies `{question}`)

Evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` should remain available to the scorer but must not be exposed to the prompt rendering path.
Literal brace-heavy examples are allowed in prompt text. A JSON example such as `{"input": "user request"}` should stay literal and must not be treated as a placeholder. Use double braces like `{{literal}}` only when you intentionally want literal braces in brace-based prompt syntax.

## Evaluator modes

| Mode | When to use | Requirement |
|---|---|---|
| `deterministic` | Exact or rule-based expected outputs | `expected` field required |
| `custom` | Normalized string matching, schema comparisons, or a scorer hook | Use row-level `scoring` such as `normalized_match`, `json_schema`, or `custom_python` |
| `llm_judge` | Open-ended tasks with no exact answer | Optional `judge_prompt_file`; recommended row fields are `reference` and `criteria` |

When `judge_mode=llm_judge` is used to optimize a judge prompt or other rubric-heavy evaluator, consult [.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md](../../../.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md) before changing the scoring prompt. That reference tracks benchmark pressure from JudgeBench, ContextualJudgeBench, RewardBench 2, locked-rubric work such as RULERS, task-adaptive rubric work such as AdaRubric and RubricRAG, and known judge failure modes such as order bias and naive chain-of-thought trust.

## Minimum dataset size

- At least **1 row** in both `train` and `val` files is required.
- For meaningful optimization, use **10+ rows** in `train` and **5+ rows** in `val`.

## Generation workflow

Work backward from the task the prompt is supposed to solve.

1. Freeze the prompt interface by listing its placeholders.
2. Pick one scoring mode first.
3. Build representative tasks for the same input type your prompt expects.
4. Add hidden scoring fields without leaking them into the prompt input path.
5. Split into `train.jsonl` and `val.jsonl`, and optionally `test.jsonl`.
6. Keep prompt optimization non-destructive by default, and only request file outputs when the workflow explicitly needs them.

Use `scripts/generate_jsonl.py` to bootstrap explicit JSONL datasets from CSV input.

## JSON Schema

See `assets/dataset.schema.json` for the formal schema definition.
