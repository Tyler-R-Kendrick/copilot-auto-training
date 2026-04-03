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

Use this skill to improve a single markdown prompt file by running Agent Lightning prompt optimization against explicit JSONL train and validation datasets, while keeping authored eval cases in the official `evals/evals.json` layout. The runtime is single-shot: it returns one optimized prompt result and does not coordinate leader election internally.

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

If those files do not exist, stop and report the missing path instead of guessing.
Do not synthesize missing datasets inside `trainer-optimize`. Any dataset creation or conversion must happen before this skill runs.

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
- `output` — optional path to write the optimized markdown without touching the source prompt
- `report` — where to write the JSON optimization report
- `beam_width` (default `4`)
- `branch_factor` (default `4`)
- `n_runners` (default `4`)
- `judge_mode` (default `deterministic`) — supported values are `deterministic`, `custom`, and `llm_judge`
- `judge_prompt_file` — optional path for `llm_judge`; falls back to `assets/judge-default.md`
- `debug_only` — run a smoke-test pass only, do not write output files
- `in_place` — overwrite the original prompt file with the optimized result

## Current implementation behavior

- Supported algorithms: `apo` and `verl`, selected through the same optimization pipeline.
- Supported judge modes: `deterministic`, `custom`, and `llm_judge`.
- The optimizer uses the repository root `.env` `COPILOT_MODEL` setting as its single model configuration.
- The runtime returns a `dashboard_url` in debug and normal JSON output. Unless `AGL_SERVER_PORT` is already set, it binds Agent Lightning to a free local port on `127.0.0.1` instead of assuming `4747`.
- Prompt rendering uses placeholder-targeted substitution rather than whole-string Python `str.format()`. Literal JSON or other brace-heavy examples remain literal, escaped braces like `{{literal}}` stay supported, and nested placeholders such as `{input.question}` are allowed.
- When no inference model is configured, or a live optimize run loses model access because of rate limiting or service unavailability, the runtime returns a `manual_followup` JSON payload instead of failing. That payload includes deterministic preparation results plus an agent-side inference handoff: the current `@trainer` agent can answer the returned `model_prompt`, save the result as a candidate prompt, and continue the workflow without an inference API token.
- By default the optimized prompt is returned in the JSON result and CLI stdout without writing files.
- The source prompt is only overwritten when `in_place` is requested.
- `output` writes a separate optimized prompt file when requested.
- `report` writes a JSON report only when requested.
- In `manual_followup` mode, the source prompt is left unchanged. The JSON payload preserves the baseline prompt, explains the blocker, and includes the `model_prompt`, `agent_handoff_instruction`, and `rerun_command` needed for the current `@trainer` agent to finish the optimize stage without an inference API token.
- `scripts/train.py` can run a Microsoft Trace self-training loop over one or more explicit prompt/train/val cases to tune the single-shot optimize policy.
- Require at least one row in both `train` and `val`.
- The repository's authored skill eval cases live under `evals/evals.json` next to the prompt or skill.
- The generator utility `scripts/generate_jsonl.py` can create explicit `train.jsonl` and `val.jsonl` files from CSV input.
- Dataset generation and conversion belong outside this runtime. Use a separate research-and-synthesis workflow before calling this skill when explicit JSONL files do not exist yet.

## Process

1. Parse the `/trainer-optimize` arguments from the user's message.
2. Resolve explicit `train` and `val` dataset paths.
3. If datasets still do not exist, stop and report the missing explicit dataset arguments or paths.
4. Validate that all resolved file paths exist and are readable.
5. Read the prompt file and inspect a sample row from the training dataset.
6. Verify the train and validation files each contain at least one JSON object row.
7. Extract template placeholders and verify they are satisfiable from the sample task schema.
8. Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` out of the prompt rendering path.
9. If the prompt contains literal JSON or brace-heavy examples, keep them literal or escaped and do not let them introduce accidental placeholders.
10. If the prompt or dataset shape is incompatible, stop and explain the mismatch clearly.
11. Run `scripts/run_optimize.py` with the resolved arguments.
12. Return the optimized prompt in JSON/stdout unless explicit persistence flags request file output.
13. If the runtime returns `manual_followup`, use the returned `model_prompt` through the current `@trainer` agent to draft the candidate prompt, then report the blocker, the handoff instruction, and the saved candidate artifact instead of claiming the code runtime produced the candidate directly.
14. Otherwise report the optimized prompt path, report path, dashboard URL, and optimization metadata from the JSON result.

## Algorithm guidance

- Default to `apo` for most prompt-file optimization tasks.
- Use `verl` when the user explicitly wants the alternative algorithm or when repo policy prefers it.
- Prefer `deterministic` when exact or rule-based scoring is available.
- Use `custom` for normalization or schema-based scoring.
- Use `llm_judge` only when deterministic or custom scoring is not a good fit.

## Output Modes

The runtime produces a single optimized prompt result. Persistence is explicit:

- **Default**: return the optimized prompt in JSON/stdout only.
- **`output` provided**: write a separate optimized prompt file.
- **`in_place` enabled**: overwrite the source `prompt_file`.
- **`report` provided**: write a JSON report file.

If a higher-level workflow wants to compare multiple optimize results, that comparison belongs outside this skill.

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

Use `evals/evals.json` for authored evaluation cases, and keep runtime-only optimization output separate from the published eval manifest.

Trace self-training:

```bash
python scripts/train.py \
  --prompt-file ../../examples/first-run/prompts/classify_support.md \
  --train-file ../../examples/first-run/datasets/train.jsonl \
  --val-file ../../examples/first-run/datasets/val.jsonl \
  --epochs 2 \
  --report-file /tmp/trace-train-report.json
```

## Outputs

After a successful run, the JSON result always contains the optimized prompt text and optimization metadata. Files are written only when requested via `output`, `report`, or `in_place`.

When the runtime returns `manual_followup`, it still reports the validated prompt/dataset metadata plus a model-ready optimization prompt and an agent-side handoff. This is the supported fallback when external models are unavailable.

`scripts/train.py` writes a JSON training report only when `--report-file` is passed; otherwise it prints the report to stdout.

## Dashboard

During an active optimization run, Agent Lightning starts a local dashboard server and returns its URL in the JSON result as `dashboard_url`.

- Open the returned dashboard root URL in a browser while the run is active.
- Unless `AGL_SERVER_PORT` is preconfigured, the runtime chooses a free local port automatically.
- The dashboard health endpoint is `<dashboard_url>/v1/agl/health`.
- Available pages include `Rollouts`, `Resources`, `Traces`, `Runners`, and `Settings`.
- If the UI shows `Offline`, verify the backend base URL in `Settings`, confirm the optimization process is still running, and check whether you opened the current `dashboard_url` rather than an older fixed port.

## Placeholder validation

Template placeholders such as `{input}` must match keys the optimizer can validate from the task rows. Double-brace escapes like `{{literal}}` are ignored. Literal JSON examples such as `{"input": "user request"}` are not placeholders and should stay literal. If any placeholder is missing from the dataset schema, stop and explain the mismatch to the user.

## Error cases

- Missing or unreadable files → report the specific path and stop
- Empty train or val dataset → require at least one task row in each
- Placeholder mismatch → list the unmatched placeholders and the actual dataset fields
- Immediate rollout failure in the dashboard → treat as a runtime exception, inspect stderr and traces first, and do not describe it as a low score
- Dashboard port conflict or stale forwarded URL → use the returned `dashboard_url`, or set `AGL_SERVER_PORT` explicitly if you need a stable port
- Missing dataset paths → report the missing explicit arguments or unreadable paths and stop
- Unsupported judge mode → explain the supported modes: `deterministic`, `custom`, and `llm_judge`
- Unsupported algorithm → explain the supported algorithms: `apo` and `verl`
- Missing model configuration or transient model availability failures such as `RateLimitError` → return `manual_followup` with deterministic preparation output and an agent-side inference handoff so the current `@trainer` agent can finish the optimize stage without an inference token

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
  [--algorithm apo|verl] \
  [--judge-mode deterministic|custom|llm_judge] \
  [--judge-prompt-file assets/judge-default.md] \
  [--debug-only] \
  [--in-place]
```

Use `--help` if you need to confirm available flags in the current script version.

Copilot `.env` example at the repository root:

```dotenv
COPILOT_MODEL=default
```

Use [/.env.sample](/workspaces/copilot-apo/.env.sample) as the canonical template for the supported Copilot setting.

See `references/dataset-format.md` for the dataset contract and `assets/examples.md` for worked examples.
