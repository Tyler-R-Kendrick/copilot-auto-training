# Operator Follow-Up: Manual Follow-Up Mode

## Blocker

The optimize runtime returned `mode=manual_followup` because no inference model was available in CI (`CopilotInferenceError: github-copilot-sdk is required` / no session authentication).

## Agent Handoff Summary

The current `@trainer` agent answered the returned `model_prompt` directly and saved the result as `optimized-prompt.md` in this optimize directory. The optimized candidate reflects the following improvements from the engineer-prompt review:

1. **MCP skill activation first**: Reordered the approach so `find_agent_skill` + `load_agent_skill` is explicitly the first action, before reading any context or proposing sources.
2. **Clarified `run_agent_skill` condition**: The `researcher-research` skill has a `scripts/run_research.py` helper, so `run_agent_skill` is always appropriate (not conditional on uncertain script presence).
3. **No-op path for pre-supplied materials**: Added step 3 in the approach to recognize when the caller has already supplied sufficient source material and skip redundant search.
4. **Non-interactive gap reporting**: Added an explicit rule to default to gap reports rather than interactive questions in non-interactive contexts.
5. **Clarified sub-agent constraint**: Changed "DO NOT involve any other agents" to "DO NOT invoke sub-agents" with a parenthetical clarifying that search/read/execute tools are permitted.

## Artifact Paths

- Optimize report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`

## Rerun Command

To rerun with a live model once credentials are available:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --judge-mode llm_judge
```
