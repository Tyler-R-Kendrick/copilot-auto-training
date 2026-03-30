# Optimize Blocker: judge-rubric

## Outcome

- `trainer-optimize` was invoked through the MCP skill runner with explicit `train.jsonl` and `val.jsonl` inputs.
- The run used `judge_mode=llm_judge`, `iterations=3`, `beam_width=1`, `branch_factor=1`, and `n_runners=1`.
- Agent Lightning started successfully and the dashboard server became healthy.
- No optimized prompt candidate was produced.

## Blocker

- GitHub Models returned `openai.RateLimitError: Too many requests` during both rollout execution and APO critique generation.
- The failure occurred before the optimizer could write `optimized-prompt.md` or `optimize-report.json`.

## Evidence

- The MCP optimize run exited with code `1` after repeated `RateLimitError` failures.
- The failure stack came from live chat-completions requests rather than prompt-schema or dataset-shape validation.
- The synthesized datasets were accepted far enough for Agent Lightning to launch, which rules out missing-file or judge-mode mismatch as the primary blocker.

## Decision

- Treat this as a runtime availability blocker, not as evidence that the current prompt scored poorly.
- Keep `skills/judge-rubric/SKILL.md` unchanged for this trainer pass.