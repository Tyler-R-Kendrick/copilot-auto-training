#!/usr/bin/env python3
"""Validate an agent skill directory against the agentskills.io specification.

Checks SKILL.md frontmatter, naming conventions, directory structure,
cross-skill references, and body quality heuristics.

Usage:
    python scripts/validate_skill.py <skill_directory>
    python scripts/validate_skill.py <skill_directory> --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Sequence

import yaml


# --- Spec constants -----------------------------------------------------------

ALLOWED_FRONTMATTER_KEYS = frozenset({
    "name", "description", "license", "allowed-tools",
    "metadata", "compatibility", "argument-hint",
})
NAME_MAX_LEN = 64
DESCRIPTION_MAX_LEN = 1024
COMPATIBILITY_MAX_LEN = 500
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BODY_MAX_LINES = 500
BODY_MIN_LINES = 5
TRIGGER_PHRASES = ("use this", "use when", "invoke when", "trigger when")
ACTION_VERBS = frozenset({
    "improve", "create", "analyze", "generate", "build", "fix",
    "optimize", "validate", "extract", "convert", "transform",
})


# --- Result types -------------------------------------------------------------

@dataclass
class Issue:
    severity: str  # "error" | "warning"
    code: str
    message: str


@dataclass
class ValidationResult:
    skill_path: str
    valid: bool = True
    issues: list[Issue] = field(default_factory=list)

    def error(self, code: str, message: str) -> None:
        self.issues.append(Issue("error", code, message))
        self.valid = False

    def warning(self, code: str, message: str) -> None:
        self.issues.append(Issue("warning", code, message))

    def to_dict(self) -> dict:
        return {
            "skill_path": self.skill_path,
            "valid": self.valid,
            "issues": [asdict(i) for i in self.issues],
        }


# --- Parsing helpers ----------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from SKILL.md content."""
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with --- frontmatter delimiter")
    closing = text.find("---", 3)
    if closing == -1:
        raise ValueError("SKILL.md must have a closing --- frontmatter delimiter")
    raw_yaml = text[3:closing].strip()
    body = text[closing + 3:].strip()
    fm = yaml.safe_load(raw_yaml)
    if not isinstance(fm, dict):
        raise ValueError("Frontmatter must be a YAML mapping")
    return fm, body


# --- Validators ---------------------------------------------------------------

def validate_frontmatter(fm: dict, result: ValidationResult) -> None:
    """Check frontmatter fields against the spec."""
    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        result.error(
            "frontmatter-unexpected-keys",
            f"Unexpected frontmatter keys: {', '.join(sorted(unexpected))}",
        )

    name = fm.get("name")
    if name is None:
        result.error("frontmatter-name-missing", "Missing required 'name' field")
    elif not isinstance(name, str) or not name.strip():
        result.error("frontmatter-name-empty", "'name' must be a non-empty string")
    else:
        name = name.strip()
        if len(name) > NAME_MAX_LEN:
            result.error("frontmatter-name-too-long", f"Name is {len(name)} chars (max {NAME_MAX_LEN})")
        if not KEBAB_CASE_RE.match(name):
            result.error("frontmatter-name-format", f"Name '{name}' is not valid kebab-case")

    desc = fm.get("description")
    if desc is None:
        result.error("frontmatter-description-missing", "Missing required 'description' field")
    elif not isinstance(desc, str) or not desc.strip():
        result.error("frontmatter-description-empty", "'description' must be a non-empty string")
    else:
        desc = desc.strip()
        if len(desc) > DESCRIPTION_MAX_LEN:
            result.error("frontmatter-description-too-long", f"Description is {len(desc)} chars (max {DESCRIPTION_MAX_LEN})")
        if "<" in desc or ">" in desc:
            result.error("frontmatter-description-brackets", "Description must not contain angle brackets")

    compat = fm.get("compatibility")
    if compat is not None:
        if not isinstance(compat, str):
            result.error("frontmatter-compatibility-type", "Compatibility must be a string")
        elif len(compat) > COMPATIBILITY_MAX_LEN:
            result.error("frontmatter-compatibility-too-long", f"Compatibility is {len(compat)} chars (max {COMPATIBILITY_MAX_LEN})")


def validate_name_matches_dir(fm: dict, skill_path: Path, result: ValidationResult) -> None:
    """Check that the name field matches the directory name."""
    name = fm.get("name", "")
    if isinstance(name, str) and name.strip():
        if name.strip() != skill_path.name:
            result.error(
                "name-dir-mismatch",
                f"Name '{name.strip()}' does not match directory '{skill_path.name}'",
            )


def validate_structure(skill_path: Path, result: ValidationResult) -> None:
    """Check directory structure recommendations."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        result.error("structure-no-skill-md", "SKILL.md not found")
        return

    for subdir in ("scripts", "references", "assets"):
        if not (skill_path / subdir).is_dir():
            result.warning("structure-missing-dir", f"Recommended directory '{subdir}/' not found")


def validate_body(body: str, result: ValidationResult) -> None:
    """Check body content quality heuristics."""
    lines = body.splitlines()
    if len(lines) < BODY_MIN_LINES:
        result.warning("body-too-short", f"Body has {len(lines)} lines (recommend at least {BODY_MIN_LINES})")
    if len(lines) > BODY_MAX_LINES:
        result.warning("body-too-long", f"Body has {len(lines)} lines (recommend under {BODY_MAX_LINES})")

    has_heading = any(line.startswith("#") for line in lines)
    has_list = any(line.lstrip().startswith(("-", "*", "1.")) for line in lines)
    if not has_heading:
        result.warning("body-no-headings", "Body has no markdown headings")
    if not has_list:
        result.warning("body-no-lists", "Body has no list items")


def validate_cross_references(
    skill_path: Path,
    body: str,
    other_skill_names: Sequence[str],
    result: ValidationResult,
) -> None:
    """Check that the body does not reference other skills by name."""
    for skill_name in other_skill_names:
        pattern = rf"(?<![A-Za-z0-9-]){re.escape(skill_name)}(?![A-Za-z0-9-])"
        for line_no, line in enumerate(body.splitlines(), 1):
            if re.search(pattern, line):
                result.error(
                    "cross-skill-reference",
                    f"References skill '{skill_name}' on line {line_no}",
                )


def validate_description_quality(desc: str, result: ValidationResult) -> None:
    """Heuristic checks for description effectiveness."""
    desc = desc.strip()
    if not desc:
        return

    # Check for trigger phrases
    has_trigger = any(phrase in desc.lower() for phrase in TRIGGER_PHRASES)
    if not has_trigger:
        result.warning(
            "description-no-trigger-phrase",
            "Description lacks explicit trigger guidance (e.g., 'Use this whenever...')",
        )

    # Check for action-oriented start
    first_word = desc.split()[0].lower() if desc else ""
    starts_with_action = first_word in ACTION_VERBS
    starts_with_article = first_word in ("a", "an", "the", "this")
    if starts_with_article and not starts_with_action:
        result.warning(
            "description-passive-start",
            "Description starts with an article instead of an action verb",
        )


# --- Main validation entry point ----------------------------------------------

def validate_skill(
    skill_path: Path | str,
    other_skill_names: Sequence[str] | None = None,
) -> ValidationResult:
    """Run all validation checks on a skill directory."""
    skill_path = Path(skill_path).resolve()
    result = ValidationResult(skill_path=str(skill_path))

    validate_structure(skill_path, result)

    skill_md = skill_path / "SKILL.md"
    if not skill_md.is_file():
        return result

    text = skill_md.read_text(encoding="utf-8")
    try:
        fm, body = parse_frontmatter(text)
    except ValueError as e:
        result.error("frontmatter-parse-error", str(e))
        return result

    validate_frontmatter(fm, result)
    validate_name_matches_dir(fm, skill_path, result)
    validate_body(body, result)
    validate_description_quality(fm.get("description", ""), result)

    if other_skill_names:
        validate_cross_references(skill_path, body, other_skill_names, result)

    return result


# --- CLI ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an agent skill directory against the agentskills.io spec.",
    )
    parser.add_argument("skill_path", help="Path to the skill directory")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")
    parser.add_argument(
        "--other-skills",
        nargs="*",
        default=[],
        help="Names of other skills to check for cross-references",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_skill(args.skill_path, args.other_skills or None)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.valid:
            print(f"✓ Skill is valid: {result.skill_path}")
        else:
            print(f"✗ Skill has errors: {result.skill_path}")
        for issue in result.issues:
            marker = "ERROR" if issue.severity == "error" else "WARN"
            print(f"  [{marker}] {issue.code}: {issue.message}")

    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
