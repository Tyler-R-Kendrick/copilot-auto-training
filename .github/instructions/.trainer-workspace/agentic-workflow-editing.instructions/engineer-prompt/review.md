# Engineer-Prompt Review: agentic-workflow-editing.instructions.md

## Target Goal

Improve `agentic-workflow-editing.instructions.md` so it gives agents clear, actionable guidance when editing agentic workflow markdown files under `.github/workflows/*.md`. The instructions should be precise enough that an agent never leaves source and lockfile out of sync.

## Current State Analysis

The current file has 4 bullet rules covering:
1. Run `gh aw compile <workflow-name>` after editing and include the `.lock.yml` in the change set
2. Do not rely on the stop hook; treat `gh aw compile` as part of the edit
3. The `agentic-workflow-validation` hook is the enforcement backstop
4. If `gh aw compile` fails, fix the source instead of leaving drift

**Gaps identified:**
- No worked example of the compile command with a concrete workflow name
- No definition of "meaningful frontmatter or import changes" — ambiguous trigger condition
- No guidance on how to confirm the lock file is in sync (e.g., `git diff` check after compile)
- No ordered sequence of steps an agent can follow mechanically
- No guidance on what `agentic-workflow-validation` checks specifically
- No guidance on what to do when the lockfile is missing entirely vs. stale
- Bullet 2 says "rerun it after meaningful frontmatter or import changes and again before final validation" — the "again before final validation" step is not separately called out as a required checkpoint

## Likely Failure Modes

1. **Ambiguous trigger**: Agent edits a workflow source but skips compile because the change "didn't seem meaningful"
2. **Stale lockfile**: Agent compiles once early but then makes another edit and forgets to recompile before committing
3. **Missing concrete sequence**: Agent misses the "verify no remaining diff after final compile" step
4. **Unknown hook name**: Agent doesn't know what `agentic-workflow-validation` checks, so cannot reason about what it enforces
5. **Compile flag confusion**: Agent uses wrong workflow name or flags for `gh aw compile`
6. **Lockfile not included in change set**: Agent compiles successfully but forgets to `git add` the `.lock.yml`

## Dataset Gaps

- No concrete examples of the compile command with a real workflow name (e.g., `gh aw compile train-prompt`)
- No example of what a stale-lockfile error looks like vs. a compile error
- No worked example showing the full "edit → compile → verify diff → commit with both files" sequence

## Optimization Hypothesis

The instruction file can be improved by:
1. Adding a minimal ordered checklist (edit → compile → verify diff clean → commit both files)
2. Providing a concrete example: `gh aw compile train-prompt` for `train-prompt.md`
3. Clarifying that "meaningful" means any change to frontmatter, imports, or step logic — when in doubt, recompile
4. Calling out the "final compile check before commit" as a separate required step
5. Noting that `agentic-workflow-validation` checks for lockfile presence and freshness, so a compile failure blocks the workflow

## Validation Plan

Run `python -m pytest -q` after applying changes to confirm no regressions. The instruction file itself is not directly tested; validation confirms no syntax errors in the markdown and no test failures in the broader suite.

## Recommended Improvement Areas

- Add a 3-step sequence: (1) edit the `.md` source, (2) run `gh aw compile <workflow-name>`, (3) verify `git diff --name-only` shows both the source and the `.lock.yml` before committing
- Add a concrete command example for the most common workflow: `gh aw compile train-prompt`
- Clarify: any edit to frontmatter, import lines, or step content counts as "meaningful" — default to recompile if unsure
- Restate the final validation requirement explicitly: run `gh aw compile` one last time before opening the pull request to confirm source and lockfile are in sync
- Add a short note on the hook: `agentic-workflow-validation` enforces that `.lock.yml` is present and matches the compiled output of the source `.md` file
