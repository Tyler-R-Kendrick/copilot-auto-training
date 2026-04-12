# Engineering Review: trainer-train-code

## Overview

`trainer-train-code` is a specialization of the trainer-train orchestration loop targeting Python code artifacts optimized through Microsoft Trace. It owns workspace initialization, trainable-surface identification, test-based feedback discipline, and write-back validation for code-type targets.

## Strengths

1. **Clear Trace surface selection guide.** The skill correctly distinguishes nodes (mutable values), bundles (callable optimization), and models (grouped behavior), matching the Microsoft Trace API surface.
2. **Feedback-first discipline.** Requiring a deterministic, repeatable feedback signal before optimization is the right gate; it prevents wasted optimization on targets with no measurable improvement signal.
3. **Custom scoring default.** Defaulting to `custom` scoring for code targets (not `llm_judge`) is architecturally sound — executable test feedback is more reliable than open-ended language quality judging.
4. **Blocker-first rule.** The skill correctly treats undefined trainable surfaces and missing feedback signals as hard blockers rather than soft warnings.

## Gaps and recommendations

1. **Feedback reset cadence.** The skill mentions "reset feedback each iteration" but does not specify when within an iteration the reset must happen (before backward pass vs. before the forward pass). Clarify the exact reset point to avoid silent feedback accumulation.
2. **Trainable surface documentation artifact.** Step 4 says to "record the trainable surface in the workspace" but does not specify the artifact name or path. Define a concrete artifact (e.g., `optimize/trainable-surface.md`) so later turns can audit the decision.
3. **Election criteria for code targets.** The skill defers to the caller-supplied elector but does not specify what makes one code candidate preferable to another. Add a brief preference rule: prefer the candidate with the highest test pass rate; break ties by smallest surface change.
4. **Write-back gate completeness.** The five-point gate is good but does not mention that the `name`-equivalent identifier (the filename) must not change. Confirm the output file path matches the input.

## Verdict

Ready for optimization loop. Priority improvements: (1) trainable surface artifact path, (2) feedback reset clarification, (3) election preference rule for code targets.
