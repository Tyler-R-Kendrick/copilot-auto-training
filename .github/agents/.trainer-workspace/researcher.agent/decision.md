# Decision Summary — researcher.agent

## Target
`.github/agents/researcher.agent.md`

## Workspace
`.github/agents/.trainer-workspace/researcher.agent/`

## Selection Reason
First `.agent.md` file alphabetically without an existing trainer workspace.

## Iteration
`iteration-1` (new run)

## Optimize Stage
`manual_followup` — no model credentials configured. `@trainer` agent answered the returned `model_prompt` directly.

## Candidate Chosen
**Student candidate** from `iterations/iteration-1/optimize/optimized-prompt.md`

### Improvements Over Baseline
1. **Evidence reading order** — Steps 1–4 sequence: target file → task description/scoring rule → existing evals → stop and plan
2. **MCP fallback rule** — Any individual MCP call failure triggers a blocker; no graceful degradation or local skill fallback allowed
3. **Inline source approval bar** — Dedicated section with 5 binary checks
4. **Blocker reporting consistency** — Consistent trigger language across step 5, Constraints, MCP fallback
5. **Stopping condition** — Step 11: stop once approved-source list is stable and mapping notes are actionable
6. **Execute scope** — Restricted to `scripts/run_research.py`

### Adversary Fix
Adversary found a credible exploit (partial MCP failure → graceful degradation, predicted score 0.93 vs 0.88). Student candidate updated to cover any individual call failure (`find_agent_skill` fails OR `load_agent_skill` fails) and prohibit local skill copy fallback.

## Validation
`856 passed` — no regressions.

## Write-Back
Applied to `.github/agents/researcher.agent.md`.
