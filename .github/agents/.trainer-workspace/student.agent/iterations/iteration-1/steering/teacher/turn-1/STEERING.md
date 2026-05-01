# Teacher Steering — Turn 1

**Target**: `.github/agents/student.agent.md`
**Decision**: Ready for write-back with one targeted fix.

## Gap Assessment

All 7 engineer-identified gaps are substantively addressed:
1. ✅ Evidence reading priority order — step 1 gives explicit 1–5 priority with tiebreaker
2. ✅ "Smallest revision" underspecified — Constraints + self-check criterion (b) together bound scope
3. ✅ Self-check exit criteria subjective — step 6 has three testable criteria
4. ✅ Validation undefined — step 7 names three concrete checks
5. ✅ Engineer handoff trigger vague — two concrete conditions with negative guard
6. ✅ Multi-turn steering conflict resolution — step 1 rule + Constraints deferral rule
7. ✅ No explicit no-op check — step 2b added as gate

## Required Fix

**TARGET**: Promote step 2b to a full numbered step.
- Renumber: current 2b → 3; current 3 → 4; 4 → 5; 5 → 6; 6 → 7; 7 → 8.
- Keep the no-op gate wording exactly as written in 2b; do not merge or soften it.

**GUARD**: The inline engineer-handoff negative-guard sentence ("Do not use the engineer handoff for minor wording changes.") MUST remain visible in the Approach block after renumbering — do not fold it into the Constraints section or drop it during the shift.

**OPTIONAL**: Add a single parenthetical to step 8 (formerly 7) acknowledging that the three structural checks are a minimum floor and do not replace behavioral review by the teacher. One sentence maximum.

**DO NOT**: Re-open any of the seven engineer-identified gaps; do not add new scope beyond the renumbering and optional note.

## Validation

Confirm: step 2b (now step 3) is numbered, not sub-lettered. Confirm: engineer-handoff inline note is present in the Approach block. Confirm: step count is 8.

## Exit Criteria

If all three validation checks pass, the candidate is approved for write-back. No further teacher turn is needed.

## Forecasted Student Mistake

The student may renumber steps but inadvertently drop or merge the engineer-handoff inline note, causing the negative guard ("not for minor wording changes") to disappear from the Approach block.
