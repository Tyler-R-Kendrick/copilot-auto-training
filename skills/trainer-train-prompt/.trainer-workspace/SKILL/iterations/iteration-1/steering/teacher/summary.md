# Teacher Steering Summary — Iteration 1

**Target:** `skills/trainer-train-prompt/SKILL.md`  
**Iteration:** iteration-1

## Turn 1

**Evidence:** Full SKILL.md, prompt-loop-contract.md, datasets, evals, engineering review  
**Decision:** Continue. 7 gaps identified, all map to rubric failures.  
**Priority order:** P1 routing table → P2 write-back gate → P3 workspace init state → P4 artifact paths → P5 placeholder example → P6 election criteria → P7 inconsistency resolution  
**Student mistakes predicted:** Table as prose, missing back-reference from evaluator-field-isolation, over-specifying mkdir  

## Outcome

Student candidate applied all 7 revisions correctly. Key improvements:
- Judge-mode routing table from contract is now verbatim in skill
- Step 11 has explicit 4-condition write-back gate
- Step 3 now names `pending_engineer_prompt` as initial state
- Output contract item 3 names both artifact-path variants
- Placeholder preservation has concrete rename example
- Election section has defensible-candidate criteria
- Blocker rule has `pending_dataset_repair` resolution path

## Adversary Findings (Turn 1 → Iteration 2 action items)

1. [HIGH] `scoring_mode` override bypasses cross-split detection — fix wording to "skip per-row inference but still validate cross-split consistency"
2. [HIGH] Single-candidate write-back allows regression — add gate condition 5: candidate score ≥ baseline
3. [MEDIUM] "Content hash" is unactionable, not in workspace schema — revert to "source snapshot under inputs/source/"
4. [MEDIUM] Resume-path skip (Step 1) can bypass Step 2 review checkpoint — add explicit carve-out
5. [LOW] Election zero-winner path has no termination path — add `pending_iteration_review` blocker state
