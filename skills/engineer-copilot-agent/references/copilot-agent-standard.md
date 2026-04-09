# Copilot Custom Agent Standard

Read this file before you draft or revise a GitHub Copilot custom agent.

## File and ownership model

- Custom agents in this repository live under `.github/agents/*.agent.md`.
- Treat the target `.agent.md` file as the routing layer, not the entire knowledge base.
- Keep reusable standards in `references/` and deterministic checks in `scripts/` when the custom agent owns companion assets.
- Re-run `python -m pytest -q` after meaningful contract changes.

## Frontmatter baseline

Repo-observed custom agents use frontmatter with fields such as:

- `name`
- `description`
- `tools`
- optional `agents`
- optional `handoffs`
- optional `user-invocable`

Keep `name` aligned with the filename stem and make `description` say both what the agent owns and when to invoke it.

## Repo-observed agent roster

The current repository documents these custom agents in public repo docs and tests:

- `trainer`
- `researcher`
- `teacher`
- `student`
- `judge`
- `conservator`
- `adversary`
- `engineer`

Do not hardcode that list blindly. Run `python scripts/discover_runtime_surface.py --repo-root <repo-root> --json` first, then reconcile against the live session inventory in case the repo has changed.

## Repo-observed tool surfaces

Public repo docs and tests currently show these recurring tool surfaces inside custom-agent contracts:

- `read`
- `edit`
- `search`
- `execute`
- `todo`
- `agent`
- `agent/runSubagent`
- `agent-skills/*`

Some agents intentionally expose only a subset. Validate against the actual target agent rather than copying a larger tool list.

## Repo-observed skill surface

The repository currently exposes packaged skills for workflow authoring, learning, judging, research, engineering, and training. The repo-root `skills/` tree currently includes:

- `create-workflow`
- `learn`
- `engineer-prompt`
- `engineer-code`
- `judge-rubric`
- `judge-outcome`
- `judge-trajectory`
- `researcher-research`
- `trainer-synthesize`
- `trainer-optimize`
- `trainer-election`
- `engineer-skill`

Treat that list as a snapshot. The live session and discovery script should override stale assumptions.

## Body structure

A good `.agent.md` body usually contains:

1. Scope and ownership
2. Tool or MCP execution contract
3. Handoff rules and non-goals
4. Output or artifact expectations
5. Validation or evidence requirements

Keep examples short. Move long standards, examples, or eval guidance to references.
