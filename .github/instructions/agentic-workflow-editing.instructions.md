---
description: "Use when editing agentic workflow markdown files under .github/workflows/*.md. Covers required compilation, lockfile sync, and hook-backed enforcement."
applyTo: ".github/workflows/*.md"
---
# Agentic Workflow Editing Guidance

- After editing any `.github/workflows/*.md` file, run `gh aw compile <workflow-name>` before finishing and include the regenerated `.lock.yml` in the change set.
- Do not rely on the stop hook as the primary mechanism; treat `gh aw compile` as part of the edit itself and rerun it after meaningful frontmatter or import changes and again before final validation.
- The `agentic-workflow-validation` hook is the enforcement backstop for this rule. If it reports required recompilation or updated lockfiles, review those changes and keep the source and lockfile synchronized before finishing.
- If `gh aw compile` fails, stop and fix the workflow source instead of leaving `.md` and `.lock.yml` drift in the branch.
