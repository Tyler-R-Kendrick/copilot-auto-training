#!/usr/bin/env python3
"""Analyze a SKILL.md body and produce actionable improvement recommendations.

Scans for content that should be extracted to reference files, sequences that
should become scripts, and body sections that exceed recommended thresholds.

Usage:
    python scripts/analyze_skill_body.py <skill_directory>
    python scripts/analyze_skill_body.py <skill_directory> --json
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Sequence

import yaml


# --- Thresholds ---------------------------------------------------------------

SECTION_LINE_THRESHOLD = 50
BODY_LINE_THRESHOLD = 500
DETERMINISTIC_INDICATORS = [
    re.compile(r"(?i)\bcheck\s+that\b"),
    re.compile(r"(?i)\bverif(?:y|ied|ies)\b"),
    re.compile(r"(?i)\bvalidate\b"),
    re.compile(r"(?i)\bparse\b"),
    re.compile(r"(?i)\bcount\s+the\b"),
    re.compile(r"(?i)\bfor\s+each\b.*\bdo\b"),
    re.compile(r"(?i)\bextract\b.*\bfrom\b"),
    re.compile(r"(?i)\bsort\b.*\bby\b"),
    re.compile(r"(?i)\bcompare\b.*\bwith\b"),
    re.compile(r"(?i)\bcalculate\b"),
    re.compile(r"(?i)\bformat\b.*\bas\b"),
]
REFERENCE_INDICATORS = [
    re.compile(r"(?i)\bexample[s]?\b.*:"),
    re.compile(r"(?i)\bfor\s+(more|detailed|further)\s+(information|details|context)\b"),
    re.compile(r"(?i)\bbackground\b"),
    re.compile(r"(?i)\bspecification\b"),
]


# --- Types --------------------------------------------------------------------

@dataclass
class Section:
    heading: str
    start_line: int
    end_line: int
    line_count: int


@dataclass
class Recommendation:
    category: str  # "extract-reference" | "extract-script" | "reduce-body" | "structure"
    severity: str  # "high" | "medium" | "low"
    description: str
    location: str  # e.g., "lines 45-90" or "section: ## Examples"


@dataclass
class AnalysisResult:
    skill_path: str
    body_lines: int = 0
    section_count: int = 0
    sections: list[Section] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    deterministic_lines: list[dict] = field(default_factory=list)
    reference_candidates: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "skill_path": self.skill_path,
            "body_lines": self.body_lines,
            "section_count": self.section_count,
            "sections": [asdict(s) for s in self.sections],
            "recommendations": [asdict(r) for r in self.recommendations],
            "deterministic_lines": self.deterministic_lines,
            "reference_candidates": self.reference_candidates,
        }


# --- Parsing ------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from SKILL.md content."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with --- frontmatter delimiter")

    closing_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = i
            break

    if closing_index is None:
        raise ValueError("SKILL.md must have a closing --- frontmatter delimiter")

    raw_yaml = "".join(lines[1:closing_index]).strip()
    body = "".join(lines[closing_index + 1:]).strip()
    try:
        fm = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in frontmatter: {exc}") from exc
    if not isinstance(fm, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return fm, body


def parse_sections(body: str) -> list[Section]:
    """Parse the body into sections by markdown headings."""
    lines = body.splitlines()
    sections: list[Section] = []
    current_heading = "(preamble)"
    current_start = 1

    for i, line in enumerate(lines, 1):
        if line.startswith("#"):
            current_section_non_empty = i > current_start
            if current_heading != "(preamble)" or current_section_non_empty:
                sections.append(Section(
                    heading=current_heading,
                    start_line=current_start,
                    end_line=i - 1,
                    line_count=i - current_start,
                ))
            current_heading = line.strip()
            current_start = i

    # Final section
    if lines:
        sections.append(Section(
            heading=current_heading,
            start_line=current_start,
            end_line=len(lines),
            line_count=len(lines) - current_start + 1,
        ))

    return sections


# --- Analysis -----------------------------------------------------------------

def find_deterministic_lines(body: str) -> list[dict]:
    """Find lines that contain deterministic/sequential instruction patterns."""
    results = []
    for line_no, line in enumerate(body.splitlines(), 1):
        for pattern in DETERMINISTIC_INDICATORS:
            if pattern.search(line):
                results.append({
                    "line": line_no,
                    "text": line.strip(),
                    "pattern": pattern.pattern,
                })
                break  # One match per line is enough
    return results


def find_reference_candidates(body: str) -> list[dict]:
    """Find lines that suggest content should be in a reference file."""
    results = []
    for line_no, line in enumerate(body.splitlines(), 1):
        for pattern in REFERENCE_INDICATORS:
            if pattern.search(line):
                results.append({
                    "line": line_no,
                    "text": line.strip(),
                    "pattern": pattern.pattern,
                })
                break
    return results


def analyze_skill(skill_path: Path | str) -> AnalysisResult:
    """Analyze a skill directory and produce improvement recommendations."""
    skill_path = Path(skill_path).resolve()
    result = AnalysisResult(skill_path=str(skill_path))

    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        result.recommendations.append(Recommendation(
            category="structure",
            severity="high",
            description="SKILL.md not found",
            location=str(skill_path),
        ))
        return result

    text = skill_md.read_text(encoding="utf-8")
    try:
        _, body = parse_frontmatter(text)
    except ValueError as e:
        result.recommendations.append(Recommendation(
            category="structure",
            severity="high",
            description=f"Frontmatter error: {e}",
            location="SKILL.md",
        ))
        return result

    lines = body.splitlines()
    result.body_lines = len(lines)

    # Parse sections
    sections = parse_sections(body)
    result.sections = sections
    result.section_count = len(sections)

    # Check body length
    if result.body_lines > BODY_LINE_THRESHOLD:
        result.recommendations.append(Recommendation(
            category="reduce-body",
            severity="high",
            description=f"Body has {result.body_lines} lines (recommend under {BODY_LINE_THRESHOLD}). Extract domain knowledge to references/ and deterministic steps to scripts/.",
            location="SKILL.md",
        ))

    # Check for oversized sections
    for section in sections:
        if section.line_count > SECTION_LINE_THRESHOLD:
            result.recommendations.append(Recommendation(
                category="extract-reference",
                severity="medium",
                description=f"Section '{section.heading}' is {section.line_count} lines (threshold: {SECTION_LINE_THRESHOLD}). Consider extracting to a reference file.",
                location=f"lines {section.start_line}-{section.end_line}",
            ))

    # Find deterministic instructions
    det_lines = find_deterministic_lines(body)
    result.deterministic_lines = det_lines
    if det_lines:
        result.recommendations.append(Recommendation(
            category="extract-script",
            severity="medium",
            description=f"Found {len(det_lines)} lines with deterministic/sequential patterns that could become scripts.",
            location="various",
        ))

    # Find reference candidates
    ref_candidates = find_reference_candidates(body)
    result.reference_candidates = ref_candidates
    if ref_candidates:
        result.recommendations.append(Recommendation(
            category="extract-reference",
            severity="low",
            description=f"Found {len(ref_candidates)} lines that suggest content suitable for reference files.",
            location="various",
        ))

    return result


# --- CLI ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a SKILL.md body and produce improvement recommendations.",
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = analyze_skill(args.skill_path)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Skill: {result.skill_path}")
        print(f"Body lines: {result.body_lines}")
        print(f"Sections: {result.section_count}")
        print()
        if result.recommendations:
            print("Recommendations:")
            for rec in result.recommendations:
                print(f"  [{rec.severity.upper()}] {rec.category}: {rec.description}")
                print(f"         Location: {rec.location}")
        else:
            print("No recommendations — skill looks good!")

        if result.deterministic_lines:
            print(f"\nDeterministic lines ({len(result.deterministic_lines)}):")
            for dl in result.deterministic_lines[:10]:
                print(f"  Line {dl['line']}: {dl['text'][:80]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
