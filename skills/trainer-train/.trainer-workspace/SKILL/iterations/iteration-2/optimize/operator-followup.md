# Operator Follow-up — Iteration 2

**Blocker:** `trainer-optimize` MCP skill not available in current environment (no MCP server connection).

**Handoff summary:** The current `@trainer` agent delegated to the `student` subagent for iteration-2 candidate revision, then merged the result into `optimized-prompt.md`. This is the v0.3.0 candidate. Four teacher coaching points were applied as a narrow clarity-and-precedence pass:

1. **Blocker-first scope:** Removed `validation has not passed on the current candidate` bullet — that is a write-back gate, not a pre-execution blocker. The blocker-first section now covers only: missing engineering review, missing datasets/evals, and `training`-state resumption.
2. **Judge-mode precedence:** Added: "When a row declares `scoring`, treat that as authoritative. Only infer from fields when `scoring` is absent." Plus: "If train and validation rows imply different scoring modes, stop and report dataset inconsistency instead of guessing."
3. **Reference callout → Before you start section:** Converted the blockquote into a `## Before you start` section positioned before `## When to use this skill` with 3 bullet points.
4. **Output contract items 2 and 6:** Item 2 now = "current-turn stage decisions: reuse choice, judge mode, selected branch, and any blockers encountered this turn". Item 6 now = "next required action: what must happen next to resume or continue the loop, and what is waiting on it."

**Optional rerun command:** Once MCP connectivity is restored:
```
trainer-optimize --target skills/trainer-train/SKILL.md \
  --train skills/trainer-train/datasets/train.jsonl \
  --val skills/trainer-train/datasets/val.jsonl \
  --evals skills/trainer-train/evals/evals.json \
  --judge-mode llm_judge \
  --iterations 3
```
