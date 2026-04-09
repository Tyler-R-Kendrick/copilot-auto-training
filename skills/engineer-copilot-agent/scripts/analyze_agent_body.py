#!/usr/bin/env python3
"""Analyze Copilot custom-agent bodies for routing and minimization issues."""
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

SECTION_LINE_THRESHOLD = 60
BODY_LINE_THRESHOLD = 500
DETERMINISTIC_PATTERNS = [
    re.compile(r"(?i)\bcheck\s+that\b"),
    re.compile(r"(?i)\bvalidate\b"),
    re.compile(r"(?i)\bfor\s+each\b.*\bdo\b"),
    re.compile(r"(?i)\bcompare\b.*\bwith\b"),
    re.compile(r"(?i)\blist\b.*\bavailable\b"),
    re.compile(r"(?i)\bscan\b.*\brepo\b"),
]
REFERENCE_PATTERNS = [
    re.compile(r"(?i)\bexample[s]?\b.*:"),
    re.compile(r"(?i)\bfor more detail\b"),
    re.compile(r"(?i)\bstandard\b"),
    re.compile(r"(?i)\boptimi[sz]ation\b"),
]


@dataclass
class Section:
    heading: str
    start_line: int
    end_line: int
    line_count: int


@dataclass
class Recommendation:
    category: str
    severity: str
    description: str
    location: str


@dataclass
class AnalysisResult:
    agent_path: str
    body_lines: int = 0
    sections: list[Section] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    deterministic_lines: list[dict[str, Any]] = field(default_factory=list)
    reference_candidates: list[dict[str, Any]] = field(default_factory=list)
    stale_surface_mentions: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_path": self.agent_path,
            "body_lines": self.body_lines,
            "sections": [asdict(section) for section in self.sections],
            "recommendations": [asdict(rec) for rec in self.recommendations],
            "deterministic_lines": self.deterministic_lines,
            "reference_candidates": self.reference_candidates,
            "stale_surface_mentions": self.stale_surface_mentions,
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
    payload = yaml.safe_load(raw_yaml) or {}
    if not isinstance(payload, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return payload, body


def parse_sections(body: str) -> list[Section]:
    lines = body.splitlines()
    sections: list[Section] = []
    current_heading = "(preamble)"
    current_start = 1
    for index, line in enumerate(lines, start=1):
        if line.startswith("#"):
            if index > current_start:
                sections.append(Section(current_heading, current_start, index - 1, index - current_start))
            current_heading = line.strip()
            current_start = index
    if lines:
        sections.append(Section(current_heading, current_start, len(lines), len(lines) - current_start + 1))
    return sections


def find_deterministic_lines(body: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for line_no, line in enumerate(body.splitlines(), start=1):
        for pattern in DETERMINISTIC_PATTERNS:
            if pattern.search(line):
                results.append({"line": line_no, "text": line.strip(), "pattern": pattern.pattern})
                break
    return results


def find_reference_candidates(body: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for line_no, line in enumerate(body.splitlines(), start=1):
        for pattern in REFERENCE_PATTERNS:
            if pattern.search(line):
                results.append({"line": line_no, "text": line.strip(), "pattern": pattern.pattern})
                break
    return results


def find_stale_surface_mentions(body: str, surface: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not surface:
        return []
    known_agents = {agent["name"] for agent in surface.get("agents", [])}
    known_skills = {skill["name"] for skill in surface.get("skills", [])}
    results: list[dict[str, Any]] = []
    for line_no, line in enumerate(body.splitlines(), start=1):
        for token in re.findall(r"`([^`]+)`", line):
            if token.endswith(".agent.md") or token in {"find_agent_skill", "load_agent_skill", "run_agent_skill"}:
                continue
            if token.startswith(".") or "/" in token:
                continue
            if token in known_agents or token in known_skills:
                continue
            if any(prefix in token for prefix in ("agent-skills", "agent/runSubagent")):
                continue
            if re.fullmatch(r"[a-z0-9][a-z0-9\-]*", token):
                results.append({"line": line_no, "text": line.strip(), "token": token})
    return results


def analyze_agent(agent_path: Path | str, repo_root: Path | str | None = None) -> AnalysisResult:
    agent_path = Path(agent_path).resolve()
    result = AnalysisResult(agent_path=str(agent_path))
    text = agent_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(text)
    result.body_lines = len(body.splitlines())
    result.sections = parse_sections(body)

    if result.body_lines > BODY_LINE_THRESHOLD:
        result.recommendations.append(
            Recommendation(
                category="reduce-body",
                severity="high",
                description=f"Body has {result.body_lines} lines; move standards to references and repeated checks to scripts.",
                location="body",
            )
        )
    for section in result.sections:
        if section.line_count > SECTION_LINE_THRESHOLD:
            result.recommendations.append(
                Recommendation(
                    category="extract-reference",
                    severity="medium",
                    description=f"Section '{section.heading}' is {section.line_count} lines; extract deeper guidance.",
                    location=f"lines {section.start_line}-{section.end_line}",
                )
            )

    result.deterministic_lines = find_deterministic_lines(body)
    if result.deterministic_lines:
        result.recommendations.append(
            Recommendation(
                category="extract-script",
                severity="medium",
                description=f"Found {len(result.deterministic_lines)} deterministic lines that likely belong in scripts.",
                location="various",
            )
        )

    result.reference_candidates = find_reference_candidates(body)
    if result.reference_candidates:
        result.recommendations.append(
            Recommendation(
                category="extract-reference",
                severity="low",
                description=f"Found {len(result.reference_candidates)} lines that look like standards or examples better kept in references.",
                location="various",
            )
        )

    lowered = body.lower()
    if "run_agent_skill" in lowered and "load_agent_skill" not in lowered:
        result.recommendations.append(
            Recommendation(
                category="routing",
                severity="medium",
                description="Body mentions run_agent_skill without a matching load step.",
                location="body",
            )
        )
    if "load_agent_skill" in lowered and "find_agent_skill" not in lowered:
        result.recommendations.append(
            Recommendation(
                category="routing",
                severity="medium",
                description="Body mentions load_agent_skill without an earlier discovery step.",
                location="body",
            )
        )

    surface = discovery.discover_surface(repo_root) if repo_root is not None else None
    result.stale_surface_mentions = find_stale_surface_mentions(body, surface)
    if result.stale_surface_mentions:
        result.recommendations.append(
            Recommendation(
                category="verify-surface",
                severity="medium",
                description=f"Found {len(result.stale_surface_mentions)} backticked names not present in the discovered repo surface.",
                location="various",
            )
        )

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a Copilot custom-agent body.")
    parser.add_argument("agent_path", help="Path to the .agent.md file")
    parser.add_argument("--repo-root", help="Optional repository root for inventory checks")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = analyze_agent(args.agent_path, repo_root=args.repo_root)
    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    print(f"Agent: {result.agent_path}")
    print(f"Body lines: {result.body_lines}")
    print(f"Sections: {len(result.sections)}")
    if result.recommendations:
        print("Recommendations:")
        for rec in result.recommendations:
            print(f"  [{rec.severity.upper()}] {rec.category}: {rec.description}")
            print(f"         Location: {rec.location}")
    else:
        print("No recommendations — agent looks lean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
