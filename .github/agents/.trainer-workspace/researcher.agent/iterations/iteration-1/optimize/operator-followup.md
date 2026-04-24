# Optimize Stage: Manual Follow-up Handoff

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no external model credentials (`.env` with `COPILOT_MODEL`) are configured in this repository. The optimizer completed all deterministic preparation steps (dataset validation, placeholder extraction, judge-mode inference) but could not execute the APO beam rounds.

## Agent Handoff Summary

The current `@trainer` agent answered the returned `model_prompt` directly, applying the improvements identified in `engineer-prompt/review.md`:

1. **Explicit evidence reading order** — target file → task description → scoring rule → existing evals → constraints → then plan
2. **MCP fallback rule** — report a blocker immediately when MCP tools are unavailable; do not substitute free-form research
3. **Inline source approval bar** — five-point checklist embedded in the agent contract so no runtime dependency on the full skill contract
4. **Blocker reporting specificity** — write a structured blocker report and stop when required constraints are missing
5. **Stopping condition** — deliver the brief once the approved-source list is stable; do not continue searching indefinitely
6. **Execute tool clarification** — use `execute` only for `scripts/run_research.py` deterministic scaffold, not as a general search tool

The generated candidate is saved at:
`iterations/iteration-1/optimize/optimized-prompt.md`

## Rerun Command

When model credentials are available, rerun the automated APO pass with:

```bash
python .agents/skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --judge-mode llm_judge
```
