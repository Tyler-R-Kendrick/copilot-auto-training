## Goal

Assess the current `student.agent.md` as an optimization target for teacher-guided candidate revision in trainer-led prompt optimization loops. Emphasis on revision discipline, teacher-loop exit criteria, reasoning trajectory quality, and handoff contract fidelity.

The optimization target is revision reliability and loop exit precision. A strong student agent should apply the smallest defensible revision that addresses teacher critique, expose a clear reasoning trajectory, accurately predict teacher approval, and exit the loop without indefinite cycling.

## Current Strengths

- Role is narrowly scoped: revise candidates from teacher critique, do not take over judging or orchestration.
- Constraints correctly prohibit invoking engineer skills directly and mandate the smallest defensible revision.
- The approach section has a logical order: read evidence → hand off if unclear → draft with reasoning → validate → predict approval.
- `engineer` handoff is appropriately limited to formatting the reasoning trajectory, not to delegating the revision.
- Output format asks for steering artifacts, reasoning trajectory, revision, engineer handoff notes, approval prediction, and validation result.

## Main Risks

1. **No evidence reading order for workspace artifacts.** Step 1 says "Read the teacher goal, latest teacher critique, current teacher turn STEERING.md, the relevant per-agent summary files, and current workspace evidence," but gives no priority or stopping rule. An agent reading stale artifacts before the current steering turn may act on outdated guidance.

2. **Approval prediction criterion is underspecified.** Step 6 says "Predict whether the `teacher` would approve the revision after your first draft, then do at most one extra self-check." The criteria for what counts as predicted teacher approval are not stated — the agent must infer them from context. This can produce inconsistent self-checks.

3. **No explicit escalation rule for conflicting critique.** The constraints say "Use the `teacher` handoff whenever the critique is incomplete, contradictory, stale, or needs a fresh evidence-based recommendation," but there is no guidance on how to detect contradiction between older summary artifacts and the latest turn STEERING.md, or which one to treat as canonical.

4. **Loop exit criteria are implicit.** The approach says "do at most one extra self-check only if the draft still looks unsupported, incomplete, or misaligned with the latest steering; if approval still looks unlikely, justify why another teacher turn is needed." The conditions that constitute "unsupported, incomplete, or misaligned" are not enumerated, making loop termination subjective.

5. **`engineer` handoff trigger is broad.** "If the task needs specialized prompt or Trace-oriented coaching, or if the teacher-facing explanation needs clearer structure" covers a wide surface area. An agent that routes every revision through `engineer` for formatting adds unnecessary latency; one that never routes misses the handoff entirely.

6. **No definition of "smallest defensible revision."** The constraint is stated but not bounded. Without criteria for "smallest," an agent may interpret it as either a single-word change or a paragraph-level rewrite, both of which could be defended.

7. **Validation step is underspecified.** Step 7 says "Run the relevant validation or measurement step and report what changed," but does not specify what constitutes a relevant validation step for a prompt revision (e.g., `python -m pytest -q`, a scoring check, or an eval run). An agent may skip validation silently.

## Rewrite Hypotheses

- Add an explicit evidence reading priority: latest STEERING.md turn artifact first → per-agent summary second → workspace evidence last; discard anything older than the latest steering turn when it contradicts that turn.
- Define the approval prediction criterion concretely: the revision is predicted approved if it addresses all critique points in the latest STEERING.md without introducing new scope, new constraints, or structural regressions relative to the original prompt interface.
- Add a conflict resolution rule: if the summary artifact contradicts the latest STEERING.md turn, treat the turn artifact as canonical and note the discrepancy in the output.
- Enumerate the loop exit conditions explicitly: exit immediately if (a) teacher predicts no further supported improvement, (b) the student predicts approval, (c) the revision count in the current iteration reaches the turn cap, or (d) the required revision objective is nil.
- Narrow the `engineer` handoff trigger: invoke only when the reasoning trajectory needs Trace-oriented terminology or prompt-engineering framing that the student cannot produce without domain knowledge, or when the teacher-facing explanation is materially ambiguous without restructuring.
- Define "smallest defensible revision" as the minimal set of sentence-level or structural changes that removes the critique gap identified in the current steering turn without touching any lines not implicated by that gap.
- Add a concrete validation instruction: after drafting the revision, run `python -m pytest -q` from the repository root and report pass/fail; if eval manifest scoring shape changed, note the judge-mode implication.

## Suggested Metrics

- Revision scope compliance: percent of revisions that change only lines implicated by the current critique.
- Loop exit accuracy: percent of loops that exit correctly without a spurious extra teacher turn.
- Approval prediction accuracy: percent of revisions where the student's predicted teacher approval matches the teacher's actual verdict on the next turn.
- Engineer handoff precision: percent of engineer handoffs that meaningfully improve teacher-facing clarity versus total handoffs.
- Validation compliance: percent of revisions followed by a reported `pytest` or eval validation result.
- Reasoning trajectory completeness: percent of outputs that include plan, tradeoffs, and uncertainty alongside the revision.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions. Review representative student outputs in `iterations/` directories against teacher steering artifacts to check revision scope, reasoning trajectory, and approval prediction fidelity.

## Next Optimization Hypothesis

Focus the first pass on: (1) adding an explicit evidence reading priority, (2) defining the approval prediction criterion concretely, (3) enumerating loop exit conditions, and (4) adding a concrete validation instruction pointing to `python -m pytest -q`. Keep the rewrite minimal — structural and precision improvements only, without expanding the student's scope or adding new tool permissions.
