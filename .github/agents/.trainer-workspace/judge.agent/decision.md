# Decision Summary

Target file: `.github/agents/judge.agent.md`

Optimization goal: improve operational reliability, routing clarity between `judge-trajectory` and `judge-outcome`, rubric stability, and output structure while preserving evidence-first judging.

## Artifact Workspace

- Local workspace: `.github/agents/.trainer-workspace/judge.agent`
- Active iteration: `iterations/iteration-1`

## What Was Created

- Research brief and source shortlist under `iterations/iteration-1/research/`.
- Authored eval manifest plus `llm_judge` train or validation datasets under `iterations/iteration-1/synthesize/`.
- Optimize-stage blocker report and runtime stderr artifacts under `iterations/iteration-1/optimize/`.
- Validation artifacts under `iterations/iteration-1/validation/`.

## Decision

- The prompt rewrite was applied directly to `judge.agent.md`.
- The winning rewrite keeps evidence-first judging intact while adding a routing table, a stable rubric shell, evidence-priority order, missing-evidence handling, anti-double-counting guidance, and a fixed decision package.

## Optimization Outcome

- Datasets were synthesized, not reused.
- Dataset row shape selected `judge_mode=llm_judge` because the rows use `reference`, `criteria`, and `scoring: "llm_judge"`.
- `trainer-optimize` did not execute meaningfully for this iteration.
- APO debug-only failed because `Trainer.dev()` in this environment rejects APO.
- VERL debug-only failed because `hydra` is missing.
- Even without those runtime exceptions, the raw target prompt is not optimizer-native because it has no task-input placeholders.

## Validation Result

- Repository validation succeeded with `./.venv/bin/python -m pytest -q`.
- Saved log: `iterations/iteration-1/validation/pytest.txt`.

## Final Call

Keep the rewritten `judge.agent.md`, keep the synthesized `llm_judge` artifacts as the evaluation contract for future runs, and treat a fuller APO pass as blocked until the runtime can inject task input into agent instruction files and the optimize environment is repaired.