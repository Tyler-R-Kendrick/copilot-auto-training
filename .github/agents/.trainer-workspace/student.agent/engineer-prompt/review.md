## Goal

Assess `student.agent.md` as an optimization target for trainer-loop candidate revision work, with emphasis on teacher-guided iteration discipline, revision scope control, and output clarity for the `trainer` agent that orchestrates the loop.

The main optimization target is operational reliability inside a teacher/student loop: clean teacher-handoff triggers, unambiguous stopping rules, smallest-revision discipline, and output that the `trainer` can act on without manual interpretation.

## Current Strengths

- The role is correctly scoped: absorb teacher critique, implement the smallest defensible revision, explain the reasoning trajectory.
- The constraints correctly block judging, adversarial review, and trainer-loop orchestration.
- The `teacher` and `engineer` handoff triggers are present and differentiated.
- The approach includes a self-check step (step 6) that asks the student to predict teacher approval before finishing, which is the right loop discipline.
- The output format asks for plan, reasoning trajectory, tradeoffs, and validation — good for transparency.
- The argument-hint correctly describes what context to supply.

## Main Risks

1. **Evidence reading order is undefined.** The approach says "Read the teacher goal, latest teacher critique, current teacher turn STEERING.md..." but does not specify which artifact takes precedence when they conflict, how many artifacts to read before planning, or when to stop gathering context and start revising.

2. **Teacher-handoff trigger is too vague.** Step 2 says "If the next revision target is unclear, explicitly hand off to teacher." This does not define what "unclear" means in terms of observable artifact state — for example, missing `STEERING.md`, conflicting critiques, or no iteration directory yet. Vague triggers lead to inconsistent handoff frequency across runs.

3. **Stopping rule for the self-check (step 6) is ambiguous.** The step says "do at most one extra self-check only if the draft still looks unsupported, incomplete, or misaligned... if approval still looks unlikely, justify why another teacher turn is needed instead of looping indefinitely." But it does not specify what to produce when the student predicts rejection: should it stop, output the draft with caveats, or immediately request a teacher turn? The ambiguity can cause infinite or premature loops.

4. **"Smallest defensible revision" is not anchored.** The constraint says to implement the smallest defensible revision, but neither the constraints nor the approach specify what scope is too large (e.g., changing prompt interface, expanding scope, adding new constraints). Without a concrete boundary, agents may interpret "small" differently across runs and loop contexts.

5. **Engineer-handoff condition is duplicated across constraints and approach.** The constraint says "Use the engineer handoff to format your reasoning trajectory... when the task needs prompt-engineering or Trace-oriented expertise." Step 4 of the approach says the same thing with different wording. Duplication invites interpretation drift.

6. **Output format lists fields without structure.** The output format says "State the current steering artifact(s)... state the reasoning trajectory... state the revision... state the predicted teacher approval outcome..." but gives no template or ordering anchor. For a trainer loop that accumulates turn artifacts, a fixed output structure improves cross-turn comparability.

7. **No explicit fallback for missing or stale steering.** If the workspace has no `STEERING.md` yet, or the latest one is from a previous iteration, the student has no instruction for what to do. The current contract only says to request teacher guidance if the target is unclear, but it does not handle the case where no steering artifact exists at all.

## Rewrite Hypotheses

- Add a concrete evidence reading order: latest `STEERING.md` first → active iteration's `summary.md` → current candidate → teacher critique notes → then stop and plan.
- Replace "if the next revision target is unclear" with an observable condition: hand off to teacher when no active-iteration `STEERING.md` exists, when the latest `STEERING.md` is ambiguous about what to change, or when two steering artifacts conflict.
- Add a three-outcome stopping rule for the self-check: (a) approve and output with confidence, (b) refine once if the draft is clearly incomplete, (c) request a teacher turn with a specific gap explanation if revision is still unlikely to satisfy the critique.
- Add a brief inline scope boundary: "smallest defensible revision" means changing phrasing, section order, constraint wording, or output structure within the current prompt interface — not adding new sections, removing required fields, or changing the task framing.
- Consolidate the engineer-handoff condition into a single location (constraints), and remove the duplicate in the approach or replace it with a forward reference.
- Add a fixed output template with labeled sections: `Steering followed`, `Reasoning trajectory`, `Revision`, `Engineer handoff (if used)`, `Predicted teacher approval`, `Validation result`.
- Add a missing-steering fallback: if no active-iteration `STEERING.md` exists, produce a summary of the candidate's current state and an explicit request for the trainer to initialize the steering artifact before proceeding.

## Suggested Metrics

- Teacher-handoff precision: percent of handoffs triggered by a clearly observable workspace condition rather than a vague "unclear target."
- Revision scope compliance: percent of revisions that stay within the declared scope boundary (no new sections, no interface changes).
- Loop termination rate: percent of student turns that conclude with one of the three defined stopping outcomes rather than an open-ended continuation.
- Output format completeness: percent of student turns that include all six labeled output sections.
- Predicted approval accuracy: fraction of "teacher would approve" predictions that match the next teacher turn's verdict.
- Evidence citation rate: percent of reasoning steps that reference a specific steering artifact or workspace file rather than general impressions.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions. Review representative student-turn outputs against the declared output template for structural compliance and revision-scope adherence.

## Next Optimization Hypothesis

Focus the first pass on: (1) adding an explicit evidence reading order, (2) replacing the vague teacher-handoff trigger with observable conditions, (3) adding a three-outcome stopping rule for the self-check step, and (4) adding a fixed output template. Keep the rewrite minimal — structural improvements only, without changing the role scope or agent handoff targets.
