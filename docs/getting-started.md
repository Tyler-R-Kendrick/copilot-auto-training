# Getting Started

This guide covers installation, model configuration, the first run, and the optimizer's output modes.

## Prerequisites

- Python 3.11 or newer
- A virtual environment for the repository
- Model credentials through either `OPENAI_API_KEY` or GitHub Models configuration in the repository root `.env`
- A model name through `OPENAI_MODEL` or `GITHUB_MODELS_MODEL`

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

Start from [/.env.sample](/workspaces/copilot-apo/.env.sample) so the supported secret and model keys stay documented in one place.

When these `GITHUB_MODELS_*` values are present, the optimizer treats the repository-root `.env` as the authoritative source for GitHub Models settings.

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

Successful optimization runs always return the optimized prompt in JSON/stdout.

Optional writes:

- `--output-file` writes a separate optimized prompt file
- `--in-place` overwrites the source prompt
- `--report-file` writes a JSON report

For authored skill evaluation, the key file is:

- [skills/trainer-optimize/evals/evals.json](../skills/trainer-optimize/evals/evals.json)

The optimizer no longer writes prompt content or reports unless you explicitly request those outputs.

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