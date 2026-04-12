## Goal

Assess the current adversary agent as an optimization target for adversarial review work in prompt-optimization workflows, with emphasis on exploit-generation discipline, artifact completeness, and judge-gaming accuracy.

The optimization target is operational reliability, not role expansion. A strong adversary agent should surface the strongest plausible exploit against a given candidate, produce complete artifact-ready content for each exploit attempt, model the judge's likely response to each candidate, and converge on a final recommendation rather than listing open-ended risks.

## Current Strengths

- The role is sharply scoped: produce exploit artifacts, not editorial suggestions.
- The constraints correctly prohibit editing and full loop re-running.
- The focus areas cover the right adversarial surface: hidden assumptions, placeholder mismatches, workflow behavior, and judge-gaming candidates.
- The output format calls for artifact-ready content for each exploit attempt, which supports the workspace staging contract.

## Main Risks

1. **No evidence order.** The approach says "inspect baseline intent first," but does not specify which artifacts to read in which order, when to stop reading, or how incomplete evidence should affect the exploit search.

2. **No convergence or comparison logic.** The output format says to return the strongest exploit, but the prompt gives no guidance on how to compare exploit candidates against the current student candidate, how many iterations of reflection to run, or when to stop generating alternatives.

3. **Artifact contract is incomplete.** The output mentions `candidate.md`, `description.md`, `predicted-judge-response.md`, and `reflection.md`, but does not describe the expected content or structure of each, leaving the agent to improvise.

4. **No trainer-specific exploit focus.** The focus areas name general adversarial patterns but do not call out the trainer-specific exploit surfaces that matter most in this repo: skill-routing assumptions, dataset shape mismatches, judge-mode selection errors, manual-followup misclassification, and explicit train/val versus authored eval blurring.

5. **Judge response modeling is implicit.** The collaboration contract requires the adversary to "model the judge's likely response" and "recursively reflect," but the current prompt does not instruct the agent to do this explicitly or persist the per-turn reasoning artifacts.

6. **No minimum exploit breadth.** The prompt says to return secondary exploit attempts only if "material," but gives no threshold for what counts as material, which can lead to surface-only single-exploit output when multiple distinct failure modes exist.

## Rewrite Hypotheses

- Add an explicit evidence order: baseline intent, changed or staged artifacts, latest validation evidence, judge scoring context, supporting notes.
- Add a structured exploit search with an explicit comparison step: after generating each exploit attempt, compare it against the current student candidate and reflect on whether a stronger exploit is likely.
- Expand the artifact contract to describe the expected content of `candidate.md`, `description.md`, `predicted-judge-response.md`, and `reflection.md`.
- Add a trainer-specific exploit surface section that names skill-routing gaps, dataset-shape mismatches, judge-mode errors, and eval/dataset blur as first-class targets.
- Promote the recursive judge-response modeling to an explicit approach step.
- Add an explicit stopping condition: stop after the adversary predicts the judge would rank its strongest exploit at or above the student candidate, or after exhausting the plausible exploit space.
- Keep the rewrite minimal: structured approach, expanded artifact contract, and a trainer-specific focus list should be enough for a first improvement pass.

## Suggested Metrics

- Exploit-vs-student ranking: percent of runs where the adversary's strongest exploit is correctly assessed against the student candidate.
- Artifact completeness: percent of exploit attempts where all four artifact files are present and non-trivial.
- Judge-response accuracy: calibration between predicted judge score and actual judge score on staged adversarial candidates.
- Exploit depth: average number of distinct exploit attempts when the input clearly has multiple failure modes.
- Convergence rate: percent of runs that include a clear stopping statement ("exhausted plausible exploit space" or "strongest exploit found").
- Trainer-specific exploit recall: percent of runs that surface at least one trainer-specific exploit (skill-routing, dataset shape, judge-mode, eval blur) when the input contains such a gap.

## Validation Plan

Run `python -m pytest -q` from the repository root after applying any rewrite to confirm no regressions in existing tests. Review representative adversarial outputs against the staged evals.json cases for artifact completeness and exploit relevance.

## Recommendation

This is a valuable optimization target because adversarial review quality directly affects judge calibration and trainer-loop safety. The current agent has the right role scoping but lacks structured exploit-search discipline, complete artifact guidance, and trainer-specific targeting.

Prioritize a rewrite that adds a fixed evidence order, an explicit exploit-vs-student comparison step, and a complete artifact contract. Measure on adversarial recall and artifact completeness first. Only add examples if the first structured rewrite still produces incomplete or shallow exploit output.
