# Teacher Steering — Turn 1

## Evidence Inspected

- Source: `.github/agents/researcher.agent.md` (baseline)
- Candidate: `iterations/iteration-1/optimize/optimized-prompt.md`
- Engineer review: `engineer-prompt/review.md`
- Datasets: 6 train rows + 2 val rows, all `llm_judge`
- Research brief: `iterations/iteration-1/research/research-brief.md`

## Comparison: Baseline vs. Candidate

### What the Candidate Fixes

1. **Input Reading Checklist** — The candidate adds a numbered checklist that specifies what to extract from each caller input before touching MCP. This directly addresses the "no evidence order" risk from the review. The stop criteria (task description and scoring rule required, others noted and continued) are defensible and proportionate.

2. **MCP Fallback Path** — The candidate explicitly states that if `find_agent_skill` or `load_agent_skill` fails, the agent must stop and deliver a blocker report rather than improvise. This directly addresses the "no fallback path" risk. The instruction is clear and actionable.

3. **Source Approval Bar Inlined** — The candidate adds the full approval bar as an agent-visible section. This means the agent can apply minimum standards even if the MCP skill load fails. The bar items match the `researcher-research/SKILL.md` approval bar without introducing new requirements.

4. **Stopping Rule Expanded** — The candidate distinguishes between hard-stop inputs (task description, scoring rule) and soft-gap inputs (domain, licensing, recency). This is the right balance: the agent stops when the gap is blocking, notes the gap when it is not.

5. **Output Format Expanded** — The candidate adds a "non-trivial content" requirement and expands mapping notes to require at least one specific field-to-eval-row mapping per approved source. This is the minimum structure needed for a downstream synthesizer.

6. **`run_agent_skill` Clarified** — The candidate now explicitly says: when the skill provides guidance only (no `scripts/` helper), use the loaded skill instructions rather than calling `run_agent_skill`. This closes the ambiguous conditional from the baseline.

### Remaining Gaps

- The candidate does not add examples of what a "non-trivial" mapping note looks like. However, adding examples would expand the prompt significantly and the current description ("which source field becomes the prompt input, which field becomes the expected output, and any transformation needed") is concrete enough to be actionable without examples.
- The candidate does not enumerate which eval datasets have been applied. This is expected — the optimization is behavioral.
- The `run_agent_skill` clarification is concise but may benefit from one more sentence indicating what "guidance only" means in context. However, this would be a cosmetic addition and does not change behavior.

## Predicted Student Mistakes

If a student drafts the next revision without guidance:
- They may add unnecessary verbosity to the input-reading checklist (e.g., instructions for what to do when every possible input is present).
- They may conflate "source approval bar" with "rejection criteria" and produce duplicate content.
- They may add examples that inadvertently become placeholders during rendering.

## Verdict

**Continue to student for one targeted revision.** The candidate is substantially improved over the baseline. The student should:
1. Add one sentence to the `run_agent_skill` clause to clarify what "guidance only" means in the context of `researcher-research`.
2. Keep all other sections intact.

This is a minimal targeted revision. After the student delivers it, the teacher would predict approval if the revision is clean.

## Stop Criteria Check

The teacher does NOT yet predict student would improve no further — one targeted fix remains. Continue to student turn 1.
