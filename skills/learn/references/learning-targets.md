# Learning Targets

Use this note when a user correction could plausibly belong in more than one repository surface.

## Preferred target order

1. Use agent memory when available and appropriate for stable cross-task facts.
2. Otherwise create or update `.agents/MEMORY.md` for durable, file-backed memory.
3. Update the narrowest instruction file that owns the behavior.
4. Update or create the relevant skill contract when the lesson changes how a reusable capability should trigger or behave.
5. Update or create a custom agent under `.github/agents/` when the lesson belongs to a persistent specialist role or handoff boundary.
6. Update `AGENTS.md` when the lesson is broad repository operating guidance for agents.
7. Update hooks under `.github/hooks/` when the lesson should be enforced or reminded automatically.
8. Update documentation when contributors need a discoverable explanation in addition to the source-of-truth instructions.
9. Update evals or tests when the lesson is objective enough to verify automatically.

## Surface selection guide

### Agent memory or `.agents/MEMORY.md`

Use for:
- durable conventions
- validated commands
- stable repository facts
- cross-task lessons that should be recalled without re-reading many files

Avoid for:
- ephemeral task notes
- speculative rules
- workflow contracts that need richer step-by-step instructions

### Copilot agent instructions or file-based instructions

Use for:
- default behavior changes
- file-pattern-specific editing rules
- instruction changes that should apply automatically without invoking a named specialist

### Copilot Custom Agents in `.github/agents/`

Use for:
- specialized roles
- explicit handoffs
- repeatable multi-step ownership boundaries

### Agent skills in `skills/`

Use for:
- reusable capabilities
- on-demand workflows
- tasks that keep failing because the instructions are faulty or incomplete
- situations where a stronger trigger contract is better than adding more global prompt text

### `AGENTS.md`

Use for:
- broad repository operating guidance
- shared expectations for agent behavior
- discoverable agent-facing rules that should be visible at the repo level

### Copilot Hooks in `.github/hooks/`

Use for:
- deterministic validation
- reminders
- sync automation
- rules that should execute automatically rather than rely on model recall

## Create, modify, or optimize

- Create a new surface when no existing artifact clearly owns the behavior and the lesson is likely to recur.
- Modify an existing surface when the repository already has a clear owner for the behavior.
- Optimize a skill or custom agent when the correct surface already exists but under-triggers, misfires, or lacks the right examples and workflow guidance.

## Signs the learning should stay local

- The correction only affects one transient task.
- The user expressed a personal preference rather than a repository convention.
- The broader rule is still unclear.
- Encoding the rule would create duplication without adding enforcement.

## Signs the learning deserves a regression check

- The same mistake has happened more than once.
- The lesson changes a strict contract such as file paths, validation commands, or response structure.
- The lesson selects or creates a persistent artifact that future runs must keep using.
- The repository already uses tests or eval manifests to guard similar behavior.
