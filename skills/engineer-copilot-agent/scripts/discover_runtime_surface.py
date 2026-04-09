#!/usr/bin/env python3
"""Discover repo-owned Copilot agents, skills, and observed tool surfaces."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentSurface:
    name: str
    path: str
    tools: list[str]
    child_agents: list[str]
    handoff_targets: list[str]


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("file must start with --- frontmatter delimiter")

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise ValueError("file must have a closing --- frontmatter delimiter")

    raw_yaml = "".join(lines[1:closing_index]).strip()
    body = "".join(lines[closing_index + 1 :]).strip()
    try:
        payload = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return payload, body


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def discover_agents(repo_root: Path) -> tuple[list[AgentSurface], list[str]]:
    agent_root = repo_root / ".github" / "agents"
    if not agent_root.is_dir():
        return [], []

    agents: list[AgentSurface] = []
    notes: list[str] = []
    for path in sorted(agent_root.glob("*.agent.md")):
        try:
            fm, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            notes.append(f"Skipped agent '{path.relative_to(repo_root)}': {exc}")
            continue
        handoffs = fm.get("handoffs") or []
        handoff_targets = [
            item.get("agent", "").strip()
            for item in handoffs
            if isinstance(item, dict) and isinstance(item.get("agent"), str) and item.get("agent", "").strip()
        ]
        agents.append(
            AgentSurface(
                name=str(fm.get("name", path.name.removesuffix(".agent.md"))).strip('"'),
                path=str(path.relative_to(repo_root)),
                tools=_as_string_list(fm.get("tools")),
                child_agents=_as_string_list(fm.get("agents")),
                handoff_targets=handoff_targets,
            )
        )
    return agents, notes


def discover_skills(repo_root: Path) -> tuple[list[dict[str, str]], list[str]]:
    skills_root = repo_root / "skills"
    if not skills_root.is_dir():
        return [], []

    skills: list[dict[str, str]] = []
    notes: list[str] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        try:
            fm, _ = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            notes.append(f"Skipped skill '{skill_md.relative_to(repo_root)}': {exc}")
            continue
        skills.append(
            {
                "name": str(fm.get("name", skill_dir.name)),
                "path": str(skill_md.relative_to(repo_root)),
            }
        )
    return skills, notes


def discover_surface(repo_root: Path | str) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    agents, agent_notes = discover_agents(repo_root)
    skills, skill_notes = discover_skills(repo_root)
    tool_union = sorted({tool for agent in agents for tool in agent.tools})
    handoff_pairs = sorted({f"{agent.name}->{target}" for agent in agents for target in agent.handoff_targets})
    child_pairs = sorted({f"{agent.name}->{target}" for agent in agents for target in agent.child_agents})
    notes = [
        "Compare this repo snapshot with the current session tool and agent inventory before editing.",
        *agent_notes,
        *skill_notes,
    ]
    if "agent-skills/*" in tool_union:
        notes.append("This repo advertises an MCP skill surface; verify the live helper names before hardcoding skill calls.")
    if any(tool.startswith("agent") for tool in tool_union):
        notes.append("At least one custom agent delegates work through subagent tooling; keep handoffs bounded and named explicitly.")
    return {
        "repo_root": str(repo_root),
        "agents": [asdict(agent) for agent in agents],
        "skills": skills,
        "tools": tool_union,
        "handoff_pairs": handoff_pairs,
        "child_agent_pairs": child_pairs,
        "notes": notes,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover repo-owned Copilot agents, skills, and tools.")
    parser.add_argument("--repo-root", required=True, help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = discover_surface(args.repo_root)
    if args.json_output:
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Repository: {payload['repo_root']}")
    print(f"Agents ({len(payload['agents'])}):")
    for agent in payload["agents"]:
        print(f"  - {agent['name']} ({agent['path']})")
        if agent["tools"]:
            print(f"      tools: {', '.join(agent['tools'])}")
        if agent["handoff_targets"]:
            print(f"      handoffs: {', '.join(agent['handoff_targets'])}")
    print(f"Skills ({len(payload['skills'])}):")
    for skill in payload["skills"]:
        print(f"  - {skill['name']} ({skill['path']})")
    if payload["tools"]:
        print("Observed tools: " + ", ".join(payload["tools"]))
    if payload["notes"]:
        print("Notes:")
        for note in payload["notes"]:
            print(f"  - {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
