## Original Candidate

The baseline `researcher.agent.md` as it existed before optimization.

**Key characteristics:**
- Correctly scopes role to source discovery, triage, and provenance review.
- States MCP execution contract (find → load → run).
- Has a 6-item output format section.
- Approach says to "read target file, task description, scoring rule, constraints first" but does not enforce order.
- No approval bar defined in the agent itself.
- No explicit elicitation step before searching.
- No blocker-report format.
- `argument-hint` lists all inputs without distinguishing required from optional.
