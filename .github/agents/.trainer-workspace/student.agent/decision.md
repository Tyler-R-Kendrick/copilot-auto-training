# Decision Summary — student.agent

## Target

`.github/agents/student.agent.md`

## Iteration

`iteration-1`

## Selected Candidate

**Student candidate** — the optimized prompt produced in the manual_followup path.

## Changes Applied

Seven improvements were applied to the baseline prompt, addressing all 5 risk areas from the engineer-prompt review:

1. **Prioritized evidence reading order** — Approach step 1 now specifies turn-scoped `STEERING.md` first, per-agent `summary.md` second, candidate text third, workspace evidence last. Includes explicit guard: "Do not use summary context to override turn-scoped steering."

2. **Pre-edit scope check** — Approach step 3 and a constraint bullet require confirming the target file is within `candidates/student/` before calling `edit`. Out-of-scope targets (judge-owned files, lock files, skill contracts) must produce a scope blocker report.

3. **Concrete stale-critique signal** — The teacher handoff condition now specifies: treat critique as stale when the STEERING.md turn number is older than the latest optimize or research artifact modification timestamp in the active iteration.

4. **Self-check termination rule** — After at most one self-check predicting rejection, the agent must hand off to `teacher` unconditionally. No further self-checking permitted.

5. **Engineer handoff scope clarification** — The `engineer` handoff is permitted only for reformatting reasoning trajectories and solution plans. It must not execute skills, edit files, or manage workspace state.

6. **Default validation step** — Approach step 8 specifies `python -m pytest -q` from the repository root plus a diff review confirming only the intended candidate file changed.

7. **Candidate persistence note** — Approach step 5 adds explicit instruction to save the revised candidate to `iterations/iteration-N/candidates/student/` in the active iteration and record that path in the output.

## Adversary Assessment

The adversary exploit (inverting reading order to make `summary.md` authoritative) does not outrank the student candidate when the eval dataset is applied. Training cases 1 and 6 explicitly test STEERING.md authority. Future judging turns should block candidates that promote `summary.md` over `STEERING.md`.

## Validation Result

`python -m pytest -q`: **856 passed**, 0 failed, 0 errors.

## Optimize Mode

`manual_followup` — no inference model was configured. The `@trainer` agent answered the `model_prompt` from `manual-followup-report.json` directly.
