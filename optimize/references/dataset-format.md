# Dataset Format Reference

The `optimize` skill uses JSONL (JSON Lines) files for training and validation datasets.

## File format

Each line in a `.jsonl` file must be a valid JSON object. Blank lines are skipped.

## Required fields

| Field | Type | Description |
|---|---|---|
| `input` | string or object | The input passed to the prompt. Must satisfy all template placeholders. |
| `expected` | string | The ideal output. Used by the `deterministic` evaluator. |

## Shapes

### Simple string input

Use when your prompt template has a single `{input}` placeholder:

```json
{"input": "How do I reset my password?", "expected": "Visit account settings and click 'Forgot password'."}
```

### Structured input

Use when your prompt template has multiple named placeholders like `{question}` and `{context}`:

```json
{"input": {"question": "What is the capital of France?", "context": "European geography."}, "expected": "Paris"}
```

Each key in the `input` object must match a placeholder in the markdown template.

## Placeholder matching rules

Given a template like:

```markdown
Context: {context}
Question: {question}
```

The dataset must have either:
- A top-level key that matches the placeholder name directly, **or**
- A nested path reachable via dot notation (e.g., `input.question` satisfies `{question}`)

## Evaluator modes

| Mode | When to use | Requirement |
|---|---|---|
| `deterministic` | Exact or rule-based expected outputs | `expected` field required |
| `custom` | Task-specific scoring logic | Edit `run_optimize.py` evaluator |
| `llm_judge` | Open-ended tasks with no exact answer | Optional `judge_prompt_file` |

## Minimum dataset size

- At least **1 row** in both `train` and `val` files is required.
- For meaningful optimization, use **10+ rows** in `train` and **5+ rows** in `val`.

## JSON Schema

See `assets/dataset.schema.json` for the formal schema definition.
