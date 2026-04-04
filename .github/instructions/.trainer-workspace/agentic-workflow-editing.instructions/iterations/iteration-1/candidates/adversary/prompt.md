---
description: "Use when editing agentic workflow markdown files under .github/workflows/*.md. Covers required compilation, lockfile sync, and hook-backed enforcement."
applyTo: ".github/workflows/*.md"
---
# Agentic Workflow Editing Guidance

- After editing any `.github/workflows/*.md` file, run `gh aw compile <workflow-name>` (for example, `gh aw compile train-prompt` for `train-prompt.md`) and include the regenerated `.lock.yml` in the change set. Compilation is particularly important after edits that touch frontmatter, step definitions, imported resources, or structural ordering — these are the changes most likely to produce lockfile drift.

- Do not rely on the `agentic-workflow-validation` hook as the primary mechanism; treat `gh aw compile` as part of the edit itself. Run it proactively after substantive edits and again before opening a pull request.

- After compiling, run `git diff --name-only` to confirm sync status: if the `.lock.yml` does not appear in the diff output, the lockfile is already current and no further action on the lockfile is needed. If it does appear, the lockfile was updated and must be staged alongside the source `.md` in the same commit.

- The `agentic-workflow-validation` hook is the enforcement backstop: it checks that the `.lock.yml` is present and matches the compiled output of the source file. If it reports stale or missing lockfiles, recompile and commit the updated `.lock.yml` before finishing.

- If `gh aw compile` fails, stop and fix the workflow source instead of leaving `.md` and `.lock.yml` drift in the branch.
