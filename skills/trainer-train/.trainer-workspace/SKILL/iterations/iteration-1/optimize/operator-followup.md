# Operator Follow-up — Iteration 1

**Blocker:** `trainer-optimize` MCP skill not available in current environment (no MCP server connection).

**Handoff summary:** The current `@trainer` agent answered the `model_prompt` from `manual-followup-report.json` directly, producing `optimized-prompt.md` as the iteration-1 optimize-stage candidate. The candidate addresses all five failure modes identified in `engineer-prompt/review.md`:

1. **Over-abstraction risk** → Added explicit resumption logic in step 1 of Core Workflow; named the three judge-mode shapes precisely.
2. **Artifact precision** → Elevated reference file reading into a callout box and added inline cues at steps where paths or scoring behavior might be improvised.
3. **Judge-mode clarity** → Replaced the vague "richer scoring" language with three named modes (exact-match, structured/normalization-aware, open-ended/LLM judge) with explicit discriminators.
4. **No-op discipline** → Added a dedicated **Blocker-first rule** section positioned before the Core Workflow so it cannot be missed.
5. **Write-back safety** → Changed "validation passes" to "both validation passes **and** the decision summary is written" in two places (Core Workflow step 11 and Validation/write-back rule).

**Optional rerun command:** Once MCP connectivity is restored, rerun with:
```
trainer-optimize --target skills/trainer-train/SKILL.md \
  --train skills/trainer-train/datasets/train.jsonl \
  --val skills/trainer-train/datasets/val.jsonl \
  --evals skills/trainer-train/evals/evals.json \
  --judge-mode llm_judge \
  --iterations 3
```
