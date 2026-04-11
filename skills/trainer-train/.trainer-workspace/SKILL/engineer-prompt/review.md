# Engineer-Prompt Review — skills/trainer-train/SKILL.md

**Review date:** 2026-04-10  
**Reviewer:** task agent  
**Target file:** `skills/trainer-train/SKILL.md`

---

## Summary

The first draft captures the trainer loop at a high level, but it still risks under-specifying several behaviors that matter during real trainer runs.

1. **Over-abstraction risk** — The prompt intentionally avoids hard-coding stage capability names, but it may now be too vague about how those stages are selected, reused, and resumed.
2. **Artifact precision** — The top-level prompt mentions steering and candidate bundles, yet the exact checkpoint expectations mostly live in references. The body may need slightly stronger cues about when to consult those deeper assets.
3. **Judge-mode clarity** — The scoring-mode section is directionally correct but could better distinguish exact-match, structured, and open-ended judge cases.
4. **No-op discipline** — The blocker or no-op rule is present, but it could be made more visible so the orchestrator resists speculative rewrites when prerequisites are missing.
5. **Write-back safety** — The write-back rule is sound, though the prompt could reinforce that validation and decision artifacts are both required before touching the source file.

---

## Likely failure modes

- The orchestrator skips reading the deeper workspace reference and improvises artifact paths.
- The orchestrator optimizes before verifying whether existing datasets and evals can be reused.
- The orchestrator collapses richer scoring cases back to exact-match behavior.
- The orchestrator treats manual follow-up as a blocker instead of a supported branch.
- The orchestrator writes back a candidate before the decision summary and validation log are both ready.

---

## Validation plan

1. Keep the authored eval cases focused on workspace setup, missing-data recovery, manual follow-up recovery, and candidate or steering organization.
2. Keep the train and validation datasets in `llm_judge` mode so optimization can reward higher-fidelity orchestration language.
3. Run at least two trainer iterations against this skill contract and compare the resulting optimized candidates against the draft.
4. Re-run targeted tests and then the full repository suite after applying any accepted revisions.

---

## Next optimization hypothesis

The next revision should stay indirect about concrete stage capability names, but tighten the body around three ideas:

1. when to read the deeper reference files
2. how reuse, judge-mode inference, and manual follow-up alter stage sequencing
3. why blocker-first behavior is safer than speculative rewriting
