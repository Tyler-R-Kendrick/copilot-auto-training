---
name: create-workflow
description: Create or update a GitHub Agentic Workflow in .github/workflows using gh aw, including frontmatter, markdown instructions, optional MCP servers, compilation, and debugging. Use this whenever the user wants new repository automation, wants to turn a repeated GitHub process into an agentic workflow, needs to add external MCP tools to a workflow, or needs help validating and fixing a workflow before commit.
argument-hint: Describe the workflow goal, trigger, outputs, engine, and any MCP or safe-output requirements.
---

# Create Workflow

Use this skill to author GitHub Agentic Workflows as markdown source files and carry them through compilation and validation.

GitHub Agentic Workflows are stored as `.github/workflows/<name>.md` and compiled into `.github/workflows/<name>.lock.yml`. The markdown body is the runtime instruction set. The frontmatter controls triggers, permissions, tools, MCP servers, network access, and safe outputs.

Read [the authoring reference](./references/gh-aw-authoring.md) before drafting the workflow when the request includes MCP setup, unfamiliar triggers, safe outputs, or troubleshooting.

Use [the starter template](./assets/workflow-template.md) when you need a clean first draft.

## gh aw CLI quick reference

`gh aw` is a GitHub CLI extension, so invoke it through `gh`, not as a standalone `gh-aw` binary.

- Run commands from the repository root.
- Use `gh aw --help` for the top-level command list.
- Use `gh aw <command> --help` for command-specific flags.
- `gh aw new <workflow-name> --engine copilot` scaffolds a new markdown workflow.
- `gh aw compile <workflow-name>` accepts either a workflow id like `my-workflow` or a filename like `my-workflow.md`; with no argument it compiles every markdown workflow under `.github/workflows/`.
- `gh aw validate <workflow-name> --strict` validates without emitting lock files and runs the full validation stack.
- `gh aw trial ./path/to/workflow.md --host-repo .` is the local-file path for exercising a `workflow_dispatch` workflow against the current repository.
- `gh aw list` is a quick readiness check; if it reports `no .github/workflows directory found`, the repository has not been set up for workflow authoring yet.

**Compilation rule:** Frontmatter changes always require recompilation (`gh aw compile <workflow-name>`). Markdown body-only changes do not require recompilation.

## When to use

- The user wants to create a new GitHub Agentic Workflow.
- The user wants to automate repository work such as triage, reporting, validation, issue handling, scheduled analysis, or orchestrated agent tasks.
- The user wants to convert a repeated GitHub process into a workflow file in `.github/workflows/`.
- The user needs to add or update MCP servers for a workflow.
- The user needs help compiling, validating, or debugging a workflow after editing it.

Do not use this skill for generic GitHub Actions YAML authoring that is not based on GitHub Agentic Workflows markdown files.

## Core workflow

Follow this order.

1. Confirm repository readiness.
2. Gather the workflow contract.
3. Author the markdown workflow file.
4. Add MCP servers or safe outputs if required.
5. Compile and validate.
6. Debug any failures.
7. Hand back the finished workflow with the exact files changed.

## 1. Confirm repository readiness

Check whether the repository has already been initialized for GitHub Agentic Workflows.

- If the repo is not initialized, instruct the user to initialize it with `gh aw init` or by following the repository setup prompt from `install.md`.
- `gh aw init` is interactive by default and sets up the dispatcher agent, `.gitattributes`, and Copilot MCP wiring unless `--no-mcp` is passed.
- Use `gh aw list` or inspect `.github/workflows/` as a quick readiness check before assuming the repo is already set up.
- Initialization is required for the full authoring experience because it installs the dispatcher agent and MCP configuration used during workflow authoring.
- If the user only wants a draft file and is not ready to initialize: create the markdown workflow, skip compilation entirely, and state explicitly that the draft is not runnable. List what still needs to happen before it can run: `gh aw init`, any required secrets, and a compile pass once initialization is complete.

## 2. Gather the workflow contract

Before writing the file, extract or ask for the minimum set of requirements:

- workflow purpose
- trigger model
- expected outputs or side effects
- target engine if not defaulting to Copilot
- required GitHub toolsets
- required external services or MCP servers
- whether the workflow must write back to GitHub
- any security or network constraints

If the user is vague, ask focused questions that close authoring gaps quickly. Prioritize these decision points:

- What event should trigger the workflow: issue, pull request, schedule, manual dispatch, discussion, or command?
- Should it only analyze and report, or should it create or update GitHub artifacts?
- Does it need external tools beyond built-in GitHub tooling?
- Is this a new workflow or a change to an existing one?

## 3. Author the markdown workflow file

Create the workflow in `.github/workflows/<workflow-name>.md` using kebab-case names.

Keep the file split into two layers:

- frontmatter for configuration
- markdown body for the runtime instructions

When writing the markdown body:

- use clear action verbs such as analyze, label, summarize, create, update, or dispatch
- include headings so the agent can follow the task structure reliably
- use numbered steps for multi-stage procedures
- include explicit decision rules when classification or branching matters
- include a result template when the output should be structured
- give concrete repository context and constraints instead of generic advice

Treat the workflow body like instructions for a new teammate. Be specific enough that the agent can act consistently without guessing.

Before finishing the file, check whether the workflow body describes any write operations (creating issues, posting comments, adding labels, updating PRs). If it does, flag that `safe-outputs` must be configured in frontmatter (see section 4) and that the frontmatter change will require recompilation.

## 4. Add MCP servers or safe outputs if required

### Safe outputs

If the workflow needs to create issues, comments, PR updates, labels, or other write operations, use `safe-outputs`. Do not model direct writes as unrestricted agent behavior.

Keep write scope minimal and configure only the output types the workflow actually needs.

### MCP servers

If the workflow needs external systems or custom tools, configure them under `mcp-servers:` in frontmatter.

Prefer the smallest viable configuration:

- limit `allowed` tools instead of exposing everything unless the workflow truly needs broad access
- pass credentials through `env` or `headers` using secrets
- prefer read-only MCP integrations
- keep network access explicit

Use the correct server form for the transport:

- `command` plus `args` for stdio servers
- `container` with optional `args`, `entrypointArgs`, and `env` for containerized servers
- `url` with optional `headers` for HTTP servers
- `registry` when using a server from the MCP registry

If the user only needs small deterministic helper tools, consider whether `mcp-scripts` is a better fit than a full external MCP server.

## 5. Compile and validate

After editing frontmatter or imports, recompile the workflow.

Use this validation loop:

1. Run `gh aw compile <workflow-name>` or `gh aw compile`.
2. For a newly authored or security-sensitive workflow, prefer `gh aw validate <workflow-name> --strict` before or after compile. `gh aw validate` is the no-emit validation command and runs the full lint and security stack.
3. If you are iterating on frontmatter frequently, use `gh aw compile --watch <workflow-name>`.
4. If errors are unclear, rerun the failing command with `--verbose`.
5. Confirm the `.lock.yml` file was regenerated after compile.
6. Commit both the `.md` and `.lock.yml` files.

Important rule:

- frontmatter changes require recompilation — always run `gh aw compile <workflow-name>` after any frontmatter edit
- markdown body only changes do not require recompilation

## 6. Debug failures

Use the shortest path that matches the failure mode.

### Compilation failures

- run `gh aw compile --verbose` first to get the full error message before trying to diagnose manually
- check YAML indentation, colons, arrays, and field names
- verify required fields like `on:` are present
- use `gh aw validate --strict` to isolate schema, lint, and security issues without rewriting lock files
- use `gh aw compile --purge` if stale lock files are causing confusion

### MCP failures

- inspect the workflow MCP configuration with `gh aw mcp inspect <workflow-name>`
- use `gh aw mcp list-tools <server> <workflow-name>` to confirm the server exposes the tools the workflow expects
- verify `allowed` tools match what the workflow expects
- verify secrets-backed env vars or headers are present
- verify container images, commands, and network access
- if a tool is missing, narrow whether the server failed to connect or the tool was never exposed

### Runtime failures

- inspect logs with `gh aw logs <workflow-name>`
- audit a failing run with `gh aw audit <run-id>`
- verify the workflow was compiled and both source and lock files were pushed
- verify repository secrets for the chosen engine and any MCP server credentials

### Common authoring mistakes

- workflow exists but was not compiled after frontmatter changes
- output requires `safe-outputs` but the workflow only describes direct writes
- permissions are broader than needed or too narrow for the configured tools
- MCP configuration is present but the workflow instructions never tell the agent when to use those tools
- network domains needed by external services are missing

## 7. Quality bar

Before finishing, check all of these:

- workflow filename is descriptive and kebab-case
- frontmatter is minimal but complete
- markdown body is specific, structured, and action-oriented
- write actions go through `safe-outputs`
- MCP configuration is scoped and secrets-aware
- `.lock.yml` exists and matches the current frontmatter
- the user can tell which edits require recompilation in the future

## Response contract

When you create or update a workflow for the user:

1. state which workflow file you changed
2. summarize the trigger, main behavior, and configured tools
3. state whether the edit touched frontmatter or the markdown body (or both), and whether you ran compilation — if you compiled, name the exact command used; if you skipped compilation, explain why (body-only change or draft-only mode)
4. call out any remaining prerequisites such as missing secrets or required initialization

## Example request shapes

- Create a scheduled workflow that posts a weekly repository health issue.
- Create an issue triage workflow that uses GitHub tools and asks clarifying questions.
- Add a Notion MCP server to this workflow and restrict it to search tools.
- Fix why this workflow compiles but fails at runtime.
- Turn this manual release checklist into an agentic workflow with safe outputs.
