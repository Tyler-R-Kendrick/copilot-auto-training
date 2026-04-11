# Teacher Steering Summary — Iteration 1

## Turn count: 1

## Key critique from turn 1

The v0.2.0 candidate successfully addresses all five engineer-review failure modes. The next gain is **clarity tuning**, not structural expansion. The teacher recommends a narrow scope-and-precedence pass for iteration-2.

### What to change in iteration-2

1. **Blocker-first section:** Keep it early, but scope it only to **pre-execution blockers and resume-state handling**. Remove the bullet `validation has not passed on the current candidate` — that is a write-back gate, not a reason the loop cannot continue. Keep validation-pass language only in the Validation/write-back section.

2. **Judge-mode inference:** Add explicit precedence rule: "When a row declares `scoring`, treat that as authoritative. Only infer from fields such as `expected`, `expected_json`, `reference`, or `criteria` when `scoring` is absent." Also add: "If train/validation rows imply different scoring modes, stop and report dataset inconsistency instead of guessing."

3. **Reference callout box → Before you start section:** Convert the top callout box into a short `Before you start` section (2–3 bullets max) immediately before "When to use this skill" so reference-reading is treated as procedure, not commentary.

4. **Output contract items 2 and 6:** Rewrite to divide by time horizon:
   - Item 2 = current-turn stage decisions (reuse choice, judge mode, selected branch, blockers encountered)
   - Item 6 = next required action or resume guidance if the loop is not terminal

## Stop-or-continue

**Continue to iteration-2.** One narrow revision pass is justified. After iteration-2, the loop should reach the accept/stop threshold assuming the student incorporates the four specific coaching points.

## Confidence level

Moderate — no optimize report, judge comparison output, or failure traces are available. Recommendations on exact-match and structured scoring branches are based on robustness reasoning only.
