# Engineer Copilot Agent

Improve GitHub Copilot custom-agent contracts by separating trigger design, tool and skill routing, handoff boundaries, and context minimization.

## Overview

This skill complements the repository's skill-engineering assets by focusing on Copilot custom agents stored as `.agent.md` files. It helps with four concerns:

1. **Frontmatter optimization** — improve discoverability and trigger accuracy.
2. **Tool and skill routing** — keep tool usage and MCP skill calls bounded to real surfaces.
3. **Handoff optimization** — define clear ownership boundaries across workspace agents.
4. **Context minimization** — move standards and deterministic work out of the agent body.

## Directory structure

```
engineer-copilot-agent/
├── SKILL.md
├── README.md
├── scripts/
│   ├── __init__.py
│   ├── discover_runtime_surface.py
│   ├── validate_agent.py
│   └── analyze_agent_body.py
├── references/
│   ├── copilot-agent-standard.md
│   ├── frontmatter-optimization.md
│   ├── tool-skill-usage-optimization.md
│   ├── handoff-optimization.md
│   └── context-minimization-loop.md
├── assets/
├── evals/
│   └── evals.json
└── datasets/
    ├── train.jsonl
    └── val.jsonl
```

## Scripts

### discover_runtime_surface.py

Scans the repository for `.github/agents/*.agent.md` files and `skills/*/SKILL.md` folders, then summarizes the discovered agents, skills, tool surfaces, and handoff pairs.

```bash
python scripts/discover_runtime_surface.py --repo-root <repo-root>
python scripts/discover_runtime_surface.py --repo-root <repo-root> --json
```

### validate_agent.py

Validates a custom-agent contract, checks required frontmatter, compares declared agents and tools against the discovered workspace surface, and reports risky routing guidance.

```bash
python scripts/validate_agent.py <agent-path> --repo-root <repo-root>
python scripts/validate_agent.py <agent-path> --repo-root <repo-root> --json
```

### analyze_agent_body.py

Analyzes an agent body for oversized sections, deterministic instructions, stale routing cues, and missing discovery-to-load ordering around MCP skill helpers.

```bash
python scripts/analyze_agent_body.py <agent-path> --repo-root <repo-root>
python scripts/analyze_agent_body.py <agent-path> --repo-root <repo-root> --json
```
