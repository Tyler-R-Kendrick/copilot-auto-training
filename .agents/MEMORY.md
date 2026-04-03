# Repository Memory

- Agentic workflow source files under `.github/workflows/*.md` must be followed by `gh aw compile <workflow-name>` before finishing so the checked-in `.lock.yml` stays in sync.
- The `agentic-workflow-validation` hook is the enforcement surface for this rule and should watch patch-based edits as well as standard write/edit tools.
