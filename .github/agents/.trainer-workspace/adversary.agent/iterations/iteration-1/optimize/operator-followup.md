# Operator Followup: manual_followup Optimize Stage

## Blocker

Model credentials not available in this environment (`CopilotInferenceError: Session was not created with authentication info or custom provider`).

## Optimize Payload

Saved as `manual-followup-report.json` in this same directory.

## Agent Handoff Summary

The `@trainer` agent completed the optimize-stage inference step. The `model_prompt` from the manual-followup report was answered using the engineer-prompt review, training dataset analysis, and the collaboration contract guidance for the adversary agent.

**Key improvements applied:**
1. Added an explicit **Evidence Order** section (5 steps) that operationalizes which artifacts to inspect first.
2. Added **trainer-specific exploit surfaces** to Focus Areas: skill-routing gaps, dataset-shape mismatches, judge-mode selection errors, `manual_followup` misclassification, and eval/dataset blur.
3. Expanded the **Approach** to include compare-vs-student logic, an explicit stopping condition, and recursive reflection before stopping.
4. Added a complete **Artifact Contract** describing the expected content of each of the four required artifact files.
5. Kept all existing constraints, role framing, frontmatter, and output format structure intact.

## Rerun Command (for future runs with model access)

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/adversary.agent.md \
  --train-file .github/agents/.trainer-workspace/adversary.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/adversary.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --beam-width 4 \
  --branch-factor 4 \
  --n-runners 4 \
  --judge-mode llm_judge
```
