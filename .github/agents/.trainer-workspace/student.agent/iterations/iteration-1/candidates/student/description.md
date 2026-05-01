# Student Candidate

This is the optimized `student.agent.md` produced by the `@trainer` agent answering the `manual-followup-report.json` model prompt.

## Changes from Original

1. **Step 1 — Evidence priority order**: Added a numbered list (1)–(5) with explicit tiebreaker: most recent STEERING.md wins.
2. **Step 2b — No-op check**: New step inserted before drafting. If STEERING.md has no actionable critique or evidence gap is too large, report a justified no-op or request a new teacher turn.
3. **Step 6 — Structural self-check**: Replaced subjective exit criteria with three checkable gates: (a) all STEERING.md items addressed, (b) no new scope introduced, (c) approval prediction positive.
4. **Step 7 — Validation definition**: Added three concrete checks: placeholder tokens preserved, no unjustified constraint removal, no syntax errors.
5. **Engineer handoff trigger**: Sharpened to two concrete conditions with explicit exclusion for minor wording changes.
6. **Constraints section**: Added "Address only the critique items from the current teacher turn STEERING.md. Defer items that appear only in older summaries unless the current turn explicitly re-raises them."

## Predicted Judge Response

The judge would score this candidate higher than the original on evidence handling, self-check reliability, no-op accuracy, and validation auditability. The changes are targeted and do not expand the agent's scope or role.
