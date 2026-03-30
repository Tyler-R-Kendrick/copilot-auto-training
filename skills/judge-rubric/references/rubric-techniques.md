# Rubric Techniques Reference

Use this brief when authoring a formal judging rubric for scoring, grading, or evaluation. It distills the current guidance already embedded in the judge agent's workspace references into rubric-authoring rules you can apply directly.

## Current synthesis

Modern judging works best when the rubric is locked, evidence-anchored, task-adaptive, verifier-aware, and explicit about robustness limits. A strong rubric should act like a compact audit contract, not a vague grading vibe.

## Benchmark pressure

### JudgeBench

- Hard response-pair judging remains brittle even for strong models.
- Practical rule: do not rely on one holistic score without dimensioned criteria and observable evidence.

### RewardBench 2

- Hard preference and ranking tasks expose shallow comparison heuristics.
- Practical rule: add explicit tie-breakers and concrete failure modes when the rubric must separate close candidates.

## Locked-rubric techniques

### RULERS

- Locked dimensions with explicit score boundaries improve stability.
- Practical rule: define immutable dimensions and pass-partial-fail anchors before scoring starts.

### Autorubric

- Behavioral anchors make scores more reproducible.
- Practical rule: describe what a strong, medium, and weak performance looks like in observable terms.

### AdaRubric

- Rubrics should adapt to the task shape rather than staying overly generic.
- Practical rule: choose dimensions from the actual task contract, artifact types, and failure modes, then freeze them.

### RubricRAG

- Related rubric examples and benchmark guidance can improve rubric quality.
- Practical rule: ground rubric dimensions in the supplied criteria, references, benchmark notes, and domain constraints instead of inventing generic categories.

## Evidence and verification

### Agent-as-a-Judge and verifier-backed judging

- Process evidence, tool traces, logs, and intermediate artifacts matter when the domain exposes them.
- Practical rule: for each dimension, declare which artifacts count as evidence and which claims are too weak without corroboration.

### VerifiAgent-style evidence discipline

- Unsupported claims should not outweigh observable artifacts.
- Practical rule: if logs, validation results, or benchmark summaries contradict the narrative, let the artifact win.

## Calibration and robustness

### Judgment distribution

- Single-pass verdicts can overstate certainty.
- Practical rule: add explicit confidence guidance and require lower confidence when evidence is thin, conflicting, or order-sensitive.

### Order and presentation bias

- Candidate order and framing can distort judgments.
- Practical rule: include an order-bias check in the rubric package and note when the margin is narrow enough that presentation effects may matter.

### Bias-bounded evaluation

- A seemingly good judge can still be fragile to framing choices.
- Practical rule: call out sensitivity risk whenever the rubric is under-specified or the domain evidence is sparse.

## Chain-of-thought caution

### Gaming the Judge

- Narrated reasoning can bias the evaluator away from observable evidence.
- Practical rule: treat chain-of-thought and self-explanations as low-trust evidence unless corroborated by artifacts or outputs.

## Rubric-authoring rules for this repo

- Keep the rubric to 3 to 7 dimensions.
- Prefer explicit pass, partial, and fail boundaries over free-form holistic grades.
- Name the allowed evidence for each dimension.
- Lock aggregation and tie-break rules before scoring.
- Include robustness checks and confidence guidance in the final rubric package.
- Stop and ask for missing domain constraints when the rubric would otherwise require invented thresholds or labels.
