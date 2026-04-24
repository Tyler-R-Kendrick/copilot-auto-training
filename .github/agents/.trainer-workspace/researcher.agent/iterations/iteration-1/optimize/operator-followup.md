# Optimize Stage — Operator Followup

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no external inference model was available (CopilotInferenceError on all candidate generation attempts). This is a deterministic fallback path, not a prompt quality failure.

## Saved Artifacts

- **Report**: `iterations/iteration-1/optimize/manual-followup-report.json`
- **Candidate**: `iterations/iteration-1/optimize/optimized-prompt.md`

## Agent Handoff Summary

The current `@trainer` agent answered the `model_prompt` from the report. The optimization focused on the four highest-priority improvements identified in `engineer-prompt/review.md`:

1. **Mandatory constraint elicitation**: replaced conditional "If any of these materially affect source selection and are missing, ask first" with a mandatory gate in a dedicated "Required Inputs — Resolve Before Searching" section that names each required input and specifies the stop-or-elicit path.

2. **Explicit stop path when constraints are unresolvable**: added an explicit clause — "if the caller cannot or does not provide it, stop and name the unresolved constraint in a blocker report rather than guessing or proceeding."

3. **Free-form research prohibition**: strengthened the MCP routing contract with an explicit prohibition ("Do not begin source search or propose source candidates before `researcher-research` is loaded. Free-form research is not a fallback when MCP is available.") and added constraint #2 in the numbered Constraints list.

4. **Consolidated and numbered constraints**: converted the four bullet `DO NOT` group into a numbered list with two additional constraints (free-form research prohibition, no eval row authoring), making the constraint set easier to audit.

5. **Tightened approach steps**: reordered so MCP activation is step 1 and constraint elicitation is step 3, making the sequence unambiguous.

## Rerun Command

```
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/researcher.agent.md \
  --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 --algorithm apo --beam-width 4 --branch-factor 4 --n-runners 4 \
  --judge-mode llm_judge
```
