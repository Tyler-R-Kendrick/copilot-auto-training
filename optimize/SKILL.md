---
name: optimize
description: Improve a markdown prompt file using Agent Lightning APO (Automatic Prompt Optimization). Use when the user asks to optimize or improve a prompt, or starts a message with /optimize.
license: Apache-2.0
compatibility: Requires Python 3.11+, agentlightning, and openai packages. Works in Claude Code and any agent that supports the Agent Skills standard.
metadata:
  author: your-org
  version: "0.1.0"
allowed-tools: Bash(python:*) Read Write
---

# Prompt Optimization with Agent Lightning APO

Optimize a markdown prompt file by running Automatic Prompt Optimization (APO) against a JSONL task dataset.

## When to use this skill

- The user says "optimize my prompt", "improve this prompt", or starts with `/optimize`
- The target artifact is a single `.md` (markdown) prompt template file
- The user provides, or can provide, a train and validation JSONL dataset

## Invocation syntax

```
/optimize prompt=<path> train=<path> val=<path> [options]
```

Required arguments:
- `prompt` — path to the markdown prompt file to optimize
- `train` — path to the JSONL training dataset
- `val` — path to the JSONL validation dataset

Optional arguments:
- `iterations` (default `3`) — number of APO beam rounds
- `algorithm` (default `apo`) — `apo` (recommended) or `verl` (advanced, not default)
- `output` — where to write the optimized markdown (default: `<stem>.optimized.md`)
- `report` — where to write the JSON optimization report (default: `<stem>.report.json`)
- `beam_width` (default `4`)
- `branch_factor` (default `4`)
- `n_runners` (default `4`)
- `judge_mode` (default `deterministic`) — `deterministic`, `custom`, or `llm_judge`
- `judge_prompt_file` — only used when `judge_mode=llm_judge`
- `debug_only` — run a smoke-test pass only, do not write output files

## Process

1. Parse the `/optimize` arguments from the user's message.
2. Validate that `prompt`, `train`, and `val` file paths exist and are readable.
3. Inspect a sample row from the train dataset and extract placeholder names from the markdown template.
4. Verify every template placeholder (`{field}`) is satisfiable from the task fields — fail fast with a clear error if not.
5. Confirm with the user before running the script (script approval required).
6. Run `scripts/run_optimize.py` with the resolved arguments.
7. Report the optimized prompt path and the score delta from the JSON report.

## Algorithm guidance

- **Default to `apo`** for all markdown prompt file optimization tasks.
- Only suggest `verl` when the user explicitly asks for RL-based or model-path optimization. Treat it as advanced and not the default path.
- Prefer `judge_mode=deterministic` when tasks have exact or rule-based expected outputs.
- Only use `judge_mode=llm_judge` when deterministic scoring is genuinely not possible.

## Dataset format

Each line in the JSONL file must be a JSON object. See `references/dataset-format.md` for details.

Simple form:
```json
{"input": "user request", "expected": "ideal answer"}
```

Structured form (input fields match template placeholders):
```json
{"input": {"question": "What is 2+2?", "context": "arithmetic"}, "expected": "4"}
```

## Outputs

After a successful run, two files are written:
1. **Optimized prompt** — the improved markdown file
2. **Report JSON** — contains `algorithm`, `prompt_file`, `output_file`, `iterations`, `train_size`, `val_size`, `beam_width`, `branch_factor`, `n_runners`, `judge_mode`, and `ok`

## Placeholder validation

Template placeholders like `{input}`, `{question}`, `{context}` must match field names in the dataset rows. Double-brace escapes like `{{literal}}` are ignored. If any placeholder is missing from the dataset schema, stop and explain the mismatch to the user.

## Error cases

- Missing or unreadable files → report the specific path and stop
- Empty train or val dataset → require at least one task row in each
- Placeholder mismatch → list the unmatched placeholders and the actual dataset fields
- `verl` algorithm → explain that APO is the correct default for prompt-file optimization

## Running the script

```bash
python scripts/run_optimize.py \
  --prompt-file <path> \
  --train-file <path> \
  --val-file <path> \
  [--iterations 3] \
  [--output-file <path>] \
  [--report-file <path>] \
  [--beam-width 4] \
  [--branch-factor 4] \
  [--n-runners 4] \
  [--judge-mode deterministic] \
  [--debug-only]
```

Always run with `--help` first to see current usage.

See `references/dataset-format.md` for the dataset contract and `assets/examples.md` for worked examples.
