# Outcome Judging Techniques

Use this reference when `judge-outcome` needs a compact reminder of the latest outcome-focused judging techniques.

## Core techniques

- Locked rubrics: use explicit outcome dimensions and score boundaries rather than free-form grading. See RULERS (`arXiv:2601.08654`).
- Task-adaptive weighting: adjust the outcome dimensions to the task before scoring instead of forcing one universal rubric. See AdaRubric (`arXiv:2603.21362`).
- Retrieval-grounded rubric design: if reusable benchmark notes or prior rubrics exist, use them to ground the outcome rubric rather than improvising from scratch. See RubricRAG.
- Distribution-aware calibration: if the evidence is thin or benchmark-sensitive, preserve uncertainty instead of manufacturing certainty. See Judgment Distribution (`arXiv:2503.03064`).
- Order robustness: check whether the selected winner depends on candidate order or presentation. See the rubric-based position-bias paper (`arXiv:2602.02219`) and PCFJudge.
- Chain-of-thought skepticism: do not trust narrated reasoning over final observable outputs. See Gaming the Judge (`arXiv:2601.14691`).

## Outcome-specific benchmark pressure

- JudgeBench (`arXiv:2410.12784`) shows that generic judges can be weak on hard pairwise outcome judgments.
- ContextualJudgeBench is a reminder that contextual outcome judging is still brittle, so force grounding in the supplied reference and criteria.
- RewardBench 2 is a pressure test for hard preference judgments, so avoid shallow winner-picking when the margin is narrow.

## Operational reminders

- Prefer outcome evidence over presentation quality.
- Use a locked rubric across all candidates in the same comparison.
- Report uncertainty when decisive evidence is thin or conflicting.
- Keep the final outcome summary concise and decision-ready.
