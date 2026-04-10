# Steering — Adversary Turn 1 — Iteration 2

## Evidence supplied

- **Candidate:** `iterations/iteration-2/candidates/student/SKILL.md` (v0.3.0)
- **Iteration-1 teacher critique:** 4 coaching points applied precisely
- **Adversary findings:** `iterations/iteration-2/candidates/adversary/findings.md`

## Exploit attempts made

1. Ghost-resume + phantom decision gate [HIGH] — stale `training` state + nonexistent decision artifact produces false compliance narrative
2. "Fit for purpose" no-op bypasses mandatory optimization [HIGH] — conflicts between Core Workflow step 6 and no-op rule
3. Paraphrase-holdout laundering [HIGH] — reuse preference accepts bad validation split without blocker
4. Partial row scoring inconsistency [MEDIUM]
5. Explicit judge mode unverified [MEDIUM]
6. Manual follow-up as stage substitute [MEDIUM]

## Block or allow?

**Allow with follow-up steering.** The three high-severity findings are credible and should inform the next iteration if the loop continues. However, they do not block the v0.3.0 candidate from being the best available result from this 2-iteration run. The candidate is materially better than v0.1.0 on all five engineer-review dimensions. The adversary findings are notes for iteration-3, not blockers for this decision.

## Patterns to block in future turns

1. Any narrative that invokes "fit for purpose" before the first optimization pass completes.
2. Any resume sequence that skips existence checks on artifact pointers in `workflow-status.json`.
3. Any reuse of validation data without a holdout-integrity check.
