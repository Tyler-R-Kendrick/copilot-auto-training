# Decision — researcher.agent Iteration 1

**Target:** `.github/agents/researcher.agent.md`
**Workspace:** `.github/agents/.trainer-workspace/researcher.agent/`
**Iteration:** iteration-1
**Outcome:** Student candidate accepted. Changes persisted to source file.

## Why the Student Candidate Wins

The student candidate (trainer-loop optimized prompt) addresses all 6 engineer-prompt risks:
1. ✅ Fixed evidence reading order (6 numbered steps).
2. ✅ Workspace artifact path guidance (`research/research-brief.json` under active iteration directory).
3. ✅ MCP fallback handling (record in `unresolved_gaps`, proceed with free-form discovery).
4. ✅ Partial-approval classification (approved / conditional / rejected).
5. ✅ Structured JSON output format with defined top-level keys.
6. ✅ Complete field-mapping notes covering all four eval fields.

## Adversary Outcome

The adversary exploit (adding `conditional_sources` to the JSON schema while removing the explicit stopping rule) did not outrank the student candidate. It wins on output-format rows only. No extra judge steering is required.

## Validation

`python -m pytest -q`: **856 passed in ~9s**. No regressions.

## Next Steps

Low-priority follow-up (optional, next iteration):
1. Add explicit stopping rule between evidence reading and constraint resolution in Approach step 1.
2. Add `conditional_sources` to the JSON output schema.
3. Clarify `stop_recommendation` and `approved_sources` mutual exclusivity.
