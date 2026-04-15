## Original Candidate Description

This is the unmodified current version of `.github/agents/researcher.agent.md`.

**Known weaknesses** (from engineer review):
1. `run_agent_skill` threshold is vague — does not specify how to determine if `scripts/run_research.py` exists.
2. Constraint resolution is implicit — no distinction between required and elicitable constraints.
3. Approval bar criteria are absent — agent depends solely on the loaded `researcher-research` skill contract for gating decisions.
4. No blocker-report template in output format — model may force a recommendation when no source clears the bar.
5. No minimum output scope — output format lists sections but does not mark them as required.
