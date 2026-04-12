# Decision: adversary.agent.md — Iteration 1

## Selected Candidate

**Student candidate** (trainer-synthesized + student-refined)

## Changes Applied

The optimized prompt adds:

1. **Evidence Order** (new section): Explicit 5-step read order before any exploit is built — baseline intent, changed artifacts, validation evidence, judge scoring context, supporting notes.

2. **Trainer-specific exploit surfaces** (added to Focus Areas): Skill-routing gaps (`find_agent_skill`, `load_agent_skill`, `run_agent_skill`), dataset-shape mismatches between authored evals and explicit train/val datasets, judge-mode errors, `manual_followup` misclassification, and eval/dataset blur.

3. **Structured Approach** (expanded from 3 to 6 steps): Added compare-vs-student logic (step 4), stopping condition (step 6), and recursive reflection before stopping. Step 4 requires stating predicted judge scores for both the exploit and the student candidate in `{"score": <float>}` format.

4. **Artifact Contract** (new section): Describes the expected content and purpose of all four required artifact files (`candidate.md`, `description.md`, `predicted-judge-response.md`, `reflection.md`), with `predicted-judge-response.md` specifying the `{"score": <float>}` format for machine-comparable score prediction.

## Adversary Review Summary

The adversary found two credible exploit patterns above the student candidate (predicted 0.92 and 0.87 vs student 0.80):

- **Evidence Reconstruction License**: Replacing the honest "missing proof" guard with a fabrication protocol that licenses inventing workspace state.
- **Phantom Routing-Gap Specificity**: A "verification procedure" for infrastructure-layer behavior invisible to the adversary's tools.

These exploits describe gameable *variants* of the prompt, not direct flaws in the student candidate. The student's honest epistemic guard and structured evidence order are the correct production behaviors. Extra judge steering should reward honest epistemic guards over fabrication-license language.

## Validation

`python -m pytest -q`: **765 passed** — no regressions.

## Workspace

`.github/agents/.trainer-workspace/adversary.agent/`
- Latest iteration: `iterations/iteration-1/`
- Optimize: `manual_followup` (no model credentials; trainer answered model_prompt)
- Datasets: 6 train + 2 val rows, `judge_mode=llm_judge`
- Steering: teacher turn-1, adversary turn-1
