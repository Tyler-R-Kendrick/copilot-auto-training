# Decision: judge-rubric trainer pass

## Target

- Prompt file: `skills/judge-rubric/SKILL.md`
- Goal: improve the skill structurally without changing the judging policy core.

## Stages run

- Research: completed using repo-owned sources already present next to the skill.
- Synthesis: completed by reusing the existing eval manifest and creating explicit `train.jsonl` and `val.jsonl` datasets.
- Optimize: attempted through `trainer-optimize` with `judge_mode=llm_judge` and a low-concurrency search budget.
- Validation: completed with the deterministic helper render check and the full repository test suite.

## Outcome

- No change was applied to `skills/judge-rubric/SKILL.md` during this run because file persistence was not explicitly requested.
- The optimize runtime hit GitHub Models rate limiting, but the trainer workflow continued through the new `manual_followup` path instead of stopping.
- The current `@trainer` agent used the saved handoff prompt to generate `iterations/iteration-1/optimize/optimized-prompt.md` as the optimize-stage candidate.
- The blocker was operational, not conceptual: Agent Lightning launched, the synthesized datasets were accepted, and the trainer could still complete the inference step without an external inference token.

## Validation

- `judge-rubric` helper render succeeded against `assets/sample-contract.json`.
- `python -m pytest -q` succeeded with `419 passed in 5.73s`.

## Recommendation

- Review `iterations/iteration-1/optimize/optimized-prompt.md` as the current best candidate from this pass.
- Apply that candidate to `skills/judge-rubric/SKILL.md` only if you want the trainer workflow to persist the prompt update now.
- Reuse the synthesized datasets already recorded in this workspace; no additional research or synthesis is needed unless the task scope changes.