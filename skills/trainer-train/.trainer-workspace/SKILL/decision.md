# Decision Summary — trainer-train SKILL.md

**Decision date:** 2026-04-10  
**Target file:** `skills/trainer-train/SKILL.md`  
**Workspace:** `skills/trainer-train/.trainer-workspace/SKILL/`  
**Run iterations:** 2  
**Winning candidate:** `iterations/iteration-2/optimize/optimized-prompt.md` (v0.3.0)

---

## Decision: Recommend v0.3.0 as the write-back candidate

The two-iteration loop produced a materially improved candidate. The engineer review's five failure modes are all addressed. The teacher's four coaching points were applied precisely in iteration-2. The adversary's three high-severity findings are credible but deferred to a future iteration-3, as they do not invalidate the v0.3.0 candidate.

**Write-back is NOT applied in this run** per the constraint that no changes should be written to `SKILL.md` directly. The recommended candidate is available at:

```
skills/trainer-train/.trainer-workspace/SKILL/iterations/iteration-2/optimize/optimized-prompt.md
```

---

## What changed across iterations

### Iteration 1 (v0.1.0 → v0.2.0)

Addressed all five engineer-review failure modes:

1. **Over-abstraction / resumption gap** → Added explicit resumption logic in Core Workflow step 1 (checks `workflow_state: "training"`, audits existing artifacts, skips completed stages, no new iteration directory for resumed run)
2. **Missing reference cues** → Added callout at document top; inline "read the relevant reference file" cue at each Core Workflow step
3. **Judge-mode vagueness** → Replaced "richer scoring" with three named modes: Exact-match, Structured/normalization-aware, Open-ended/LLM judge — each with explicit field discriminators
4. **Low-visibility no-op / blocker rule** → Added dedicated **Blocker-first rule** section before Core Workflow
5. **Weak write-back gate** → Changed "validation passes" to "validation passes **and** the decision summary is written" in two places

### Iteration 2 (v0.2.0 → v0.3.0)

Applied four teacher coaching points as a narrow clarity-and-precedence pass:

1. **Blocker-first scope** → Removed `validation has not passed on the current candidate` bullet (write-back gate, not pre-execution blocker)
2. **Judge-mode precedence** → Added: "When a row declares `scoring`, treat that as authoritative. Only infer from fields when `scoring` is absent." Plus inconsistency-stop rule.
3. **Reference callout → Before you start section** → Converted blockquote to a 3-bullet procedural section before "When to use this skill"
4. **Output contract items 2 and 6** → Item 2 = current-turn stage decisions; Item 6 = next required action for loop continuation

---

## Deferred items (adversary findings — iteration-3 scope)

| # | Finding | Severity |
|---|---|---|
| 1 | Ghost-resume: stale `training` state + nonexistent artifact pointers can produce false compliance narrative | HIGH |
| 2 | "Fit for purpose" can bypass mandatory first optimization pass | HIGH |
| 3 | Paraphrase-holdout laundering through reuse preference | HIGH |
| 4 | Intra-split scoring inconsistency underspecified | MEDIUM |
| 5 | Explicit judge mode unverified at optimization runtime | MEDIUM |
| 6 | Manual follow-up as undetected stage-capability substitute | MEDIUM |

---

## Validation outcome

- Structural validation: PASS
- Eval heuristic (all 4 evals): PASS
- Repository test suite: BLOCKED (`opto` module not available) — not a candidate-quality failure

---

## Next step

Apply v0.3.0 candidate to `SKILL.md` when the operator approves. Then run the full repository test suite with `opto` available to confirm no regressions. Consider an iteration-3 to address the three high-severity adversary findings.
