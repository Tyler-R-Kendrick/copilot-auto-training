# Troubleshooting

This page collects the most common setup, dataset, runtime, and dashboard issues.

## Setup Issues

- If you see `ModuleNotFoundError: No module named 'poml'`, reinstall dependencies with `pip install -r requirements.txt`.
- If you see `GitHub Models configuration requires GITHUB_MODELS_API_KEY or OPENAI_API_KEY`, add a valid repository-root `.env` before running optimization.
- If `python -m pytest -q` fails immediately on async tests, make sure you installed all dependencies from [requirements.txt](../requirements.txt).

## Dataset Issues

- If you are authoring skill eval cases, verify that `evals/evals.json` exists next to the prompt or skill and that any referenced assets live under `evals/files/`.
- If the optimizer cannot resolve dataset files, pass explicit `--train-file` and `--val-file` paths and verify the files actually exist.
- If you only have CSV input, generate explicit datasets with [skills/trainer-optimize/scripts/generate_jsonl.py](../skills/trainer-optimize/scripts/generate_jsonl.py).
- If placeholder validation fails, compare the markdown template placeholders with the dataset row keys and keep evaluator-only fields out of the prompt rendering path.
- If the prompt contains literal JSON or other brace-heavy examples, keep them literal or escaped. They should not create new placeholders unless they intentionally match the prompt interface.
- If the prompt has no placeholders at all, the runtime will append an implicit `Task Context:` block during rollouts. Use explicit placeholders only when you need tighter control over where row fields land in the rendered prompt.

## Runtime Issues

- If the optimizer appears stuck during startup, wait for the local Uvicorn server to finish booting before refreshing the dashboard.
- If the run completes but trainer workflow artifacts are missing, check the explicit report path you passed or the local `<prompt-dir>/.trainer-workspace/<prompt-name>/benchmark.json` rollup when that workflow generated benchmark artifacts.
- If you used `--debug-only`, the optimizer intentionally skips writing the optimized prompt and temporary run artifacts. It now runs a single live smoke rollout against the first training row, so failures in that mode usually point to prompt rendering, model access, or judge configuration rather than APO or VERL internals.
- If a rollout is marked `failed`, treat that as an exception path rather than a poor score. Check CLI stderr, saved `optimize-stderr.txt`, and dashboard traces first.
- If you see `404 page not found` from `responses.create` on GitHub Models, that is an endpoint/API compatibility problem. Use a runtime version that falls back to chat completions automatically, or verify the configured endpoint.
- If the dashboard URL changes between runs, use the returned `dashboard_url` from the JSON result or report file. The runtime now chooses a free local port unless `AGL_SERVER_PORT` is set explicitly.
- If a full `verl` run fails at import time with `ModuleNotFoundError: No module named 'hydra'`, reinstall dependencies from [requirements.txt](../requirements.txt) so the VERL runtime extras are available.

## Dashboard Issues

- If the dashboard does not load, confirm that an optimization run is currently active and open the current `dashboard_url` returned by the runtime.
- If the dashboard loads but shows `Offline`, open `Settings` and verify the backend base URL still points to the current `dashboard_url` rather than an older fixed port.
- If the dashboard is empty, confirm the optimization process is still running in another terminal.
- If you are in Codespaces or another remote container, verify that the active dashboard port is forwarded and reachable from your browser session.
- If the port is already busy because you pinned `AGL_SERVER_PORT`, stop the older run or choose a different port before starting a new one.

## More Context

- [docs/getting-started.md](getting-started.md)
- [docs/dashboard.md](dashboard.md)
- [skills/trainer-optimize/references/dataset-format.md](../skills/trainer-optimize/references/dataset-format.md)