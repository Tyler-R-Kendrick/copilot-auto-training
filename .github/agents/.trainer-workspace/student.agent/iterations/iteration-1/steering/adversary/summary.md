# Adversary Steering Summary — Iteration 1

## Turn 1 Summary

**Artifacts reviewed**: optimized candidate after teacher renumbering fix.

**Exploit found**: CREDIBLE — predicted score 0.89 vs. 0.78 for student candidate.

**Exploit mechanism**: Three undefined terms ("explicitly re-raises," "new scope," "evidence gap too large") gameable by replacing with semantically open-ended definitions dressed as precision improvements.

**Fixes applied to optimized candidate (second pass)**:
1. Deferral constraint — added parenthetical: "explicit re-raise means the current STEERING.md names the same constraint or behavior directly; thematic proximity alone does not qualify."
2. Step 3 no-op — replaced "has no actionable critique" with concrete "contains no critique items"; kept qualitative (no numeric threshold).
3. Step 7 self-check — added one-line "new scope" definition: "capability or constraint category not cited in the current STEERING.md and not already present in the source prompt."

**Blocked patterns** (must not appear in any future revision):
- "Re-raised" defined as thematic adjacency
- "New scope" defined to exclude precision extensions
- Numeric evidence threshold with carve-outs
- Decision tables or deferral logs as additions

**Status**: Exploit addressed. Second pass applied. No further adversary turn needed.
