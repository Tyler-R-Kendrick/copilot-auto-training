# Copilot Execution Plan

This repository now supports a Copilot-backed inference path for `trainer-optimize` without requiring model-provider API keys.

## How the current implementation maps to this requested Copilot adapter design

The existing runtime already centers on `skills/trainer-optimize/scripts/run_optimize.py`, `optimize_support.py`, and `train.py`, so the adapter lives there instead of introducing a second root-level training stack.

Implemented equivalents:

- `skills/trainer-optimize/scripts/inference/contract.py`
- `skills/trainer-optimize/scripts/inference/config.py`
- `skills/trainer-optimize/scripts/inference/copilot_provider.py`
- `skills/trainer-optimize/scripts/inference/smoke_test.py`
- `skills/trainer-optimize/scripts/inference/local_adapter_service.py`
- `skills/trainer-optimize/scripts/training/lightning_integration.py`
- `skills/trainer-optimize/scripts/training/trace_logger.py`

## Authentication

Copilot mode is activated with:

```dotenv
INFERENCE_PROVIDER=github_copilot
COPILOT_INFERENCE_MODE=local_cli
COPILOT_MODEL=default
```

The runtime then looks for a signed-in Copilot CLI:

1. `COPILOT_INFERENCE_COMMAND` when explicitly provided
2. a bundled CLI path when `COPILOT_INFERENCE_MODE=bundled_cli`
3. `copilot` on `PATH`

No provider API key fields are used for this mode. If `OPENAI_API_KEY`, `GITHUB_MODELS_API_KEY`, or similar provider secrets are present, the Copilot provider fails fast so the run stays keyless.

## Supported environments

- Local CLI mode: the `copilot` executable is installed and already signed in
- Bundled CLI mode: a repo-managed or external Copilot CLI is supplied through `COPILOT_BUNDLED_CLI_PATH`
- OAuth mode: reserved for signed-in Copilot runtimes that expose the same local CLI contract

## Runtime shape

The current flow is:

```text
run_optimize.py / train.py
  -> config.resolve_model_settings()
  -> config.create_openai_client()
  -> training.lightning_integration.ProviderBackedOpenAIClient
  -> inference.copilot_provider.CopilotInferenceProvider
  -> signed-in Copilot CLI
```

`ProviderBackedOpenAIClient` preserves the minimal OpenAI-compatible methods used by the current optimizer:

- `responses.create(...)`
- `chat.completions.create(...)`
- `judge_score(...)`

That keeps Agent Lightning integration pluggable without changing the optimization logic.

## Session management

- Episode/session IDs can be passed through request metadata.
- The Copilot provider keeps per-session message history.
- Calling `reset_session(session_id)` clears state at episode boundaries.

The existing optimizer mostly uses single-message prompt execution, so session history matters most for future multi-turn integrations and the optional local adapter service.

## Reliability controls

The Copilot provider adds:

- per-request timeout control
- up to 2 retries with exponential backoff
- structured failure logging
- clear authentication/runtime errors

The existing manual-followup response path remains in place for live-inference failures that should degrade gracefully inside `trainer-optimize`.

## Observability

`skills/trainer-optimize/scripts/training/trace_logger.py` emits structured inference logs with:

- `training_run_id`
- `episode_id`
- `step_id`
- `latency_ms`
- `model_name`
- `response_length`
- `timestamp`

The logger omits prompt bodies and response text to avoid leaking sensitive content into logs.

## Smoke test

Run the direct provider smoke test:

```bash
python skills/trainer-optimize/scripts/inference/smoke_test.py --model default
```

Run the optimizer smoke test:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --debug-only
```

## Optional local adapter service

If a local OpenAI-compatible endpoint is required, start:

```bash
python skills/trainer-optimize/scripts/inference/local_adapter_service.py --port 8787
```

It exposes:

- `POST /v1/chat/completions`

and forwards requests into the same Copilot-backed provider.

## Current limitations

- The repository does not bundle a Copilot CLI binary; local or bundled runtime setup is still required.
- The exact CLI command can vary by environment, so `COPILOT_INFERENCE_COMMAND` is the escape hatch when the default `copilot chat --json --stdio` contract is not correct.
- Legacy OpenAI and GitHub Models support remains in the repo for backward compatibility; Copilot mode is the keyless path, not a destructive removal of the old providers.

## Future provider switching

Provider selection still flows through `skills/trainer-optimize/scripts/config.py`, so future providers can be added behind the same interface without changing the optimization loop itself.
