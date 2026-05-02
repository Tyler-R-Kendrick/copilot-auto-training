# Teacher Steering: Turn 1

## Artifacts Reviewed

- `engineer-prompt/review.md` — full gap analysis for student.agent.md
- `inputs/source/student.agent.md` — baseline candidate
- `iterations/iteration-1/optimize/optimized-prompt.md` — student candidate
- `iterations/iteration-1/candidates/adversary/` — adversary candidate and artifacts
- Training dataset (6 rows) and validation dataset (2 rows) from iteration-1/synthesize

## Optimization Goal

Improve the `student.agent.md` agent for reliable, precise teacher-guided candidate revision in the trainer loop. Key dimensions: revision precision, reasoning transparency, teacher-approval accuracy, handoff correctness, and no-op defensibility.

## Evidence Assessment

The student candidate addresses all seven gaps identified in the engineering review:

1. Evidence reading order is now explicit (five steps, with STEERING.md precedence over summary.md)
2. Engineer handoff trigger is sharpened to three specific conditions
3. Smallest defensible revision is defined with measurable criteria
4. Teacher-approval criteria are explicit (alignment, no interface expansion, no out-of-scope constraints, no regression)
5. Revision scope boundary is clear
6. Contradiction exit is added (two consecutive unresolved turns → blocker report)
7. Adjacent-issue handling is explicit (note but do not fix)

The adversary candidate's exploit (removing the contradiction exit and precedence rule) is credible but does not outrank the student candidate when evaluated against the full dataset, especially training case 6.

## Forecasted Student Mistake

The most likely student mistake in a future iteration would be over-specifying the evidence reading order — adding more than five steps or making the order context-dependent in ways that reintroduce ambiguity. The current five-step order is simple and should be kept stable.

## Recommendation

**Continue to apply.** The student candidate is defensible, improves all seven identified gaps, and survives the adversary test. No additional teacher turns are needed for this iteration.

## Steering Note

Apply the student candidate to the source file. The adversary candidate confirms that the contradiction exit condition is the most valuable addition — guard against any future revision that replaces it with a "synthesize both perspectives" or similar soft instruction. Validate with `python -m pytest -q` before committing.
