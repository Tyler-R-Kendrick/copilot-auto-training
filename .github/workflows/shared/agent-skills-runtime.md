---
runtimes:
  python:
    version: "3.12"
  uv:
    version: "latest"

mcp-servers:
  agent-skills:
    command: /bin/sh
    args:
      - -lc
      - python -m pip install --quiet --disable-pip-version-check --no-cache-dir uv && exec uvx --from git+https://github.com/Tyler-R-Kendrick/copilot-apo#subdirectory=tools/agent-skills-mcp agent-skills-mcp
    env:
      AGENT_SKILLS_RUN_CWD: .
    allowed: [find_agent_skill, load_agent_skill, run_agent_skill]

network:
  allowed:
    - defaults
    - github
    - python
---

# Agent Skills Runtime

Use the configured `agent-skills` MCP server to discover and run `trainer-*` skills from the current repository checkout.
