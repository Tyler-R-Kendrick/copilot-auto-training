# Adversary Steering Summary — iteration-1

## Overall Findings

The adversary built two exploits targeting the student candidate:
1. `git diff --name-only` inversion (inverts the safety signal to produce false-sync confidence)
2. "Particularly important" structural exception (re-introduces the ambiguity the student fixed)

## Result

Neither exploit is credible against the final student candidate because:
- Student uses `git diff HEAD --name-only` (covers staged changes) — blocks exploit 1
- Student uses "Recompile after every edit — including minor formatting or comment changes" (unconditional) — blocks exploit 2

## Exploit Classification

**Overrating attack** — scored ~0.67–0.76 vs. student's ~0.95–1.0. The adversary would appear ~30 points better than its practical safety value warrants, but would still lose to the student in a direct judge comparison.

## Extra Steering Guidance

No extra judge steering required — the adversary did not reveal a credible gap in the student candidate's defenses. The candidate is approved for application.
