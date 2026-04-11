# Steering — Teacher Turn 1 — Iteration 1

## Evidence supplied

- **Source:** `inputs/source/SKILL.md` (v0.1.0 baseline)
- **Candidate:** `iterations/iteration-1/candidates/student/SKILL.md` (v0.2.0, manual_followup path)
- **Engineer review:** `engineer-prompt/review.md`
- **Train dataset:** `skills/trainer-train/datasets/train.jsonl` (5 rows, all `scoring: "llm_judge"`)
- **Val dataset:** `skills/trainer-train/datasets/val.jsonl` (5 rows, same shape)
- **Eval manifest:** `skills/trainer-train/evals/evals.json` (4 structured eval cases)
- **Optimize report:** `iterations/iteration-1/optimize/manual-followup-report.json` (mode=manual_followup)

## What changed in iteration-1 candidate vs. baseline

| Dimension | Baseline (v0.1.0) | Candidate (v0.2.0) |
|---|---|---|
| Reference file cues | One sentence at top, easy to skip | Callout box before Core Workflow + inline cues at uncertain steps |
| Blocker-first | Buried in loop rules | Dedicated section before Core Workflow |
| Judge-mode clarity | "exact-match / richer scoring" (2 shapes) | 3 named modes with explicit discriminators |
| Resumption logic | Not mentioned in Core Workflow steps | Step 1 explicitly handles `training` state resumption |
| Write-back gate | "validation passes" | "validation passes AND decision summary is written" (dual gate) |

## Predicted response to eval cases

- **Eval 1 (workspace init):** Both versions likely pass — candidate adds explicit resumption check.
- **Eval 2 (missing-data path):** Both versions pass — candidate adds "keep authored evals, train, and val as separate files" as an extra signal.
- **Eval 3 (manual_followup recovery):** Candidate strongly passes — has 6-step enumerated recovery sequence. Baseline is weaker (1 paragraph).
- **Eval 4 (candidate/steering staging):** Candidate passes — references collaboration contract for bundle layout.
- **Train row 5 (blocker-first):** Candidate strongly passes — dedicated blocker-first section. Baseline was marginal.

## Requested revision from teacher

Please assess:

1. Whether the blocker-first section and the validation/write-back rule duplicate each other enough to warrant consolidation without losing the signal.
2. Whether the three-mode judge-mode taxonomy (exact-match / structured / open-ended) is clear enough, or whether the discriminators need sharper language (e.g., row-field examples).
3. Whether the reference-file callout box is well-placed, or whether it should move to a "Before you start" preamble section.
4. Whether the candidate's output contract (item 6 now reads "next-step guidance when the loop should continue") is distinct enough from item 2's "stage decision" to avoid ambiguity.

## Stop-or-continue decision

**Continue.** The candidate is stronger than the baseline across all five failure modes. At least one more iteration is warranted to address potential verbosity and duplication before finalizing.

## Agent notes

- No judge subagent invoked this turn; the candidate manifest's predicted scores are sufficient for this steering pass.
- Adversarial review deferred to iteration-2 after teacher critique is incorporated.
