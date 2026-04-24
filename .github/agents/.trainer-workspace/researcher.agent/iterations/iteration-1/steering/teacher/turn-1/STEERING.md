# Steering — Teacher — Turn 1

## Evidence Used

- `engineer-prompt/review.md`: identified four high-priority weaknesses (conditional elicitation, no stop path, implicit MCP prohibition, fragmented constraints)
- `iterations/iteration-1/synthesize/datasets/train.jsonl`: 8 training rows; all scoring `llm_judge` targeting constraint elicitation, MCP routing, stop-report, and scope discipline
- `iterations/iteration-1/optimize/manual-followup-report.json`: returned `mode=manual_followup` (CopilotInferenceError); baseline prompt confirmed correct, datasets accepted
- `iterations/iteration-1/optimize/optimized-prompt.md`: candidate produced by @trainer agent from `model_prompt`

## Predicted Response

The student candidate is expected to score higher than the original on constraint elicitation (now mandatory), MCP routing compliance (explicit prohibition added), stop-report accuracy (explicit stop path added), and scope discipline (eval-row prohibition added to Scope and Constraints). The changes are minimal and targeted; the discovery surface, output format, and frontmatter are preserved.

## Requested Revision

None. The candidate addresses all four reviewer-identified issues. The changes are defensible, surgical, and consistent with the review.md hypothesis ("smallest defensible rewrite").

## Stop-or-Continue Decision

**Stop.** The candidate is ready for validation. The teacher would likely approve given that all identified weaknesses are addressed, the interface is preserved, and the changes are evidence-grounded.

## Judge Notes

- Dataset rows use `scoring: llm_judge` with `reference` and `criteria` fields — `judge_mode=llm_judge` is correct.
- The MCP routing criterion is objectively checkable from agent behavior traces.
- Constraint elicitation and stop-report criteria are observable from response content.
