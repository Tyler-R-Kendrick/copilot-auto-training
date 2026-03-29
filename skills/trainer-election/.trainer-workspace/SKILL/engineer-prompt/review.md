# Engineer Prompt Review: trainer-election

## Current shape

- The skill clearly positions election as a post-run selection step rather than an optimizer.
- It has strong coverage of accepted workspace layouts, raw artifact preference, and tie-breaking behavior.
- The prompt is narrower than `trainer-optimize`, but it still blends operator guidance, scoring logic, and workspace discovery rules in one pass.

## Likely friction points

- The accepted-layout section is detailed, but the main operator flow does not surface the minimum viable inputs early enough.
- The output contract is strong, yet the connection between discovered artifacts and winner explanation could be easier to scan.
- The guardrails and election behavior sections overlap on what the runtime will refuse to invent or regenerate.
- Because this skill depends on existing artifacts, the prompt should make the preconditions feel more binary and less interpretive.

## Optimization goal

Sharpen the prompt so an operator can quickly determine whether the workspace is ready for election and what evidence the runtime will use, while preserving these constraints:

- election only happens after scored candidate artifacts already exist
- missing `grading.json` must remain unscored rather than inferred
- incomplete coverage must continue to be penalized
- the runtime must not regenerate candidates or rerun optimization

## Target todo list

- Make the prerequisite artifact contract more front-loaded and easier to verify.
- Collapse overlapping guidance between election behavior and guardrails.
- Clarify the order of workspace discovery, coverage resolution, aggregation, and tie-breaking.
- Keep baseline configurations explicit so comparison remains explainable.
- Preserve the JSON output fields and prompt-artifact discovery behavior unchanged.
