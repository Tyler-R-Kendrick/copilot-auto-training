## Goal

Assess the current student agent as an optimization target for teacher-guided candidate revision inside trainer-led optimization loops. The optimization focus is reliable revision quality: the agent should consistently apply teacher critique into the smallest defensible prompt rewrite, expose a clear reasoning trajectory, and produce self-contained output that the teacher can act on without guessing.

The target is operational reliability, not role expansion. A strong student agent should interpret teacher steering without ambiguity, revise prompt candidates without scope creep, predict teacher approval accurately, and surface the reasoning and tradeoffs that justify the choice—so that teacher, trainer, and judge can all evaluate the revision without extra interrogation.

## Current Strengths

- The role is tightly scoped: revise candidates from teacher guidance, do not orchestrate the loop.
- The constraint list explicitly blocks judging, adversarial review, and trainer-owned orchestration.
- The approach includes a forward-looking teacher-approval prediction, which catches low-confidence revisions before they waste a teacher turn.
- The output format requires plan, reasoning trajectory, tradeoffs, and uncertainty alongside the revision, not just the diff itself.
- The `engineer` handoff is correctly positioned as a formatting and structure aid, not a skill-execution path.

## Main Risks

1. **No evidence reading order.** The approach says "read the teacher goal, latest teacher critique, current teacher turn STEERING.md, the relevant per-agent summary files, and the current workspace evidence"—but this is a flat enumeration, not a prioritized order. When artifacts are inconsistent or partially missing, the agent has no tiebreaker.

2. **"Smallest revision" is underspecified.** The constraint says "implement the smallest defensible candidate revision," but the prompt gives no guidance on what counts as in-scope vs. out-of-scope for a revision, how to decide when multiple critique points are present, or when "smallest" means ignoring a legitimate but lower-priority fix.

3. **Self-check exit criteria are weak.** Step 6 says "do at most one extra self-check only if the draft still looks unsupported, incomplete, or misaligned." These adjectives require subjective assessment. There is no measurable or structural criterion that tells the agent when the draft is good enough to stop.

4. **Validation step is ambiguous.** Step 7 and the output format both mention "run the relevant validation or measurement step," but the prompt does not define what validation means for a student producing a prompt candidate—whether that is running pytest, checking placeholder integrity, verifying eval dataset consistency, or something else.

5. **Engineer handoff guidance is thin.** The current text says to use the engineer handoff when "the task needs specialized prompt or Trace-oriented coaching, or if the teacher-facing explanation needs clearer structure." The agent has no concrete signal for which of those conditions is active, which risks either over-using or under-using the handoff.

6. **No conflict resolution for multi-turn steering.** The prompt references both the current teacher turn STEERING.md and rolling per-agent summary files. When those disagree—e.g., the summary says to tighten scope but the latest turn says to add examples—the agent has no tiebreaker rule.

7. **No explicit handling of no-op conditions.** The constraint says to "report a justified no-op when the supplied evidence does not support a better candidate." But the approach steps never surface this as a first-class decision point: there is no step that explicitly checks whether a revision is warranted before drafting one.

## Rewrite Hypotheses

- Add an explicit evidence priority order: (1) current teacher turn STEERING.md, (2) latest per-agent summary, (3) optimize or manual-followup report, (4) engineer-prompt review, (5) source snapshot. When items conflict, the most recent STEERING.md wins.
- Add a no-op check as step 2b: after reading evidence, explicitly decide whether a revision is warranted before drafting. If the evidence gap is too large, request a teacher turn instead of guessing.
- Operationalize "smallest revision": address only the critique items from the current teacher turn STEERING.md; defer items that appear only in older summaries unless the current turn explicitly re-raises them.
- Replace the subjective self-check exit with a structural one: the self-check passes when (a) every critique item from the current STEERING.md is addressed, (b) no new scope was introduced, and (c) the approval prediction is positive.
- Define "validation" explicitly for the student: at minimum, check that all placeholder tokens in the revised prompt are preserved from the source, that no constraints were removed without justification, and that the revised candidate can be applied to the target file without syntax errors.
- Sharpen the engineer handoff trigger: use it when the revision requires selecting between competing prompt-engineering techniques, or when the teacher-facing explanation involves multi-step rationale that benefits from Trace-style structuring. Do not use it for minor wording changes.

## Suggested Metrics

- Teacher approval rate: fraction of student turns where the predicted teacher approval is correct (teacher approves on next turn without major re-critique).
- Scope containment: fraction of revisions that address only the cited critique items without introducing uncited changes.
- Reasoning completeness: fraction of outputs where plan, tradeoffs, and uncertainty are all non-trivial (not boilerplate).
- No-op accuracy: fraction of no-op decisions that the teacher agrees were correct.
- Validation correctness: fraction of outputs where the revised candidate passes placeholder and constraint-preservation checks.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions. Inspect representative eval cases for reasoning completeness and scope containment after each iteration.

## Next Optimization Hypothesis

The highest-value change for a first pass is the explicit evidence priority order combined with the structural self-check exit. These two changes make the agent's decision-making legible to the teacher without changing the role, scope, or output interface. The no-op check and validation definition follow as the second pass if teacher-approval rate is still low after the first optimization.
