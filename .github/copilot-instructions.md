# Project Guidelines

## Build and Test

- Use the repository virtual environment for Python commands: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
- Run `python -m pytest -q` before finishing meaningful changes.
- For `trainer-optimize` smoke tests, pass explicit `--prompt-file`, `--train-file`, and `--val-file` arguments and start with `--debug-only`. See [docs/getting-started.md](../docs/getting-started.md) and [examples/first-run/README.md](../examples/first-run/README.md).

## Architecture

- Keep spec-owned content and runtime code separate: skill contracts live in `skills/*/SKILL.md`, authored evals live in adjacent `evals/evals.json`, and executable code belongs under `skills/*/scripts/`.
- `trainer-optimize` is a single-shot optimizer. Do not fold leader election or baseline comparison into that runtime; use `trainer-election` only as a separate step when a workflow explicitly compares multiple optimize outputs.
- The local MCP server lives under `tools/agent-skills-mcp` and reloads skill content from disk on each tool call.

## Conventions

- When editing prompt-like files, agents, or instruction files, follow [instructions/prompt-optimization.instructions.md](instructions/prompt-optimization.instructions.md). When editing authored eval manifests, follow [instructions/evals-dataset.instructions.md](instructions/evals-dataset.instructions.md).
- Preserve prompt placeholders and keep evaluator-only fields out of prompt-visible render paths.
- `trainer-optimize` requires explicit `train.jsonl` and `val.jsonl` inputs; do not infer or synthesize missing datasets at runtime. Use [README.md](../README.md), [docs/troubleshooting.md](../docs/troubleshooting.md), and [docs/dashboard.md](../docs/dashboard.md) for repository-wide context instead of duplicating those details here.
- Optimization runs require model credentials from the repository root `.env`; start from [/.env.sample](../.env.sample) when you need the supported variables.