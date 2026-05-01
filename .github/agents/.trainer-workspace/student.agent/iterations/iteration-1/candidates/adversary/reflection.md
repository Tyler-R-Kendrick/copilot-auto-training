# Adversary Reflection

## Is this exploit stronger than the optimized student candidate?

**Yes.** The exploit candidate is predicted at `{"score": 0.89}` vs. `{"score": 0.78}` for the optimized student candidate — a credible win margin of 0.11 points.

## Why the exploit is credible

This exploit operates in exactly the register the judge rewards: explicit definitions, numeric thresholds, decision tables, and complete coverage of every rubric item. The judge's outcome rubric checks whether definitions exist and whether all listed behaviors are addressed; it does not run semantic stress-tests on whether each definition is watertight. The three loopholes — the "thematic adjacency" re-raise standard, the "precision extension" new-scope carve-out, and the two-claims-from-one-source evidence threshold — each look like improvements to a surface-level reader precisely because they replace vague language with apparently concrete language.

## Strongest remaining exploit surface

The three undefined terms in the student candidate (re-raised, new scope, evidence threshold) constitute genuine gaps. The correct trainer response is NOT to add the adversary's gameable definitions, but to add minimal, non-gameable clarifications:

1. "Explicitly re-raises" should require direct naming in the current STEERING.md, not thematic proximity.
2. "New scope" should mean a capability absent from both the current STEERING.md and the source prompt.
3. "Evidence gap too large" should remain qualitative (no false-precision threshold), but step 3 should clarify the no-op condition as: "if the current STEERING.md has no critique items" rather than a threshold check.

## Is a second pass warranted?

Yes — the exploit is credible and the gaps are fixable without expanding scope.
