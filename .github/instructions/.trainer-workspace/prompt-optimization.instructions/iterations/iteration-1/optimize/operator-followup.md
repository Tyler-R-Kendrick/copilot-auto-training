# Operator Followup

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no inference model was configured (`COPILOT_MODEL` not set or authentication unavailable).

## Agent Handoff Summary

The current `@trainer` agent answered the `model_prompt` from the `manual-followup-report.json` payload directly, producing 3 candidate revisions:

1. **Original** (`candidates/original/candidate.md`): baseline unchanged
2. **Student** (`candidates/student/candidate.md`): gap-filling candidate selected as the optimized result
3. **Adversary** (`candidates/adversary/candidate.md`): over-specified with H2 headers (exploit blocked — violates flat-bullet convention)

The **student candidate** was selected as `optimized-prompt.md` because it covers all 4 identified gaps with minimal structural change and follows the flat-bullet convention of sibling instruction files.

## Saved Artifacts

- `manual-followup-report.json`: the JSON payload from the runtime
- `optimized-prompt.md`: the chosen candidate (student/candidate.md)
- `candidates/`: all 3 candidates with descriptions, predicted judge responses, and reflections

## Rerun Command

When model access is available, the fully automated optimize pass can be rerun with:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/instructions/prompt-optimization.instructions.md \
  --train-file .github/instructions/datasets/train.jsonl \
  --val-file .github/instructions/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --judge-mode llm_judge
```
