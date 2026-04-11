# Steering — Teacher Turn 1 — Iteration 2

## Evidence supplied

- **Candidate:** `iterations/iteration-2/candidates/student/SKILL.md` (v0.3.0)
- **Iteration-1 teacher coaching:** All 4 points applied precisely by student
- **Adversary findings:** `iterations/iteration-2/candidates/adversary/findings.md` (3 high, 3 medium)

## What changed from v0.2.0 to v0.3.0

| Coaching point | Applied? | Notes |
|---|---|---|
| Blocker-first scope fix (remove validation-not-passed) | ✅ | Validation-pass bullet removed from blocker-first section |
| Judge-mode precedence rule | ✅ | `scoring` authoritative + inconsistency stop added |
| Reference callout → Before you start section | ✅ | 3-bullet preamble section added |
| Output contract items 2 vs 6 by time horizon | ✅ | Items 2 and 6 now explicitly divided by current-turn vs. next-required-action |

## Predicted eval performance (v0.3.0)

- **Eval 1 (workspace init):** Strong pass — resumption logic explicit in Core Workflow step 1
- **Eval 2 (missing-data path):** Strong pass — separate files, reuse rule, pause before optimization
- **Eval 3 (manual_followup recovery):** Strong pass — 6-step enumerated recovery
- **Eval 4 (candidate/steering staging):** Strong pass — collaboration contract referenced
- **Train row 5 (blocker-first):** Strong pass — dedicated section, validation bullet correctly removed

## Adversary findings disposition

The 3 high-severity findings are credible future work items, not iteration-2 blockers. No additional revision required before decision.

## Stop-or-continue decision

**Stop.** The v0.3.0 candidate addresses all five engineer-review failure modes plus all four iteration-1 teacher coaching points. The adversary findings identify future improvements but do not block the current candidate. The two-iteration loop goal has been met.

## Next step recommendation

Write the decision.md at the workspace root summarizing the v0.3.0 candidate as the recommended result, note the adversary-identified deferred items for a future iteration-3, and set workflow-status.json to `complete`.
