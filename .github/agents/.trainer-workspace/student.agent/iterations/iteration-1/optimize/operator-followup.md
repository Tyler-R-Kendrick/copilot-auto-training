# Operator Followup: student.agent.md Optimization

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no model authentication was available in the current execution environment. The JSON payload was saved to `manual-followup-report.json`.

## Agent Handoff Summary

The current `@trainer` agent answered the `model_prompt` from the report directly, applying the optimization criteria from the datasets and the `engineer-prompt/review.md`:

1. Added an explicit evidence reading order (step 1 of Approach) with four numbered sources and a stop-reading condition.
2. Replaced the vague "if the next revision target is unclear" teacher-handoff trigger with three observable workspace conditions (no STEERING.md, ambiguous STEERING.md, conflicting artifacts).
3. Added the three-outcome self-check rule as a constraint and in step 6 of Approach.
4. Added an inline scope boundary definition for "smallest defensible revision" in the body introduction.
5. Consolidated the engineer-handoff condition into Constraints only (removed the duplicate phrasing in the Approach section).
6. Added a fixed six-section output template replacing the previous unstructured "State the..." list.
7. Added a missing-steering fallback in step 2 of Approach.

The result was saved as `optimized-prompt.md` in this iteration's optimize directory.

## Rerun Command

```
trainer-optimize --prompt-file .github/agents/student.agent.md \
  --train-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --judge-mode llm_judge --iterations 3
```
