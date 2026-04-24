# Decision: researcher.agent.md Optimization

**Target:** `.github/agents/researcher.agent.md`
**Iteration:** iteration-1
**Date:** 2026-04-13
**Outcome:** Student candidate applied ✅

## Changes Applied

Five improvements were made to the baseline `researcher.agent.md`:

1. **Clarified `run_agent_skill` fallback**: Added explicit note that when no deterministic helper script exists, the loaded skill contract is the active operating guide. The MCP contract bullet now reads "otherwise use the loaded skill instructions as the active operating contract."

2. **Fixed constraint wording**: "DO NOT involve any other agents." is preserved (required by tests), but a clarifying note is appended: "The `agent-skills` MCP server is not an agent handoff — it may be used freely for skill discovery and execution." This removes the contradiction.

3. **Strengthened approach step 2**: "before proposing sources or a search plan" → "before any research action — this is a hard prerequisite, not a step that can follow initial source gathering."

4. **Added scope exclusion**: "Do not author eval rows, JSONL datasets, or synthesized test cases; those belong to a separate synthesis workflow." — prevents scope creep into synthesis tasks.

5. **Added artifact-saving guidance**: Step 7 and output format section now cover saving the brief to the caller-supplied location and confirming the path.

Additionally, the opening paragraph was expanded to mention artifact-saving behavior upfront.

## Validation

- `python -m pytest -q`: **856 passed, 0 failed**
- `test_researcher_agent_contract_structure`: **PASS**

## Adversarial Review

The adversary candidate (scope expansion + optional MCP) does not constitute a credible exploit against the dataset's explicit scoring criteria. Student candidate wins.

## Artifacts

- `iterations/iteration-1/optimize/optimized-prompt.md` — final prompt candidate
- `iterations/iteration-1/optimize/manual-followup-report.json` — optimize run payload
- `iterations/iteration-1/synthesize/train.jsonl` — 5 training rows (llm_judge)
- `iterations/iteration-1/synthesize/val.jsonl` — 3 validation rows (llm_judge)
- `iterations/iteration-1/validation/pytest.txt` — 856 passed
- `iterations/iteration-1/steering/teacher/turn-1/STEERING.md` — teacher: STOP, persist student candidate
