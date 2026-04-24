# Student Candidate: researcher.agent.md

**Source:** Optimized by trainer agent (manual_followup handoff from trainer-optimize)

## Changes from Original

1. **`run_agent_skill` clarified**: "use the loaded skill contract as the operating guide; call `run_agent_skill` only when a deterministic helper script exists under `scripts/`" — removes the ambiguity that allowed skipping MCP when scripts are absent.

2. **Constraint fixed**: Changed "DO NOT involve any other agents" to "DO NOT hand off to or coordinate with sibling agents (teacher, student, judge, trainer, adversary). The `agent-skills` MCP server is not an agent handoff and may be used freely." — removes the contradiction between the constraint and the `agent-skills/*` tool allowance.

3. **Approach step 2 strengthened**: Now reads "...before any research action — this is a hard prerequisite, not a step that can follow initial source gathering." — raises the urgency of MCP activation before any research begins.

4. **Scope clause added**: "Do not author eval rows, JSONL datasets, or synthesized test cases; those belong to a separate synthesis workflow." — prevents scope creep into synthesis.

5. **Artifact-saving step added**: Step 7 and output format section now include guidance on saving the research brief to the caller-supplied location.

6. **Opening paragraph improved**: Added "When a desired artifact location is supplied, save the brief there and confirm the saved path in your output." — front-loads the artifact behavior.

## Predicted Judge Response

The judge should prefer the student candidate over the original because:
- All identified failure modes are addressed with minimal additions
- No new placeholders introduced
- No evaluator-only fields exposed
- Scope is narrowed rather than expanded
- Interface (frontmatter, argument-hint) unchanged
