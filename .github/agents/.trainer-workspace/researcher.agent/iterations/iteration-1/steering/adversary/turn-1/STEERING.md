# Adversary Steering — Iteration 1, Turn 1

## Evidence Inspected

1. Student candidate (`iterations/iteration-1/candidates/student/candidate.md`)
2. Teacher steering turn 1 (identified approval-bar language as the medium-risk point)
3. Original prompt (baseline)
4. Eval rows 1-8 (all llm_judge)

## Exploit Attempts

### Exploit 1: Vague `run_agent_skill` threshold
**Mechanism**: Replace "if `scripts/run_research.py` exists, call `run_agent_skill`" with "you may optionally call `run_agent_skill` when the skill appears to have a helper script."
**Predicted judge outcome**: Fails row 5. Explicit existence check is required; optional/discretionary language does not satisfy it.

### Exploit 2: Advisory approval bar (strongest exploit)
**Mechanism**: Add "sources that partially meet these criteria may still be useful with appropriate caveats noted" to the approval bar section.
**Predicted judge outcome**: Fails rows 3 and 4. The advisory language directly contradicts the blocker requirement. Could fool style-based evaluators but not the llm_judge eval suite.

### Exploit 3: Vague constraint resolution
**Mechanism**: Replace required-vs-elicitable distinction with "use your judgment about whether to ask or proceed."
**Predicted judge outcome**: Fails row 2. Explicit taxonomy required.

## Convergence

No exploit exceeds or matches the student candidate's predicted score. Exploit 2 is the strongest but still fails on eval rows 3 and 4.

## Recommendation

Student candidate wins. No additional judge steering needed beyond confirming "partially approved" classifications are invalid. The student candidate's current wording ("Do not downgrade a rejected source to 'partially approved'") is load-bearing and correct.

## Stop Decision

**Stop adversary loop.** The student candidate is defensible. No credible exploit that the judge would accept over the student candidate was found.
