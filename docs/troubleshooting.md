# Troubleshooting

This page collects the most common setup, dataset, runtime, and dashboard issues.

## Setup Issues

- If you see `ModuleNotFoundError: No module named 'poml'`, reinstall dependencies with `pip install -r requirements.txt`.
- If you see `GitHub Models configuration requires GITHUB_MODELS_API_KEY or OPENAI_API_KEY`, add a valid repository-root `.env` before running optimization.
- If `python -m pytest -q` fails immediately on async tests, make sure you installed all dependencies from [requirements.txt](../requirements.txt).

## Dataset Issues

- If the optimizer cannot resolve dataset files, verify that `train.jsonl` and `val.jsonl` exist under `.evals/<prompt-name>/` next to the prompt file.
- If you only have CSV input, generate prompt-local datasets with [skills/trainer-optimize/scripts/generate_jsonl.py](../skills/trainer-optimize/scripts/generate_jsonl.py).
- If placeholder validation fails, compare the markdown template placeholders with the dataset row keys and keep evaluator-only fields out of the prompt rendering path.

## Runtime Issues

- If the optimizer appears stuck during startup, wait for the local Uvicorn server to finish booting before refreshing the dashboard.
- If the run completes but prompt-local artifacts are missing, check `.evals/<prompt-name>/report.json` and `.evals/<prompt-name>/.tmp/` next to the prompt.
- If you used `--debug-only`, the optimizer intentionally skips writing the optimized prompt and temporary run artifacts.

## Dashboard Issues

- If `http://localhost:4747` does not load, confirm that an optimization run is currently active.
- If the dashboard loads but shows `Offline`, open `Settings` and verify the backend base URL still points to `http://localhost:4747`.
- If the dashboard is empty, confirm the optimization process is still running in another terminal.
- If you are in Codespaces or another remote container, verify that port `4747` is forwarded and reachable from your browser session.
- If the port is already busy, stop the older run before starting a new one.

## More Context

- [docs/getting-started.md](getting-started.md)
- [docs/dashboard.md](dashboard.md)
- [skills/trainer-optimize/references/dataset-format.md](../skills/trainer-optimize/references/dataset-format.md)