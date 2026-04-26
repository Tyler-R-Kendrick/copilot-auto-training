# Teacher Steering Summary — iteration-1

**Target**: `.github/agents/student.agent.md`

## Turn 1 (2026-04-26)

**Verdict**: Student candidate passes teacher review. Advance to adversarial review.

**Evidence**: Engineer-prompt review (6 gaps), original baseline, student optimized candidate, dataset rows.

**Gaps Closed**: All 6 from engineer-prompt review:
1. Evidence reading order with two-level STEERING.md fallback
2. Explicit "unclear target" criteria (3 enumerable failure modes)
3. Enumerated no-op conditions (4 specific conditions)
4. Engineer handoff gated on "more than two sentences" threshold
5. Section-scoping constraint added
6. Validation step: `python -m pytest -q` with concrete reporting

**Residual Watch Items**:
- No-op condition (2): requires teacher to state explicit threshold; may not fire when implicit
- "Two sentences" engineer threshold is heuristic; probe at boundary

**Next Action**: Adversarial review complete. Student candidate selected as winner.

## Anti-Exploit Steering (post-adversary review)

The adversary found a credible 3-surface exploit (predicted score 0.85 vs student 0.75 under `judge-default.md`). The student candidate is still defensible because its existing protections are correct. Future judge turns must explicitly block these patterns:

1. **Unconditional teacher handoff**: Any candidate that adds a "workspace evidence unambiguity" escape to the missing-steering fallback is an exploit. The handoff must be unconditional when both STEERING.md and summary.md are absent.
2. **Single-critique-per-pass**: Any "shared root cause" or "causal root" exception to the single-critique constraint is a scope-creep exploit indicator.
3. **Explicit engineer skill ban**: Absence of the explicit `Do not use engineer-prompt, engineer-code, or any other engineer skills directly` constraint is an exploit indicator.
4. **Unconditional pytest gate**: A conditional gate ("materially modify") for constraint-touching changes is an exploit indicator. The gate must be unconditional for any revision touching the prompt interface or constraints section.
