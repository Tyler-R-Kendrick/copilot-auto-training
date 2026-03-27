# Agent Skills Support Plan

This plan maps the Agent Skills client implementation guide at https://agentskills.io/client-implementation/adding-skills-support onto the local `agent-skills` MCP server.

## Step 1: Discover skills

- Current implementation:
  - Repo-scoped roots are discovered on every request from `skills/`, `.github/skills/`, `.claude/skills/`, and `.agents/skills/`.
  - Duplicate names are resolved deterministically.
  - Symlink and out-of-repo safety checks are enforced.
- Implemented now:
  - Skills that opt out of model-driven activation are excluded from model-facing discovery.
- Remaining alignment work:
  - Add user-level scan roots such as `~/.agents/skills/` and `~/.<client>/skills/` when this moves beyond repo-local MCP support.
  - Add trust gating for project-level skills when the hosting client exposes a workspace trust signal.
  - Add scan bounds and ignore rules if discovery expands beyond the current shallow repo-root search.

## Step 2: Parse `SKILL.md`

- Current implementation:
  - YAML frontmatter and markdown body are parsed on demand.
  - Hot reload is preserved by re-reading files on each request.
  - Optional resources are indexed without mutating skill directories.
- Implemented now:
  - Model-invocation opt-out flags are read from either `disable-model-invocation` / `disable_model_invocation` at the top level or under `metadata` for compatibility with non-spec client conventions.
- Remaining alignment work:
  - Add a lenient YAML retry path for common malformed frontmatter cases noted in the guide.
  - Record user-visible diagnostics for compatibility warnings instead of only logging invalid-skill skips.

## Step 3: Disclose available skills

- Current implementation:
  - `find_agent_skill` acts as the model-facing skill catalog/search surface.
  - Only filtered, model-visible skills are returned.
- Implemented now:
  - Skills that disable model-driven activation are hidden entirely from the catalog rather than being listed and rejected later.
- Remaining alignment work:
  - If this MCP server is used to generate a prompt catalog directly, expose `name`, `description`, and `location` in a prompt-ready structure.
  - If no visible skills exist, consider suppressing model-facing registration at the client layer when that does not conflict with the requirement for a stable MCP tool surface.

## Step 4: Activate skills

- Current implementation:
  - `load_agent_skill` loads the full instructions.
  - `run_agent_skill` executes only existing Python files under `scripts/`.
  - Resource reads stay on-demand via MCP resources instead of eager loading.
- Implemented now:
  - Hidden skills cannot be activated through `load_agent_skill` or `run_agent_skill`.
- Remaining alignment work:
  - Add a structured activation wrapper for clients that want tagged skill content and bundled-resource listings in a single activation payload.
  - Add permission allowlisting in the host client for skill directories if the caller uses gated file access.

## Step 5: Manage skill context over time

- Current implementation:
  - Out of scope for the MCP server itself.
- Host-client follow-up:
  - Preserve activated skill content during context compaction.
  - Deduplicate repeated activations within a session.
  - Support explicit user activation syntax at the chat harness layer.