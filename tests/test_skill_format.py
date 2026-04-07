"""Validate all skill directories against the Anthropic Agent Skills specification."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


def _skill_dirs() -> list[Path]:
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def _skill_md(skill_root: Path) -> Path:
    return skill_root / "SKILL.md"


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


def _cross_skill_mentions(skill_root: Path) -> list[str]:
    text = _skill_md(skill_root).read_text(encoding="utf-8")
    other_skill_names = sorted(path.name for path in _skill_dirs() if path != skill_root)
    matches: list[str] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        for skill_name in other_skill_names:
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(skill_name)}(?![A-Za-z0-9-])", line):
                matches.append(f"{skill_name} on line {line_number}: {line.strip()}")

    return matches


class TestSkillFileExists:
    def test_skills_dir_exists(self):
        assert SKILLS_DIR.is_dir(), f"skills/ directory not found: {SKILLS_DIR}"

    def test_expected_skills_exist(self):
        names = {path.name for path in _skill_dirs()}
        assert {
            "judge-trajectory",
            "judge-outcome",
            "judge-rubric",
            "learn",
            "researcher-research",
            "trainer-election",
            "trainer-optimize",
            "trainer-synthesize",
        } <= names

    def test_old_unprefixed_skill_dirs_are_absent(self):
        names = {path.name for path in _skill_dirs()}
        assert {"optimize", "election", "research", "synthesize"}.isdisjoint(names)

    @pytest.mark.parametrize("skill_root", _skill_dirs())
    def test_skill_dir_inside_skills(self, skill_root: Path):
        assert skill_root.parent == SKILLS_DIR, (
            f"Skill must live inside skills/ directory, not {skill_root.parent}"
        )

    @pytest.mark.parametrize("skill_root", _skill_dirs())
    def test_skill_md_exists(self, skill_root: Path):
        skill_md = _skill_md(skill_root)
        assert skill_md.is_file(), f"SKILL.md not found: {skill_md}"

    @pytest.mark.parametrize("skill_root", _skill_dirs())
    def test_skill_md_is_not_empty(self, skill_root: Path):
        assert _skill_md(skill_root).stat().st_size > 0


class TestSkillFrontmatter:
    @pytest.fixture(params=_skill_dirs(), ids=lambda path: path.name)
    def loaded_skill(self, request):
        skill_root = request.param
        text = _skill_md(skill_root).read_text(encoding="utf-8")
        raw_yaml, body = _parse_frontmatter(text)
        fields = _parse_yaml_simple(raw_yaml)
        return skill_root, text, fields, body

    def test_has_frontmatter_delimiters(self, loaded_skill):
        _, text, _, _ = loaded_skill
        assert text.startswith("---"), "Must start with ---"
        assert "---" in text[3:], "Must have closing ---"

    def test_name_field_present(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert "name" in fields, "frontmatter must have a 'name' field"

    def test_description_field_present(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert "description" in fields, "frontmatter must have a 'description' field"

    def test_name_not_empty(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert fields.get("name", "").strip() != ""

    def test_description_not_empty(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert fields.get("description", "").strip() != ""

    def test_name_max_64_chars(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert len(fields["name"]) <= 64

    def test_description_max_1024_chars(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert len(fields["description"]) <= 1024

    def test_name_lowercase_alphanumeric_hyphens_only(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        name = fields["name"]
        assert re.fullmatch(r"[a-z0-9][a-z0-9\-]*[a-z0-9]|[a-z0-9]", name), (
            f"name '{name}' must contain only lowercase letters, digits, and hyphens"
        )

    def test_name_does_not_start_with_hyphen(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert not fields["name"].startswith("-")

    def test_name_does_not_end_with_hyphen(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert not fields["name"].endswith("-")

    def test_name_no_consecutive_hyphens(self, loaded_skill):
        _, _, fields, _ = loaded_skill
        assert "--" not in fields["name"]

    def test_name_matches_directory_name(self, loaded_skill):
        skill_root, _, fields, _ = loaded_skill
        assert fields["name"] == skill_root.name, (
            f"name '{fields['name']}' must match directory name '{skill_root.name}'"
        )


class TestSkillBody:
    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_body_is_not_empty(self, skill_root: Path):
        _, body = _parse_frontmatter(_skill_md(skill_root).read_text(encoding="utf-8"))
        assert body.strip() != "", "SKILL.md body (after frontmatter) must not be empty"

    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_body_has_instructions(self, skill_root: Path):
        # Body should contain at least one heading or bullet point
        _, body = _parse_frontmatter(_skill_md(skill_root).read_text(encoding="utf-8"))
        assert any(line.startswith(("#", "-", "*", "1.")) for line in body.splitlines()), (
            "SKILL.md body should contain instructions (headings or list items)"
        )

    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_skill_does_not_reference_other_agent_skills(self, skill_root: Path):
        matches = _cross_skill_mentions(skill_root)
        assert not matches, "SKILL.md must not reference other agent skills:\n" + "\n".join(matches)


class TestSkillOptionalFiles:
    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_scripts_dir_exists(self, skill_root: Path):
        assert (skill_root / "scripts").is_dir()

    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_assets_dir_exists(self, skill_root: Path):
        assert (skill_root / "assets").is_dir()

    @pytest.mark.parametrize("skill_root", _skill_dirs(), ids=lambda path: path.name)
    def test_references_dir_exists(self, skill_root: Path):
        assert (skill_root / "references").is_dir()

    def test_optimize_runtime_exists(self):
        assert (SKILLS_DIR / "trainer-optimize" / "scripts" / "run_optimize.py").is_file()

    def test_election_runtime_exists(self):
        assert (SKILLS_DIR / "trainer-election" / "scripts" / "run_election.py").is_file()

    def test_research_runtime_exists(self):
        assert (SKILLS_DIR / "researcher-research" / "scripts" / "run_research.py").is_file()

    def test_synthesize_runtime_exists(self):
        assert (SKILLS_DIR / "trainer-synthesize" / "scripts" / "run_synthesize.py").is_file()

    def test_judge_rubric_runtime_exists(self):
        assert (SKILLS_DIR / "judge-rubric" / "scripts" / "render_rubric.py").is_file()


class TestOfficialEvalFixtures:
    def test_judge_rubric_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "judge-rubric" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "judge-rubric"
        assert len(payload["evals"]) >= 3
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()  # Lowercased for case-insensitive keyword checks.
        assert "pass-partial-fail" in manifest_text or "pass, partial, and fail" in manifest_text
        assert "tie-break" in manifest_text
        assert "confidence" in manifest_text

    def test_trainer_synthesize_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "trainer-synthesize" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "trainer-synthesize"
        assert len(payload["evals"]) >= 4
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        prompts = "\n".join(case["prompt"] for case in payload["evals"])
        assertions = "\n".join(
            assertion
            for case in payload["evals"]
            for assertion in case.get("assertions", [])
        )
        manifest_text = f"{prompts}\n{assertions}".lower()

        assert "train.jsonl" in manifest_text
        assert "val.jsonl" in manifest_text
        assert "placeholder" in manifest_text
        assert "scoring" in manifest_text
        assert "do not guess" in manifest_text or "instead of guessing" in manifest_text

    def test_trainer_election_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "trainer-election" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "trainer-election"
        assert len(payload["evals"]) >= 3
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        prompts = "\n".join(case["prompt"] for case in payload["evals"])
        assertions = "\n".join(
            assertion
            for case in payload["evals"]
            for assertion in case.get("assertions", [])
        )
        manifest_text = f"{prompts}\n{assertions}".lower()

        assert "benchmark.json" in manifest_text
        assert "incomplete eval coverage" in manifest_text
        assert "runs/" in manifest_text
        assert "baseline" in manifest_text
        assert "prompt artifact" in manifest_text

    def test_trainer_optimize_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "trainer-optimize" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "trainer-optimize"
        assert len(payload["evals"]) >= 2
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])

    def test_judge_outcome_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "judge-outcome" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "judge-outcome"
        assert len(payload["evals"]) >= 3
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()
        assert "final outputs" in manifest_text or "final-output" in manifest_text
        assert "confidence" in manifest_text
        assert "order bias" in manifest_text or "order-robust" in manifest_text

    def test_judge_trajectory_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "judge-trajectory" / "evals" / "evals.json"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "judge-trajectory"
        assert len(payload["evals"]) >= 3
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()
        assert "trajectory" in manifest_text or "trace" in manifest_text
        assert "runtime failures" in manifest_text or "runtime failure" in manifest_text
        assert "chain-of-thought" in manifest_text

    def test_engineer_code_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "engineer-code" / "evals" / "evals.json"
        assert manifest_path.is_file(), f"Expected engineer-code eval manifest at {manifest_path}"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "engineer-code"
        assert len(payload["evals"]) >= 4
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()
        assert "microsoft trace" in manifest_text or "trace-opt" in manifest_text
        assert "zero_feedback()" in manifest_text
        assert "@trace.bundle" in manifest_text
        assert "@trace.model" in manifest_text
        assert "runtime performance" in manifest_text

    def test_engineer_prompt_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "engineer-prompt" / "evals" / "evals.json"
        assert manifest_path.is_file(), f"Expected engineer-prompt eval manifest at {manifest_path}"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "engineer-prompt"
        assert len(payload["evals"]) >= 5
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()
        assert "structured output" in manifest_text
        assert "grounding" in manifest_text
        assert "retrieval freshness" in manifest_text
        assert "token-efficient" in manifest_text or "token budget" in manifest_text

    def test_learn_official_eval_manifest_exists(self):
        manifest_path = SKILLS_DIR / "learn" / "evals" / "evals.json"
        assert manifest_path.is_file(), f"Expected learn eval manifest at {manifest_path}"
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "learn"
        assert len(payload["evals"]) >= 3
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])
        assert all(case.get("assertions") for case in payload["evals"])

        manifest_text = json.dumps(payload).lower()
        assert "active conversation" in manifest_text or "conversation context" in manifest_text
        assert "correction" in manifest_text or "learning" in manifest_text
        assert "instructions" in manifest_text or "docs" in manifest_text
        assert ".agents/memory.md" in manifest_text or "agent memory" in manifest_text
        assert "agents.md" in manifest_text
        assert "custom agent" in manifest_text or ".github/agents" in manifest_text
        assert "hook" in manifest_text or ".github/hooks" in manifest_text

    def test_trainer_optimize_training_fixtures_use_local_trainer_workspace_contract(self):
        dataset_dir = SKILLS_DIR / "trainer-optimize" / "datasets"
        train_text = (dataset_dir / "train.jsonl").read_text(encoding="utf-8")
        val_text = (dataset_dir / "val.jsonl").read_text(encoding="utf-8")
        combined = f"{train_text}\n{val_text}"

        assert ".trainer-workspace/<prompt-name>/" in combined
        assert "<prompt-dir>/<prompt-name>-workspace/" not in combined

    def test_first_run_example_official_eval_manifest_exists(self):
        manifest_path = (
            Path(__file__).resolve().parent.parent
            / "examples"
            / "first-run"
            / "prompts"
            / "evals"
            / "evals.json"
        )
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert payload["skill_name"] == "classify-support-example"
        assert len(payload["evals"]) >= 2
        assert all("prompt" in case for case in payload["evals"])
        assert all("expected_output" in case for case in payload["evals"])

    def test_repo_does_not_ship_legacy_evals_directories(self):
        legacy_paths = list(Path(__file__).resolve().parent.parent.glob("**/.evals"))
        assert legacy_paths == []
