---
description: "Use when editing agentic workflow markdown files under .github/workflows/*.md. Covers required compilation, lockfile sync, and hook-backed enforcement."
applyTo: ".github/workflows/*.md"
---
# Agentic Workflow Editing Guidance

- After editing any `.github/workflows/*.md` file, run `gh aw compile <workflow-name>` before finishing and include the regenerated `.lock.yml` in the change set. For example, after editing `train-prompt.md`, run `gh aw compile train-prompt`.
- Do not rely on the stop hook as the primary mechanism; treat `gh aw compile` as part of the edit itself. Recompile after every edit — including minor formatting or comment changes — and again before opening a pull request to confirm the lockfile is in sync.
- The `agentic-workflow-validation` hook is the enforcement backstop: it checks that the `.lock.yml` is present and matches the compiled output of the source file. If it reports stale or missing lockfiles, recompile and commit the updated `.lock.yml` before finishing.
- If `gh aw compile` fails, stop and fix the workflow source instead of leaving `.md` and `.lock.yml` drift in the branch.
