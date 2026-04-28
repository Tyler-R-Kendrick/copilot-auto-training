# Engineer-Prompt Review: skills/create-workflow/SKILL.md

## Target Goal

Improve the `create-workflow` skill so that it consistently produces well-structured, compilable GitHub Agentic Workflow files, reduces authoring mistakes, and clearly communicates compilation requirements to agents.

## Current Skill Assessment

### Strengths
- Comprehensive 7-step authoring flow with clear phase headings
- Good CLI quick reference section
- Strong debugging section covering compilation, MCP, and runtime failures
- Quality bar checklist at the end is actionable

### Likely Failure Modes
1. **Compilation ambiguity**: The rule "markdown body only changes do not require recompilation" is buried in section 5; agents may forget to compile after frontmatter changes
2. **Vague trigger description in YAML**: The `description:` field frontmatter says "Create or update a GitHub Agentic Workflow" but doesn't surface triage scenarios (debug, fix existing)
3. **Safe outputs coupling gap**: Section 4 covers safe outputs but doesn't link back to step 3 (authoring), so agents may draft write-heavy workflows without safe-output frontmatter
4. **Response contract underselling compilation**: The 4-point response contract doesn't require agents to state specifically whether frontmatter or body changed—key for knowing if recompilation was needed
5. **Ordering issue**: "Quality bar" (section 7) comes after "Example request shapes" (section end), making it easy to skip
6. **No explicit early exit**: If a user only wants a draft and is not ready to initialize, the skill should remind agents to defer compilation clearly (currently a brief note in section 1)

## Dataset Gaps
- No authored evals or train/val datasets exist for this skill
- Need synthesis of eval cases covering: new workflow creation, MCP addition, debugging, draft-only requests, re-compilation after frontmatter edit

## Validation Plan
1. Run `python -m pytest -q` for baseline passing (no regressions)
2. Evaluate optimized SKILL.md against synthesized evals with `llm_judge` scoring
3. Ensure description/frontmatter triggering accuracy is maintained

## Optimization Hypotheses
1. **Primary**: Move the compilation rule (frontmatter vs body) earlier—ideally into the Quick Reference and Step 3—so agents never forget to recompile
2. **Secondary**: Strengthen the response contract to explicitly require stating whether frontmatter changed and whether recompilation ran
3. **Tertiary**: Add a brief "When NOT to use" clarification so agents don't trigger the skill for pure YAML debugging outside gh aw context
4. **Progressive disclosure**: Consider front-loading the core contract (What, When, How) and deferring reference material (MCP examples, debug details) to a reference file

## Scoring Shape
- Eval cases should use `scoring: llm_judge` with `criteria` checking for correct compilation behavior, safe-output usage, and accurate response contracts
- Use `reference` outputs where the expected skill behavior is objective (e.g., compilation required after frontmatter edit)
