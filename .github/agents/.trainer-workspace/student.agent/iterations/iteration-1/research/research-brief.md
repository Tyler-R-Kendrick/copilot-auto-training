# Research Brief: student.agent.md Optimization

## Target and Task Summary

**Target:** `.github/agents/student.agent.md`
**Task:** Identify grounded sources and patterns for evaluating the student agent's ability to implement teacher-guided candidate revisions in trainer-led optimization loops, with correct reasoning trajectories, loop exit discipline, and validation compliance.

**Optimization Goal:** Improve evidence reading priority, approval prediction precision, loop exit criteria explicitness, revision scope bounding, and validation specificity.

## Research Plan

**Target layout:**
- Eval manifest: `.github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/evals/evals.json`
- APO datasets: `.github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl` and `val.jsonl`

**Approval bar for sources:**
Each source must provide:
- Accountable maintainer or standards body
- Traceable data origin and schema
- Stable version or date
- Acceptable licensing for eval use

## Source Evaluation

### Primary Authoritative Sources

1. **The student agent itself** (`student.agent.md`) — defines expected behaviors, handoff contract, output format, and constraints.
   - Authority: repository-owned canonical contract
   - License: project-internal, freely reusable for eval authoring
   - Fit: exact match; forms the ground truth for correct/incorrect behavior

2. **The `engineer-prompt/review.md`** in the student.agent workspace — identifies the specific failure modes and optimization hypotheses for the current run.
   - Authority: repository-internal analysis artifact
   - License: project-internal
   - Fit: defines the behavioral dimensions to cover in eval rows

3. **Adjacent agent workspaces** (`researcher.agent`, `adversary.agent`) — provide structural reference for eval case format, candidate staging, and judge-mode selection decisions.
   - Authority: repository-internal prior run artifacts
   - License: project-internal
   - Fit: structural reference only

4. **The `trainer-synthesize` skill** (`skills/trainer-synthesize/SKILL.md`) — defines what downstream optimizer needs from train/val datasets.
   - Authority: repository-owned skill contract
   - License: project-internal
   - Fit: defines minimum viable dataset shape for APO

### Public Source Evaluation

No public benchmark datasets are an exact fit for teacher-guided iterative revision loops in agent orchestration. Candidates reviewed:

- **IFEval (instruction-following eval, 2023):** Covers instruction-following compliance. Useful for testing whether agents follow explicit constraints, but lacks the iterative revision loop structure needed here. Partially relevant.
- **LIMA (2023, Meta AI):** Covers diverse instruction-response quality alignment. No teacher-critique loop structure. Rejected as a primary source.
- **Alpaca (Stanford, 2023):** Instruction-response pairs without iterative revision. Rejected.
- **AgentBench / WebArena:** Too broad and web-action-focused; no coverage of in-loop critique response behavior. Rejected.

**Decision:** Use repository-internal sources plus simulated examples grounded in the behavioral contract. The agent contract itself, the review.md analysis, and existing workspace examples provide sufficient ground truth.

## Approved Sources

| Source | Fit | Risk | Notes |
|--------|-----|------|-------|
| student.agent.md | Direct | None | Primary behavioral contract |
| engineer-prompt/review.md | Direct | None | Failure mode and hypothesis analysis |
| researcher.agent workspace | Structural | None | Format reference for eval shape |

## Rejected Candidates

- **IFEval:** Not structured around teacher-critique revision loops. Rejected as primary source.
- **LIMA, Alpaca:** No iterative revision structure. Rejected.
- **AgentBench, WebArena:** Too broad and unrelated to teacher-student orchestration. Rejected.

## Behavioral Dimensions for Eval Coverage

The student agent should be evaluated on six behavioral dimensions (from engineer-prompt review):

1. **Evidence reading priority** — Does the agent read the latest STEERING.md turn first before the summary and workspace evidence?
   - Eval type: behavioral process check (`llm_judge` with criteria)

2. **Revision scope discipline** — Does the agent change only lines implicated by the current critique (smallest defensible revision)?
   - Eval type: output quality check (`llm_judge` with criteria)

3. **Approval prediction accuracy** — Does the agent predict whether the teacher would approve, with a stated criterion?
   - Eval type: output structure check (`llm_judge` with criteria)

4. **Loop exit discipline** — Does the agent exit the loop when criteria are met, without unnecessary extra turns?
   - Eval type: loop behavior check (`llm_judge` with criteria)

5. **Conflict resolution** — When the summary contradicts the latest STEERING.md, does the agent treat the turn artifact as canonical?
   - Eval type: tie-breaking rule check (`llm_judge` with criteria)

6. **Validation compliance** — Does the agent run `python -m pytest -q` and report the result after revision?
   - Eval type: tool usage check (`llm_judge` with criteria)

## Schema for APO Dataset Rows

Each row uses `llm_judge` scoring with these fields:
- `input`: the student agent's task context (teacher goal, critique, workspace evidence, revision objective)
- `reference`: a description of what a fully compliant response looks like
- `criteria`: list of checkable behavioral assertions
- `scoring`: `"llm_judge"`

## Stop Recommendation

No stop required. Sufficient ground truth is available from the behavioral contract and review analysis. Proceed to synthesis.
