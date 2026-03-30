# copilot-training

Reference implementation and reusable workflow for optimizing prompt-like markdown files with Agent Lightning, official `evals/evals.json` manifests, and an operator-facing trainer toolchain.

## Best Use

Use this project when you need to:

- optimize checked-in prompt-like files such as `SKILL.md`, `AGENTS.md`, `*.prompt.md`, `*.instructions.md`, and `.prompty`
- keep authored eval cases plus explicit `train.jsonl` and `val.jsonl` datasets under version control
- run one target at a time with artifacts stored next to the prompt in a local `.trainer-workspace/<prompt-name>/`
- gate prompt updates on deterministic repository validation before opening a pull request

This project is not the right fit when you need to:

- optimize general application code instead of prompt-like markdown
- guess missing datasets at runtime instead of researching or synthesizing them first
- fold leader election into `trainer-optimize`; multi-candidate selection belongs in `trainer-election`

## What The Repo Provides

This repository shows how to keep authored skill evaluation cases aligned with the Agent Skills guidance while still running APO against explicit datasets:

- prompts stay in markdown
- authored eval cases live under `evals/evals.json`
- supporting eval assets live under `evals/files/`
- optimization datasets can be passed explicitly when APO needs `train.jsonl` and `val.jsonl`
- Agent Lightning exposes a local dashboard while runs are active

The main example in this repository is the [trainer-optimize skill](skills/trainer-optimize/SKILL.md), backed by the runtime in [skills/trainer-optimize/scripts/run_optimize.py](skills/trainer-optimize/scripts/run_optimize.py).

## Ways To Use It

### 1. Run It Locally

Use the local scripts when you are iterating on a prompt in this repository, or when you want full control over datasets, iterations, and validation.

### 2. Install Copilot CLI Plugins From This Repo

Use the plugin marketplace when you want these skills available inside Copilot CLI without copying files by hand.

Register the marketplace:

```bash
copilot plugin marketplace add Tyler-R-Kendrick/copilot-apo
```

Install the published plugin:

```bash
copilot plugin install copilot-training@copilot-training
```

If you prefer a direct repository import instead of marketplace registration, install from the subdirectory path:

```bash
copilot plugin install Tyler-R-Kendrick/copilot-apo:plugins/copilot-training
```

The installable plugin bundles live under `plugins/`, and the marketplace manifest lives at `.github/plugin/marketplace.json`.
For the full import flow, see [docs/copilot-cli-plugins.md](docs/copilot-cli-plugins.md).

### 3. Import The Workflow Into Another Repo

Use the reusable workflow when another repository already stores prompt-like markdown in git and you want scheduled or manual optimization runs that produce reviewable pull requests.

Prerequisites for the target repository:

- GitHub Agentic Workflows is initialized with `gh aw init`
- `COPILOT_GITHUB_TOKEN` is configured for the chosen engine
- the repository contains prompt-like markdown files the workflow can select
- `python -m pytest -q` is the correct repository validation command, or the imported workflow is adjusted to the repository's validation command and recompiled

Install the workflow with an explicit path:

```bash
gh aw add Tyler-R-Kendrick/copilot-apo/.github/workflows/optimize-next-prompt.md --name optimize-next-prompt
```

Update it later with:

```bash
gh aw update optimize-next-prompt
```

The imported workflow will:

- select exactly one prompt-like file
- create or update that file's local `.trainer-workspace/<prompt-name>/`
- use packaged `trainer-research`, `trainer-synthesize`, `trainer-optimize`, and `trainer-election` skills from this repository through a bundled MCP server runtime
- open a pull request only when the optimization produced a meaningful diff and `python -m pytest -q` passed

The workflow source lives in [`.github/workflows/optimize-next-prompt.md`](.github/workflows/optimize-next-prompt.md). Frontmatter changes require recompiling it with `gh aw compile optimize-next-prompt`.

## Features

- Agent Lightning optimization with `apo` and `verl`
- Official `evals/evals.json` authored-eval layout
- Explicit dataset inputs for APO runs
- Workspace-based reports, candidate snapshots, and steering artifacts inside the optimizer runtime
- GitHub Models support through a repository-root `.env`
- A small copy-paste example under [examples/first-run](examples/first-run/README.md)
- Tested behavior for config resolution, artifact writing, and optimization flow
- A reusable GitHub Agentic Workflow that packages its trainer skill runtime for downstream repositories
- A Copilot CLI plugin marketplace that publishes installable skill bundles from this repository

## Requirements

- Python 3.11+
- Dependencies from [requirements.txt](requirements.txt)
- Model credentials via `OPENAI_API_KEY` or the GitHub Models variables documented in [docs/getting-started.md](docs/getting-started.md)

## Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Inside the devcontainer, `.devcontainer/post-start.sh` now repairs or recreates `.venv` with Python 3.12 and installs `requirements.txt` automatically when the environment is missing, stale, or broken.

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
- [docs/copilot-cli-plugins.md](docs/copilot-cli-plugins.md): how to register this repo as a Copilot CLI marketplace and install its plugins
- [docs/dashboard.md](docs/dashboard.md): how to open and use the Agent Lightning dashboard
- [docs/troubleshooting.md](docs/troubleshooting.md): common setup, dataset, runtime, and dashboard issues
- [examples/first-run/README.md](examples/first-run/README.md): smallest runnable example in the repo
- [skills/trainer-optimize/SKILL.md](skills/trainer-optimize/SKILL.md): skill contract and operator instructions
- [skills/trainer-optimize/references/dataset-format.md](skills/trainer-optimize/references/dataset-format.md): dataset schema and scoring guidance

## Repository Layout

```text
docs/
plugins/
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

Skill layout:

- `skills/`, `.agents/skills/`, and `.claude/skills/` are the canonical in-repo skill roots.
- `plugins/copilot-training/` is the single installable Copilot CLI plugin for this repo; its `skills/`, `agents/`, `hooks/`, and `mcps/` entries symlink back to the canonical repo sources rather than copying them.
- `.agents/skills/` is the managed symlink mirror maintained by [`.github/hooks/sync-skill-links.py`](.github/hooks/sync-skill-links.py) so the repo does not keep copied skill directories.
- The helper can also link skills from `~/skills` and `~/.agents/skills` into `.agents/skills/` when those home-level roots exist.
- Local home-skill symlinks created by the watcher are ignored by [`.agents/skills/.gitignore`](.agents/skills/.gitignore) so they do not dirty the repository.
- Use `python .github/hooks/sync-skill-links.py --check` to verify that `.agents/skills/` exactly matches the discovered skill roots.
- The launcher at [`.github/hooks/ensure-skill-link-watcher.sh`](.github/hooks/ensure-skill-link-watcher.sh) performs an immediate sync and starts a background watcher so future additions to `~/skills` and `~/.agents/skills` are linked automatically during the session.
- The write-time hook in [`.github/hooks/prompt-workflow-reminder.json`](.github/hooks/prompt-workflow-reminder.json) starts that launcher automatically after file edits.

The repository currently ships official eval manifests for [skills/trainer-optimize/SKILL.md](skills/trainer-optimize/SKILL.md) and a smaller onboarding example under [examples/first-run](examples/first-run/README.md).

## License

This project is licensed under the terms of the [LICENSE](LICENSE) file.
