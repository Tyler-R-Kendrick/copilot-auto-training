# Getting Started

This guide covers installation, model configuration, the first run, and the files written by the optimizer.

## Prerequisites

- Python 3.11 or newer
- A virtual environment for the repository
- Model credentials through either `OPENAI_API_KEY` or GitHub Models configuration in the repository root `.env`

## Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The runtime dependency set includes `poml`, which Agent Lightning APO requires during optimization.

## Configure Model Access

If you are using GitHub Models, create a repository-root `.env` file like this:

```dotenv
GITHUB_MODELS_API_KEY=<github-pat>
GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference
GITHUB_MODELS_GRADIENT_MODEL=openai/gpt-4.1-mini
GITHUB_MODELS_APPLY_EDIT_MODEL=openai/gpt-4.1-mini
```

When these `GITHUB_MODELS_*` values are present, the optimizer treats the repository-root `.env` as the authoritative source for GitHub Models settings.

## Verify the Environment

Run the test suite before starting an optimization run:

```bash
python -m pytest -q
```

## First Run

The smallest runnable example in this repository is documented in [examples/first-run/README.md](../examples/first-run/README.md).

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

While the full run is active, open the dashboard described in [docs/dashboard.md](dashboard.md).

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
<prompt-dir>/<prompt-name>-workspace/iteration-N/
```

If you are starting from CSV input for APO, bootstrap explicit datasets with:

```bash
python skills/trainer-optimize/scripts/generate_jsonl.py \
  --prompt-file skills/trainer-optimize/SKILL.md \
  --csv-file examples.csv
```

For the full dataset contract, see [skills/trainer-optimize/references/dataset-format.md](../skills/trainer-optimize/references/dataset-format.md).

## Outputs and Artifacts

Successful optimization runs write:

- the winning prompt back to the original markdown file
- a report at the explicit `--report-file` path or the runtime default
- runtime artifacts under `<prompt-dir>/<prompt-name>-workspace/`

For authored skill evaluation, the key file is:

- [skills/trainer-optimize/evals/evals.json](../skills/trainer-optimize/evals/evals.json)

The optimizer workspace directory is gitignored and keeps `benchmark.json`, per-run summaries, candidate snapshots, and steering notes.

## Next Reading

- [docs/dashboard.md](dashboard.md)
- [docs/troubleshooting.md](troubleshooting.md)
- [examples/first-run/README.md](../examples/first-run/README.md)