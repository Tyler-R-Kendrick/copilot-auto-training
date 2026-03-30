# Getting Started

This guide covers installation, model configuration, the first run, and the optimizer's output modes.

## Prerequisites

- Python 3.11 or newer
- A virtual environment for the repository
- Model credentials through either `OPENAI_API_KEY` or GitHub Models configuration in the repository root `.env`
- A model name through `OPENAI_MODEL` or `GITHUB_MODELS_MODEL`

## Install Dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The runtime dependency set includes `poml`, which Agent Lightning APO requires during optimization.

In the devcontainer, the post-start hook automatically recreates `.venv` with Python 3.12 and reinstalls dependencies when the local environment is missing, stale, or missing `pip`.

## Configure Model Access

If you are using GitHub Models, create a repository-root `.env` file like this:

```dotenv
GITHUB_MODELS_API_KEY=<github-pat>
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_MODEL=openai/gpt-4.1-mini
GITHUB_MODELS_GRADIENT_MODEL=openai/gpt-4.1-mini
GITHUB_MODELS_APPLY_EDIT_MODEL=openai/gpt-4.1-mini
```

Start from [/.env.sample](/workspaces/copilot-apo/.env.sample) so the supported secret and model keys stay documented in one place.

When these `GITHUB_MODELS_*` values are present, the optimizer treats the repository-root `.env` as the authoritative source for GitHub Models settings.
On GitHub Models endpoints, the runtime will try the OpenAI Responses API first and automatically fall back to chat completions when the endpoint rejects that route with `404`.

## Verify the Environment

Run the test suite before starting an optimization run:

```bash
python -m pytest -q
```

## First Run

The smallest runnable example in this repository is documented in [examples/first-run/README.md](../examples/first-run/README.md).

`trainer-optimize` requires explicit `--train-file` and `--val-file` inputs. It does not infer, synthesize, or collect missing datasets at runtime.

Smoke test:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --debug-only
```

Small full run:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

By default, the optimized prompt is returned in JSON/stdout and the source prompt is left unchanged.
The JSON output also includes `dashboard_url`; open that value instead of assuming a fixed dashboard port.

Write to a separate file:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --output-file /tmp/optimized.md
```

Overwrite the source prompt explicitly:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --in-place
```

While the full run is active, open the `dashboard_url` returned by the command, as described in [docs/dashboard.md](dashboard.md). If you need a stable port for forwarding, set `AGL_SERVER_PORT` before starting the run.

## Using The Repository Prompt

The main project prompt is [skills/trainer-optimize/SKILL.md](../skills/trainer-optimize/SKILL.md).

Its authored eval manifest already follows the official structure:

- [skills/trainer-optimize/evals/evals.json](../skills/trainer-optimize/evals/evals.json)

When you want to run APO on the repository prompt, use explicit datasets:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file skills/trainer-optimize/SKILL.md \
  --train-file skills/trainer-optimize/datasets/train.jsonl \
  --val-file skills/trainer-optimize/datasets/val.jsonl
```

You can pass options explicitly when you want to override defaults:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file skills/trainer-optimize/SKILL.md \
  --train-file skills/trainer-optimize/datasets/train.jsonl \
  --val-file skills/trainer-optimize/datasets/val.jsonl \
  --algorithm apo \
  --iterations 3 \
  --judge-mode deterministic
```

## Eval Convention

Authored skill evals follow the Agent Skills article layout:

```text
<prompt-dir>/evals/evals.json
<prompt-dir>/evals/files/
<prompt-dir>/.trainer-workspace/<prompt-name>/iterations/iteration-N/
```

If you are starting from CSV input for APO, bootstrap explicit datasets with:

```bash
python skills/trainer-optimize/scripts/generate_jsonl.py \
  --prompt-file skills/trainer-optimize/SKILL.md \
  --csv-file examples.csv
```

For the full dataset contract, see [skills/trainer-optimize/references/dataset-format.md](../skills/trainer-optimize/references/dataset-format.md).

## Outputs and Artifacts

Successful optimization runs always return the optimized prompt in JSON/stdout.
Successful debug and full runs also return `dashboard_url`, which points at the active local Agent Lightning dashboard.

Optional writes:

- `--output-file` writes a separate optimized prompt file
- `--in-place` overwrites the source prompt
- `--report-file` writes a JSON report

Prompt binding notes:

- Templates that declare placeholders such as `{input}` render directly from dataset rows.
- Prompt-like files with no placeholders, including agent instruction files, now receive an implicit `Task Context:` block during rollouts so they can be optimized against explicit datasets without changing the source prompt interface.
- `--debug-only` runs a live smoke rollout against the first training row without instantiating APO or VERL, which makes it useful for validating prompt, dataset, and model wiring separately from full optimization.

For authored skill evaluation, the key file is:

- [skills/trainer-optimize/evals/evals.json](../skills/trainer-optimize/evals/evals.json)

The optimizer no longer writes prompt content or reports unless you explicitly request those outputs.

## Interpreting Failed Rollouts

In the Agent Lightning dashboard, a rollout with `status: failed` means the worker hit an exception path. It does not mean the prompt merely earned a `0.0` score.

Check these in order:

1. CLI stderr or any saved `optimize-stderr.txt` for the actual exception.
2. `Traces` in the dashboard for attempt-level detail.
3. Placeholder compatibility between the prompt and dataset.
4. The current `dashboard_url` or `AGL_SERVER_PORT` if the UI is connected to an old server.

## Trace Training

To tune the optimize runtime itself with Microsoft Trace, run the helper on one or more explicit prompt cases:

```bash
python skills/trainer-optimize/scripts/train.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --epochs 2 \
  --report-file /tmp/trace-train-report.json
```

The Trace helper keeps `trainer-optimize` single-shot. It tunes the policy that selects optimize settings and writes a JSON training report only when you request `--report-file`.

## Next Reading

- [docs/dashboard.md](dashboard.md)
- [docs/troubleshooting.md](troubleshooting.md)
- [examples/first-run/README.md](../examples/first-run/README.md)