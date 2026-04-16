# Decision: researcher.agent.md — Iteration 1

## Selected Candidate

**Student candidate** (optimized prompt from manual_followup + teacher verification)

## Key Changes

1. **Evidence reading order** — approach step 1 now specifies target file → task description → scoring rule → caller constraints.
2. **Elicitation step** — approach step 2 explicitly stops and asks for missing constraints before building the search plan.
3. **Explicit fallback** — MCP contract and approach both state: when no `scripts/` helper exists, use loaded skill instructions as the active contract. Agents must not refuse to help when the script is unavailable.
4. **Source approval bar** — compact checklist added directly to the agent: accountable maintainer, traceable origin, compatible license, stable version, acceptable contamination/privacy risk.
5. **Blocker-report format** — output format section names what a blocker report should contain and explicitly recommends stopping synthesis.
6. **Improved argument-hint** — distinguishes required (target file, task description, scoring rule) from recommended (constraints) from optional (artifact location) inputs.

## Validation

`python -m pytest -q`: **856 passed, 0 failed** (2026-04-16)

## Adversary Verdict

No credible exploit found. Over-elicitation trap and MCP bypass both fail against the student candidate.

## Next Steps

None. Optimization complete. Workspace state: `complete`.
