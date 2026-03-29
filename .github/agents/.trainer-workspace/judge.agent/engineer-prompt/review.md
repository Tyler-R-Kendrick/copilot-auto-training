## Goal

Assess the current judge prompt as an optimization target for iterative prompt tuning, with emphasis on whether it reliably routes to judge-trajectory and judge-outcome, produces stable evidence-anchored verdicts, and stays concise enough for repeated trainer-loop use.

The main optimization target is not basic quality. It is operational reliability: correct routing, rubric stability, evidence discipline, and decision usefulness under repeated runs. There is no benchmark baseline yet, so this review is a pre-optimization diagnosis rather than a measured improvement claim.

## Current Strengths

- The prompt already has a strong core task shape. It frames judging as an evidence-anchored comparison for optimization loops, not a generic grading task.
- The routing contract is unusually strong. It distinguishes process-heavy judgments from outcome-only judgments and explicitly orders dual-mode use: trajectory first, outcome second.
- It pushes the model toward good judge behavior: locked rubric, evidence ledger, fixed scoring criteria, explicit tie-breakers, and calibrated confidence.
- It correctly treats runtime failure as first-class evidence instead of collapsing everything into vague prompt quality.
- It uses the local judging reference as a support artifact rather than copying benchmark lore into the runtime prompt, which is the right separation between durable guidance and execution-time instructions.
- The output goal is decision-oriented. It asks for a package a parent optimization agent can act on, not a long essay.

## Main Risks

- The prompt is dense and partly repetitive. Scope, operational instructions, approach, focus areas, and output format all restate similar constraints. That raises token cost and increases the chance that the model latches onto one phrasing while ignoring another.
- Routing is directionally good but still somewhat ambiguous at the boundary. In mixed cases, the prompt says to load both skills, but it does not clearly define when outcome evidence is merely supportive versus actually decisive.
- Rubric adaptation may drift across runs. The prompt wants task-adaptive dimensions while also asking for a locked rubric. Without a tighter shell, repeated runs may produce different dimension sets for the same task.
- Evidence gathering is broad but not prioritized. The prompt lists many artifact types, but it does not clearly tell the model what to read first, what is optional, or when it has enough evidence to stop searching.
- The output contract is human-readable but not rigid. For optimization loops, loose prose can reduce comparability across iterations and make downstream synthesis harder.
- Confidence handling is under-specified. The prompt asks for confidence notes, but not for a stable scale or explicit triggers for low confidence, close call, or insufficient evidence.
- In dual-skill cases, the prompt does not explicitly prevent double-counting the same evidence in both process and outcome judgments.
- The prompt is strong on anti-vibe language, but weaker on anti-overreach mechanics. It says not to invent evidence, but does not force a visible missing-evidence section when key artifacts are absent.

## Rewrite Hypotheses

- Compress the prompt into a shorter execution spine: route, lock rubric, build evidence ledger, score, report. Reducing duplication should improve instruction adherence and lower token overhead without changing intent.
- Replace the routing prose with a small decision table. One row each for trajectory-only, outcome-only, and combined cases should improve routing consistency and reduce boundary confusion.
- Add a fixed output scaffold with explicit fields such as Routed skills, Locked rubric, Decisive evidence, Rejected candidate failure modes, Confidence, and Missing evidence. This should improve comparability across optimization runs.
- Introduce a rubric shell that is stable by mode. For example: process mode defaults to plan, evidence gathering, tool use, failure handling, outcome; outcome mode defaults to compliance, correctness, completeness, format, safety. Let the judge adapt within that shell rather than inventing dimensions from scratch each time.
- Add evidence priority order. For example: task contract and criteria first, then benchmark or validation artifacts, then trajectories or outputs, then supporting notes. This should cut unnecessary context loading and reduce noise.
- Add an explicit anti-double-counting rule for combined judging: process evidence determines operational reliability, outcome evidence determines end-state quality, and shared artifacts should only support one primary dimension unless clearly distinct.
- Add confidence thresholds tied to evidence quality and margin. This should reduce false certainty on close comparisons and make order-robustness warnings more consistent.
- Require an explicit blocker path: if required artifacts are missing, the judge should say what cannot be concluded rather than infer from presentation quality.

## Suggested Metrics

- Routing accuracy: percent of evaluation cases where the judge selects the expected mode of outcome-only, trajectory-only, or combined.
- Rubric stability: consistency of rubric dimensions across repeated runs on the same task.
- Order robustness: verdict agreement when candidate order is reversed.
- Evidence anchoring rate: share of decisive claims that cite observable artifacts rather than general impressions.
- Unsupported-claim rate: frequency of references to evidence, failures, or benchmark results that are not actually present.
- Failure separation accuracy: percent of cases where runtime failures are correctly separated from prompt-quality weaknesses.
- Output contract completeness: percent of runs containing all required decision fields.
- Confidence calibration: whether low-confidence labels correlate with close margins, conflicting artifacts, or order-sensitive verdicts.
- Decision utility: percent of judge outputs that a parent trainer step can use without manual normalization or clarification.
- Cost and latency: prompt plus response token count and average runtime per judging task.

## Recommendation

This is already a strong prompt and does not need a conceptual rewrite. The right next step is a focused operational rewrite that preserves the current evidence-anchored philosophy while making three things tighter: routing boundaries, rubric stability, and output structure.

Prioritize a smaller, more deterministic prompt over a smarter-sounding one. The best hypothesis is that a leaner routing-and-rubric scaffold will outperform the current version on repeatability and trainer-loop usability without sacrificing judgment quality. The first evaluation pass should measure routing accuracy, order robustness, evidence anchoring, and output completeness before optimizing anything more ambitious.