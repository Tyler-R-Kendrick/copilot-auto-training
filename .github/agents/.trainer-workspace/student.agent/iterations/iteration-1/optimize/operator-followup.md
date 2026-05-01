# Operator Follow-up

## Blocker

External model credentials were not available in this environment. The `trainer-optimize` runtime returned `mode=manual_followup` because it could not reach the inference endpoint.

## Agent Handoff Summary

The `@trainer` agent answered the `model_prompt` from `manual-followup-report.json` directly.

The five identified gaps from the engineer-prompt review were addressed in one pass:
1. Added numbered evidence priority order to approach step 1.
2. Inserted step 2b as an explicit no-op/revision-warranted decision checkpoint.
3. Replaced subjective self-check wording in step 6 with three structural criteria: (a) all STEERING.md items addressed, (b) no new scope introduced, (c) approval prediction positive.
4. Expanded step 7 with three concrete validation checks: placeholder preservation, no unjustified constraint removal, syntax correctness.
5. Sharpened the engineer handoff trigger with two concrete conditions (competing technique selection, multi-step Trace-style structuring) and an explicit exclusion for minor wording changes.

The optimized candidate is saved as `optimized-prompt.md` in this directory.

## Rerun Command

When model credentials are available, rerun with:
```
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/student.agent.md \
  --train-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --judge-mode llm_judge
```
