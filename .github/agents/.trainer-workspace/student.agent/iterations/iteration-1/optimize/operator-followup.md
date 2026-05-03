# Operator Follow-up: manual_followup Optimize Stage

## Blocker

The `trainer-optimize` runtime returned `mode=manual_followup` because no inference model was configured in the repository `.env` (error: `Session was not created with authentication info or custom provider`).

## Agent Handoff Summary

The current `@trainer` agent answered the `model_prompt` from `manual-followup-report.json` directly and produced the candidate at:

```
iterations/iteration-1/optimize/optimized-prompt.md
```

**Changes applied in the candidate:**
1. Added a prioritized evidence reading order (turn-scoped STEERING.md first → summary.md second → candidate text → workspace evidence), with an explicit note that summary context must not override turn-scoped steering.
2. Added a pre-edit scope check before `edit` — the student must confirm the target is within `candidates/student/` before editing; otherwise report a scope blocker and stop.
3. Replaced the vague "stale" criterion with a concrete signal: treat critique as stale when the STEERING.md turn number is older than the latest optimize or research artifact modification timestamp.
4. Tightened the self-check termination rule: after at most one self-check predicting rejection, hand off to `teacher` unconditionally; do not continue self-checking.
5. Clarified the `engineer` handoff scope: permitted only for reformatting reasoning trajectories; not permitted for skill execution, file editing, or workspace management.
6. Identified the default validation step: `python -m pytest -q` plus a diff review confirming only the candidate file changed.
7. Added a candidate persistence note: save the revised candidate to `iterations/iteration-N/candidates/student/` and record the path in the output.

## Rerun Command

To re-run with model access when credentials are available:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file .github/agents/student.agent.md \
  --train-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl \
  --val-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl \
  --iterations 3 \
  --judge-mode llm_judge \
  --report-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimize-report.json \
  --output-file .github/agents/.trainer-workspace/student.agent/iterations/iteration-1/optimize/optimized-prompt.md
```
