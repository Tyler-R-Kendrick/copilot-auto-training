# Approval Decision Extraction

Use these canonical references instead of carrying the full contract inline:
- Schema: `evals/files/approval-decision.schema.json`
- Workflow: `evals/files/approval-routing.mmd`

## Task

Extract the current approval decision from the request and return one JSON object that conforms to the schema.

## Critical rules

- Use only evidence present in the request and the workflow.
- Do not infer missing approvals, approvers, budgets, deadlines, or exceptions.
- If the evidence does not support a field, use the schema-safe empty value instead of guessing.

## Compact reasoning

If shorthand helps, reason internally with:
- `s` = current workflow state
- `H` = hard schema and workflow constraints
- `r` = candidate route

Choose the `r` with the strongest evidence that satisfies `H`.
Do not output this reasoning.

## Output

Return JSON only.
Before finalizing, re-check the highest-risk rule: every populated field must be evidence-backed.

## Approval request

[insert request text here]