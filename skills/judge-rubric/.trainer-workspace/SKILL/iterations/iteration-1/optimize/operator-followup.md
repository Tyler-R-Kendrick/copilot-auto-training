# Operator Follow-Up: judge-rubric

## Status

- Optimize fallback mode: `manual_followup`
- Blocker: GitHub Models returned a rate-limit response before Agent Lightning could produce a candidate prompt.
- Saved report: `skills/judge-rubric/.trainer-workspace/SKILL/iterations/iteration-1/optimize/manual-followup-report.json`
- Agent-authored candidate: `skills/judge-rubric/.trainer-workspace/SKILL/iterations/iteration-1/optimize/optimized-prompt.md`

## Rerun Command

```bash
python skills/trainer-optimize/scripts/run_optimize.py --prompt-file skills/judge-rubric/SKILL.md --train-file skills/judge-rubric/datasets/train.jsonl --val-file skills/judge-rubric/datasets/val.jsonl --iterations 3 --algorithm apo --beam-width 1 --branch-factor 1 --n-runners 1 --judge-mode llm_judge
```

## Agent Handoff Used

The current `@trainer` agent answered the manual-followup `model_prompt` directly and saved the result as `optimized-prompt.md`.

Short handoff summary:

Return only a revised markdown prompt for `skills/judge-rubric/SKILL.md`.

Keep these constraints fixed:

- Preserve the current skill purpose and trigger surface.
- Keep the implicit-task-context interface; do not add unsupported placeholders.
- Keep evaluator-only fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` out of the prompt body.
- Preserve the judging-policy core: 3 to 7 locked dimensions, explicit pass-partial-fail boundaries, allowed-evidence requirements, tie-breakers, robustness checks, and blocker-first behavior.
- Prefer the deterministic helper path early when the rubric contract is already structured.
- Keep the output package aligned to: Judging Target, Locked Rubric, Aggregation Rules, Robustness Checks, and Blockers.

Ground the rewrite in the train and validation examples captured in `manual-followup-report.json`, then return only the revised markdown prompt text.