# Teacher Steering — Turn 1

## Evidence used

- Original `student.agent.md` candidate (baseline)
- Optimized candidate from `iterations/iteration-1/optimize/optimized-prompt.md`
- 7 issues from `engineer-prompt/review.md`

## Assessment summary

Issues 1, 2, 3, 4, 6, 7 are all correctly fixed in the optimized candidate. Issue 5 is partially fixed but self-contradictory.

## Primary gap: Issue 5 self-contradiction

The Constraints section adds the meta-note `"Do not duplicate this condition in the Approach section."` while Approach Step 5 still contains a near-identical restatement of the engineer-handoff condition. This is worse than either the original duplication or a clean removal.

## Fix required (narrow and mechanical)

1. Delete the parenthetical meta-sentence from Constraints: `"Do not duplicate this condition in the Approach section."`
2. In Approach Step 5, replace the substantive restatement of the engineer-handoff condition with a cross-reference: *"See Constraints for engineer-handoff conditions; hand off when those conditions are met."*

## Preserve unchanged

Everything else in the optimized candidate must be preserved:
- Evidence reading order (Step 1)
- Observable teacher-handoff triggers
- Three-outcome self-check rule
- Scope boundary definition
- Output template (six labeled sections)
- Missing-steering fallback (Step 2)
- Conflict resolution rule (Step 3)

## Forecasted student mistake

The student is likely to delete the meta-note from Constraints rather than the duplicate content from Step 5. The steering must explicitly name Step 5 content as the thing to trim and Constraints as the single authoritative home.

## Stop/continue decision

One targeted student turn. If the fix is applied correctly, approve to apply.
