# Operator Followup: manual_followup Optimize Stage

## Blocker

Model credentials not available in this environment (`CopilotInferenceError: Session was not created with authentication info or custom provider`).

## Optimize Payload

Saved as `manual-followup-report.json` in this same directory.

## Agent Handoff Summary

The `@trainer` agent completed the optimize-stage inference step. The baseline `researcher.agent.md` was analyzed against the training dataset and engineer-prompt review, and an optimized candidate was produced directly.

**Key improvements applied:**

1. Added a **Pre-Research Constraint Check** section that specifies a fixed evidence-reading order (prompt file → task description → scoring rule → source constraints) and requires surfacing missing constraints as blockers before calling `find_agent_skill`.

2. Clarified the **`run_agent_skill` guard clause**: after loading, the agent explicitly checks whether the loaded skill contract mentions a scripts/ helper. If yes, call `run_agent_skill`; if not, use the loaded instructions as the operating contract directly.

3. Added a **synthesis boundary** to the Scope section: "Stop at mapping notes. Do not author eval rows, train.jsonl entries, or val.jsonl entries; that work belongs to a synthesis workflow."

4. Added **artifact path guidance** to the Approach: when the caller requests a saved artifact, save the research brief under `iterations/iteration-N/research/` and return the path.

5. Expanded **Output Format descriptions**: each of the six sections now has a one-to-three sentence description of minimum required content and expected depth, including an explicit note that the stop recommendation section is always present.

6. Added the blocker-report step to the Approach: if required inputs are missing after the constraint check, surface the gap and wait for clarification before proceeding.

All existing frontmatter, constraints, scope role, and tool configuration were preserved.

## Rerun Command (for future runs with model access)

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --algorithm apo \
  --beam-width 4 \
  --branch-factor 4 \
  --n-runners 4 \
  --judge-mode llm_judge
```
