# Steering — Iteration 2 / Teacher / Turn 1

**Target:** `skills/trainer-train-prompt/SKILL.md`  
**Iteration:** iteration-2  
**Agent:** teacher  
**Turn:** 1

## Evidence Used

- iteration-2 optimized-prompt.md (full content)
- validation/pytest.txt (849 passed)
- references/prompt-loop-contract.md
- evals/evals.json (4 evals, all llm_judge)
- manual-followup-report.json

## Decision: Continue

Two surgical fixes for iteration-3. All 5 adversary issues from iteration-1 are correctly fixed. Validation passes.

## Gaps for Iteration-3

### Gap 1 — Step 3: unnamed subdirectory
"Create the review subdirectory" → "Create the `engineer-prompt/` subdirectory"
**Reason:** Eval 1 rubric grades on producing the correct artifact path (`engineer-prompt/review.md`). Ambiguous "review subdirectory" causes students to omit the name.

### Gap 2 — Step 8: missing placeholder confirmation in manual follow-up
Append to Step 8: "After persisting `optimized-prompt.md`, confirm placeholder preservation (full set unchanged, no renames) before proceeding to election or write-back."
**Reason:** Eval 3 rubric explicitly requires "mentions placeholder preservation before write-back" in the manual follow-up context. Step 8 currently ends with "continue the loop" without mentioning this.

## Forecasted Student Mistake

Student will expand Step 8 into a sub-list or full duplication. Prevent: one appended sentence only.

## Stop-or-Continue

**Continue to iteration-3** for these two fixes. After iteration-3, the candidate should be ready for write-back.
