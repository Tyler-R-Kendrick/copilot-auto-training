## Goal

Assess the current `student.agent.md` as an optimization target for teacher-guided candidate revision inside trainer-led optimization loops.

The optimization target is revision discipline and steering fidelity. A strong student agent should read available steering artifacts before acting, implement the smallest defensible revision that the teacher would approve, expose an explicit reasoning trajectory, predict teacher approval before finishing, and hand off to teacher when steering is ambiguous rather than guessing.

## Current Strengths

- The role is clearly scoped: absorb teacher critique, draft the smallest defensible revision, expose the reasoning trajectory.
- The self-approval prediction step is structurally correct and capped at "at most one extra self-check."
- The constraint against taking over judging, adversarial review, or trainer orchestration is explicit.
- The `engineer` handoff condition is specified (prompt/Trace coaching, formatting help), and the boundary "do not invoke engineer skills directly" is explicit.
- The output format requires all key sections: steering artifact followed, reasoning trajectory, revision or no-op, engineer handoff summary if used, predicted teacher approval, validation result.

## Main Risks

1. **No evidence reading order when STEERING.md is absent.** Step 1 reads "teacher goal, latest teacher critique, current teacher turn STEERING.md, per-agent summary.md, workspace evidence" — but if STEERING.md is missing or stale, the agent has no fallback path. It may proceed with an incorrect assumption or fail silently.

2. **"Unclear next revision target" is underspecified.** The approach tells the agent to hand off to teacher when the target is unclear, but gives no criteria for deciding whether it is unclear. This can lead to either too-frequent teacher calls (wasting turns) or too-rare calls (proceeding with stale guidance).

3. **No-op path is vague.** The constraint says "report a justified no-op when the supplied evidence does not support a better candidate" but does not enumerate the specific conditions: e.g., steering already satisfied, candidate already at parity with teacher expectation, validation passing, no actionable critique.

4. **Engineer handoff conditions are implicit.** The approach says to use engineer "when the task needs specialized prompt or Trace-oriented coaching, or if the teacher-facing explanation needs clearer structure." In practice, agents over-invoke engineer to get formatting help they could provide themselves, inflating turn count.

5. **Revision scope boundary is not examples-anchored.** "Smallest defensible revision" is a principle without concrete exclusion examples. Agents can misread it as an invitation for minimal surface-level edits (e.g., adding a bullet) that do not address the underlying critique, rather than the minimal complete change that resolves the critique.

6. **Validation step is underspecified.** Step 7 says "run the relevant validation or measurement step and report what changed" but does not name what counts as valid validation: running `python -m pytest -q`, invoking an eval script, or comparing the candidate against an eval manifest.

## Rewrite Hypotheses

- Add a brief evidence fallback order: if STEERING.md is missing, fall back to the per-agent `summary.md`; if both are missing, hand off to teacher before editing.
- Add an explicit decision criterion for "unclear revision target": missing or empty STEERING.md, contradictory criteria in summary.md vs latest steering turn, or steering that dates from more than one iteration ago without a fresher follow-up.
- Enumerate no-op conditions inline: steering already satisfied by the current candidate, candidate already at or above teacher's stated acceptance threshold, validation passing with no regression, or critique containing no actionable instruction.
- Tighten the engineer handoff to "use engineer only when the teacher-ready explanation requires reformatting that would take more than 2 sentences to do inline, or when Trace/prompt-engineering domain expertise is explicitly needed for the revision."
- Add one concrete exclusion example for "smallest defensible revision": fix the single strongest critique, not every open comment; leave unrelated structure, phrasing, or scope intact.
- Specify the validation step: run `python -m pytest -q` from the repo root; if the revision touches eval datasets or prompt scoring, also run the relevant eval manifest command.

## Suggested Metrics

- Steering fidelity: percent of revisions that directly address the explicit critique in the latest STEERING.md.
- Teacher approval prediction accuracy: percent of predictions that match the teacher's actual verdict on the next turn.
- No-op precision: percent of cases where the agent correctly identifies no actionable revision and reports a justified no-op instead of a cosmetic change.
- Engineer handoff rate: average number of engineer handoffs per student turn (target ≤ 1).
- Revision completeness: percent of revisions that fully resolve the primary critique without introducing a new regression.
- Validation pass rate: percent of revisions that pass `python -m pytest -q` without modification.

## Validation Plan

Run `python -m pytest -q` from the repository root after any rewrite to confirm no regressions. Review representative student outputs against teacher critique artifacts in existing workspaces (e.g., `.github/agents/.trainer-workspace/researcher.agent/`) for steering compliance and no-op precision.

## Next Optimization Hypothesis

Focus the first pass on: (1) adding an explicit evidence fallback order for missing STEERING.md, (2) defining the criterion for "unclear revision target," (3) enumerating no-op conditions, and (4) specifying the validation step concretely. Keep the rewrite minimal — structural clarity improvements only, without expanding scope or adding new handoff paths.
