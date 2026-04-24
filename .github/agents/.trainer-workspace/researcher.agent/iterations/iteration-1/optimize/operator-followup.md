# Operator Followup: researcher.agent.md

## Blocker

The external model was not available (no COPILOT_MODEL credential configured):
> Session error: Execution failed: Error: Session was not created with authentication info or custom provider

## Agent Handoff Summary

The `trainer-optimize` runtime completed all deterministic preparation steps (placeholder extraction, dataset validation, judge-mode selection), then returned `mode=manual_followup` with a `model_prompt` payload.

The current `@trainer` agent answered the `model_prompt` directly, applying the identified improvements from `engineer-prompt/review.md`:
1. Clarified `run_agent_skill` condition: use loaded skill contract as operating guide when no scripts exist
2. Fixed constraint wording: "DO NOT hand off to or coordinate with sibling agents" (previously "DO NOT involve any other agents")
3. Strengthened approach step 2: MCP discovery/load is now a hard prerequisite before any research action
4. Added scope clause explicitly excluding eval row authoring
5. Added step 7: save artifact to caller-supplied location and confirm path

The result was saved as `optimized-prompt.md` and is used as the optimize-stage candidate for the rest of the workflow.

## Rerun Command

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/val.jsonl \
  --output-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/optimize/optimized-prompt.md \
  --report-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/optimize/optimize-report.json \
  --iterations 3 \
  --judge-mode llm_judge
```

Run this command after configuring COPILOT_MODEL in the `.env` file for a fully automated model-backed optimization pass.
