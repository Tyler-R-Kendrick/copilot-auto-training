"""Tests for engineer-skill validation and analysis scripts."""
from __future__ import annotations

import importlib.util
import json
import io
import runpy
import sys
import textwrap
from pathlib import Path
from contextlib import redirect_stdout

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "engineer-skill"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    mod = sys.modules.setdefault(name, mod)
    spec.loader.exec_module(mod)
    return mod


_validate_mod = _load_module("validate_skill", SKILL_DIR / "scripts" / "validate_skill.py")
_analyze_mod = _load_module("analyze_skill_body", SKILL_DIR / "scripts" / "analyze_skill_body.py")

# Re-export names for convenience
ValidationResult = _validate_mod.ValidationResult
parse_frontmatter = _validate_mod.parse_frontmatter
validate_frontmatter = _validate_mod.validate_frontmatter
validate_name_matches_dir = _validate_mod.validate_name_matches_dir
validate_body = _validate_mod.validate_body
validate_cross_references = _validate_mod.validate_cross_references
validate_description_quality = _validate_mod.validate_description_quality
validate_skill = _validate_mod.validate_skill
ALLOWED_FRONTMATTER_KEYS = _validate_mod.ALLOWED_FRONTMATTER_KEYS
NAME_MAX_LEN = _validate_mod.NAME_MAX_LEN
DESCRIPTION_MAX_LEN = _validate_mod.DESCRIPTION_MAX_LEN
validate_main = _validate_mod.main

parse_sections = _analyze_mod.parse_sections
find_deterministic_lines = _analyze_mod.find_deterministic_lines
find_reference_candidates = _analyze_mod.find_reference_candidates
analyze_skill = _analyze_mod.analyze_skill
analyze_main = _analyze_mod.main


# === Frontmatter parsing tests ================================================

class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        text = textwrap.dedent("""\
            ---
            name: test-skill
            description: A test skill.
            ---
            # Body
            Some content.
        """)
        fm, body = parse_frontmatter(text)
        assert fm["name"] == "test-skill"
        assert fm["description"] == "A test skill."
        assert "# Body" in body

    def test_missing_opening_delimiter(self):
        with pytest.raises(ValueError, match="must start with ---"):
            parse_frontmatter("name: test\n---\n# Body")

    def test_missing_closing_delimiter(self):
        with pytest.raises(ValueError, match="must have a closing"):
            parse_frontmatter("---\nname: test\n# Body")

    def test_non_dict_frontmatter(self):
        with pytest.raises(ValueError, match="YAML mapping"):
            parse_frontmatter("---\n- item1\n- item2\n---\n# Body")


class TestAnalyzeParseFrontmatter:
    def test_missing_opening_delimiter(self):
        with pytest.raises(ValueError, match="must start with ---"):
            _analyze_mod.parse_frontmatter("name: test\n---\n# Body")

    def test_missing_closing_delimiter(self):
        with pytest.raises(ValueError, match="must have a closing"):
            _analyze_mod.parse_frontmatter("---\nname: test\n# Body")

    def test_non_dict_frontmatter(self):
        with pytest.raises(ValueError, match="YAML mapping"):
            _analyze_mod.parse_frontmatter("---\n- item1\n- item2\n---\n# Body")


# === Frontmatter validation tests =============================================

class TestValidateFrontmatter:
    def test_valid_minimal(self):
        fm = {"name": "my-skill", "description": "Does something useful."}
        result = ValidationResult(skill_path="/tmp/my-skill")
        validate_frontmatter(fm, result)
        assert result.valid

    def test_missing_name(self):
        fm = {"description": "Does something."}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-missing" for i in result.issues)

    def test_missing_description(self):
        fm = {"name": "test-skill"}
        result = ValidationResult(skill_path="/tmp/test-skill")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-description-missing" for i in result.issues)

    def test_name_too_long(self):
        fm = {"name": "a" * 65, "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-too-long" for i in result.issues)

    def test_name_at_max_length(self):
        name = "a" * NAME_MAX_LEN
        fm = {"name": name, "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        errors = [i for i in result.issues if i.code == "frontmatter-name-too-long"]
        assert not errors

    def test_name_not_kebab_case(self):
        fm = {"name": "MySkill", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/MySkill")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-format" for i in result.issues)

    def test_name_with_underscores(self):
        fm = {"name": "my_skill", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/my_skill")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-format" for i in result.issues)

    def test_name_with_spaces(self):
        fm = {"name": "my skill", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/my skill")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-format" for i in result.issues)

    def test_name_with_special_chars(self):
        fm = {"name": "my.skill!", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/my.skill!")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-format" for i in result.issues)

    def test_name_with_consecutive_hyphens(self):
        fm = {"name": "my--skill", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/my--skill")
        validate_frontmatter(fm, result)
        assert not result.valid

    def test_name_starting_with_hyphen(self):
        fm = {"name": "-my-skill", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/-my-skill")
        validate_frontmatter(fm, result)
        assert not result.valid

    def test_description_too_long(self):
        fm = {"name": "test", "description": "x" * (DESCRIPTION_MAX_LEN + 1)}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-description-too-long" for i in result.issues)

    def test_description_with_angle_brackets(self):
        fm = {"name": "test", "description": "Use <template> tags."}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-description-brackets" for i in result.issues)

    def test_unexpected_keys(self):
        fm = {"name": "test", "description": "Valid.", "custom-field": "value"}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-unexpected-keys" for i in result.issues)

    def test_all_allowed_keys_pass(self):
        fm = {
            "name": "test",
            "description": "Valid.",
            "license": "MIT",
            "compatibility": "Python 3.11+",
            "metadata": {"author": "test"},
            "allowed-tools": "python bash",
            "argument-hint": "Describe the task.",
        }
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert result.valid

    def test_compatibility_too_long(self):
        fm = {"name": "test", "description": "Valid.", "compatibility": "x" * 501}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-compatibility-too-long" for i in result.issues)

    def test_compatibility_wrong_type(self):
        fm = {"name": "test", "description": "Valid.", "compatibility": 123}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-compatibility-type" for i in result.issues)

    def test_empty_name_string(self):
        fm = {"name": "  ", "description": "Valid."}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-name-empty" for i in result.issues)

    def test_empty_description_string(self):
        fm = {"name": "test", "description": "   "}
        result = ValidationResult(skill_path="/tmp/test")
        validate_frontmatter(fm, result)
        assert not result.valid
        assert any(i.code == "frontmatter-description-empty" for i in result.issues)


# === Name matches dir tests ===================================================

class TestNameMatchesDir:
    def test_matching_name(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        fm = {"name": "my-skill"}
        result = ValidationResult(skill_path=str(skill_dir))
        validate_name_matches_dir(fm, skill_dir, result)
        assert result.valid

    def test_mismatched_name(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        fm = {"name": "other-skill"}
        result = ValidationResult(skill_path=str(skill_dir))
        validate_name_matches_dir(fm, skill_dir, result)
        assert not result.valid
        assert any(i.code == "name-dir-mismatch" for i in result.issues)


# === Body validation tests ====================================================

class TestValidateBody:
    def test_adequate_body(self):
        body = "# Title\n\n- Item 1\n- Item 2\n\nSome content.\n\nMore content.\n\nEven more."
        result = ValidationResult(skill_path="/tmp/test")
        validate_body(body, result)
        # Should not have error-level issues
        assert result.valid

    def test_short_body(self):
        body = "# Title\nShort."
        result = ValidationResult(skill_path="/tmp/test")
        validate_body(body, result)
        warnings = [i for i in result.issues if i.code == "body-too-short"]
        assert len(warnings) == 1

    def test_no_headings(self):
        body = "\n".join(["Line " + str(i) for i in range(10)])
        result = ValidationResult(skill_path="/tmp/test")
        validate_body(body, result)
        warnings = [i for i in result.issues if i.code == "body-no-headings"]
        assert len(warnings) == 1

    def test_no_lists(self):
        body = "# Title\n\n" + "\n".join(["Paragraph " + str(i) for i in range(10)])
        result = ValidationResult(skill_path="/tmp/test")
        validate_body(body, result)
        warnings = [i for i in result.issues if i.code == "body-no-lists"]
        assert len(warnings) == 1

    def test_long_body(self):
        body = "# Title\n" + "\n".join(f"- Item {i}" for i in range(600))
        result = ValidationResult(skill_path="/tmp/test")
        validate_body(body, result)
        assert any(i.code == "body-too-long" for i in result.issues)


# === Cross-reference tests ====================================================

class TestCrossReferences:
    def test_no_cross_references(self):
        body = "# My Skill\n\nDo something useful."
        result = ValidationResult(skill_path="/tmp/test")
        validate_cross_references(Path("/tmp/test"), body, ["other-skill", "another-skill"], result)
        assert result.valid

    def test_detects_cross_reference(self):
        body = "# My Skill\n\nUse other-skill for this."
        result = ValidationResult(skill_path="/tmp/test")
        validate_cross_references(Path("/tmp/test"), body, ["other-skill"], result)
        assert not result.valid
        assert any(i.code == "cross-skill-reference" for i in result.issues)

    def test_partial_match_not_flagged(self):
        body = "# My Skill\n\nUse my-other-skill-helper for this."
        result = ValidationResult(skill_path="/tmp/test")
        validate_cross_references(Path("/tmp/test"), body, ["other-skill"], result)
        assert result.valid


# === Description quality tests ================================================

class TestDescriptionQuality:
    def test_good_description(self):
        desc = "Improve agent skills by validating structure and optimizing frontmatter. Use this whenever the user wants to create, improve, or debug an agent skill."
        result = ValidationResult(skill_path="/tmp/test")
        validate_description_quality(desc, result)
        warnings = [i for i in result.issues if i.severity == "warning"]
        # Should have no trigger-phrase warning since "Use this" is present
        assert not any(i.code == "description-no-trigger-phrase" for i in warnings)

    def test_description_without_trigger(self):
        desc = "A tool for managing agent skills."
        result = ValidationResult(skill_path="/tmp/test")
        validate_description_quality(desc, result)
        warnings = [i for i in result.issues if i.code == "description-no-trigger-phrase"]
        assert len(warnings) == 1

    def test_description_with_passive_start(self):
        desc = "A skill for improving prompts."
        result = ValidationResult(skill_path="/tmp/test")
        validate_description_quality(desc, result)
        warnings = [i for i in result.issues if i.code == "description-passive-start"]
        assert len(warnings) == 1

    def test_empty_description_is_ignored(self):
        result = ValidationResult(skill_path="/tmp/test")
        validate_description_quality("", result)
        assert result.issues == []


# === Section parsing tests ====================================================

class TestParseSections:
    def test_leading_heading_does_not_create_empty_preamble(self):
        body = "# Title\n\nContent here."
        sections = parse_sections(body)
        assert len(sections) == 1
        assert sections[0].heading == "# Title"

    def test_single_section(self):
        body = "# Title\n\nContent here."
        sections = parse_sections(body)
        assert len(sections) >= 1
        assert any(s.heading == "# Title" for s in sections)

    def test_multiple_sections(self):
        body = "# Title\n\nIntro.\n\n## Section A\n\nContent A.\n\n## Section B\n\nContent B."
        sections = parse_sections(body)
        headings = [s.heading for s in sections]
        assert "## Section A" in headings
        assert "## Section B" in headings

    def test_empty_body(self):
        sections = parse_sections("")
        assert len(sections) == 0

    def test_preamble_without_heading_is_preserved(self):
        body = "Intro line\nAnother line"
        sections = parse_sections(body)
        assert len(sections) == 1
        assert sections[0].heading == "(preamble)"
        extracted = body.splitlines()[sections[0].start_line - 1:sections[0].end_line]
        assert "\n".join(extracted) == body


# === Deterministic line detection tests =======================================

class TestFindDeterministicLines:
    def test_detects_check_that(self):
        body = "Step 1: Check that the name matches the directory.\nStep 2: Do something else."
        results = find_deterministic_lines(body)
        assert len(results) >= 1
        assert any("check that" in r["text"].lower() for r in results)

    def test_detects_validate(self):
        body = "You should validate the frontmatter fields."
        results = find_deterministic_lines(body)
        assert len(results) >= 1

    def test_detects_for_each(self):
        body = "For each item, do the transformation."
        results = find_deterministic_lines(body)
        assert len(results) >= 1

    def test_no_false_positives_on_clean_prose(self):
        body = "This skill helps agents improve their work.\nIt provides clear guidance."
        results = find_deterministic_lines(body)
        assert len(results) == 0

    def test_detects_parse(self):
        body = "Parse the YAML frontmatter and extract fields."
        results = find_deterministic_lines(body)
        assert len(results) >= 1

    def test_detects_count(self):
        body = "Count the number of sections in the body."
        results = find_deterministic_lines(body)
        assert len(results) >= 1


# === Reference candidate detection tests =====================================

class TestFindReferenceCandidates:
    def test_detects_example_pattern(self):
        body = "Example: using the skill with a PDF.\nOther line."
        results = find_reference_candidates(body)
        assert len(results) >= 1

    def test_detects_detailed_info(self):
        body = "For more information, see the specification."
        results = find_reference_candidates(body)
        assert len(results) >= 1

    def test_no_false_positives(self):
        body = "Run the validation script.\nCheck the results."
        results = find_reference_candidates(body)
        assert len(results) == 0


# === Integration tests ========================================================

class TestValidateSkillIntegration:
    def test_valid_skill_directory(self, tmp_path):
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()

        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: test-skill
            description: Improve test coverage. Use this whenever the user asks about testing.
            ---
            # Test Skill

            - Run tests
            - Check coverage
            - Report results

            Some more content here.
        """))

        result = validate_skill(skill_dir)
        assert result.valid

    def test_invalid_skill_no_skill_md(self, tmp_path):
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        result = validate_skill(skill_dir)
        assert not result.valid

    def test_invalid_frontmatter(self, tmp_path):
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            description: Missing name field.
            ---
            # Bad Skill
            - Content
            - More content
            - Even more
            - And more
            - Still more
        """))
        result = validate_skill(skill_dir)
        assert not result.valid

    def test_invalid_yaml_returns_parse_error(self, tmp_path):
        skill_dir = tmp_path / "yaml-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: [unterminated\n---\n# Body\n- Item\n")
        result = validate_skill(skill_dir)
        assert not result.valid
        assert any(i.code == "frontmatter-parse-error" for i in result.issues)

    def test_non_string_description_does_not_crash(self, tmp_path):
        skill_dir = tmp_path / "typed-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: typed-skill\ndescription: 123\n---\n# Body\n- Item\n- Item 2\n- Item 3\n- Item 4\n- Item 5\n")
        result = validate_skill(skill_dir)
        assert not result.valid
        assert any(i.code == "frontmatter-description-empty" for i in result.issues)

    def test_other_skills_triggers_cross_reference_check(self, tmp_path):
        skill_dir = tmp_path / "cross-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: cross-skill
            description: Improve skills. Use this whenever skill work is needed.
            ---
            # Cross Skill

            - Use other-skill for comparison
            - Keep going
            - Keep going
            - Keep going
            - Keep going
        """))
        result = validate_skill(skill_dir, ["other-skill"])
        assert any(i.code == "cross-skill-reference" for i in result.issues)

    def test_missing_subdirectories_emit_warnings(self, tmp_path):
        skill_dir = tmp_path / "minimal-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: minimal-skill
            description: Improve skills. Use this whenever skill work is needed.
            ---
            # Minimal Skill

            - One
            - Two
            - Three
            - Four
            - Five
        """))
        result = validate_skill(skill_dir)
        warnings = [i for i in result.issues if i.code == "structure-missing-dir"]
        assert len(warnings) == 3


class TestAnalyzeSkillIntegration:
    def test_analyze_clean_skill(self, tmp_path):
        skill_dir = tmp_path / "clean-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: clean-skill
            description: A clean skill.
            ---
            # Clean Skill

            - Step 1
            - Step 2

            Content.
        """))
        result = analyze_skill(skill_dir)
        assert result.body_lines > 0
        assert result.section_count >= 1

    def test_analyze_detects_deterministic_content(self, tmp_path):
        skill_dir = tmp_path / "det-skill"
        skill_dir.mkdir()
        body_lines = [
            "# Skill",
            "",
            "Check that the name field is valid.",
            "Validate the description length.",
            "Parse the frontmatter YAML.",
            "For each section, do the extraction.",
            "Count the number of headings.",
            "",
            "- Item",
        ]
        (skill_dir / "SKILL.md").write_text(
            "---\nname: det-skill\ndescription: Test.\n---\n" + "\n".join(body_lines)
        )
        result = analyze_skill(skill_dir)
        assert len(result.deterministic_lines) >= 4

    def test_analyze_no_skill_md(self, tmp_path):
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()
        result = analyze_skill(skill_dir)
        assert len(result.recommendations) >= 1
        assert result.recommendations[0].category == "structure"

    def test_analyze_invalid_yaml_returns_structure_recommendation(self, tmp_path):
        skill_dir = tmp_path / "broken-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: [broken\n---\n# Body\n- Item\n")
        result = analyze_skill(skill_dir)
        assert any("Frontmatter error:" in rec.description for rec in result.recommendations)

    def test_analyze_detects_long_body_and_large_section_and_reference_candidates(self, tmp_path):
        skill_dir = tmp_path / "large-skill"
        skill_dir.mkdir()
        long_section = "\n".join(f"Line {i}" for i in range(60))
        filler = "\n".join(f"- Item {i}" for i in range(460))
        (skill_dir / "SKILL.md").write_text(
            "---\nname: large-skill\ndescription: Analyze skills.\n---\n"
            f"## Large Section\n{long_section}\n"
            "For more information, see the specification.\n"
            f"{filler}\n"
        )
        result = analyze_skill(skill_dir)
        categories = [rec.category for rec in result.recommendations]
        assert "reduce-body" in categories
        assert "extract-reference" in categories
        assert result.reference_candidates


class TestSerializationAndCli:
    def test_validation_result_to_dict(self):
        result = ValidationResult(skill_path="/tmp/test")
        result.warning("warn-code", "warn message")
        payload = result.to_dict()
        assert payload["skill_path"] == "/tmp/test"
        assert payload["valid"] is True
        assert payload["issues"][0]["code"] == "warn-code"

    def test_analysis_result_to_dict(self, tmp_path):
        skill_dir = tmp_path / "clean-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: clean-skill
            description: Analyze skills.
            ---
            # Clean Skill
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        payload = analyze_skill(skill_dir).to_dict()
        assert payload["skill_path"] == str(skill_dir.resolve())
        assert isinstance(payload["sections"], list)

    def test_validate_main_json_output(self, tmp_path):
        skill_dir = tmp_path / "cli-skill"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: cli-skill
            description: Improve skills. Use this whenever skill work is needed.
            ---
            # CLI Skill
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = validate_main([str(skill_dir), "--json"])
        payload = json.loads(buffer.getvalue())
        assert exit_code == 0
        assert payload["valid"] is True

    def test_validate_main_text_output_failure(self, tmp_path):
        skill_dir = tmp_path / "cli-bad"
        skill_dir.mkdir()
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = validate_main([str(skill_dir)])
        output = buffer.getvalue()
        assert exit_code == 1
        assert "Skill has errors" in output

    def test_validate_main_text_output_success(self, tmp_path):
        skill_dir = tmp_path / "cli-good"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: cli-good
            description: Improve skills. Use this whenever skill work is needed.
            ---
            # CLI Skill
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = validate_main([str(skill_dir)])
        output = buffer.getvalue()
        assert exit_code == 0
        assert "Skill is valid" in output

    def test_analyze_main_json_output(self, tmp_path):
        skill_dir = tmp_path / "analyze-cli"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: analyze-cli
            description: Analyze skills.
            ---
            # Analyze
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = analyze_main([str(skill_dir), "--json"])
        payload = json.loads(buffer.getvalue())
        assert exit_code == 0
        assert payload["skill_path"] == str(skill_dir.resolve())

    def test_analyze_main_text_output_with_recommendations(self, tmp_path):
        skill_dir = tmp_path / "analyze-text"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: analyze-text\ndescription: Analyze skills.\n---\n"
            "Check that the result is valid.\n"
        )
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = analyze_main([str(skill_dir)])
        output = buffer.getvalue()
        assert exit_code == 0
        assert "Recommendations:" in output
        assert "Deterministic lines" in output

    def test_analyze_main_text_output_without_recommendations(self, tmp_path):
        skill_dir = tmp_path / "analyze-clean"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: analyze-clean
            description: Analyze skills.
            ---
            # Analyze
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = analyze_main([str(skill_dir), "--json"])
        assert exit_code == 0

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = analyze_main([str(skill_dir)])
        output = buffer.getvalue()
        assert exit_code == 0
        assert "No recommendations — skill looks good!" in output

    def test_validate_script_dunder_main(self, monkeypatch, tmp_path):
        skill_dir = tmp_path / "script-main"
        skill_dir.mkdir()
        for subdir in ("scripts", "references", "assets"):
            (skill_dir / subdir).mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: script-main
            description: Improve skills. Use this whenever skill work is needed.
            ---
            # Script Main
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        monkeypatch.setattr(sys, "argv", ["validate_skill.py", str(skill_dir)])
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(SKILL_DIR / "scripts" / "validate_skill.py"), run_name="__main__")
        assert exc.value.code == 0

    def test_analyze_script_dunder_main(self, monkeypatch, tmp_path):
        skill_dir = tmp_path / "script-analyze"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(textwrap.dedent("""\
            ---
            name: script-analyze
            description: Analyze skills.
            ---
            # Script Analyze
            - One
            - Two
            - Three
            - Four
            - Five
        """))
        monkeypatch.setattr(sys, "argv", ["analyze_skill_body.py", str(skill_dir), "--json"])
        with pytest.raises(SystemExit) as exc:
            runpy.run_path(str(SKILL_DIR / "scripts" / "analyze_skill_body.py"), run_name="__main__")
        assert exc.value.code == 0
