# Turn 1 Steering — agentv SKILL.md Iteration-2 (Teacher → Student)

**Iteration:** 2  
**Turn:** 1  
**Agent:** teacher  
**Date:** 2026-04-10

## Context
Iteration-1 achieved 1.0/1.0 on all 5 test cases. Iteration-2 focuses on real-world usability gaps not covered by the test suite.

## Evidence used
- Iteration-1 SKILL.md (current state, scored 1.0/1.0)
- Judge gap analysis from iteration-1 validation
- `references/eval-yaml-schema.md` (code-grader syntax: `command:` field, not `path:`)

## Changes for iteration-2 (3 targeted inline additions only)

**Change 1 — code-grader inline YAML** (after the evaluator types table, before llm-grader section):
- Add a minimal YAML snippet showing `type: code-grader` with `command:` field (verified from schema).
- Add ONE sentence explaining stdin/exit-code convention.
- Use verified syntax: `command: python ./graders/check_output.py` (not `path:`)

**Change 2 — flaky llm-grader debugging** (inside existing debugging section, as step 4):
- Non-deterministic/flaky score guidance.
- Concrete mitigations: lower temperature in targets.yaml, widen threshold margin.
- Do NOT create a new ## section.

**Change 3 — compare --last 2 clarification** (one sentence under that command):
- Runs ordered chronologically by run directory timestamp.

## Constraints
- Do NOT add new ## sections.
- Do NOT touch CI/CD, llm-grader, conversion table, targets.yaml, or project structure sections.
- Net addition: ~10-15 lines only.

## Stop/continue decision
**CONTINUE** — one more student turn with narrow scope.

## Predicted student mistakes
- May use wrong syntax (`path:` instead of `command:`) — verified: use `command:`
- May bloat the code-grader explanation into a full section
- May add vague flakiness advice without concrete action
