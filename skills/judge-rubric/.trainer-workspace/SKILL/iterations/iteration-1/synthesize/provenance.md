# Provenance Note: judge-rubric

- Grounded sources: `skills/judge-rubric/SKILL.md`, `skills/judge-rubric/evals/evals.json`, `skills/judge-rubric/scripts/render_rubric.py`, `skills/judge-rubric/assets/sample-contract.json`, `tests/test_judge_rubric.py`, and `skills/judge-rubric/.trainer-workspace/SKILL/engineer-prompt/review.md`.
- Synthetic rows: none.
- Split rule: hold out the incomplete structured-contract case and one stricter hybrid-format case for validation so the optimizer cannot rely only on the training phrasing.