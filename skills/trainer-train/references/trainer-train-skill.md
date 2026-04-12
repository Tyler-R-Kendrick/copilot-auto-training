# Delegation: trainer-train-skill

## When to delegate

Route to `trainer-train-skill` when the selected target is:

- A `SKILL.md` file in any skill directory following the agentskills.io specification
- A skill directory where the improvement focus is frontmatter triggering, body content, structure, or all three

## What it handles

- Skill-specific workspace initialization (uses skill directory name as `<skill-name>`)
- Engineering review checkpoint enforcement
- Two-concern separation: frontmatter (triggering) vs. body (execution reliability)
- Spec-compliance validation: required YAML fields, body length limit (500 lines), progressive disclosure structure
- Judge-mode defaulting to `llm_judge` for open-ended skill quality tasks
- `name` field preservation (must not change during optimization)
- Evaluator field isolation before write-back

## How to invoke

Tell the caller: "The selected target is a SKILL.md file. Use `trainer-train-skill` for this run." Pass the skill directory path, workspace root, validation command, improvement focus, any observed failure modes (under-trigger, over-trigger, bloated body), and the stage capability map.

## What it does not handle

- Prompt files → use `trainer-train-prompt`
- Python code targets → use `trainer-train-code`
- Agent contracts → use `trainer-train-agent`
