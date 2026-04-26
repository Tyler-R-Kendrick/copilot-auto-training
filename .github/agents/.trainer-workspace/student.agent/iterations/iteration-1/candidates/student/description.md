# Student Candidate Description

**Source**: `iterations/iteration-1/optimize/optimized-prompt.md` (agent-authored via manual_followup)
**Iteration**: 1
**Optimization**: Manual followup — no live model; @trainer agent answered model_prompt

## Summary

The student candidate improves `student.agent.md` by closing all 6 gaps identified in the engineer-prompt review:

1. **Evidence reading order** (Approach step 1): Added explicit numbered reading order (teacher goal → critique → STEERING.md → summary.md → workspace evidence) with a two-level fallback: if STEERING.md missing, use summary.md; if both missing/empty, hand off to teacher.

2. **Unclear target criteria** (Approach step 2): Replaced implicit "if unclear" with three specific failure modes: STEERING.md missing/empty; summary vs. turn contradiction; critique with no section/behavior/success criterion.

3. **No-op conditions** (Constraints): Enumerated 4 specific conditions that justify a no-op, replacing the vague "evidence does not support a better candidate."

4. **Engineer handoff threshold** (body + Approach step 4): Tightened to "only when the teacher-ready explanation requires more than two sentences to format inline, or when Trace-specific or prompt-engineering domain expertise is explicitly needed."

5. **Section-scoping constraint** (Constraints): Added "Fix the single strongest critique; do not address every open comment" and "When the critique names a specific section, scope the revision to that section only."

6. **Validation step** (Approach step 7): Added `python -m pytest -q` from repo root with concrete reporting requirement.

## Teacher Review Verdict

All 6 gaps closed. No further student revision needed. Residual fragilities are appropriate for adversarial stress-testing.
