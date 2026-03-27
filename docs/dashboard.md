# Dashboard Guide

Agent Lightning starts a local dashboard server during active optimization runs.

## URLs

- Dashboard root: `http://localhost:4747`
- Health endpoint: `http://localhost:4747/v1/agl/health`

The dashboard is mounted at the server root rather than under `/v1/`.

## Open the Dashboard

Start an optimization run in one terminal:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file skills/optimize/SKILL.md
```

Open the dashboard from the dev container:

```bash
$BROWSER http://localhost:4747
```

If you are using VS Code remote development or Codespaces, you can also open the forwarded port from the browser UI.

## Recommended Workflow

```mermaid
flowchart LR
  A[Start an optimization run] --> B[Open http://localhost:4747]
  B --> C[Rollouts]
  C --> D[Inspect the active rollout]
  D --> E[Open Traces for span-level detail]
  D --> F[Open Resources for prompt versions]
  B --> G[Open Runners to check worker health]
  B --> H[Open Settings to verify base URL and refresh]
```

Use the dashboard in this order:

1. Open `Rollouts` to confirm the run exists and is progressing.
2. Open `Runners` if the run looks stuck and verify workers are alive.
3. Open `Traces` to inspect detailed spans for a rollout or attempt.
4. Open `Resources` to inspect prompt and resource snapshots tied to the run.
5. Open `Settings` if the UI shows `Offline` and verify the backend base URL.

## Available Pages

- `Rollouts`: high-level optimization executions and attempts
- `Resources`: prompt and resource versions tracked by the run
- `Traces`: span-level execution detail for rollouts and attempts
- `Runners`: worker and runner status
- `Settings`: backend base URL, refresh interval, and theme

## Screenshot Checklist

For documentation, issues, or pull requests, these views are the most useful capture sequence:

1. `Rollouts` showing an active optimization run
2. `Resources` showing the prompt or resource versions for that run
3. `Traces` filtered to a rollout or attempt
4. `Runners` showing worker health
5. `Settings` showing the backend base URL and refresh interval

## Related Docs

- [docs/getting-started.md](getting-started.md)
- [docs/troubleshooting.md](troubleshooting.md)