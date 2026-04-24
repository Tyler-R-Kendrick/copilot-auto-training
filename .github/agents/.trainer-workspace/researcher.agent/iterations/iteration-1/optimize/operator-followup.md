# Operator Follow-up: manual_followup Optimize Pass

## Blocker

`trainer-optimize` returned `mode=manual_followup` because the external model endpoint was unavailable.

**Blocker reason:** Session error: Execution failed: Error: Session was not created with authentication info or custom provider

## Agent Handoff Summary

The current `@trainer` agent answered the `model_prompt` from the `manual-followup-report.json` by:

1. Reading the baseline prompt (`researcher.agent.md`) and the training/validation datasets.
2. Applying the improvements identified in the `engineer-prompt/review.md`:
   - Added explicit evidence reading order (target file → task description → scoring rule → constraints).
   - Added elicitation step: ask for missing constraints before searching.
   - Added explicit fallback path when no `scripts/` helper is available from the MCP skill.
   - Added a compact source approval bar section directly in the agent.
   - Added a named blocker-report format to the output section.
   - Improved the `argument-hint` to distinguish required from optional inputs.
3. Saved the revised prompt as `optimized-prompt.md`.

## Artifacts

- `manual-followup-report.json` — full report from trainer-optimize
- `optimized-prompt.md` — agent-authored optimized candidate

## Optional Rerun Command

```
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 --algorithm apo --beam-width 4 --branch-factor 4 --n-runners 4 --judge-mode llm_judge
```
