#!/usr/bin/env python3
"""Validate a GitHub Copilot custom-agent contract."""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
import discover_runtime_surface as discovery

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIGGER_PHRASES = ("use when", "use this when", "use this whenever", "use whenever")


@dataclass
class Issue:
    severity: str
    code: str
    message: str


@dataclass
class ValidationResult:
    agent_path: str
    valid: bool = True
    issues: list[Issue] = field(default_factory=list)
    surface: dict[str, Any] | None = None

    def error(self, code: str, message: str) -> None:
        self.valid = False
        self.issues.append(Issue("error", code, message))

    def warning(self, code: str, message: str) -> None:
        self.issues.append(Issue("warning", code, message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_path": self.agent_path,
            "valid": self.valid,
            "surface": self.surface,
            "issues": [asdict(issue) for issue in self.issues],
        }


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("agent file must start with --- frontmatter delimiter")
    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        raise ValueError("agent file must have a closing --- frontmatter delimiter")
    raw_yaml = "".join(lines[1:closing_index]).strip()
    body = "".join(lines[closing_index + 1 :]).strip()
    try:
        payload = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"frontmatter is not valid YAML: {exc}") from exc
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


def validate_frontmatter(agent_path: Path, fm: dict[str, Any], result: ValidationResult) -> None:
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        result.error("frontmatter-name-missing", "Missing required 'name' field")
    else:
        stripped = name.strip().strip('"')
        if not NAME_RE.fullmatch(stripped):
            result.error("frontmatter-name-format", f"Name '{stripped}' is not valid kebab-case")
        expected_name = agent_path.name.removesuffix(".agent.md")
        if stripped != expected_name:
            result.error("name-file-mismatch", f"Name '{stripped}' does not match filename '{expected_name}.agent.md'")

    description = fm.get("description")
    if not isinstance(description, str) or not description.strip():
        result.error("frontmatter-description-missing", "Missing required 'description' field")
    else:
        lowered = description.lower()
        if not any(phrase in lowered for phrase in TRIGGER_PHRASES):
            result.warning("description-no-trigger-phrase", "Description should include explicit trigger guidance such as 'Use when ...'.")

    tools = _as_string_list(fm.get("tools"))
    if not tools:
        result.error("frontmatter-tools-missing", "Frontmatter should declare at least one tool")

    agents = fm.get("agents")
    if agents is not None and not isinstance(agents, list):
        result.error("frontmatter-agents-type", "'agents' must be a list when present")

    handoffs = fm.get("handoffs")
    if handoffs is not None and not isinstance(handoffs, list):
        result.error("frontmatter-handoffs-type", "'handoffs' must be a list when present")
    elif isinstance(handoffs, list):
        for index, item in enumerate(handoffs):
            if not isinstance(item, dict):
                result.error("handoff-item-type", f"handoff #{index + 1} must be a mapping")
                continue
            if not isinstance(item.get("label"), str) or not item.get("label", "").strip():
                result.error("handoff-label-missing", f"handoff #{index + 1} must include a non-empty label")
            if not isinstance(item.get("agent"), str) or not item.get("agent", "").strip():
                result.error("handoff-agent-missing", f"handoff #{index + 1} must include a non-empty agent target")


def validate_body(body: str, result: ValidationResult) -> None:
    lines = body.splitlines()
    if not body.strip():
        result.error("body-empty", "Body must not be empty")
        return
    if not any(line.startswith("#") for line in lines):
        result.warning("body-no-headings", "Body should contain markdown headings")
    if not any(line.lstrip().startswith(("-", "*")) or re.match(r"\d+\.\s", line.lstrip()) for line in lines):
        result.warning("body-no-lists", "Body should contain actionable bullet points or steps")
    lowered = body.lower()
    if "run_agent_skill" in lowered and "load_agent_skill" not in lowered:
        result.warning("routing-missing-load-step", "Body references run_agent_skill without also describing a load step.")
    if "load_agent_skill" in lowered and "find_agent_skill" not in lowered:
        result.warning("routing-missing-find-step", "Body references load_agent_skill without first describing discovery.")


def validate_surface_alignment(
    agent_path: Path,
    fm: dict[str, Any],
    result: ValidationResult,
    surface: dict[str, Any] | None,
) -> None:
    if not surface:
        return
    known_agents = {agent["name"] for agent in surface.get("agents", [])}
    repo_root = Path(surface["repo_root"])
    try:
        agent_path.relative_to(repo_root)
    except ValueError:
        result.warning(
            "surface-repo-root-mismatch",
            f"Agent path '{agent_path}' is not under repo root '{repo_root}'; validating against repo-wide surfaces only.",
        )
    known_tools = set(_as_string_list(surface.get("tools")))
    if not known_tools:
        known_tools = {
            tool
            for agent in surface.get("agents", [])
            for tool in agent.get("tools", [])
            if isinstance(tool, str)
        }
    for agent_name in _as_string_list(fm.get("agents")):
        if known_agents and agent_name not in known_agents:
            result.error("unknown-child-agent", f"Declared child agent '{agent_name}' is not present in the discovered repo surface")
    for handoff in fm.get("handoffs") or []:
        if isinstance(handoff, dict):
            target = handoff.get("agent")
            if isinstance(target, str) and target and known_agents and target not in known_agents:
                result.error("unknown-handoff-agent", f"Handoff target '{target}' is not present in the discovered repo surface")
    for tool in _as_string_list(fm.get("tools")):
        if known_tools and tool not in known_tools:
            result.warning("unknown-tool-surface", f"Tool '{tool}' is not present in the discovered repo surface; verify against the live session before shipping.")


def validate_agent(agent_path: Path | str, repo_root: Path | str | None = None) -> ValidationResult:
    agent_path = Path(agent_path).resolve()
    result = ValidationResult(agent_path=str(agent_path))
    if not agent_path.is_file():
        result.error("agent-missing", "Agent file not found")
        return result
    try:
        fm, body = parse_frontmatter(agent_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        result.error("frontmatter-parse-error", str(exc))
        return result

    surface = None
    if repo_root is not None:
        surface = discovery.discover_surface(repo_root)
        result.surface = surface

    validate_frontmatter(agent_path, fm, result)
    validate_body(body, result)
    validate_surface_alignment(agent_path, fm, result, surface)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a GitHub Copilot custom-agent contract.")
    parser.add_argument("agent_path", help="Path to the .agent.md file")
    parser.add_argument("--repo-root", help="Optional repository root for inventory checks")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_agent(args.agent_path, repo_root=args.repo_root)
    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        marker = "✓" if result.valid else "✗"
        print(f"{marker} {result.agent_path}")
        for issue in result.issues:
            level = "ERROR" if issue.severity == "error" else "WARN"
            print(f"  [{level}] {issue.code}: {issue.message}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
