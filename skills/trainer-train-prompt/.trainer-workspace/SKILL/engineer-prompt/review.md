# Engineering Review — trainer-train-prompt/SKILL.md

**Reviewed:** 2026-04-12  
**Target:** `skills/trainer-train-prompt/SKILL.md`  
**Workspace:** `skills/trainer-train-prompt/.trainer-workspace/SKILL/`

---

## Summary

The `trainer-train-prompt` SKILL.md is the orchestration contract for trainer-loop execution against prompt-like targets (`.prompt.md`, `.prompty`, `.instructions.md`, system prompts). It is consumed by the `@trainer` agent when the selected target is a prompt file, not a code or skill file.

---

## Strengths

1. **Clear target-type declaration** — The frontmatter `description` correctly scopes the skill to natural-language instruction files.
2. **Ordered core workflow** — Steps 1–11 provide a traceable execution order with actionable sub-rules.
3. **Blocker-first rule** — Explicit stop conditions (missing review, missing datasets, inconsistent splits) prevent silent failures.
4. **Manual follow-up path** — Section 8 documents the `manual_followup` branch clearly.
5. **Output contract** — Seven-point output contract gives callers a verifiable checklist.

---

## Weaknesses and Improvement Opportunities

1. **Judge-mode section is thin** — Section "Judge mode" only restates the default; it does not reference the routing table in `references/prompt-loop-contract.md` or explain when `custom` mode applies.
2. **Placeholder preservation lacks examples** — The rule exists but gives no concrete illustration of what a failing candidate looks like (e.g., renamed `{{input}}` → `{input}`).
3. **Step 3 (initialize workspace) is vague** — It says "create or update `workflow-status.json`, source snapshot, review subdirectory …" without naming the helper script (`trainer-workspace.py`).
4. **Election branch underdeveloped** — Step 9 says "use the caller-supplied elector when optimization produces more than one defensible candidate" but gives no criteria for when multiple candidates are "defensible."
5. **Output contract is incomplete** — Item 3 says "Optimization or manual follow-up status with artifact paths" but does not list which artifact paths are expected (e.g., `optimize-report.json` vs. `manual-followup-report.json`).
6. **Evaluator field isolation rule is buried** — It appears in "Prompt-specific loop rules" but is not cross-referenced from Step 11 (write-back), which is where violations are most likely caught.
7. **Scoring inconsistency blocker lacks resolution path** — The blocker rule mentions reporting inconsistency between train/val splits but does not suggest how to resolve it (re-synthesize, pick authoritative split, etc.).
8. **No version bump guidance** — The frontmatter has `version: "0.1.0"` but no note about when or how the version should be bumped after optimization.

---

## Dataset and Eval Assessment

- **Train split:** 6 rows, all `scoring: llm_judge` with `reference` + `criteria` fields. Consistent shape.
- **Val split:** 4 rows, all `scoring: llm_judge` with `reference` + `criteria` fields. Consistent with train.
- **Judge mode:** `llm_judge` (authoritative from explicit `scoring` field; confirmed by `reference`+`criteria` presence).
- **No placeholders** in the SKILL.md that need preservation tracking (the skill itself is not a template).
- **Eval manifest:** 4 evals, all `scoring: "llm_judge"` — consistent with dataset.

---

## Rewrite Notes for Optimizer

- Keep the frontmatter block unchanged (name, description, argument-hint, license, metadata).
- Strengthen the judge-mode section with a direct reference to the routing table and add the `custom` mode case.
- Add one concrete placeholder-preservation example in the "Placeholder preservation" sub-rule.
- Reference `python .github/hooks/trainer-workspace.py` explicitly in Step 3.
- Expand Step 9 (election) with a simple criterion: "run election when two or more candidates score within 5% of each other on the validation split."
- Add artifact-path specifics to output-contract item 3.
- Add a cross-reference from Step 11 back to the evaluator field isolation rule.
- Add a brief resolution path for scoring-inconsistency blockers.

---

## Validation Gate

- Validation command: `python -m pytest -q`
- Baseline: 849 tests pass.
- No template placeholders to track for preservation (SKILL.md is not a template).
- Write-back gate: validation must still pass 849+ tests; decision.md must exist.
