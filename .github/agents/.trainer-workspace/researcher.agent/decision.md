# Decision: researcher.agent.md Optimization — iteration-1

## Result: Student Candidate Approved ✅

## Target File

`.github/agents/researcher.agent.md`

## Optimization Summary

The optimization applied 5 discipline-focused improvements to the researcher agent contract:

1. **MCP skill activation first**: Approach step 1 now explicitly requires `find_agent_skill` + `load_agent_skill` before reading any target file or proposing sources. This addresses the training data finding that skill activation was previously in step 2.

2. **`run_agent_skill` clarity**: Added explicit note that `run_agent_skill` is called when the loaded skill exposes a deterministic helper under `scripts/`. The original conditional wording was retained verbatim (required by test contract) with a clarifying annotation.

3. **No-op path for pre-supplied materials**: Approach step 3 now handles the case where the caller has already supplied sufficient source material. The agent recognizes this and maps supplied sources to eval-authoring notes rather than re-running redundant search.

4. **Non-interactive gap reporting**: Added bullet to Constraints and Approach step 7 to default to gap reports rather than interactive questions when running in non-interactive contexts.

5. **Sub-agent constraint clarification**: The `DO NOT involve any other agents.` constraint (preserved verbatim) is supplemented with a gap-reporting preference note in the adjacent constraint bullet.

## Teacher Verdict

**APPROVE_WITH_MINOR_EDITS**: One edit applied — removed hard-coded `scripts/run_research.py` filename from the MCP contract (used general description instead), to avoid fabricating a specific helper filename not verified in workspace artifacts. After this edit, the student candidate was approved.

## Adversary Review

Scope-widening exploit was not credible. Student candidate scored higher on all eval cases.

## Validation

`python -m pytest -q` — **856 passed** — no regressions.

## Artifacts

- Optimize report: `iterations/iteration-1/optimize/manual-followup-report.json` (manual_followup mode)
- Optimized candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Candidates manifest: `iterations/iteration-1/candidates/candidates.json`
- Teacher steering: `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
- Validation log: `iterations/iteration-1/validation/pytest.txt`
