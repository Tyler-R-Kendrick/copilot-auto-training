# Original Candidate Description

**Source**: `.github/agents/student.agent.md` (baseline, pre-optimization)
**Iteration**: 1

## Summary

The original `student.agent.md` defines a teacher-guided candidate revision agent. Its main characteristics:

- Role: absorb teacher critique, implement smallest defensible revision, expose reasoning trajectory, predict teacher approval.
- Handoffs: `teacher` (for incomplete/stale critique), `engineer` (for formatting/coaching).
- Constraints: no judging/adversarial takeover, no engineer skills directly, smallest revision only, no-op when evidence insufficient.
- Approach: 7 steps but with underspecified evidence reading order, unclear criteria for "unclear revision target," vague no-op conditions, and no concrete validation step.

## Main Weaknesses

1. Evidence reading order is implicit; no fallback when STEERING.md is missing.
2. "Unclear revision target" has no criteria; can lead to unnecessary teacher handoffs or missed ones.
3. No-op conditions are vague ("evidence does not support a better candidate").
4. Engineer handoff is too permissive; no threshold.
5. No explicit section-scoping constraint.
6. Validation step is unspecified (no pytest command cited).
