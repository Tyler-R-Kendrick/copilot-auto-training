# Decision Summary — researcher.agent.md

## Target

`.github/agents/researcher.agent.md`

## Workspace

`.github/agents/.trainer-workspace/researcher.agent/`

## Winner

**Student candidate** (iteration-1) — based on optimizer output with one targeted teacher-guided fix.

## Why This Candidate Was Chosen

The student candidate addressed all six issues identified in the engineer-prompt review:

1. **Input Reading Checklist** added with explicit stop criteria for missing task description and scoring rule.
2. **MCP Fallback Blocker** added: when `find_agent_skill` or `load_agent_skill` fails, agent stops with a named blocker report.
3. **Source Approval Bar** inlined into agent body so the agent can apply standards even when MCP skill load fails.
4. **Stopping Rule Expanded** to distinguish hard-stop inputs (task description, scoring rule) from soft-gap inputs (domain, licensing, recency).
5. **Output Format Expanded** with non-trivial content requirement and minimum mapping note structure (field-to-eval-row mapping per approved source).
6. **`run_agent_skill` Condition Clarified**: when the skill provides guidance only (no `scripts/` helper or instructions-only), use loaded instructions directly.

## Adversary Result

Soft MCP fallback substitution exploit was attempted and found not credible. Student candidate dominates across all 8 eval dimensions.

## Validation

`python -m pytest -q` → **856 passed** (0 failures)

## Iteration

- `iterations/iteration-1/` contains all research, synthesize, optimize, candidates, steering, and validation artifacts.
- Optimize stage ran as `manual_followup` (no inference model configured). Agent answered `model_prompt` and saved as `optimized-prompt.md`.
- One teacher steering turn and one student revision turn completed.
