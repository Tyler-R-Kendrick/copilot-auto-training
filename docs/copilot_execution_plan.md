# Copilot Execution Plan

This repository uses GitHub Copilot for `trainer-optimize` inference.

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

## Configuration

Set the repository root `.env` like this:

```dotenv
COPILOT_MODEL=default
```

The runtime initializes the Python Copilot SDK and uses the logged-in Copilot user session managed by that SDK.

## Supported environments

- The Python Copilot SDK can reach the signed-in Copilot runtime for the current user

## Runtime shape

The current flow is:

```text
run_optimize.py / train.py
  -> config.resolve_model_settings()
  -> config.create_openai_client()
  -> training.lightning_integration.ProviderBackedOpenAIClient
  -> inference.copilot_provider.CopilotInferenceProvider
  -> GitHub Copilot SDK
  -> signed-in Copilot session
```

`ProviderBackedOpenAIClient` preserves the minimal OpenAI-compatible methods used by the current optimizer:

- `responses.create(...)`
- `chat.completions.create(...)`
- `judge_score(...)`

That keeps Agent Lightning integration pluggable without changing the optimization logic.

## Session management

- Episode/session IDs can be passed through request metadata.
- The Copilot provider keeps one SDK session per episode/session ID.
- Calling `reset_session(session_id)` clears state at episode boundaries.

The existing optimizer mostly uses single-message prompt execution, so the SDK session mapping matters most for future multi-turn integrations and the optional local adapter service.

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

Run the direct smoke test:

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

If a local HTTP interface is required, start:

```bash
python skills/trainer-optimize/scripts/inference/local_adapter_service.py --port 8787
```

It exposes:

- `POST /v1/chat/completions`

and forwards requests into the same Copilot runtime.

## Current limitations

- The implementation depends on `github-copilot-sdk` and assumes the signed-in Copilot runtime that the SDK talks to is available.
- The SDK still depends on the logged-in Copilot user session, so environments without that session will fail fast.
