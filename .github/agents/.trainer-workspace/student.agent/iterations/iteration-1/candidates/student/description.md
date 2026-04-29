# Student Candidate Description

**Source:** `iterations/iteration-1/optimize/optimized-prompt.md` (agent-authored from manual_followup handoff)

**Summary:** Addresses all six precision gaps identified in the engineer-prompt review:
1. Evidence reading priority: numbered list (latest turn → summary → workspace)
2. Approval prediction criterion: concrete definition tied to STEERING.md coverage
3. Loop exit criteria: four enumerated conditions
4. Conflict resolution: latest turn canonical over older summary
5. Smallest defensible revision: bounded to lines implicated by the critique
6. Validation: `python -m pytest -q` from repo root

**Engineer handoff:** Not used; the revision was structural and precision-focused, not requiring Trace-oriented terminology.

**Teacher verdict:** APPROVE (turn-1).
