# Iteration-1 Judge Validation

**Date:** 2026-04-10  
**Candidate:** `iterations/iteration-1/optimize/optimized-prompt.md`  
**Judge mode:** llm_judge (manual)

## Per-test scores

| Test | Score | Summary |
|------|-------|---------|
| Test 1 (EVAL.yaml from evals.json) | 1.0 | All 4 assertions directly covered by conversion table, minimal example, quickstart, skills integration pattern |
| Test 2 (Debug failing llm-grader) | 1.0 | Dedicated debugging section covers JSONL inspection, judge prompt improvement, threshold adjustment, re-run command |
| Test 3 (CI pipeline) | 1.0 | GitHub Actions snippet, --threshold 0.8, exit code semantics, JUnit XML all present |
| Test 4 (Multi-target compare) | 1.0 | targets.yaml setup, --target flag, agentv compare, sample output table all present |
| Test 5 (LLM judge authoring) | 1.0 | Full judge prompt template, llm-grader YAML, score range, placeholder table all present |

**Mean: 1.0**

## Remaining gaps (for iteration-2)
- No worked example for `code-grader` type (evaluator table lists it but no usage snippet)
- `rubric` evaluator has YAML but no explanation of score rollup with suite pass rate
- No guidance on flaky llm-grader scores across repeated runs (temperature sensitivity, retry behavior)
- `agentv compare --last 2` mentioned but not explained (how runs are ordered, directory scanned)
- No mention of passing secrets/env vars to `code-grader` or CLI-type targets in CI
