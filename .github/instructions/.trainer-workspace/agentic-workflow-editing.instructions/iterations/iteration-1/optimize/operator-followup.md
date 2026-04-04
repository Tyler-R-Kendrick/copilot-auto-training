# Operator Follow-up: manual_followup from trainer-optimize

## Blocker

No inference model was configured. The trainer-optimize runtime completed deterministic preparation (dataset loading, prompt validation, placeholder analysis) but could not reach an external model to generate candidate revisions.

## Agent Handoff Summary

The `@trainer` agent answered the `model_prompt` directly to complete the optimize stage. The following changes were made based on analysis of the 6 training rows and 4 validation rows:

1. **Concrete compile example added**: `gh aw compile train-prompt` for `train-prompt.md` — removes ambiguity about how to invoke the command.
2. **"Meaningful changes" clarified**: Changed to "every edit — including minor formatting or comment changes" — training rows showed agents skip compile for "trivial" edits with the ambiguous original wording.
3. **Verify step added**: `git diff --name-only` check after compile — validation rows required agents to confirm both files are in the diff.
4. **Final pre-PR checkpoint made explicit**: "Run `gh aw compile` one final time before opening a pull request" — training row 5 showed agents assume one early compile is sufficient.
5. **Hook description clarified**: Explained what `agentic-workflow-validation` checks (lockfile presence and freshness) — training row 6 required agents to understand the hook's scope.

## Saved Artifacts

- `optimized-prompt.md`: the candidate optimized prompt (this iteration's best candidate)
- `manual-followup-report.json`: the full JSON payload from the optimize runtime

## Rerun Command

When an inference model becomes available:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/instructions/agentic-workflow-editing.instructions.md \
  --train-file .github/instructions/.trainer-workspace/agentic-workflow-editing.instructions/iterations/iteration-1/synthesize/train.jsonl \
  --val-file .github/instructions/.trainer-workspace/agentic-workflow-editing.instructions/iterations/iteration-1/synthesize/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --beam-width 4 \
  --branch-factor 4 \
  --n-runners 4 \
  --judge-mode llm_judge
```
