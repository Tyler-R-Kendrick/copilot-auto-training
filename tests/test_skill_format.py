"""
Validate skills/optimize/SKILL.md against the Anthropic Agent Skills specification.

Spec constraints:
  - The skill must exist inside a `skills/` directory
  - SKILL.md must exist at the root of the skill directory
  - Must have YAML frontmatter (between --- delimiters)
  - `name` field: required, 1-64 chars, lowercase letters/numbers/hyphens only,
    must not start or end with a hyphen, no consecutive hyphens,
    must match the containing directory name
  - `description` field: required, 1-1024 chars, non-empty
  - Body (after frontmatter) must be non-empty
  - Optional fields (license, compatibility, metadata, allowed-tools) may be present
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
SKILL_ROOT = SKILLS_DIR / "optimize"
SKILL_MD = SKILL_ROOT / "SKILL.md"


def _parse_frontmatter(text: str) -> tuple[str, str]:
    """Return (raw_yaml_block, body) from a SKILL.md string, or raise AssertionError."""
    if not text.startswith("---"):
        raise AssertionError("SKILL.md must start with --- frontmatter delimiter")
    closing = text.find("---", 3)
    if closing == -1:
        raise AssertionError("SKILL.md must have a closing --- frontmatter delimiter")
    raw_yaml = text[3:closing].strip()
    body = text[closing + 3:].strip()
    return raw_yaml, body


def _parse_yaml_simple(raw: str) -> dict:
    """
    Very minimal YAML key: value parser (handles only scalar top-level keys).
    Sufficient for validating the required frontmatter fields.
    """
    result: dict = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


class TestSkillFileExists:
    def test_skills_dir_exists(self):
        assert SKILLS_DIR.is_dir(), f"skills/ directory not found: {SKILLS_DIR}"

    def test_skill_dir_inside_skills(self):
        assert SKILL_ROOT.parent == SKILLS_DIR, (
            f"Skill must live inside skills/ directory, not {SKILL_ROOT.parent}"
        )

    def test_skill_dir_exists(self):
        assert SKILL_ROOT.is_dir(), f"Skill directory not found: {SKILL_ROOT}"

    def test_skill_md_exists(self):
        assert SKILL_MD.is_file(), f"SKILL.md not found: {SKILL_MD}"

    def test_skill_md_is_not_empty(self):
        assert SKILL_MD.stat().st_size > 0


class TestSkillFrontmatter:
    @pytest.fixture(autouse=True)
    def load(self):
        self.text = SKILL_MD.read_text(encoding="utf-8")
        self.raw_yaml, self.body = _parse_frontmatter(self.text)
        self.fields = _parse_yaml_simple(self.raw_yaml)

    def test_has_frontmatter_delimiters(self):
        assert self.text.startswith("---"), "Must start with ---"
        assert "---" in self.text[3:], "Must have closing ---"

    def test_name_field_present(self):
        assert "name" in self.fields, "frontmatter must have a 'name' field"

    def test_description_field_present(self):
        assert "description" in self.fields, "frontmatter must have a 'description' field"

    def test_name_not_empty(self):
        assert self.fields.get("name", "").strip() != ""

    def test_description_not_empty(self):
        assert self.fields.get("description", "").strip() != ""

    def test_name_max_64_chars(self):
        assert len(self.fields["name"]) <= 64

    def test_description_max_1024_chars(self):
        assert len(self.fields["description"]) <= 1024

    def test_name_lowercase_alphanumeric_hyphens_only(self):
        name = self.fields["name"]
        assert re.fullmatch(r"[a-z0-9][a-z0-9\-]*[a-z0-9]|[a-z0-9]", name), (
            f"name '{name}' must contain only lowercase letters, digits, and hyphens"
        )

    def test_name_does_not_start_with_hyphen(self):
        assert not self.fields["name"].startswith("-")

    def test_name_does_not_end_with_hyphen(self):
        assert not self.fields["name"].endswith("-")

    def test_name_no_consecutive_hyphens(self):
        assert "--" not in self.fields["name"]

    def test_name_matches_directory_name(self):
        assert self.fields["name"] == SKILL_ROOT.name, (
            f"name '{self.fields['name']}' must match directory name '{SKILL_ROOT.name}'"
        )


class TestSkillBody:
    @pytest.fixture(autouse=True)
    def load(self):
        text = SKILL_MD.read_text(encoding="utf-8")
        _, self.body = _parse_frontmatter(text)

    def test_body_is_not_empty(self):
        assert self.body.strip() != "", "SKILL.md body (after frontmatter) must not be empty"

    def test_body_has_instructions(self):
        # Body should contain at least one heading or bullet point
        assert any(line.startswith(("#", "-", "*", "1.")) for line in self.body.splitlines()), (
            "SKILL.md body should contain instructions (headings or list items)"
        )


class TestSkillOptionalFiles:
    def test_scripts_dir_exists(self):
        assert (SKILL_ROOT / "scripts").is_dir()

    def test_run_optimize_script_exists(self):
        assert (SKILL_ROOT / "scripts" / "run_optimize.py").is_file()

    def test_assets_dir_exists(self):
        assert (SKILL_ROOT / "assets").is_dir()

    def test_references_dir_exists(self):
        assert (SKILL_ROOT / "references").is_dir()
