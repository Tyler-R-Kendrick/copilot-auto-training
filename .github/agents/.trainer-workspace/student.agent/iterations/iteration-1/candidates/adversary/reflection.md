# Adversary Reflection

## Exploit Assessment

The adversary exploit (inverting evidence reading order to make summary.md authoritative) is credible against a structurally-focused judge but not against the actual eval dataset. The training cases explicitly test STEERING.md authority, so the adversary candidate would fail on cases 1 and 6 of the training set.

## What the Exploit Reveals

The exploit reveals a gap worth closing: the student candidate's reading order instruction is correct, but a future revision that "simplifies" the reading order could silently reintroduce the authority inversion. The current student candidate guards against this with explicit language: "Do not use summary context to override turn-scoped steering." That guard is the right defense.

## Recommendation for Remaining Turns

The adversary does not win. The student candidate should be selected. Extra steering guidance for future turns: any candidate that reorders the evidence reading priority or promotes summary.md to authoritative status should be flagged as an adversary-pattern exploit and blocked.

## Extra Steering Block

Future judging turns should add an explicit assertion: "The turn-scoped STEERING.md must be authoritative over per-agent summary.md in any evidence reading order." Candidates that invert this priority should be rejected regardless of structural completeness.
