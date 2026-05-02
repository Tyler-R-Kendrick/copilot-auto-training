# Operator Follow-Up: manual_followup Handoff

## Blocker

The `trainer-optimize` runtime could not reach an external inference model:

> Session error: Execution failed: Error: Session was not created with authentication info or custom provider

No model credentials (`COPILOT_MODEL`) are configured in the environment. The optimizer completed all deterministic preparation steps (dataset loading, prompt parsing, input binding) but could not execute inference passes.

## Agent Handoff Summary

The `@trainer` agent answered the returned `model_prompt` directly, applying the seven improvements identified in `engineer-prompt/review.md`:

1. Added explicit numbered evidence reading order (iteration goal → STEERING.md → summary.md → candidate → validation evidence)
2. Added artifact precedence rule: turn-scoped STEERING.md takes priority over summary.md
3. Sharpened the `engineer` handoff trigger to three specific conditions
4. Defined "smallest defensible revision" with explicit criteria
5. Added teacher-approval criteria (alignment, no interface expansion, no out-of-scope constraints, no regression)
6. Clarified revision scope: fix only what the iteration goal and critique address; note but do not fix adjacent issues
7. Added contradiction exit: report as a blocker after two consecutive teacher turns with the same unresolved contradiction

The result is saved as `optimized-prompt.md` and used as the optimize-stage candidate for the rest of the workflow.

## Rerun Command

To rerun this optimization with a live inference model after configuring credentials:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/student.agent.md \
  --train-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --output-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimized-prompt.md \
  --report-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimize-report.json \
  --judge-mode llm_judge \
  --iterations 3
```
