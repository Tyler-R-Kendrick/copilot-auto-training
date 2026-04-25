# Engineer-Prompt Review: student.agent.md

## Target Goal

Improve the `student` agent's instruction clarity and reliability within the teacher-student optimization loop. The agent must absorb teacher critique, produce defensible candidate revisions, expose explicit reasoning trajectories, and predict teacher approval accurately — all while staying in its narrow revision role without taking over orchestration.

## Current Prompt Analysis

### Strengths
- Clear role statement: "specialist in teacher-guided candidate revision"
- Well-structured constraints that prevent scope creep
- Explicit mention of reasoning trajectory formats (chain-of-thought, tree-of-thought, etc.)
- Good handoff conditions for `teacher` and `engineer`

### Likely Failure Modes

1. **Over-revision**: The student may implement broader changes than the teacher critique requires, violating the "smallest defensible revision" constraint. The constraint exists but the guidance doesn't show concretely how to scope revisions.

2. **Reasoning trajectory gap**: The agent is instructed to expose reasoning, but the approach doesn't specify _when_ to switch between reasoning formats (chain-of-thought vs. sketch-of-thought). This can lead to inconsistent, hard-to-read output for teachers.

3. **Teacher approval prediction quality**: Step 6 says "predict whether the teacher would approve" but doesn't give criteria or evidence to use for that prediction. The student may predict approval optimistically without consulting actual steering artifacts.

4. **Stale steering artifacts**: If the student reads an outdated `summary.md` instead of the latest turn-scoped `STEERING.md`, revisions may miss the current critique. The approach says to read both but doesn't specify priority.

5. **Loop exit ambiguity**: The constraint "do at most one extra self-check" is clear, but the condition "approval still looks unlikely, justify why another teacher turn is needed" may cause the student to loop indefinitely through teacher handoffs instead of exiting.

6. **Engineer handoff over-use**: The agent can invoke `engineer` to "format reasoning and solution plan" — but lacks clear criteria for when this is warranted vs. when the student should just present output directly.

## Dataset Gaps

No eval cases exist for the student agent. Synthesis is needed for:
- Teacher critique → minimal defensible revision scenarios
- Reasoning trajectory format selection based on task type
- Teacher approval prediction accuracy
- Proper handoff triggering vs. proceeding directly

## Validation Plan

1. Synthesize `evals/evals.json` and `train.jsonl`/`val.jsonl` datasets covering the above failure modes
2. Run `trainer-optimize` with `judge_mode=llm_judge` (open-ended quality task)
3. Validate with `python -m pytest -q` after applying changes
4. Adversarial check: can an exploit candidate game the teacher-approval prediction?

## Next Optimization Hypothesis

The highest-value improvement is adding **concrete revision-scope guidance**: explicit criteria for what counts as "smallest defensible revision" (e.g., one constraint at a time, one section only), and a concrete ordered checklist for teacher-approval prediction anchored to the latest steering artifact rather than the student's own judgment.

Secondary improvement: clarify the `engineer` handoff trigger condition with a concrete threshold (e.g., "when the plan involves more than one section or crosses prompt-engineering vs. code-optimization concerns").

## Recommended Judge Mode

`llm_judge` — the student agent produces open-ended reasoning trajectories and candidate revisions that require qualitative assessment against criteria rather than deterministic matching.
