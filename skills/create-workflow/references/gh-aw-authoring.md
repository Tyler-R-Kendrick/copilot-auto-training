# GitHub Agentic Workflows Authoring Reference

Use this reference when drafting or debugging a GitHub Agentic Workflow.

## Workflow shape

GitHub Agentic Workflows are markdown files in `.github/workflows/`.

- Source file: `.github/workflows/<name>.md`
- Compiled file: `.github/workflows/<name>.lock.yml`

Each workflow has:

1. YAML frontmatter between `---` markers
2. Markdown instructions loaded at runtime

Only frontmatter changes require recompilation. Markdown-only instruction edits take effect on the next run without recompilation.

## Repository setup

For full authoring support, initialize the repository:

```bash
gh aw init
```

This sets up the repository for authoring, including the dispatcher agent and MCP configuration used by the GitHub authoring experience.

`gh aw` is a GitHub CLI extension, so run it as `gh aw ...` from the repository root. Use `gh aw --help` for the top-level command list and `gh aw <command> --help` for command-specific flags.

Quick readiness check:

```bash
gh aw list
```

If that reports `no .github/workflows directory found`, the repository has not been set up for workflow authoring yet.

## Basic creation flow

1. Create `.github/workflows/<workflow-name>.md`
2. Add frontmatter with trigger, permissions, engine, tools, and any network or output configuration
3. Write clear markdown instructions with headings, numbered steps, and decision rules
4. Compile the workflow
5. Commit both the `.md` and `.lock.yml`

Useful commands:

```bash
gh aw new my-workflow
gh aw compile my-workflow
gh aw validate my-workflow --strict
gh aw compile --watch
gh aw run my-workflow
gh aw logs my-workflow
gh aw audit <run-id>
gh aw trial ./my-workflow.md --host-repo .
```

## Manual authoring checklist

- Use a descriptive kebab-case filename
- Keep permissions minimal
- Add explicit network access when the workflow needs external domains
- Configure only the GitHub toolsets and MCP tools the workflow actually needs
- Use `safe-outputs` for any writes back to GitHub
- Recompile after frontmatter changes
- Commit the source markdown and generated lock file together

## Writing the markdown body

Write the workflow body like instructions for a new teammate.

Preferred patterns:

- start with the task goal
- separate phases with headings
- use numbered steps for ordered work
- encode decision logic explicitly
- give output templates when the result shape matters
- mention repository-specific context, conventions, and constraints

Good patterns:

- `Analyze issue #... and classify it using the rules below.`
- `If the issue is missing reproduction steps, ask clarifying questions before labeling priority.`
- `Produce a report with Summary, Key Findings, Risks, and Next Actions.`

## MCP configuration summary

Configure external MCP servers under `mcp-servers:`.

Supported patterns:

### Stdio server

```yaml
mcp-servers:
  serena:
    command: "uvx"
    args: ["--from", "git+https://github.com/oraios/serena", "serena"]
    allowed: ["*"]
```

### Container server

```yaml
mcp-servers:
  custom-tool:
    container: "mcp/custom-tool:v1.0"
    args: ["-v", "/host/data:/app/data"]
    entrypointArgs: ["serve", "--port", "8080"]
    env:
      API_KEY: "${{ secrets.API_KEY }}"
    allowed: ["tool1", "tool2"]
network:
  allowed:
    - defaults
    - api.example.com
```

### HTTP server

```yaml
mcp-servers:
  authenticated-api:
    url: "https://api.example.com/mcp"
    headers:
      Authorization: "Bearer ${{ secrets.API_TOKEN }}"
    allowed: ["*"]
```

### Registry-backed server

```yaml
mcp-servers:
  markitdown:
    registry: https://api.mcp.github.com/v0/servers/microsoft/markitdown
    container: "ghcr.io/microsoft/markitdown"
    allowed: ["*"]
```

Guidance:

- Prefer read-only MCP servers.
- Keep the `allowed` list tight unless broad access is required.
- Store credentials in secrets-backed fields.
- Use `gh aw mcp inspect <workflow-name>` and `gh aw mcp list-tools <server> <workflow-name>` to debug exposure issues.

## Safe outputs reminder

Workflow agents should not perform arbitrary GitHub writes directly. Use `safe-outputs` for creating or updating issues, comments, labels, discussions, and related operations.

If the workflow needs to publish results, include the required safe output types in frontmatter and make the workflow body explicitly produce the data those outputs expect.

## Common failure patterns

### Workflow will not compile

- check YAML indentation and list syntax
- verify `on:` is present when the file is meant to be runnable
- use `gh aw compile --verbose`
- use `gh aw validate --strict`

### Lock file not generated

- fix compile errors first
- verify `.github/workflows/` is writable
- run `gh aw compile --purge` if stale files are obscuring the result

### Frontmatter field seems ignored

- verify spelling against the current frontmatter reference
- rerun with `gh aw compile --verbose` to confirm what was parsed

### MCP server connection failure

- verify command or container syntax
- verify env vars and secret references
- verify network allow-list entries
- inspect with `gh aw mcp inspect`
- confirm exposed tools with `gh aw mcp list-tools <server> <workflow-name>`

### Tool not found at runtime

- verify the tool is exposed by the configured MCP server
- verify the workflow instructions tell the agent to use it
- audit the run and compare requested tools to configured tools

### Write actions fail

- verify the workflow uses `safe-outputs`
- verify the output type is configured in frontmatter
- audit the run for safe-output failures

## Final handoff checklist

- `.md` source created or updated
- `.lock.yml` compiled if frontmatter changed
- secrets or initialization prerequisites called out
- trigger, tools, and output behavior summarized for the user