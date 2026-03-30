from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "skills" / "judge-rubric" / "scripts" / "render_rubric.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "judge_rubric"


def _load_module():
    spec = importlib.util.spec_from_file_location("judge_rubric_render", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("judge_rubric_render", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def judge_rubric_module():
    return _load_module()


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_validate_contract_returns_summary_for_valid_fixture(judge_rubric_module):
    contract = _read_json(FIXTURES_DIR / "valid_contract.json")

    summary = judge_rubric_module.validate_contract(contract)

    assert summary["valid"] is True
    assert summary["dimension_count"] == 3
    assert summary["evidence_mode"] == "hybrid"
    assert summary["has_aggregation_rules"] is True
    assert summary["has_robustness_checks"] is True
    assert summary["has_blockers"] is True


def test_render_markdown_uses_valid_fixture(judge_rubric_module):
    contract = _read_json(FIXTURES_DIR / "valid_contract.json")

    markdown = judge_rubric_module.render_markdown(contract)

    assert "# Rubric Package" in markdown
    assert "## Locked Rubric" in markdown
    assert "| Correctness |" in markdown
    assert "## Robustness Checks" in markdown


def test_validate_contract_rejects_missing_dimension_field(judge_rubric_module):
    contract = _read_json(FIXTURES_DIR / "invalid_missing_dimension_field.json")

    with pytest.raises(ValueError, match="allowed_evidence"):
        judge_rubric_module.validate_contract(contract)


def test_validate_only_cli_emits_json_summary(tmp_path: Path):
    output = __import__("subprocess").run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--input-file",
            str(FIXTURES_DIR / "valid_contract.json"),
            "--validate-only",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(output.stdout)
    assert payload["valid"] is True
    assert payload["dimension_count"] == 3


def test_validate_only_cli_reports_invalid_contract():
    output = __import__("subprocess").run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--input-file",
            str(FIXTURES_DIR / "invalid_missing_dimension_field.json"),
            "--validate-only",
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert output.returncode == 1
    assert "allowed_evidence" in output.stderr