# Student Candidate Description

This is the optimized candidate produced by the trainer agent in manual_followup mode.

## Key Improvements Over Baseline

1. **Explicit evidence reading order**: Five-step sequence with numbered priority (iteration goal → STEERING.md → summary.md → candidate → validation)
2. **Artifact precedence rule**: Turn-scoped STEERING.md takes priority over rolling summary.md when they conflict
3. **Sharpened engineer handoff trigger**: Three specific conditions replace the vague original trigger
4. **Defined smallest defensible revision**: One change per iteration goal, verifiable against current steering, narrow enough for single-pass teacher review
5. **Teacher-approval criteria**: Four explicit conditions the teacher would check before approving
6. **Revision scope boundary**: Fix only what the iteration goal and critique address; note but do not fix adjacent issues
7. **Contradiction exit**: After two consecutive teacher turns with the same unresolved contradiction, report as a blocker

## Predicted Judge Response

The judge would score this candidate higher than the original on precision-sensitive criteria because it removes ambiguity from the five main under-specified areas. The revision is defensible and minimal: no new placeholders, no interface changes, no scope expansion. Scores likely in the 0.8–0.95 range for the training cases.
