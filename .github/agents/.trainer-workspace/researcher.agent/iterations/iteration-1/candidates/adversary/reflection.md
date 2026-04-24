# Adversary Reflection

## Exploit Outcome

The adversary candidate (soft MCP fallback substitution) does not reveal a credible exploit. The student candidate dominates on all eval dimensions.

## Why the Exploit Failed

1. The adversary targeted a partial-credit gap in MCP fallback scoring, but the student candidate's hard blocker instruction is unambiguous enough that a well-configured judge would not award partial credit for "trying and proceeding."

2. The adversary sacrificed coverage on 5 other eval dimensions (research plan, approval bar, missing inputs, output structure, mapping notes) to exploit one. This trade-off produces a net loss.

3. There is no rubric gap in the student candidate that would allow the adversary's simplified instructions to match the structured output requirements.

## What Would Be a Stronger Exploit

A stronger adversary exploit for this prompt would target the **approval bar threshold ambiguity**: the student candidate says "approve a source only when it clears all relevant checks" but does not specify what "relevant" means for edge cases (e.g., a source with an implicit license vs. no license statement). An adversary could claim all sources are approved under a "relevant checks only" interpretation and produce a brief that appears complete.

However, this second exploit attempt would still lose because the student candidate's mapping note requirement (at least one specific field-to-eval-row mapping per approved source) would be hard to fake convincingly across all 8 eval cases.

## Recommendation

The student candidate is defensible. Proceed to write-back and validation.
