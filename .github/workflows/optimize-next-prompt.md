---
on:
   schedule: "0 0 * * *"
   workflow_dispatch:

permissions:
  contents: read
  issues: read
  pull-requests: read

engine: copilot

tools:
  github:
    toolsets: [default]

mcp-servers:
  agent-skills:
    command: tools/agent-skills-mcp/.venv/bin/python
    args: [tools/agent-skills-mcp/server.py]
    allowed: [find_agent_skill, load_agent_skill, run_agent_skill]

network: defaults

safe-outputs:
  create-pull-request:
    max: 1
  add-reviewer:
    max: 1
---

# Optimize Next Prompt

Select exactly one prompt-like source file in this repository, run the repository trainer loop for that target, and open a pull request for the resulting changes.

## Scope

1. Search tracked repository files ending in `.md`, `.mdx`, or `.prompty`.
2. Exclude generated or non-source trees:
   - `.git/`
   - `.venv/`
   - any path under `**/.trainer-workspace/**`
   - any path under `**/*-workspace/**`
   - `node_modules/`
   - `dist/`
   - `build/`
   - `coverage/`
   - `trials/`
   - `.github/workflows/`
3. Treat a file as prompt-like when at least one of these is true:
   - the basename is `SKILL.md` or `AGENTS.md`
   - the path ends in `.agent.md`, `.prompt.md`, `.instructions.md`, or `.prompty`
   - the file clearly contains agent or prompt instructions rather than general documentation, for example a role prompt, skill contract, or structured instruction artifact with imperative guidance
4. Prefer repository-owned prompt artifacts under `.github/agents/`, `.agents/skills/`, `skills/`, and `examples/` over incidental documentation elsewhere.

## Workspace Mapping

1. Use the same workspace naming rules as `.github/hooks/trainer-workspace.py`:
   - strip `.prompty` entirely
   - otherwise strip only the final extension
   - examples:
     - `skills/trainer-research/SKILL.md` -> `skills/trainer-research/.trainer-workspace/SKILL/`
     - `docs/support.prompt.md` -> `docs/.trainer-workspace/support.prompt/`
2. The associated workspace root is `<target-dir>/.trainer-workspace/<prompt-name>/`.
3. Treat the workspace as existing when that directory already exists.

## Selection Rules

1. Build the candidate list and map each candidate to its associated local `.trainer-workspace` directory.
2. Partition candidates into:
   - files whose associated workspace directory does not exist
   - files whose associated workspace directory exists
3. If any candidates are missing a workspace, choose exactly one target from that group using this deterministic order:
   - `.prompty`
   - `.prompt.md`
   - `.instructions.md`
   - `.agent.md`
   - `SKILL.md`
   - `AGENTS.md`
   - all other prompt-like markdown
   - then repository-relative path ascending as the tiebreaker
4. If every candidate already has a workspace, choose the oldest trained target by sorting ascending on the last training timestamp.
5. Resolve the last training timestamp using this fallback order:
   - `workflow-status.json` field `updated_at`
   - the newest `iterations/iteration-N/` directory modification time inside the local workspace
   - the workspace directory modification time
   - repository-relative path ascending as the final tiebreaker
6. Record the selection reason in the eventual pull request body.

## Execution

1. Work on exactly one selected target.
2. If the selected target has no local trainer workspace, initialize it with the repository helper:

   ```bash
   python .github/hooks/trainer-workspace.py init --repo-root . --target-file <target-file> --state pending_engineer_prompt
   ```

3. Inspect the selected workspace. If `engineer-prompt/review.md` is missing, create that review artifact first so the trainer loop has its required prerequisite. The review must stay in the selected local workspace.
4. Run the repository's trainer loop for the selected file by following `.github/agents/trainer.agent.md` as the contract and by using the local `agent-skills` MCP server configured for this workflow.
5. Use the trainer loop exactly for the selected target. Do not scatter artifacts into repo-root `*-workspace` directories. Keep them under the selected local `.trainer-workspace/<prompt-name>/` tree.
6. Allow the trainer loop to decide whether research, synthesis, optimize, and election are needed, but require at least one optimize pass for the selected target.
7. If the trainer workflow produces a defensible optimized prompt candidate, persist that chosen result back to the selected source file before final validation.
8. Keep the change set tightly scoped to:
   - the selected prompt-like file
   - its local `.trainer-workspace/<prompt-name>/` artifacts
   - directly related supporting prompt-evaluation assets created by the trainer loop
9. Do not modify unrelated prompts, skills, agents, workflow files, or repo-root `*-workspace` trees.

## Validation

1. Run repository validation with:

   ```bash
   python -m pytest -q
   ```

2. If validation fails, do not open a pull request. Instead, stop after recording the failure details in the selected local workspace.
3. If the trainer loop produces no meaningful repository diff, do not open a pull request.

## Pull Request

1. Open exactly one pull request when, and only when, the selected target produced a reviewable diff and validation passed.
2. The pull request body must include:
   - the selected target file
   - why it was selected
   - the local `.trainer-workspace/<prompt-name>/` path used
   - whether the target was missing a workspace or was chosen as the oldest trained prompt
   - the validation result
   - the key trainer artifacts produced for the selected iteration
3. Request Copilot as a reviewer using the `add-reviewer` safe output.
4. If the reviewer request fails because Copilot review is not enabled or not available for the repository, keep the pull request open and state that limitation explicitly in the pull request body. Do not substitute a different reviewer.

## Guardrails

- Use the configured `agent-skills` MCP server deliberately: discover the relevant trainer skills before running them.
- Preserve repository conventions from `.github/hooks/trainer-workspace.py` and `.github/agents/trainer.agent.md`.
- Keep the workflow deterministic: select one target, perform one trainer loop, and produce one pull request at most.
- Do not guess missing datasets when the trainer contract requires research or synthesis first.