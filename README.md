# copilot-apo

Reference implementation for optimizing markdown prompt files with Agent Lightning, official `evals/evals.json` skill-eval manifests, and an operator-facing `trainer-optimize` skill.

## Overview

This repository shows how to keep authored skill evaluation cases aligned with the Agent Skills guidance while still running APO against explicit datasets:

- prompts stay in markdown
- authored eval cases live under `evals/evals.json`
- supporting eval assets live under `evals/files/`
- optimization datasets can be passed explicitly when APO needs `train.jsonl` and `val.jsonl`
- Agent Lightning exposes a local dashboard while runs are active

The main example in this repository is the [trainer-optimize skill](skills/trainer-optimize/SKILL.md), backed by the runtime in [skills/trainer-optimize/scripts/run_optimize.py](skills/trainer-optimize/scripts/run_optimize.py).

## Features

- Agent Lightning optimization with `apo` and `verl`
- Official `evals/evals.json` authored-eval layout
- Explicit dataset inputs for APO runs
- Workspace-based reports, candidate snapshots, and steering artifacts inside the optimizer runtime
- GitHub Models support through a repository-root `.env`
- A small copy-paste example under [examples/first-run](examples/first-run/README.md)
- Tested behavior for config resolution, artifact writing, and optimization flow

## Requirements

- Python 3.11+
- Dependencies from [requirements.txt](requirements.txt)
- Model credentials via `OPENAI_API_KEY` or the GitHub Models variables documented in [docs/getting-started.md](docs/getting-started.md)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

Run the test suite:

```bash
python -m pytest -q
```

Run the smallest example in this repository:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --debug-only
```

Run a small optimization pass:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

For the full setup, configuration, and artifact walkthrough, start with [docs/getting-started.md](docs/getting-started.md).

## Documentation

- [docs/getting-started.md](docs/getting-started.md): installation, configuration, examples, and outputs
- [docs/dashboard.md](docs/dashboard.md): how to open and use the Agent Lightning dashboard
- [docs/troubleshooting.md](docs/troubleshooting.md): common setup, dataset, runtime, and dashboard issues
- [examples/first-run/README.md](examples/first-run/README.md): smallest runnable example in the repo
- [skills/trainer-optimize/SKILL.md](skills/trainer-optimize/SKILL.md): skill contract and operator instructions
- [skills/trainer-optimize/references/dataset-format.md](skills/trainer-optimize/references/dataset-format.md): dataset schema and scoring guidance

## Repository Layout

```text
docs/
examples/
  first-run/
skills/trainer-optimize/
  assets/
  references/
  scripts/
tests/
README.md
requirements.txt
```

## Development

Key entry points:

- [skills/trainer-optimize/scripts/run_optimize.py](skills/trainer-optimize/scripts/run_optimize.py): optimization runtime
- [skills/trainer-optimize/scripts/generate_jsonl.py](skills/trainer-optimize/scripts/generate_jsonl.py): CSV-to-JSONL dataset bootstrapper
- [tests/test_run_optimize.py](tests/test_run_optimize.py): end-to-end behavior coverage

The repository currently ships official eval manifests for [skills/trainer-optimize/SKILL.md](skills/trainer-optimize/SKILL.md) and a smaller onboarding example under [examples/first-run](examples/first-run/README.md).

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
