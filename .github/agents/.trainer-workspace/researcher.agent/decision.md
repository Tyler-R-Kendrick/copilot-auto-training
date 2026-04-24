# Decision Summary — researcher.agent

## Selected Target

**File**: `.github/agents/researcher.agent.md`
**Reason for selection**: First `.agent.md` file missing a trainer workspace, sorted alphabetically among candidates without workspaces.

## Optimization Goal

Improve MCP execution discipline, blocker-report reliability, and research brief completeness, based on the engineer-prompt review in `engineer-prompt/review.md`.

## Iteration 1 Results

**Workspace**: `.github/agents/.trainer-workspace/researcher.agent/`
**Iteration**: `iterations/iteration-1/`
**Datasets**: 8 train rows, 3 val rows — all `llm_judge` scoring with `reference` and `criteria`.
**Judge mode**: `llm_judge`

### Changes Applied

Six targeted improvements applied to the source file:

1. **Pre-Research Constraint Check** (new section): fixed reading order, explicit blocker condition before `find_agent_skill`.
2. **`run_agent_skill` guard**: preserved original text + added clarification about checking loaded contract for scripts/ helper.
3. **Blocker-report step**: added as Approach step 1, before `find_agent_skill`.
4. **Synthesis boundary**: added to Scope — "Stop at mapping notes."
5. **Artifact path guidance**: added as Approach step 8.
6. **Output format descriptions**: expanded each section with minimum content requirements.

### Adversary Review

Adversary exploit removed the blocker gate ("proceed with reasonable assumptions"). Predicted judge score: 0.3–0.4. Student candidate wins — exploit not credible against the training dataset.

### Validation

**Result**: 856 passed, 0 failed
**Command**: `python -m pytest -q`
**Log**: `iterations/iteration-1/validation/pytest.txt`

## Final Candidate

`iterations/iteration-1/candidates/student/candidate.md` → persisted to `.github/agents/researcher.agent.md`

## Status

`complete`
