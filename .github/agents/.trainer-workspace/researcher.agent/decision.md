# Decision Summary — researcher.agent.md

## Target

`.github/agents/researcher.agent.md`

## Workspace

`.github/agents/.trainer-workspace/researcher.agent/`

## Selection Reason

First alphabetically among `.agent.md` files without an existing trainer workspace.

## Iteration

`iteration-1`

## Optimization Path

`manual_followup` — the `opto`/`agentlightning` runtime was unavailable; the current `@trainer` agent answered the `model_prompt` from `manual-followup-report.json` and produced `optimized-prompt.md` directly.

## Changes Applied

The student candidate resolves all six engineer-identified gaps:

1. **Evidence Order** — numbered read sequence with explicit pre-research stop condition
2. **MCP routing condition** — clarified to apply to any task involving identifying, evaluating, approving, or rejecting public-source material; fallback-to-improvisation loophole closed
3. **Approval Bar** — four named binary criteria; failure of any criterion requires rejection with recorded failure mode
4. **Rejection evidence** — five labeled failure modes (`license_failure`, `accessibility_failure`, `annotation_quality_failure`, `field_mapping_failure`, `provenance_risk`)
5. **Gap Report Format** — four required fields for pre-research stop condition (new section)
6. **Blocker Report Format** — five required fields for post-research stop condition (new section)
7. **Artifact Completeness** — five required fields per approved source; downstream-synthesis gate
8. **Output Format** — two stop paths explicitly labeled with cross-references

## Adversary Assessment

The adversary identified a credible exploit: the scoring-rule derivation bypass (making the gap-report safety gate for missing scoring rules dead code by adding an implicit derivation path). The student candidate's strict gate (`DO NOT start a research plan without the target prompt file and scoring rule`) already guards against this exploit — confirming the strict gate is the correct behavior.

## Validation Result

856 tests passed, 0 failures.

## Decision

**ACCEPTED** — Student candidate persisted to `.github/agents/researcher.agent.md`. All tests pass.
