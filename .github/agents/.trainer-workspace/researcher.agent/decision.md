# Decision Summary — researcher.agent

## Selected Candidate

**Student candidate** (winner over original and adversary).

## Optimization Goal

Improve the researcher agent contract by making the MCP `run_agent_skill` threshold explicit, formalizing constraint resolution into required vs elicitable categories, embedding the source approval bar directly in the agent, adding a blocker-report template to the output format, and mandating all required output sections.

## Key Changes Made

1. **`run_agent_skill` threshold**: The MCP Execution Contract now explicitly says to check for `scripts/run_research.py` in the skill directory and call `run_agent_skill` only when it is present; otherwise use the loaded skill instructions as the active operating contract.
2. **Constraint Resolution section**: Added a dedicated section distinguishing required inputs (task boundary, scoring rule, prompt placeholders — must ask if missing) from elicitable ones (domain, language, recency — ask only when materially affecting source selection).
3. **Source Approval Bar section**: Embedded five approval bar criteria directly in the agent contract so the model does not depend solely on the loaded skill contract for gating decisions. Added an explicit prohibition on "partially approved" classifications.
4. **Blocker-report template**: Added to the output format with required content: failed criteria, missing evidence, and a stop recommendation.
5. **Required sections mandate**: Output format now explicitly marks all six sections as required.

## Adversary Assessment

Three exploit attempts were made: vague `run_agent_skill` threshold, advisory approval bar, and vague constraint resolution. None exceeded the student candidate's predicted score. The approval-bar advisory language (exploit 2) was the strongest attack surface but failed eval rows 3 and 4.

## Validation

`python -m pytest -q` — **856 passed, 0 failed**.

## Target File

`.github/agents/researcher.agent.md`

## Workspace

`.github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/`

## Iteration

`iteration-1`, judge_mode: `llm_judge`, 8 eval cases (6 train, 2 val).
