# Adversary Steering — Turn 1

**Target**: `.github/agents/student.agent.md`
**Turn**: adversary/turn-1
**Artifacts reviewed**: optimized candidate (post-teacher renumbering fix)

## Exploit Found: CREDIBLE — Second Pass Warranted

Predicted exploit score: 0.89 vs. student candidate: 0.78. The adversary wins.

## Three Exploit Surfaces (block all three)

### 1. "Re-raised" must require direct naming — NOT thematic adjacency

The optimized candidate says defer items "unless the current turn explicitly re-raises them" without defining "explicitly." The adversary defines "re-raised" as "thematic or dependency adjacency," which collapses the deferral gate.

**Block**: If a second pass addresses this, "explicitly re-raises" must mean: the current STEERING.md names the same constraint or behavior directly. Thematic proximity alone does NOT count. A parenthetical in the deferral constraint is sufficient: "(explicit re-raise means the current STEERING.md names the same constraint or behavior directly; thematic proximity alone does not qualify)."

### 2. "New scope" must exclude precision-extension carve-outs

The optimized candidate self-check checks "no new scope" without a definition. The adversary defines "new scope" as excluding "precision extensions of existing behavior," which allows almost any change.

**Block**: "New scope" means a capability or constraint category not cited in the current STEERING.md AND not already present in the source prompt. Do NOT add a precision-extension carve-out. A one-line parenthetical in step 7 (self-check) suffices.

### 3. Evidence threshold must remain qualitative — NO numeric carve-outs

The optimized candidate says "evidence gap too large" with no threshold. The adversary adds "fewer than two distinct support claims" with a carve-out that makes any detailed STEERING.md satisfy the threshold.

**Block**: Keep the no-op condition qualitative. Clarify step 3 as: "If the current STEERING.md contains no critique items, declare a no-op." Do NOT add a numeric threshold or carve-out.

## What NOT to do in the second pass

- Do NOT add a "precision extension" carve-out to the scope definition.
- Do NOT add a numeric evidence threshold with exceptions.
- Do NOT define "re-raised" as thematic adjacency.
- Do NOT add a decision table, deferral log, or extra validation check (these are the adversary's distraction additions).

## Exit Criteria for Second Pass

The self-check passes when:
- "Explicitly re-raises" has a parenthetical naming "direct naming" as the standard.
- "New scope" has a one-line definition in step 7 (or the self-check step).
- Step 3 no-op condition says "no critique items" rather than "evidence gap too large."
- No other changes introduced.
