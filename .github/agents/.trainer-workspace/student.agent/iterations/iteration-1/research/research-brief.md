# Research Brief: student.agent.md

## Target Task

The `student.agent.md` is a teacher-guided candidate revision agent in the trainer prompt-optimization loop. Its primary task is to absorb teacher critique, implement the smallest defensible revision to a candidate prompt, expose a reasoning trajectory, and predict whether the teacher would approve the result.

## Source Material

This brief is derived from direct inspection of the repository's agent collaboration contract:
- `.github/agents/student.agent.md` (optimization target)
- `.github/agents/teacher.agent.md` (collaborator)
- `.github/agents/adversary.agent.md` (reference for exploit risks)
- `.github/agents/.trainer-workspace/adversary.agent/engineer-prompt/review.md` (review pattern)
- Existing evals at `.github/agents/.trainer-workspace/adversary.agent/iterations/iteration-1/synthesize/`

## Task Shape

Input: teacher critique + current candidate prompt + workspace evidence (steering artifacts)
Output: revised candidate prompt + reasoning trajectory + teacher-approval prediction

## Evaluation Dimensions

1. **Revision precision**: Does the student change only what the critique targets?
2. **Reasoning transparency**: Does the student expose plan, tradeoffs, and uncertainty?
3. **Teacher-approval accuracy**: Does the student accurately predict whether the teacher would approve?
4. **Handoff correctness**: Does the student correctly identify when to request a teacher turn vs. proceed?
5. **No-op defensibility**: Does the student correctly justify a no-op when evidence doesn't support revision?

## Dataset Split Strategy

- 6 train rows: range from clear revisions to justified no-ops, including handoff requests
- 2 val rows: held-out cases testing precision and approval prediction

## Scoring

All rows use `llm_judge` scoring since evaluation requires qualitative assessment of revision quality and reasoning.
