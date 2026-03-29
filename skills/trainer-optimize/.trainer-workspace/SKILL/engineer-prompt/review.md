# Engineer Prompt Review: trainer-optimize

## Current shape

- The skill is operational and specific about explicit `train` and `val` inputs.
- It already documents single-shot behavior, output modes, and guardrails against hidden dataset synthesis.
- The prompt mixes invocation help, repository policy, runtime behavior, dashboard usage, and script help into one long contract.

## Likely friction points

- The description is accurate, but the body repeats the same dataset and persistence rules in several sections.
- The output contract is easy to miss because default-return behavior, file persistence, and report-writing guidance are split across multiple headings.
- The dashboard section is useful, but it interrupts the main operator flow and may weaken priority around path validation and placeholder checks.
- The script examples still carry a broad CLI-help tone instead of emphasizing the repo's intended operator workflow.

## Optimization goal

Make the skill easier to execute correctly on the first read while preserving these constraints:

- explicit `train.jsonl` and `val.jsonl` inputs are mandatory
- authored evals remain in `evals/evals.json`
- optimization is single-shot and does not do leader election
- prompt updates happen only when `in_place` is requested

## Target todo list

- Tighten the opening contract so the operator sees the mandatory inputs and stop conditions immediately.
- Reduce repetition around persistence modes, report output, and dataset ownership.
- Reorder the body so the operational path reads as: when to use -> required inputs -> process -> output modes -> troubleshooting details.
- Keep the repo-specific constraints explicit without making the skill read like general CLI help.
- Preserve placeholders, flags, and supported modes exactly unless the runtime contract requires a change.
