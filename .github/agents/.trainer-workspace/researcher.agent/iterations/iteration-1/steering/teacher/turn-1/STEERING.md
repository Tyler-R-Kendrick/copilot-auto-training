# Teacher Steering — Turn 1

## Target

`.github/agents/researcher.agent.md`

## Evidence Used

- Original baseline prompt
- Optimized candidate (`iterations/iteration-1/optimize/optimized-prompt.md`)
- Engineer-prompt review (`engineer-prompt/review.md`)

## Gap Assessment

| Gap | Status |
|-----|--------|
| No evidence order | Fully addressed |
| MCP routing condition under-specified | Fully addressed |
| No approval bar definition | Fully addressed |
| Rejection evidence is weak | Fully addressed |
| Stop condition (blocker report) undefined | Fully addressed |
| No artifact completeness contract | Fully addressed |

All six engineer-identified gaps are resolved.

## Predicted Student Mistakes

Without explicit steering, the student is most likely to merge both stop conditions into a single section (calling it "Gap or Blocker Report") rather than keeping them as distinct output paths triggered at different stages.

## Required Revision

One structural ambiguity remains: the candidate defines two stop conditions (pre-research gap report; post-research blocker report) but the Output Format only names one of them, creating conflation risk.

**Required fix:**
1. Add a `Gap Report Format` section that specifies required fields when inputs (target file, scoring rule) are missing before research begins.
2. Update the `Output Format` section to list both stop paths explicitly:
   - "Gap report — if target file or scoring rule is missing (stop before research)"
   - "Blocker report — if no source clears the approval bar (stop after evaluation)"

## Secondary Notes (do not block on these)

- Preamble trigger condition and MCP contract section are slightly redundant; a one-line cross-reference would unify them but is not required for approval.
- "Evidence Order" step 4 (prior research briefs) has no conflict-resolution rule; note the gap but do not require a fix this turn.

## Stop / Continue Decision

**Continue** — apply the two-stop-condition fix via student, then approve.

## Approval Prediction

Very likely approved if the two-stop-condition fix is clean and distinct. Merge or inline fix risks another review cycle.
