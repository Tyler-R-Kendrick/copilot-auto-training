---
name: trainer-optimize
description: Improve a markdown prompt file using Agent Lightning APO (Automatic Prompt Optimization). Use when the user asks to optimize or improve a markdown prompt, or starts a message with /trainer-optimize.
license: MIT
compatibility: Requires Python 3.11+, agentlightning, and openai packages. Works in Claude Code and any agent that supports the Agent Skills standard.
metadata:
  author: your-org
  version: "0.1.0"

---

# Prompt Optimization with Agent Lightning

Use this skill to improve a single markdown prompt file by running Agent Lightning prompt optimization against explicit JSONL train and validation datasets, while keeping authored eval cases in the official `evals/evals.json` layout.

## When to use this skill

- The user says "optimize my prompt", "improve this prompt", or starts with `/trainer-optimize`
- The target artifact is a single `.md` (markdown) prompt template file
- The user provides, or can provide, train and validation JSONL datasets with expected outputs

Do not use this skill for general code optimization or non-markdown prompts.

## Required inputs

The skill always needs a prompt path. It also needs train and validation datasets. In this repository, authored eval cases live under `evals/evals.json`, while APO datasets are passed explicitly.

- `prompt`: path to the markdown prompt file to optimize
- `train`: path to the JSONL training dataset
- `val`: path to the JSONL validation dataset

If those files do not exist, ask the user for the missing path instead of guessing.
If the files do not exist anywhere, return a dialog-shaped request for the bare minimum information needed to generate them: representative examples or a CSV source, values for every prompt placeholder, and the expected answer format or scoring rule.

## Invocation syntax

```
/trainer-optimize prompt=<path> train=<path> val=<path> [options]
```

Required arguments:
- `prompt` — path to the markdown prompt file to optimize
- `train` — path to the JSONL training dataset
- `val` — path to the JSONL validation dataset

Optional arguments:
- `iterations` (default `3`) — number of APO beam rounds
- `algorithm` (default `apo`) — supported values are `apo` and `verl`
- `output` — backup copy path for the optimized markdown (the original prompt file is always replaced in-place)
- `report` — where to write the JSON optimization report
- `beam_width` (default `4`)
- `branch_factor` (default `4`)
- `n_runners` (default `4`)
- `n_variants` (default `4`) — when search yields only one candidate, hand that candidate to the `trainer-election` skill runtime to generate fallback variants and elect the leader
- `judge_mode` (default `deterministic`) — supported values are `deterministic`, `custom`, and `llm_judge`
- `judge_prompt_file` — optional path for `llm_judge`; falls back to `assets/judge-default.md`
- `debug_only` — run a smoke-test pass only, do not write output files

## Current implementation behavior

- Supported algorithms: `apo` and `verl`, selected through the same optimization pipeline.
- Supported judge modes: `deterministic`, `custom`, and `llm_judge`.
- The optimizer loads GitHub Models settings from the repository root `.env` when `GITHUB_MODELS_*` variables are present.
- Supported root `.env` variables are `GITHUB_MODELS_API_KEY`, `GITHUB_MODELS_ENDPOINT`, `GITHUB_MODELS_GRADIENT_MODEL`, and `GITHUB_MODELS_APPLY_EDIT_MODEL`.
- The prompt file is overwritten in place on success. `output` is only a backup copy destination.
- Require at least one row in both `train` and `val`.
- The final selection pool always includes the original prompt as a baseline candidate to guard against regression.
- Candidate scores are persisted into the JSON report.
- The repository's authored skill eval cases live under `evals/evals.json` next to the prompt or skill.
- If datasets are missing, the optimizer returns a structured dialog request for the minimum information needed to generate `train.jsonl` and `val.jsonl`.
- Each run also writes runtime artifacts under `<prompt-dir>/<prompt-name>-workspace/`, including a workspace `benchmark.json`, a rolling `steering.md`, and per-iteration candidate summaries.
- Steering from previous runs is reused during later selections so failed patterns can be penalized instead of repeated.
- The generator utility `scripts/generate_jsonl.py` can create explicit `train.jsonl` and `val.jsonl` files from CSV input.
- The final search-and-election stage is delegated to [skills/trainer-election/SKILL.md](../trainer-election/SKILL.md).
- When datasets are missing, use the dialog response to collect inputs, hand public-source discovery to [skills/trainer-research/SKILL.md](../trainer-research/SKILL.md), and then hand dataset generation to [skills/trainer-synthesize/SKILL.md](../trainer-synthesize/SKILL.md).

## Process

1. Parse the `/trainer-optimize` arguments from the user's message.
2. Resolve explicit `train` and `val` dataset paths.
3. If datasets still do not exist, return a dialog request for only the minimum information needed to generate them.
4. Validate that all resolved file paths exist and are readable.
5. Read the prompt file and inspect a sample row from the training dataset.
6. Verify the train and validation files each contain at least one JSON object row.
7. Extract template placeholders and verify they are satisfiable from the sample task schema.
8. Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` out of the prompt rendering path.
9. If the prompt or dataset shape is incompatible, stop and explain the mismatch clearly.
10. Run `scripts/run_optimize.py` with the resolved arguments.
11. Delegate the search-and-election stage to the `trainer-election` skill runtime.
12. Inspect the runtime steering file before later runs so repeated failures can be avoided.
13. Report the optimized prompt path, report path, winner details, temp run directory, and persisted candidate summary from the JSON result.

## Algorithm guidance

- Default to `apo` for most prompt-file optimization tasks.
- Use `verl` when the user explicitly wants the alternative algorithm or when repo policy prefers it.
- Prefer `deterministic` when exact or rule-based scoring is available.
- Use `custom` for normalization or schema-based scoring.
- Use `llm_judge` only when deterministic or custom scoring is not a good fit.

## Leader election

After the search step completes, the leader is selected by the `trainer-election` skill as follows:

- **Multiple candidates**: all search candidates plus the original prompt are scored on the validation dataset, and the highest-scoring prompt wins.
- **Single candidate**: `n_variants` paraphrases of the sole candidate are generated, then those variants plus the original prompt are scored on the validation dataset.

The leader content **replaces the original `prompt_file` in-place**. An optional backup copy is written to `output` if provided.

## Dataset format

Each line in the JSONL file must be a JSON object. See `references/dataset-format.md` for details.

Recommended form:
```json
{"input": "user request", "expected": "ideal answer", "scoring": "exact_match"}
```

Repository-authored eval convention:

```text
skills/
  trainer-optimize/
    SKILL.md
    evals/
      evals.json
      files/
```

For APO runs, keep `train.jsonl` and `val.jsonl` as explicit dataset files and pass them on the command line.

Temp run artifacts:

```text
prompts/
  support.md
datasets/
  train.jsonl
  val.jsonl
support-workspace/
  benchmark.json
  steering.md
  iteration-001/
    report.json
    summary.md
    candidates/
```

Use each iteration `summary.md` to review why the winner beat the field, what caused low-scoring candidates to fail, and what should change next. Use workspace `steering.md` as the rolling summary of prior runs so future iterations do not repeat the same failures, reward hacking, or verbose and redundant output patterns.

Use `evals/evals.json` for authored evaluation cases, and keep runtime-only optimization artifacts separate from the published eval manifest.

## Outputs

After a successful run, two files are written:
1. **Optimized prompt** — the improved markdown file
2. **Report JSON** — contains `algorithm`, resolved dataset paths, `output_file`, optimization settings, `ok`, and a persisted `candidates` list with scores, baseline markers, and winner markers

Runtime artifacts are also written under `<prompt-dir>/<prompt-name>-workspace/`:
- `benchmark.json` — the default top-level report path when `report` is not passed explicitly
- `steering.md` — rolling cross-run lessons and failure patterns to avoid
- `iteration-.../summary.md` — run-specific markdown summary of winner, failures, and next improvements
- `iteration-.../candidates/*.md` — candidate-specific notes and content snapshots

By default, the runtime writes the top-level report to `<prompt-dir>/<prompt-name>-workspace/benchmark.json` unless you pass `report` explicitly.

## Dashboard

During an active optimization run, Agent Lightning starts a local dashboard server at `http://localhost:4747`.

- Open the dashboard root URL in a browser while the run is active.
- The dashboard uses `http://localhost:4747/v1/agl/health` for health checks and API connectivity.
- Available pages include `Rollouts`, `Resources`, `Traces`, `Runners`, and `Settings`.
- If the UI shows `Offline`, verify the backend base URL in `Settings` and confirm the optimization process is still running.

## Placeholder validation

Template placeholders such as `{input}` must match keys the optimizer can validate from the task rows. Double-brace escapes like `{{literal}}` are ignored. If any placeholder is missing from the dataset schema, stop and explain the mismatch to the user.

## Error cases

- Missing or unreadable files → report the specific path and stop
- Empty train or val dataset → require at least one task row in each
- Placeholder mismatch → list the unmatched placeholders and the actual dataset fields
- Missing dataset paths → report the missing resolved paths and stop
- Missing dataset paths → return a dialog request for only the minimum information needed to generate the files
- Unsupported judge mode → explain the supported modes: `deterministic`, `custom`, and `llm_judge`
- Unsupported algorithm → explain the supported algorithms: `apo` and `verl`

## Running the script

```bash
python scripts/run_optimize.py \
  --prompt-file <path> \
  [--train-file <path>] \
  [--val-file <path>] \
  [--iterations 3] \
  [--output-file <path>] \
  [--report-file <path>] \
  [--beam-width 4] \
  [--branch-factor 4] \
  [--n-runners 4] \
  [--n-variants 4] \
  [--algorithm apo|verl] \
  [--judge-mode deterministic|custom|llm_judge] \
  [--judge-prompt-file assets/judge-default.md] \
  [--debug-only]
```

Use `--help` if you need to confirm available flags in the current script version.

GitHub Models `.env` example at the repository root:

```dotenv
GITHUB_MODELS_API_KEY=<github-pat>
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_GRADIENT_MODEL=openai/gpt-4.1-mini
GITHUB_MODELS_APPLY_EDIT_MODEL=openai/gpt-4.1-mini
```

See `references/dataset-format.md` for the dataset contract and `assets/examples.md` for worked examples.
