# Create Workflow

Create or update a GitHub Agentic Workflow in .github/workflows using gh aw, including frontmatter, markdown instructions, optional MCP servers, compilation, and debugging. Use this whenever the user wants new repository automation, wants to turn a repeated GitHub process into an agentic workflow, needs to add external MCP tools to a workflow, or needs help validating and fixing a workflow before commit.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts.
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- The user wants to create a new GitHub Agentic Workflow.
- The user wants to automate repository work such as triage, reporting, validation, issue handling, scheduled analysis, or orchestrated agent tasks.
- The user wants to convert a repeated GitHub process into a workflow file in `.github/workflows/`.
- The user needs to add or update MCP servers for a workflow.
- The user needs help compiling, validating, or debugging a workflow after editing it.

Do not use this skill for generic GitHub Actions YAML authoring that is not based on GitHub Agentic Workflows markdown files.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
