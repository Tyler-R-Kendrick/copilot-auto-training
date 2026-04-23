# Steering Turn 1 — Teacher Review

## Evidence Used

- Original `researcher.agent.md`
- Optimized candidate from manual-followup optimize pass
- Engineer-prompt review summary (5 identified improvements)

## Teacher Assessment

All 5 improvements were implemented correctly, with one partial regression:

**Improvement 1 (Reorder skill activation):** ✅ Correct  
**Improvement 2 (`run_agent_skill` condition):** ⚠️ Partial regression — MCP contract bullet hard-codes `scripts/run_research.py` which is a fabricated specific filename not verified in workspace artifacts.  
**Improvement 3 (No-op path):** ✅ Correct  
**Improvement 4 (Non-interactive gap reporting):** ✅ Correct  
**Improvement 5 (Sub-agent constraint):** ✅ Correct  

## Predicted Student Mistake

Student will likely retain `scripts/run_research.py` because the engineer review implied it exists — but the specific filename was never cited in workspace artifacts.

## Requested Revision

In MCP Execution Contract bullet 3, replace:
> "the `researcher-research` skill exposes a `scripts/run_research.py` helper"

With:
> "the deterministic helper exposed under `scripts/` by the loaded skill contract"

## Verdict

**APPROVE_WITH_MINOR_EDITS** — one targeted edit, no structural changes needed.

## Stop-or-Continue

Apply the targeted edit and write back. Teacher predicts no further improvement is needed after this change.
