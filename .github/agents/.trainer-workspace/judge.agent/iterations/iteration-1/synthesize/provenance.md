# Synthesis Note

## Plan Status

The synthesis plan is satisfied from local grounded material:

- The engineer review defines the failure modes and rewrite hypotheses.
- The local judging reference supplies the benchmark and method families that justify the rewrite.
- The `judge-trajectory` and `judge-outcome` skill contracts define the routing boundary that the eval rows must test.

## Derived Output Contract

- Authored eval cases exercise four behaviors: mixed routing, outcome-only routing, runtime-failure handling, and order-robustness under close calls.
- JSONL rows use `reference`, `criteria`, and `scoring: "llm_judge"` because exact matching would not faithfully score open-ended comparison summaries.
- The correct `judge_mode` for optimization is therefore `llm_judge`.

## Verification Path

- Each eval case asserts only observable behaviors: routed skill choice, locked rubric handling, missing-evidence behavior, runtime-failure separation, or confidence calibration.
- Each JSONL row uses explicit criteria so the scoring contract is inspectable even though the runtime judge prompt only reads the reference text directly.

## Split Note

- Train split: routing boundary, rubric stability, runtime failure separation, and outcome-only evidence discipline.
- Validation split: order-robustness on a close call and process or outcome separation without double-counting.
- All rows are synthetic but grounded by the engineer review plus the local public-source judging reference rather than by ad hoc invented style preferences.

## Runtime Caution

The source prompt file has no task-input placeholders. The synthesized datasets are correct for future optimizer-compatible harnesses, but the current `trainer-optimize` runtime cannot inject row-specific task input into `judge.agent.md` itself. A debug-only or blocked optimize path is the reliable choice for this iteration unless a temporary wrapper prompt is introduced.