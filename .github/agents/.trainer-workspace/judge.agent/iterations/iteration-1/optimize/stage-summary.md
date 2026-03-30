# Optimize Stage Summary

## Selected Judge Mode

- `judge_mode=llm_judge`
- Reason: the synthesized dataset rows use `reference`, `criteria`, and `scoring: "llm_judge"`.

## Prompt Preflight

- The target file is a subagent instruction file with no task-input placeholders.
- The current `trainer-optimize` runtime renders task rows only through prompt placeholders.
- That means the runtime can validate the file, but it cannot inject row-specific judging tasks into the rendered prompt text for a meaningful APO pass.

## MCP Runtime Attempts

1. `trainer-optimize` with `--debug-only --judge-mode llm_judge --algorithm apo`
   - Result: failed before any useful scoring.
   - Runtime exception: `Trainer.dev() requires an algorithm that inherits from FastAlgorithm. Received APO.`

2. `trainer-optimize` with `--debug-only --judge-mode llm_judge --algorithm verl`
   - Result: failed during import.
   - Runtime exception: `ModuleNotFoundError: No module named 'hydra'`.

## Decision

- Optimization did not execute meaningfully for this iteration.
- The prompt rewrite applied to `judge.agent.md` is therefore a manual optimization informed by the engineer review, the local judging reference, and the synthesized `llm_judge` datasets.
- A fuller optimize run needs both of these fixes:
  - an input-aware wrapper or runtime path that can feed per-row task content into the judge prompt,
  - a working debug or normal optimize environment for the requested algorithm.