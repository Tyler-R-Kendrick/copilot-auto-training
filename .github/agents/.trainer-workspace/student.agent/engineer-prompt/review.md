## Goal

Assess the current `student.agent.md` as an optimization target for teacher-guided candidate revision inside trainer-led optimization loops. The optimization objective is revision reliability and trajectory quality: a strong student agent should read and follow workspace steering artifacts before editing, draft the smallest defensible revision with an explicit reasoning trajectory, predict whether the teacher would approve before finalizing, and avoid scope drift or answer-only output.

## Current Strengths

- The role is tightly scoped: draft or revise prompt candidates from teacher guidance, expose the reasoning trajectory, and let the teacher validate.
- The constraints correctly prohibit scope expansion (judging, adversarial review, trainer orchestration) and direct skill invocation.
- The handoff definitions for `teacher` and `engineer` are concise and carry clear do-not-delegate instructions.
- The `teacher` approval prediction in step 6 of Approach is a useful convergence guard.
- The output format requires explicit reasoning artifacts (chain-of-thought, tree-of-thought, etc.) rather than answer-only responses.

## Main Risks

1. **No evidence reading order before revision.** Approach step 1 lists five artifact types to read, but gives no priority order. An agent could read a stale `summary.md` before the turn-scoped `STEERING.md`, producing a revision anchored to outdated guidance.

2. **No scoping check before editing.** The agent may revise a file that is outside its granted scope (e.g., judge-owned artifacts, lock files, or skill contracts) because neither the constraints nor the approach explicitly require a scope check before calling `edit`.

3. **`teacher` handoff trigger condition is underspecified.** The body says to hand off "whenever the critique is incomplete, contradictory, stale, or needs a fresh evidence-based recommendation," but provides no concrete signal for "stale" — an agent making multiple self-checks may never decide to hand off.

4. **No stopping rule for the self-check loop.** Step 6 says "do at most one extra self-check," but the constraint block says "if approval still looks unlikely, justify why another teacher turn is needed instead of looping indefinitely." These two rules can conflict: after one self-check the agent might keep justifying additional teacher turns without ever terminating.

5. **`engineer` handoff purpose is narrowly stated.** The body says to use `engineer` to "format your reasoning trajectory and solution plan into a clearer teacher-ready explanation," but the constraint says "Do not use `engineer-prompt`, `engineer-code`, or any other engineer skills directly." This creates confusion: when exactly is the `engineer` handoff permitted if no skills may be used?

6. **Validation step is underspecified.** Approach step 7 says "run the relevant validation or measurement step," but does not identify what that step is — pytest, eval command, diff review, or something else. This leaves the validation result undefined for most runs.

7. **No explicit artifact persistence contract.** The agent edits candidates but there is no guidance on where to write the candidate file so the trainer can find it (e.g., `candidates/student/` in the active iteration).

## Rewrite Hypotheses

- Add an explicit evidence reading order as a prioritized list: turn-scoped `STEERING.md` first → per-agent `summary.md` second → current candidate text third → workspace evidence last.
- Add a pre-edit scope check: before calling `edit`, confirm the target file is the current candidate, not a judge-owned, lock, or skill-contract file.
- Replace "stale" with a concrete signal: treat critique as stale when the STEERING.md turn number is older than the latest optimize or research artifact modification time.
- Clarify the self-check termination rule: after one self-check, if approval is still unlikely, hand off to `teacher` unconditionally; do not continue self-checking.
- Clarify the `engineer` handoff scope: permitted to reformat reasoning trajectory and solution plan; prohibited for skill execution, file editing, or workspace management.
- Identify the default validation step: `python -m pytest -q` from the repository root plus a diff review confirming only the intended candidate file changed.
- Add an artifact persistence note: write the revised candidate to `iterations/iteration-N/candidates/student/` in the active iteration and record the path in the output.

## Suggested Metrics

- Evidence reading compliance: percent of revisions that read turn-scoped `STEERING.md` before `summary.md`.
- Scope drift rate: percent of runs that edit files outside the current candidate.
- Teacher approval prediction accuracy: percent of approved revisions where the student correctly predicted approval.
- No-op justification rate: percent of runs where evidence was insufficient and the student correctly reported a justified no-op rather than a speculative edit.
- Validation compliance: percent of runs that produce a `pytest -q` result in the output.
- Candidate persistence rate: percent of runs that write the candidate to `candidates/student/` before finishing.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions. Review representative student outputs against the trainer steering artifacts for compliance with the reading order, scope discipline, teacher-approval prediction, and candidate persistence requirements.

## Next Optimization Hypothesis

Focus the first pass on: (1) adding a prioritized evidence reading order, (2) adding a pre-edit scope check, (3) clarifying the teacher handoff staleness signal, (4) tightening the self-check termination rule, and (5) identifying the default validation step. Keep the rewrite minimal — structural and clarity improvements only, without changing the prompt interface or expanding scope.
