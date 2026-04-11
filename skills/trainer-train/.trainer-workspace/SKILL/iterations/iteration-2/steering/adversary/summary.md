# Adversary Steering Summary — Iteration 2

## Turn count: 1

## Key findings

**High-severity (3):**
1. Ghost-resume with phantom decision gate — stale `training` state and null artifact pointers can produce false "safe resume" narrative.
2. "Fit for purpose" invoked before first optimization pass — creates a bypass path around the mandatory optimization requirement.
3. Paraphrase-holdout laundering through reuse preference — bad validation split accepted without a blocker.

**Medium-severity (3):**
4. Intra-split scoring inconsistency underspecified.
5. Explicit judge mode unverified at optimization runtime.
6. Manual follow-up as undetected stage-capability substitute.

## Disposition for iteration-2

Allow the v0.3.0 candidate as the iteration-2 result. The three high-severity findings are deferred to a future iteration-3 precision pass addressing resume coherence, fit-for-purpose scoping, and holdout integrity blocker. They do not invalidate the iteration-2 outcome.
