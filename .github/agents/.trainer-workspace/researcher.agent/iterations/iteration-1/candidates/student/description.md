The optimized `researcher.agent.md` candidate produced by the `@trainer` agent in manual-followup mode.

**Key improvements over baseline:**
1. **Evidence reading order** — Steps 1–4 sequence: target file → task description/scoring rule → existing evals → stop reading and plan
2. **MCP fallback rule** — Explicit paragraph: when all MCP tool calls fail, report a blocker and stop; do not substitute free-form research
3. **Inline source approval bar** — Dedicated section with 5 binary checks: maintainer, origin/schema, license, version stability, contamination risk
4. **Blocker reporting consistency** — Trigger language is consistent across step 5 (missing constraints), Constraints section, and MCP fallback paragraph
5. **Stopping condition** — Step 11: stop once approved-source list is stable and mapping notes can support downstream synthesis
6. **Execute tool scope** — Restricted to `scripts/run_research.py` in MCP contract; not for general search

**Teacher assessment: STOP — approved for write-back on all 5 criteria.**
