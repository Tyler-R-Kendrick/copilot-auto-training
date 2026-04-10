# Teacher Steering Summary — iteration-1

**Iteration:** 1  
**Agent:** teacher  
**Last updated:** 2026-04-10 (turn 1)

## What the teacher taught this iteration

### Turn 1
The current SKILL.md has 7 issues ranging from critical (broken code fence, Test 3 directly affected) to low (cosmetic prose duplication). The priority order for the student is:

1. Fix broken code fence in CI section (critical, Test 3)
2. Add `--target` flag to Quickstart + Targets (Test 4)
3. Add standalone "Debugging" section (Test 2)
4. Extend minimal EVAL.yaml example with `assert: [llm-grader]` (Tests 1, 5)
5. Add fenced judge prompt markdown example (Test 5)
6. Fix expected_output mapping in conversion table (Test 1)
7. Trim opening paragraph, add "comparing two agent versions" trigger (cosmetic)

## Iteration focus
Structural integrity (broken fence), CLI completeness (`--target` flag), and concrete examples for the three most-tested workflows (debug llm-grader, multi-target compare, judge prompt authoring).

## Status
Turn 1 complete. Awaiting student revision.
