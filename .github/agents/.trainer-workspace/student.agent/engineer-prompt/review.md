## Goal

Assess the current `student.agent.md` as an optimization target for teacher-guided candidate revision work in trainer-led prompt optimization loops, with emphasis on revision discipline, reasoning trajectory quality, and teacher-approval prediction accuracy.

The optimization target is reliable, focused candidate improvement: a strong student agent should absorb teacher critique with minimal ambiguity, implement the smallest defensible revision, expose the reasoning trajectory that justified the plan, and accurately predict whether the teacher would approve the result.

## Current Strengths

- The role is sharply scoped: absorb teacher critique and implement the smallest defensible revision.
- The constraints correctly prohibit judging, adversarial review, and trainer-loop orchestration.
- The approach step 6 calls for a teacher-approval prediction and a bounded self-check, which limits runaway loops.
- The output format requires explicit reasoning trajectory, plan, tradeoffs, and uncertainty, which helps the teacher surface over-specified or under-supported revisions.
- The `engineer` handoff is listed as a formatting aid, not a delegation path, which maintains the student's ownership of the revision.

## Main Risks

1. **No evidence order.** The approach says "read the teacher goal, latest teacher critique, current teacher turn STEERING.md, per-agent summary.md files, and workspace evidence," but does not specify which artifact to read first when artifacts conflict, or how to handle incomplete or stale evidence.

2. **Engineer handoff trigger is vague.** The trigger condition—"when the task needs specialized prompt or Trace-oriented coaching, or if the teacher-facing explanation needs clearer structure"—is too open. It does not distinguish between cases that warrant an engineer handoff and cases where the student should proceed independently.

3. **No minimum revision criteria.** "Smallest defensible revision" is undefined. The agent has no signal for when a candidate change is too small (trivially non-impactful), too large (scope creep), or defensible enough to send to the teacher.

4. **Teacher-approval prediction is underspecified.** Step 6 says to predict approval "after your first draft" and do "at most one extra self-check," but gives no criteria for what teacher approval looks like, what evidence signals likely disapproval, or when to stop self-checking and request a new teacher turn.

5. **No explicit workspace artifact precedence.** The approach references "steering/<agent>/turn-N/STEERING.md" and "steering/<agent>/summary.md" but does not specify which takes precedence when they contradict, or how the student should handle a missing steering artifact.

6. **No revision scope boundary.** The prompt does not define what counts as "in scope" for a candidate revision, leaving the student susceptible to scope creep when teacher critique references adjacent issues outside the current iteration goal.

7. **No loop exit when evidence is contradictory.** The prompt says to hand off to teacher if "critique is incomplete, contradictory, stale," but does not instruct the student to stop and report instead of looping indefinitely when contradictions remain unresolved across teacher turns.

## Rewrite Hypotheses

- Add an explicit evidence reading order: current iteration goal first, latest turn-scoped STEERING.md second, per-agent summary.md third, current candidate fourth, workspace validation evidence last.
- Sharpen the engineer handoff trigger to specific conditions: reasoning trajectory is too long for teacher review, revision plan needs Trace-node or prompt-engineering rationale, or the teacher-facing explanation has structural gaps.
- Define "smallest defensible revision": one change per iteration goal, verifiable against the current steering, and narrow enough that the teacher can assess it in one pass.
- Add explicit teacher-approval criteria: alignment with the latest steering goal, no expansion of the prompt interface, no new constraints not in scope, and no revision that weakens existing validated behavior.
- Specify workspace artifact precedence: turn-scoped STEERING.md takes priority over the rolling summary.md; missing STEERING.md triggers a teacher handoff request.
- Clarify revision scope: changes are bounded to what the current iteration goal and teacher critique explicitly address; adjacent issues should be noted but not fixed.
- Add a contradiction exit: if the same contradiction persists across two consecutive teacher turns, report it as a blocker rather than looping again.

## Suggested Metrics

- Revision precision: percent of student revisions that address exactly the current steering goal and nothing else.
- Teacher-approval accuracy: calibration between student's predicted approval outcome and actual teacher verdict.
- Loop bound compliance: percent of runs where the student does not exceed one self-check per teacher turn.
- Engineer handoff rate: proportion of runs triggering an engineer handoff; a very high or very low rate may signal a mismatched trigger threshold.
- Contradiction detection rate: percent of runs that correctly report a blocking contradiction rather than looping with conflicting guidance.
- Reasoning transparency: whether the output exposes a plan, tradeoffs, and uncertainty rather than an answer-only result.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions in existing tests. Review student outputs against representative trainer-loop steering artifacts to confirm revision scope compliance, reasoning trajectory quality, and teacher-approval prediction accuracy.

## Recommendation

This is a good optimization target because student reliability directly affects teacher-student loop efficiency and trainer-loop convergence. The current agent has the right role scoping and output format, but lacks a structured evidence order, a defensible-revision threshold, and clear stopping criteria when guidance is contradictory or approval signals are ambiguous.

Prioritize a rewrite that adds an explicit evidence reading order, a precise revision scope boundary, and concrete teacher-approval criteria. Measure on revision precision and teacher-approval accuracy first. Only add examples if structured rewriting still produces over-specified or under-constrained revisions.
