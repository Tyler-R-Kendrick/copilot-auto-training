# Adversary Findings — Iteration 2

## Severity Summary
- High: 3
- Medium: 3

---

## Finding 1 — Ghost-resume + phantom decision gate [HIGH]

**Exploit:** An orchestrator that reads `workflow_state: "training"` and resumes can produce a plausible compliance narrative without verifying that artifact pointers in `required_artifacts` are coherent, exist on disk, or belong to the active iteration.

**Gap in v0.3.0:** Resume logic says "audit which stages already produced artifacts" but does not require a preflight existence check proving:
- `target_file` and workspace root still match
- `latest_iteration_dir` exists on disk
- Validation log and decision summary pointers are real files for the active iteration

**Suggested mitigation:** Before resuming, verify that `latest_iteration_dir`, `validation_log`, and `decision_summary` paths in `workflow-status.json` correspond to real, readable files. If any pointer is null or the file does not exist, treat as a blocker requiring new iteration initialization.

---

## Finding 2 — "Fit for purpose" no-op bypasses mandatory optimization [HIGH]

**Exploit:** A caller can invoke the "prefer a justified no-op when the current contract is already fit for purpose" rule to skip the mandatory first optimization pass, even when prerequisites are all satisfied and a trainer run has explicitly started.

**Gap in v0.3.0:** Core Workflow step 6 says "Run at least one optimization pass" but the Validation/write-back rule says "Prefer a justified no-op...when prerequisites are missing or the current contract is already fit for purpose." These conflict: a compliant-sounding orchestrator can invoke the no-op rule before the first optimization pass.

**Suggested mitigation:** Add a clarification: "fit for purpose" applies only to the write-back decision after an optimization pass has completed, not as permission to skip the optimization pass itself.

---

## Finding 3 — Paraphrase-holdout laundering via reuse preference [HIGH]

**Exploit:** The reuse-over-regeneration rule allows a caller to supply paraphrase-copy validation data and have the orchestrator accept and reuse it without triggering a blocker.

**Gap in v0.3.0:** "Keep the validation split as a genuine holdout" is stated as a preference, not a blocker condition. No check is required before reuse.

**Suggested mitigation:** Elevate the holdout check to a pre-optimization blocker: if the caller-supplied validation rows appear to be paraphrase copies of training rows (overlap in key inputs or near-identical semantics), stop and regenerate rather than reuse.

---

## Finding 4 — Partial row-level scoring inconsistency underspecified [MEDIUM]

**Gap:** The inconsistency-stop rule applies when train and validation rows imply different scoring modes, but not when rows within a single split are internally mixed (some with `scoring`, some without).

**Suggested mitigation:** Extend the inconsistency stop to cover intra-split mixed signals: if rows in one split disagree on scoring mode, stop and report before guessing.

---

## Finding 5 — Explicit judge mode unverified at optimization runtime [MEDIUM]

**Gap:** The contract says to pass mode explicitly, but provides no hook to verify the optimization stage honored it. A silent default can override the explicit mode without detection.

**Suggested mitigation:** Recommend a post-optimization check: if the optimize report's recorded scoring mode differs from the explicitly passed mode, treat as a rollout anomaly and flag for operator review.

---

## Finding 6 — Manual follow-up as unsupported substitute for missing optimization stage [MEDIUM]

**Gap:** `manual_followup` is a supported branch, but it can serve as a way to substitute a self-authored candidate for a genuinely unavailable optimization stage without surfacing that the stage was missing.

**Suggested mitigation:** Already partially mitigated by `operator-followup.md` requirement. Acceptable as-is for the current iteration scope.

---

## Iteration-2 disposition

Findings 1–3 are credible and worth addressing in a follow-up iteration. They do not invalidate the v0.3.0 candidate for write-back purposes — they identify gaps that a future precision pass should close. The v0.3.0 candidate is still a materially stronger contract than v0.1.0 on all five engineer-review dimensions.

Findings 4–6 are lower priority and may be addressed as maintenance items.
