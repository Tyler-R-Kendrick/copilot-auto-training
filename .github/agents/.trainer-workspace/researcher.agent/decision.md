# Decision — researcher.agent — Iteration 1

## Selected Candidate

**Student candidate** (manual-followup optimize pass)

## Changes Applied

The following improvements were applied to `.github/agents/researcher.agent.md`:

1. **Mandatory constraint elicitation gate** — Added a "Required Inputs — Resolve Before Searching" section listing all six required inputs. Replaced the conditional "If any of these materially affect source selection and are missing, ask first" phrasing with a mandatory gate: elicit missing inputs, and stop with a blocker report if the caller cannot or does not provide them.

2. **Explicit stop path when constraints are unresolvable** — The new gate explicitly states: "stop and name the unresolved constraint in a blocker report rather than guessing or proceeding with an assumed value."

3. **Strengthened MCP routing prohibition** — Added "Do not begin source search or propose source candidates before `researcher-research` is loaded. Free-form research is not a fallback when MCP is available." to the MCP Execution Contract. Also added constraint #2 in the numbered list.

4. **Consolidated and numbered constraints** — Converted the `DO NOT` bullet groups into a numbered list of 6 constraints, adding explicit prohibitions for free-form research and eval-row authoring.

5. **Tightened Approach steps** — MCP activation is now step 1; constraint resolution gate is step 3 with a clear stop path.

6. **Scope clarification** — Added "Stop at mapping notes. Do not author eval rows or hand off to other agents." to the Scope section.

## Validation Result

856 tests passed, 0 failed (`python -m pytest -q`).

## Optimize Mode

`manual_followup` — no external model available. Candidate produced by @trainer agent from returned `model_prompt`.

## Artifacts

- `iterations/iteration-1/research/research-brief.json`
- `iterations/iteration-1/synthesize/evals/evals.json` (5 eval cases)
- `iterations/iteration-1/synthesize/datasets/train.jsonl` (8 rows, llm_judge)
- `iterations/iteration-1/synthesize/datasets/val.jsonl` (4 rows, llm_judge)
- `iterations/iteration-1/optimize/manual-followup-report.json`
- `iterations/iteration-1/optimize/optimized-prompt.md`
- `iterations/iteration-1/optimize/operator-followup.md`
- `iterations/iteration-1/candidates/candidates.json`
- `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
- `iterations/iteration-1/validation/pytest.txt`
