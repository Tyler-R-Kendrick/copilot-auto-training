# copilot-training

Reference implementation and reusable workflow for optimizing prompt-like markdown files with Agent Lightning, official `evals/evals.json` manifests, and an operator-facing trainer toolchain.

## Best Use

Use this project when you need to:

- optimize your prompts
- optimize your agent-skills
- optimize your agent instuctions (AGENTS.md, copilot-instructions.md. CLAUDE.md, etc)
- enable automatic optimization in a loop or on a schedule.

## What The Repo Provides

### Agents

The repo uses multiple agents that can be invoked as custom agents or subagents for the goal of running self-improvement loops on prompts. These agents adhere to the Copilot Custom Agents standard.

#### Trainer Agent

The trainer agent coordinates state-of-the-art self-improvement loops with the other agents to produce optimized prompts.

#### Judge Agent

The judge implements the current state-of-the-art techniques to judge, grade, and score responses using dynamic metrics and rubrics.
The one exception is that the judge explicitly considers token usage as a metric for optimization, making sure to minimize tokens whilst not degrading performance.

#### Conservator Agent

The conservator inspects the training history and repo documentation to ensure we don't introduce regressions or repeat previous failures

#### Engineer Agent

The engineer applies state-of-the-art practices from prompt engineering and context engineering to guide and steer prompt optimization.

### Skills

The repo exposes multiple skills to enhance the capabilities of each of the agents. For each agent, there are multiple skills implemented as agent-skills to support them.

#### Trainer Skills
- `trainer-optimize`: Runs Agent-Lightning optimization with APO or VERL
- `trainer-election`: Creates multiple candidates with leader election.
- `trainer-research`: Researches sources to use training data, test data, rubric generation, and data synthesis. 
- `trainer-synthesize`: Generates new data from existing data.

#### Judge Skills
- `judge-rubric`: Creates a rubric for given dimensions to optimize against.
- `judge-trajectory`: Evaluates the trajectory and provides steering recommendations.
- `judge-outcome`: Evaluates the outcome and provides steering recommendations.

#### Engineer Skills
- `engineer-prompt`: Applies prompt-engineering best practices to the prompt as suggestions.

### GitHub Agentic Workflows

We expose a single `train-prompt` agentic workflow to run these capabilities automatically.
The workflow searches for and triages prompts that should be optimized against a repo.

### Plugins

We expose all capabilities in this repo as a single plugin.

### MCP servers

#### agent-skills

In order to make agent-skills available to tool discovery, we created an MCP server that exposes agent-skills to built-in discovery for GitHub Copilot.

## Ways To Use It

### Using it as a GitHub Copilot Local Agentic Workflow

Use the reusable workflow when another repository already stores prompt-like markdown in git and you want scheduled or manual optimization runs that produce reviewable pull requests.

Prerequisites for the target repository:

- GitHub Agentic Workflows is initialized with `gh aw init`
- `COPILOT_GITHUB_TOKEN` is configured for the chosen engine
- the repository contains prompt-like markdown files the workflow can select
- `python -m pytest -q` is the correct repository validation command, or the imported workflow is adjusted to the repository's validation command and recompiled

Install the workflow with an explicit path:

```bash
gh aw add Tyler-R-Kendrick/copilot-apo/.github/workflows/train-prompt.md --name train-prompt
```

Update it later with:

```bash
gh aw update train-prompt
```

The imported workflow will:

- select exactly one prompt-like file
- create or update that file's local `.trainer-workspace/<prompt-name>/`
- use packaged `trainer-research`, `trainer-synthesize`, `trainer-optimize`, and `trainer-election` skills from this repository through a bundled MCP server runtime
- open a pull request only when the optimization produced a meaningful diff and `python -m pytest -q` passed

The workflow source lives in [`.github/workflows/train-prompt.md`](.github/workflows/train-prompt.md). Frontmatter changes require recompiling it with `gh aw compile train-prompt`.

### Using it as a Repository Template

Fork the repository and use it when creating a repository.

### Using it locally

Use the local scripts when you are iterating on a prompt in this repository, or when you want full control over datasets, iterations, and validation. Simply clone it and run locally.
Tell Copilot to: `run @trainer on #<prompt-name>.`

### 2. Using it as a GitHub Copilot Plugin

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

### Using it as a GitHub Copilot Cross-Repo Agentic Workflow

Use it locally as either a repo template or a locally cloned copy.
Then, follow the documention [here](https://github.github.com/gh-aw/reference/cross-repository/) to point it to the repos you want to optimize.

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

Inside the devcontainer, `.devcontainer/post-start.sh` now repairs or recreates `.venv` with Python 3.12 and installs `requirements.txt` automatically when the environment is missing, stale, or broken. The Copilot coding-agent bootstrap workflow at `.github/workflows/copilot-setup-steps.yml` reuses that same script so the hosted agent gets the repository's shared setup, plus `gh aw`.

## Quick Start

Run the smallest example in this repository:

```bash
run @trainer on #:examples/first-run/prompts/classify_support.md \
  --debug-only
```

Run a small optimization pass:

```bash
run @trainer on #:examples/first-run/prompts/classify_support.md \
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
