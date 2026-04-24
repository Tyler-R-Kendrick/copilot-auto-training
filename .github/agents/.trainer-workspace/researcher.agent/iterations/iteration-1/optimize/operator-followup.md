# Operator Followup: manual_followup Optimize Stage

## Blocker

The `opto` module is not installed in this environment. The `trainer-optimize` runtime returned `mode=manual_followup` because it could not reach the Agent Lightning APO runtime.

## Resolution

The current `@trainer` agent answered the `model_prompt` from the `manual-followup-report.json` payload directly and saved the result as `optimized-prompt.md` in this same directory.

## Artifacts

- `manual-followup-report.json` — the deterministic preparation result from the optimize runtime
- `optimized-prompt.md` — the agent-generated optimized candidate for `researcher.agent.md`

## Rerun Command

```
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 --algorithm apo --beam-width 4 --branch-factor 4 --n-runners 4 \
  --judge-mode llm_judge
```

Run this command after installing `agentlightning` and `opto` (and configuring `COPILOT_MODEL` in `.env`) for a fully automated model-backed pass.
