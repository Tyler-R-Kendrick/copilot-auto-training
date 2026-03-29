## Goal

Assess the current conservator prompt as an optimization target for iterative prompt tuning, with emphasis on whether it can reliably detect regressions across prompt, dataset, evaluator, and validation changes after optimization.

The main target is operational reliability, not stylistic improvement. A strong conservator prompt should surface real contract drift, avoid speculative findings when evidence is thin, and produce review output that is stable enough to use repeatedly inside a trainer loop.

## Current Strengths

- The role is sharply scoped. It is clearly a review-only subagent, which reduces drift into editing, re-optimizing, or open-ended debugging.
- The prompt already anchors the review to the right evidence classes: changed artifacts, baseline expectations, and recent validation results.
- It includes several repo-specific high-value checks that are easy to lose during optimization work, especially skill-routing, single-shot optimize boundaries, and explicit `train.jsonl` versus `val.jsonl` handling.
- It pushes the model toward regression review rather than generic feedback, which is the right task framing for a conservator agent.
- The output format is intentionally concise and risk-first, which is useful when this review feeds a larger optimization workflow.

## Main Risks

- Coverage is uneven. Prompt and dataset regressions are foregrounded, but evaluator and validation regressions are only partly explicit, so the model may underweight scorer assumptions, authored eval compatibility, or “validation passed but proved too little” cases.
- The evidence order is underspecified. The prompt says what to inspect, but not what to inspect first, what is optional, or when missing evidence should stop the review and become the main finding.
- The output contract is a bit too loose for repeated optimization loops. Different runs may vary in structure, number of issues raised, and how clearly they separate confirmed regressions from unproven risk.
- The prompt is strong on repo-specific failure modes, but weaker on general contract drift such as placeholder loss, prompt-visible evaluator fields, schema changes, assertion mismatch, or altered pass or fail boundaries.
- It asks for the “highest-risk” issue first, but does not clearly define whether secondary issues should also be reported. That can cause either overcompression or inconsistent breadth across runs.
- There is no explicit no-finding path. In iterative review loops, that increases the risk of forced findings when the change is probably safe but only lightly validated.

## Rewrite Hypotheses

- Rewrite the prompt around a fixed audit sequence: baseline intent, changed artifacts, contract mismatches, validation proof, then verdict. This should improve consistency more than adding new domain detail.
- Make evaluator and validation review first-class rather than implicit. Explicitly name scorer assumptions, eval manifest compatibility, assertions, split hygiene, and missing negative checks as core review areas.
- Add an artifact priority order. A likely order is baseline contract first, changed files second, latest validation evidence third, supporting notes last. This should reduce noise and overreading.
- Introduce a small risk taxonomy such as `breaking regression`, `silent contract drift`, and `missing proof`. That would help the agent distinguish observed failures from plausible but unverified concerns.
- Tighten the output into a fixed decision package: highest-risk regression, secondary risks, evidence inspected, missing validation, and confidence. This should make trainer-loop consumption easier.
- Add an explicit blocker path and a no-regression path. If key evidence is missing, the agent should say the change is under-validated rather than inventing a behavioral regression.
- Keep the rewrite simple. Clearer instructions, task decomposition, and output priming are more likely to help than few-shot examples on the first pass.

## Suggested Metrics

- Seeded regression recall across four buckets: prompt, dataset, evaluator, and validation changes.
- False-positive rate on benign edits such as wording cleanup, formatting-only changes, or refactors that preserve behavior.
- Evidence anchoring rate: share of findings tied to concrete artifacts and observable validation evidence.
- Blocker accuracy: percent of cases where the agent correctly reports missing proof instead of speculating when baseline or validation evidence is absent.
- Review stability: consistency of top finding and overall verdict across repeated runs on the same input.
- Coverage completeness: percent of relevant cases where the review checks placeholders, schema or field names, split hygiene, scoring assumptions, and validation scope.
- Actionability: percent of reviews that include a concrete follow-up validation or artifact check the parent workflow can use.
- Cost and latency: token count and runtime per review, since this subagent is likely to run often inside iterative optimization.

## Recommendation

This is a good optimization target because the task is narrow, high-value, and already grounded in real workflow risks. The best next rewrite is not a broader or smarter-sounding prompt. It is a more deterministic audit prompt.

Prioritize a revision that makes evaluator and validation checks explicit, adds a fixed evidence order, and separates confirmed regressions from missing proof. Measure it first on seeded regression-detection cases and false-positive resistance. Only add examples if the first structured rewrite still misses specific regression classes consistently.