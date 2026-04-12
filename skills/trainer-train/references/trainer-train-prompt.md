# Delegation: trainer-train-prompt

## When to delegate

Route to `trainer-train-prompt` when the selected target is:

- A `*.prompt.md` file (e.g., `prompts/summarize.prompt.md`)
- A `*.prompty` artifact
- A `*.instructions.md` file (e.g., `instructions/triage.instructions.md`)
- A system prompt or natural-language instruction file that is not a SKILL.md or agent contract

## What it handles

- Prompt-specific workspace initialization (strips `.prompty` entirely; strips final extension otherwise)
- Engineering review checkpoint enforcement
- Judge-mode defaulting to `llm_judge` for open-ended prompt tasks
- Placeholder preservation before write-back
- Evaluator field isolation (keeping `expected`, `reference`, `criteria`, `scoring` out of the prompt body)
- Few-shot and chain-of-thought pattern preservation

## How to invoke

Tell the caller: "The selected target is a prompt file. Use `trainer-train-prompt` for this run." Pass the target path, workspace root, validation command, and stage capability map.

## What it does not handle

- SKILL.md files → use `trainer-train-skill`
- Python code targets → use `trainer-train-code`
- Agent contracts (`*.agent.md`) → use `trainer-train-agent`
