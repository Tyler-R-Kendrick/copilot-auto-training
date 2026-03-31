# Learning Targets

Use this note when a user correction could plausibly belong in more than one repository surface.

## Preferred target order

1. Update the narrowest instruction file that owns the behavior.
2. Update the relevant skill contract when the lesson changes how a reusable skill should trigger or behave.
3. Update documentation when contributors need a discoverable explanation in addition to the source-of-truth instructions.
4. Update evals or tests when the lesson is objective enough to verify automatically.

## Signs the learning should stay local

- The correction only affects one transient task.
- The user expressed a personal preference rather than a repository convention.
- The broader rule is still unclear.
- Encoding the rule would create duplication without adding enforcement.

## Signs the learning deserves a regression check

- The same mistake has happened more than once.
- The lesson changes a strict contract such as file paths, validation commands, or response structure.
- The repository already uses tests or eval manifests to guard similar behavior.
