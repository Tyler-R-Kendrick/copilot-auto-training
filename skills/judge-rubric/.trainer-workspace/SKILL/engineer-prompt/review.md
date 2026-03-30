# Engineer Review
## Target
- Review /workspaces/copilot-apo/skills/judge-rubric/SKILL.md for trainer optimization opportunities that improve rubric-format determinism, eval reliability, and token efficiency without changing the skill contract.

## Current strengths
- The frontmatter, description, and argument hint make the trigger conditions and required user inputs easy to infer.
- The body defines a concrete authoring workflow with strong judging invariants: locked dimensions, explicit pass-partial-fail anchors, evidence ledgers, tie-breakers, and robustness checks.
- The prompt already encodes repo-specific discipline that matters to the evals, especially order-bias checks, blocker handling, and skepticism toward unsupported chain-of-thought.
- The deterministic helper contract is tight: scripts/render_rubric.py validates the same core fields the prose asks for and enforces the 3 to 7 dimension range.
- Local assets and references reinforce the same output shape, so the skill has good grounding and does not depend on external datasets or hidden conventions.

## Risks or weaknesses
- The highest-value branch, using scripts/render_rubric.py when inputs are already structured, appears relatively late, so the model may default to verbose manual drafting before recognizing the deterministic path.
- The output package is described semantically, but the prose does not strongly anchor the exact section structure used by the helper and assets, which can reduce formatting consistency across runs.
- Several important constraints are spread across multiple sections, so under token pressure the model could preserve the general idea of rubric authoring while dropping concrete requirements such as allowed-evidence fields or blocker-first behavior.
- The skill mixes operating rules with explanatory narration, which may add tokens without improving recall on the three current eval prompts.
- The eval manifest mainly checks content invariants, not template fidelity, so trainer optimization could drift toward passing assertions with looser rubric packaging unless the prompt sharpens the final output contract.

## Rewrite hypotheses
1. Move the structured-helper decision to the top of the workflow and state it as a default branch when contract fields are present; this should improve determinism and reduce average token usage on structured rubric tasks.
2. Replace the current output-package bullets with an explicit required section list aligned to the helper template, especially Judging Target, Locked Rubric, Aggregation Rules, Robustness Checks, and Blockers; this should improve formatting consistency and eval reliability.
3. Pull the non-negotiable rubric constraints into one compact checklist near the top: lock 3 to 7 dimensions, define pass-partial-fail boundaries, name allowed evidence, freeze criteria before scoring, and avoid invented thresholds; this should improve instruction retention and lower omission errors.
4. Make blocker handling more operational by stating that when domain constraints are under-specified, the skill should return missing inputs instead of drafting provisional boundaries; this should improve precision and reduce hallucinated scoring criteria.
5. Add a short evidence-mode mapping for outcome-focused, process-aware, and hybrid judgments tied to likely artifacts; this should improve task classification accuracy on prompts like the trajectory-versus-final-answer eval.

## Validation focus
- Check whether an optimized prompt preserves the early routing to scripts/render_rubric.py and still matches the script's accepted contract fields and validation behavior.
- Measure whether free-form outputs more consistently follow the asset/helper section structure without losing any required rubric content.
- Verify that the optimized prompt still passes all existing eval cases, especially low-trust chain-of-thought handling, order-bias checks, and blocker-first behavior.
- Compare token count and response length against the current skill to confirm that any rewrite reduces or at least does not inflate prompt overhead.
- Inspect whether the optimizer introduces wording that weakens the fixed 3 to 7 dimension constraint or the pre-scoring lock on rubric criteria.

## Recommendation
Optimization is justified, but only as a small structural rewrite rather than a conceptual rewrite. Preserve the current judging policy, the helper contract, the 3 to 7 dimension rule, and the low-trust treatment of unsupported chain-of-thought; the main opportunity is to make the deterministic path and final output shape easier for the model to follow consistently.