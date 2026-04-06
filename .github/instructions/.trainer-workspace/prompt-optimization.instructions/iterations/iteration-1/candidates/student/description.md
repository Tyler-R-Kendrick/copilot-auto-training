## Description

**Candidate 1 — Gap-filling**

Preserves the original 8-bullet structure while adding the 4 rules missing from the baseline:
1. Explicit dataset path requirement (don't rely on auto-discovery)
2. Skill routing order with election scope (research → synthesize → optimize; election = multiple outputs only)
3. `judge_mode` selection rule from row shape (`llm_judge` for reference+criteria, `custom` for `expected_json`, `deterministic` for exact-match)
4. Named validation command (`python -m pytest -q`)

**Approach**: Minimal structural change — mostly additive. Merges the explicit-path rule into bullet 3 and expands the skill routing bullet to include order and election scope. Adds `judge_mode` rule as a new bullet. Names `python -m pytest -q` in the validation bullet.

**Rationale**: The original 8-bullet structure is already well-understood. Adding gaps surgically reduces the risk of regressions on existing behaviors while closing all identified failure modes.
