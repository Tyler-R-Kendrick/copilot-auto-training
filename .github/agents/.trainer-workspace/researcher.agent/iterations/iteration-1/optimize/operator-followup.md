# Operator Follow-up Note

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no external inference model was configured in the repository `.env` file. The `COPILOT_MODEL` setting was absent or unreachable during the optimization run.

## Agent Handoff Summary

The current `@trainer` agent completed the optimize stage by:

1. Reading the `model_prompt` from `manual-followup-report.json`.
2. Drafting a revised candidate prompt addressing the six issues identified in `engineer-prompt/review.md`:
   - Added Input Reading Checklist with explicit stop criteria for missing task description and scoring rule.
   - Added MCP fallback blocker path when `find_agent_skill` or `load_agent_skill` fails.
   - Inlined the source approval bar into the agent prompt body.
   - Expanded stopping rule to name which missing inputs require a blocker vs. which can be noted and continued.
   - Expanded output format with minimum structure requirements for mapping notes and unresolved gaps.
   - Clarified `run_agent_skill` conditions: when skill provides guidance only, use loaded instructions instead of calling `run_agent_skill`.
3. Saved the candidate as `optimized-prompt.md` in this optimize directory.

## Rerun Command

To rerun with a live model after configuring `COPILOT_MODEL` in `.env`:

```
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --beam-width 4 \
  --branch-factor 4 \
  --n-runners 4 \
  --judge-mode llm_judge
```
