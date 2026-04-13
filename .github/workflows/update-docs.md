---
on:
  pull_request_target:
    types:
      - closed
    branches:
      - main
if: >-
  ${{
    github.event.pull_request.merged == true
    && !(
      startsWith(github.event.pull_request.head.ref || '', 'copilot/update-docs/')
      || startsWith(github.event.pull_request.title || '', 'docs: update documentation after merge to main (')
    )
  }}

description: Review all documentation after each merge to main and open a pull request with corrections if any docs are out-of-date.

labels: [documentation, maintenance]

permissions:
  contents: read
  pull-requests: read
  issues: read

engine: copilot

tools:
  github:
    toolsets: [default]

network:
  allowed:
    - defaults

safe-outputs:
  create-pull-request:
    max: 1
    github-token: ${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}
---

# Update Docs

After each merged pull request to `main`, review all documentation files in this repository for accuracy and completeness relative to the current source code and project configuration. If any documentation is out-of-date, produce corrected versions and open exactly one pull request. If every document is already accurate, do nothing.

## Context

This repository is `Tyler-R-Kendrick/copilot-auto-training`. The primary documentation lives under:

- `README.md` — repository overview and quick-start
- `docs/` — extended guides (getting-started, dashboard, troubleshooting, copilot-cli-plugins, copilot_execution_plan)
- `examples/` — runnable first-run example with its own `README.md`
- `skills/*/SKILL.md` — individual skill contracts

Authoritative source of truth for the current state of the project is the repository itself: code under `skills/`, configuration under `.github/`, Python source under `skills/*/scripts/`, and dependency files such as `requirements.txt` and `pyproject.toml`.

## Procedure

1. Use the merged pull request from the event payload (`github.event.pull_request`), including its number, title, head branch, and merge commit SHA.
2. List all files changed in that merged pull request using the GitHub pull request files API. Do not scope the review to a single commit.
3. For each changed source file in that merged pull request, determine which documentation files could reference or describe that source file.
4. Read the candidate documentation files and the changed source files.
5. Compare each documentation file against the current source:
   - Check that commands, file paths, environment variables, CLI flags, and configuration keys are still accurate.
   - Check that described behavior matches what the code actually does.
   - Check that any linked files still exist at the stated paths.
   - Check that version numbers, dependency names, and Python version requirements match `requirements.txt` and any `pyproject.toml`.
6. Also review the top-level `README.md` whenever any file changes, because it describes the overall repository.

## Decision Rules

If one or more documentation files contain inaccurate, outdated, or broken content relative to the current source:

- Produce corrected versions of only the affected files.
- Limit edits to factual corrections: update commands, paths, flag names, environment variable names, version numbers, and descriptions that no longer match the code. Do not rewrite sections that are still accurate.
- Open exactly one pull request containing all corrections.

If every documentation file is already accurate relative to the current source code, do nothing and stop.

## Pull Request Format

Branch: `copilot/update-docs/<short-sha>`

Title: `docs: update documentation after merge to main (<short-sha>)`

Body:
- List each file changed and a one-sentence summary of what was corrected.
- Include the merged pull request number and merge commit SHA that triggered this review.

## Guardrails

- Do not modify source code, tests, or workflow files. This includes all files under `skills/*/scripts/`, `tests/`, and `.github/workflows/`.
- `skills/*/SKILL.md` files are documentation and may be corrected when stale, but the scripts and code under `skills/*/scripts/` must never change.
- Only modify files under `docs/`, `README.md`, `examples/*/README.md`, and `skills/*/SKILL.md` when those files contain stale or incorrect content.
- Do not open a pull request if no documentation corrections are needed.
- Do not rewrite accurate content for style or verbosity.
- Keep each correction minimal and targeted.
