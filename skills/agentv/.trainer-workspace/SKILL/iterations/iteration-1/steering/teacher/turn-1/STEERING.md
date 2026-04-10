# Turn 1 Steering — agentv SKILL.md (Teacher → Student)

**Iteration:** 1  
**Turn:** 1  
**Agent:** teacher  
**Date:** 2026-04-10

## Evidence used
- Current `skills/agentv/SKILL.md` (full text)
- `skills/agentv/evals/evals.json` (5 test cases, llm_judge scoring)
- Engineer-prompt review findings (7 issues, severity-ranked)
- `skills/agentv/references/eval-yaml-schema.md` (schema ground truth)

## Priority fixes (ordered by score impact)

1. **[CRITICAL] Fix broken code fence** in the CI section.
   The bash block with `--exit-on-failure`, `--threshold`, `-o results.xml` must be
   inside a fenced block. Merge with the preceding YAML block or open a new
   ` ```bash ` fence. Do NOT leave duplicate commands.

2. **[HIGH] Add `agentv eval --target <name>` to Quickstart and Targets section.**
   Add one Quickstart line: `agentv eval evals/my.yaml --target claude`
   Add a "Multi-target comparison" subsection showing both target runs before
   `agentv compare`. Verify the exact flag name against references/targets.md.

3. **[HIGH] Add "Debugging failing evaluations" section (standalone h2 or h3).**
   Cover: path to JSONL results, fields to inspect (score, reasoning, pass),
   how to iterate on the judge markdown file, and per-assertion vs. CLI threshold.

4. **[HIGH] Extend the minimal EVAL.yaml example to include `assert:` with
   `type: llm-grader`** alongside rubrics. The example currently shows only rubrics.

5. **[MEDIUM] Add a fenced markdown judge prompt example** immediately after the
   template-variable list. Show `{{answer}}`, `{{criteria}}`, `{{expected_output}}` in
   use with 3–5 lines of grading instructions.

6. **[MEDIUM] Fix expected_output conversion mapping**: clarify that evals.json
   `expected_output` maps to EVAL.yaml `tests[].expected_output` (not just
   `criteria`). Add a table note.

7. **[LOW] Trim opening paragraph** under `# AgentV Skill` (verbatim restatement).
   Add "comparing two agent versions" as an explicit "When to use" trigger.

## Stop/continue decision
**CONTINUE** — significant structural and content gaps affect all 5 test cases.

## Predicted response
Student will produce a revised SKILL.md addressing the 7 issues above. Risk of duplicating commands if fence merge is sloppy.

## Engineer / judge notes
- Verify `agentv eval --target` flag against targets.md before committing
- Debugging section should be a standalone section (h2), not buried in a list
- Judge prompt markdown example must be fenced, not prose
