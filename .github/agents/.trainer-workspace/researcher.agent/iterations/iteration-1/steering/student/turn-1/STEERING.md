# Student Revision — Turn 1

## Task

Apply the teacher's targeted fix from Turn 1 of steering: clarify the `run_agent_skill` clause to explain what "guidance only" means in the context of `researcher-research`.

## Reasoning

The baseline MCP contract said: "Call `run_agent_skill` only when the skill exposes a deterministic helper under `scripts/`; otherwise use the loaded skill instructions as the active operating contract."

The phrase "otherwise use the loaded skill instructions" was ambiguous — an agent might wonder: does this mean I should call `run_agent_skill` with a different mode, or should I literally treat the loaded markdown as my operating instructions?

The targeted fix adds: "no `scripts/` helper is present or the skill only returns instructions rather than running code" — making the condition concrete — and appends "to guide the research task directly instead" to make the action unambiguous.

## Justification

The teacher predicted this single-sentence addition would reach approval. The revision is minimal, non-breaking, and does not introduce new sections, examples, or placeholders.

## Predicted Teacher Response

The teacher would predict approval: the candidate now covers all six engineer-prompt review issues with clear, actionable language, and the one remaining ambiguity has been resolved without introducing new risks.
