# Engineer-Prompt Review — skills/agentv/SKILL.md

**Review date:** 2026-04-10  
**Reviewer:** trainer orchestration (auto-generated from analysis)  
**Target file:** `skills/agentv/SKILL.md`

---

## Summary

The AgentV SKILL.md is a well-structured document but has several issues that reduce its effectiveness as a retrieval skill:

1. **Trigger reliability** — The `description` front-matter is long but not optimally keyword-dense. The "when to use" section is accurate but lacks priority ordering.
2. **Clarity issues** — The CI section has a broken code fence (missing opening ``` before "# Run with exit code"). The file mixes three levels of detail inconsistently.
3. **EVAL.yaml completeness** — The minimal example omits the `assert` field entirely; users rely on it. The field mapping table (evals.json → EVAL.yaml) omits `expected_output` mapping.
4. **Actionability** — CLI examples are mostly good, but the `agentv compare` examples could show `--target` flag usage during a run (not just comparison phase).
5. **Redundancy** — "Set up targets" section duplicates `references/targets.md` nearly verbatim without adding skill context.

---

## Identified Issues

### Critical (must fix)
- **Broken code fence in CI section**: Text above a code block appears outside the fence — causes rendering issues in markdown viewers.
- **Missing opening fence**: Around lines 155–165, the CI best-practice commands (`agentv eval evals/*.yaml --exit-on-failure`) are outside a code block.

### High priority (should fix)
- **"When to use" triggers lack specificity**: Should list concrete user phrases that trigger the skill, not just abstract use cases.
- **Minimal EVAL.yaml example missing `assert`**: The example omits assertion types, leaving new users uncertain how to add checks.
- **evals.json conversion table incomplete**: Missing the `expected_output` → `expected_output` pass-through and `assertions` string → `rubrics` string (not just the array form).

### Medium priority (consider)
- **Targets section is just a partial copy of references/targets.md**: Instead, briefly show the two most common target types and point to the reference file.
- **Judge prompt template variables could be tabular**: The 4 template variables (`{{answer}}`, etc.) are listed as bullets but a small table would improve scannability.

### Low priority (style)
- **`compatibility` front-matter field not rendered by most skills frameworks**: Consider moving Node.js ≥18 requirement into the body.
- **Opening paragraph redundantly repeats the skill name**: The `# AgentV Skill` heading plus the first paragraph say the same thing as the front-matter description.

---

## Rewrite Notes for Optimization

### Goal 1 — Trigger reliability
- Add explicit user-intent phrases to the "When to use" section (e.g., "User says 'write an EVAL.yaml'", "User asks how to run agentv").
- Keep the `description` field as-is (it is already used by the discovery system) but make "When to use" the primary in-skill trigger document.

### Goal 2 — Fix broken code fence
- Merge the orphaned CI commands back into the preceding GitHub Actions code block, or add a new fenced block with a heading.

### Goal 3 — EVAL.yaml accuracy
- Extend the minimal example to include at least one `assert:` entry (type: `contains` or `rubric`).
- Expand the conversion table to cover all 5 field mappings including `expected_output`.

### Goal 4 — More actionable CLI examples
- Add `--target claude` flag to the `agentv eval` quick start.
- Show `agentv targets test default` next to `agentv init`.

### Goal 5 — Reduce redundancy
- Compress the "Set up targets" section to a 4-line YAML snippet for the two most common types (OpenAI, Anthropic), then point to `references/targets.md` for the rest.

---

## Validation Criteria

After optimization, the improved SKILL.md should pass all 5 test cases in `evals/evals.json`:
1. EVAL.yaml creation from evals.json — field mapping must be accurate and complete
2. LLM grader debugging — threshold field and JSONL inspection must be mentioned
3. CI pipeline integration — --threshold and -o results.xml flags must appear
4. Multi-target comparison — --target flag and agentv compare must appear
5. LLM judge authoring — markdown template variables must be shown with example

**Scoring:** `llm_judge` on all 5 test cases (train: 4, val: 1).
