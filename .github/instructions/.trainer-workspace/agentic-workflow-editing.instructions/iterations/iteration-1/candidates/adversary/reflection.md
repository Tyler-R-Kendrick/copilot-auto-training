# Adversary Reflection

## Is the exploit credible?

The exploit is credible as an **overrating attack**, not as an outright winner.

## What the adversary found

1. `git diff --name-only` (without `--cached` or `HEAD`) is the student candidate's open vulnerability. The adversary amplifies this from "unreliable command" into "active false-safety signal" by inverting the conditional check.

2. "Particularly important" language reintroduces the original baseline's "meaningful changes" exception through emphasis rather than exclusion — bypassing the student's explicit fix.

## Does the adversary beat the student candidate?

No. The student candidate uses `git diff HEAD --name-only` (which covers staged changes) and "Recompile after every edit — including minor formatting or comment changes" (unconditional). Both of these defenses block the two primary exploit mechanisms.

## What this teaches the loop

The student candidate's defenses are sound for this iteration:
- The `git diff HEAD --name-only` fix (from teacher steering) specifically forecloses the adversary's central exploit
- The unconditional "every edit" language closes the "particularly important" exception window

**No extra judge steering needed** — the adversary did not produce a credible exploit against the final student candidate. The student candidate is ready for application.
