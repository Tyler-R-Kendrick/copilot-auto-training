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
python skills/optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --debug-only
```

Small full run:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

While the full run is active, open the dashboard described in [docs/dashboard.md](dashboard.md).

## Using the Repository Prompt

The main project prompt is [skills/optimize/SKILL.md](../skills/optimize/SKILL.md).

Its prompt-adjacent datasets are already present:

- [skills/optimize/.evals/SKILL/train.jsonl](../skills/optimize/.evals/SKILL/train.jsonl)
- [skills/optimize/.evals/SKILL/val.jsonl](../skills/optimize/.evals/SKILL/val.jsonl)

Run optimization from the repository root:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file skills/optimize/SKILL.md
```

You can pass options explicitly when you want to override defaults:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file skills/optimize/SKILL.md \
  --algorithm apo \
  --iterations 3 \
  --judge-mode deterministic
```

## Dataset Convention

Prompt-local datasets live under this layout:

```text
<prompt-dir>/.evals/<prompt-name>/train.jsonl
<prompt-dir>/.evals/<prompt-name>/val.jsonl
```

If you are starting from CSV input, bootstrap prompt-local datasets with:

```bash
python skills/optimize/scripts/generate_jsonl.py \
  --prompt-file skills/optimize/SKILL.md \
  --csv-file examples.csv
```

For the full dataset contract, see [skills/optimize/references/dataset-format.md](../skills/optimize/references/dataset-format.md).

## Outputs and Artifacts

Successful optimization runs write:

- the winning prompt back to the original markdown file
- a prompt-local report at `.evals/<prompt-name>/report.json`
- run artifacts under `.evals/<prompt-name>/.tmp/`

For the repository prompt, useful artifact locations include:

- [skills/optimize/.evals/SKILL/datasets.json](../skills/optimize/.evals/SKILL/datasets.json)
- [skills/optimize/.evals/SKILL/README.md](../skills/optimize/.evals/SKILL/README.md)

The `.tmp/` directory is gitignored and keeps per-run summaries, candidate snapshots, and steering notes.

## Next Reading

- [docs/dashboard.md](dashboard.md)
- [docs/troubleshooting.md](troubleshooting.md)
- [examples/first-run/README.md](../examples/first-run/README.md)