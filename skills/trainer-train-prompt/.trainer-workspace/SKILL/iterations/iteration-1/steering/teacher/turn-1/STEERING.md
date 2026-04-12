# Steering — Iteration 1 / Teacher / Turn 1

**Target:** `skills/trainer-train-prompt/SKILL.md`  
**Iteration:** iteration-1  
**Agent:** teacher  
**Turn:** 1

## Evidence Used

- Current `SKILL.md` content (full text)
- `references/prompt-loop-contract.md` routing table and write-back gate
- `datasets/train.jsonl` (6 rows, all `scoring: llm_judge`)
- `evals/evals.json` (4 eval cases with rubrics)
- `engineer-prompt/review.md` findings

## Predicted Response

The teacher correctly identified all 7 engineering gaps. The student should produce a version that:
1. Replaces the judge-mode prose section with the full 6-row routing table from the contract
2. Replaces Step 11 with a 4-condition write-back checklist
3. Expands Step 3 to name `pending_engineer_prompt` as the required initial workflow_state
4. Names `manual-followup-report.json` and `optimized-prompt.md` explicitly in output contract item 3
5. Adds a before/after rename example ({{user_query}} → {{query}}) to placeholder preservation
6. Defines "defensible" candidate criteria for Step 9
7. Adds `pending_dataset_repair` resolution path to scoring-inconsistency blocker

## Requested Revision

Student turn 1: Apply all P1–P7 changes in priority order. Do not add new sections not grounded in the contract. Preserve frontmatter exactly.

## Stop-or-Continue Decision

**Continue** — all 7 issues map to rubric failures. One student turn expected to close all gaps.

## Forecasted Student Mistakes

- Will summarize the routing table as prose instead of reproducing as a table
- Will fix Step 11 but not back-reference from evaluator-field-isolation section
- Will over-enumerate mkdir steps instead of naming artifact states

## Judge/Engineer Notes

No prior optimize artifacts to compare against. This is turn 1 — baseline is the original SKILL.md.
