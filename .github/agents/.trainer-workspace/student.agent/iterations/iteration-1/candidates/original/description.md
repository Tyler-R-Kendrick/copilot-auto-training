# Original Candidate Description

**Source:** `student.agent.md` (unmodified baseline)

**Summary:** The original student agent prompt provides correct role scoping and handoff contracts but has six precision gaps identified in the engineer-prompt review:
1. No evidence reading priority order
2. Approval prediction criterion underspecified
3. Loop exit criteria implicit
4. No conflict resolution rule for stale vs. fresh steering artifacts
5. "Smallest defensible revision" not bounded
6. Validation step unspecified
