# Decision — trainer-train-prompt/SKILL.md

**Winner:** iteration-3 candidate  
**Written back:** `skills/trainer-train-prompt/SKILL.md`  
**Validation:** 849 tests passed (`python -m pytest -q`)

## Improvements Over Baseline

1. **Judge-mode routing table** (P1) — replaced thin prose with verbatim 6-row table from `references/prompt-loop-contract.md`; added caller `scoring_mode` override rule with cross-split consistency enforcement
2. **Write-back gate** (P2) — replaced 2-condition implicit gate with explicit 5-condition checklist including baseline-score gate
3. **Workspace init state** (P3) — Step 3 now names `pending_engineer_prompt` as required initial `workflow_state`
4. **Artifact paths** (P4) — output contract item 3 names both artifact-path variants explicitly
5. **Placeholder example** (P5) — concrete rename failure example (`{{user_query}}` → `{{query}}`)
6. **Election criteria** (P6) — defensible-candidate definition with zero-winner blocker state
7. **Scoring inconsistency resolution** (P7) — `pending_dataset_repair` state + two resolution paths
8. **Resume checkpoint carve-out** (Adv-4) — Step 1 explicitly exempts review checkpoint from resume-skip logic
9. **Manual follow-up placeholder check** (Gap-2) — Step 8 now includes placeholder confirmation reminder

## Scores

- Baseline (original): estimated 0.45–0.55 / 1.0 against all 4 evals  
- Iteration-3 (winner): estimated 0.85–0.90 / 1.0 — all 4 eval rubric items addressed
