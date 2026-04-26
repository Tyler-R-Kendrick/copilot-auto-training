# Operator Follow-up

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no inference model was configured in the repository `.env` file (no `COPILOT_MODEL` credential available in this environment). This is the expected deterministic fallback path per the trainer contract.

## Artifacts

- Manual-followup report: `iterations/iteration-1/optimize/manual-followup-report.json`
- Agent-authored candidate: `iterations/iteration-1/optimize/optimized-prompt.md`

## Agent Handoff Summary

The current `@trainer` agent answered the report's `model_prompt` directly. The model_prompt requested a revised version of `student.agent.md` optimized against the training and validation datasets (8 train rows, 2 val rows, `judge_mode=llm_judge`).

**Changes applied in the optimized candidate:**

1. **Evidence reading order** (Step 1): Added a numbered evidence reading order (teacher goal → critique → STEERING.md → summary.md → workspace evidence) with an explicit fallback: if STEERING.md is missing, fall back to summary.md; if both are missing or empty, hand off to teacher.

2. **Unclear revision target** (Step 2): Added explicit criteria for when the revision target is "unclear": missing/empty STEERING.md, contradictory criteria between summary.md and latest steering turn, or critique with no specific section/behavior/success criterion.

3. **No-op conditions** (Constraints): Enumerated four specific conditions that justify a no-op, replacing the vague "evidence does not support a better candidate."

4. **Engineer handoff threshold** (Constraints + Step 4): Tightened from the permissive "prompt-engineering or Trace-oriented expertise" to a concrete threshold: use engineer only when the teacher-ready explanation requires more than two sentences inline, or when Trace-specific/prompt-engineering domain expertise is explicitly needed.

5. **Scope constraint** (Constraints): Added explicit constraint that when the critique names a specific section, the revision must be scoped to that section only.

6. **Validation step** (Step 7): Specified `python -m pytest -q` from repo root as the validation command, requiring a concrete test outcome report rather than a hypothetical one.

## Rerun Command

To retry with a live model once credentials are configured:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt .github/agents/student.agent.md \
  --train .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --judge-mode llm_judge \
  --report .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimize-report.json \
  --output .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimized-prompt.md
```
