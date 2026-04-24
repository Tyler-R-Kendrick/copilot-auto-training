# Candidate Description — Student

## Source

Student revision of the initial optimize-stage candidate, addressing teacher steering from turn 1.

## Changes from Baseline

1. **Evidence Order section** (new) — numbered read sequence with explicit pre-research stop condition
2. **Approval Bar section** (new) — four named binary criteria; failure of any criterion requires rejection with recorded failure mode
3. **Constraints** — added "DO NOT start a research plan without the target prompt file and scoring rule" and replaced "ask for them" with "issue a gap report instead" for consistency
4. **Approach** — expanded from 6 steps to 8; added failure-mode taxonomy in step 6 (five labeled modes)
5. **MCP Execution Contract** — clarified `run_agent_skill` gate: when no `scripts/` helper, use loaded contract as full operating guide (not just a hint)
6. **Gap Report Format section** (new) — four required fields for pre-research stop condition
7. **Blocker Report Format section** (new) — five required fields for post-research stop condition
8. **Artifact Completeness section** (new) — five required fields per approved source; downstream-synthesis gate
9. **Output Format** — restructured to label both stop paths explicitly with cross-references to format sections

## Why This Candidate Is Stronger

All six engineer-identified gaps are resolved. The two stop conditions are now distinct sections triggered at different stages. The artifact completeness contract prevents incomplete briefs from reaching downstream synthesis.
