"""Tests for engineer-copilot-agent helper scripts."""
from __future__ import annotations

import importlib.util
import io
import json
import runpy
import sys
import textwrap
from contextlib import redirect_stdout
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "engineer-copilot-agent"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


discover_mod = _load_module(
    "discover_runtime_surface_engineer_copilot_agent",
    SKILL_DIR / "scripts" / "discover_runtime_surface.py",
)
validate_mod = _load_module(
    "validate_agent_engineer_copilot_agent",
    SKILL_DIR / "scripts" / "validate_agent.py",
)
analyze_mod = _load_module(
    "analyze_agent_body_engineer_copilot_agent",
    SKILL_DIR / "scripts" / "analyze_agent_body.py",
)


@pytest.fixture()
def demo_repo(tmp_path: Path) -> Path:
    (tmp_path / ".github" / "agents").mkdir(parents=True)
    (tmp_path / "skills" / "demo-skill" / "scripts").mkdir(parents=True)
    (tmp_path / "skills" / "demo-skill" / "references").mkdir(parents=True)
    (tmp_path / "skills" / "demo-skill" / "assets").mkdir(parents=True)
    (tmp_path / "skills" / "demo-skill" / "SKILL.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: demo-skill
            description: Improve demo tasks. Use this whenever the user needs demo help.
            ---

            # Demo skill
            - Do demo work.
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / ".github" / "agents" / "planner.agent.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: "planner"
            description: "Use when planning demo work with a small specialist roster."
            tools: [read, search, agent, agent-skills/*]
            agents: ["helper"]
            handoffs:
              - label: "Ask helper"
                agent: "helper"
            ---

            # Planner

            - Call `find_agent_skill` before `load_agent_skill`.
            - Call `load_agent_skill` before `run_agent_skill`.
            """
        ),
        encoding="utf-8",
    )
    (tmp_path / ".github" / "agents" / "helper.agent.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: "helper"
            description: "Use when handling the narrow helper task."
            tools: [read, edit]
            ---

            # Helper

            - Finish the assigned helper task.
            """
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_discover_surface_finds_agents_skills_and_tools(demo_repo: Path):
    payload = discover_mod.discover_surface(demo_repo)
    assert [agent["name"] for agent in payload["agents"]] == ["helper", "planner"]
    assert payload["skills"] == [{"name": "demo-skill", "path": "skills/demo-skill/SKILL.md"}]
    assert "agent-skills/*" in payload["tools"]
    assert "planner->helper" in payload["handoff_pairs"]


def test_discover_surface_skips_malformed_files_and_records_notes(demo_repo: Path):
    (demo_repo / ".github" / "agents" / "broken.agent.md").write_text(
        "---\nname: [oops\n---\n# Broken\n",
        encoding="utf-8",
    )
    (demo_repo / "skills" / "broken-skill").mkdir()
    (demo_repo / "skills" / "broken-skill" / "SKILL.md").write_text(
        "---\nname: broken-skill\ndescription: [oops\n---\n# Broken\n",
        encoding="utf-8",
    )

    payload = discover_mod.discover_surface(demo_repo)

    assert [agent["name"] for agent in payload["agents"]] == ["helper", "planner"]
    assert payload["skills"] == [{"name": "demo-skill", "path": "skills/demo-skill/SKILL.md"}]
    assert any("Skipped agent '.github/agents/broken.agent.md'" in note for note in payload["notes"])
    assert any("Skipped skill 'skills/broken-skill/SKILL.md'" in note for note in payload["notes"])


def test_validate_agent_accepts_known_repo_surface(demo_repo: Path):
    result = validate_mod.validate_agent(demo_repo / ".github" / "agents" / "planner.agent.md", repo_root=demo_repo)
    assert result.valid
    assert not [issue for issue in result.issues if issue.severity == "error"]


def test_validate_agent_flags_unknown_handoff_and_tool(demo_repo: Path):
    agent_path = demo_repo / ".github" / "agents" / "broken.agent.md"
    agent_path.write_text(
        textwrap.dedent(
            """\
            ---
            name: "broken"
            description: "Use when breaking the routing contract on purpose."
            tools: [read, imaginary-tool]
            agents: ["missing-agent"]
            handoffs:
              - label: "Bad handoff"
                agent: "missing-agent"
            ---

            # Broken

            - Call `run_agent_skill` without loading anything.
            """
        ),
        encoding="utf-8",
    )
    result = validate_mod.validate_agent(agent_path, repo_root=demo_repo)
    codes = {issue.code for issue in result.issues}
    assert "unknown-child-agent" in codes
    assert "unknown-handoff-agent" in codes
    assert "routing-missing-load-step" in codes
    assert not result.valid


def test_validate_agent_warns_when_repo_root_does_not_contain_agent(demo_repo: Path, tmp_path: Path):
    external_root = tmp_path.parent / f"{tmp_path.name}-outside"
    external_root.mkdir()
    external_agent = external_root / "external.agent.md"
    external_agent.write_text(
        textwrap.dedent(
            """\
            ---
            name: "external"
            description: "Use when validating an external agent."
            tools: [read]
            ---

            # External

            - Do the work directly.
            """
        ),
        encoding="utf-8",
    )

    result = validate_mod.validate_agent(external_agent, repo_root=demo_repo)

    assert result.valid
    assert any(issue.code == "surface-repo-root-mismatch" for issue in result.issues)


def test_validate_agent_reports_malformed_frontmatter(demo_repo: Path):
    agent_path = demo_repo / ".github" / "agents" / "malformed.agent.md"
    agent_path.write_text(
        "---\nname: [oops\n---\n# Broken\n",
        encoding="utf-8",
    )

    result = validate_mod.validate_agent(agent_path, repo_root=demo_repo)

    assert not result.valid
    assert any(issue.code == "frontmatter-parse-error" for issue in result.issues)


def test_analyze_agent_reports_deterministic_and_stale_surface_issues(demo_repo: Path):
    agent_path = demo_repo / ".github" / "agents" / "analyzer.agent.md"
    body = "\n".join(
        [
            "---",
            'name: "analyzer"',
            'description: "Use when analyzing a large contract."',
            "tools: [read, search]",
            "---",
            "# Analyzer",
            "",
            "- Check that the repo surface matches the contract.",
            "- For more detail, read the full standard before changing anything.",
            "- Ask `ghost-agent` for help if you get stuck.",
        ]
        + ["paragraph"] * 70
    )
    agent_path.write_text(body, encoding="utf-8")
    result = analyze_mod.analyze_agent(agent_path, repo_root=demo_repo)
    categories = {rec.category for rec in result.recommendations}
    assert "extract-script" in categories
    assert "extract-reference" in categories
    assert "verify-surface" in categories
    assert any(item["token"] == "ghost-agent" for item in result.stale_surface_mentions)


def test_analyze_agent_reports_missing_file():
    result = analyze_mod.analyze_agent("/tmp/does-not-exist.agent.md")

    assert result.recommendations
    assert result.recommendations[0].category == "structure"
    assert result.recommendations[0].severity == "high"


def test_analyze_agent_reports_malformed_frontmatter(demo_repo: Path):
    agent_path = demo_repo / ".github" / "agents" / "malformed.agent.md"
    agent_path.write_text(
        "---\nname: [oops\n---\n# Broken\n",
        encoding="utf-8",
    )

    result = analyze_mod.analyze_agent(agent_path, repo_root=demo_repo)

    assert result.recommendations
    assert result.recommendations[0].category == "structure"
    assert "Frontmatter error" in result.recommendations[0].description


def test_cli_entrypoints_emit_json(demo_repo: Path, monkeypatch: pytest.MonkeyPatch):
    stream = io.StringIO()
    monkeypatch.setattr(sys, "argv", ["discover_runtime_surface.py", "--repo-root", str(demo_repo), "--json"])
    with redirect_stdout(stream):
        with pytest.raises(SystemExit) as discover_exit:
            runpy.run_path(str(SKILL_DIR / "scripts" / "discover_runtime_surface.py"), run_name="__main__")
    assert discover_exit.value.code == 0
    payload = json.loads(stream.getvalue())
    assert payload["repo_root"] == str(demo_repo.resolve())

    stream = io.StringIO()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "validate_agent.py",
            str(demo_repo / ".github" / "agents" / "planner.agent.md"),
            "--repo-root",
            str(demo_repo),
            "--json",
        ],
    )
    with redirect_stdout(stream):
        with pytest.raises(SystemExit) as validate_exit:
            runpy.run_path(str(SKILL_DIR / "scripts" / "validate_agent.py"), run_name="__main__")
    assert validate_exit.value.code == 0
    payload = json.loads(stream.getvalue())
    assert payload["valid"] is True

    stream = io.StringIO()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "analyze_agent_body.py",
            str(demo_repo / ".github" / "agents" / "planner.agent.md"),
            "--repo-root",
            str(demo_repo),
            "--json",
        ],
    )
    with redirect_stdout(stream):
        with pytest.raises(SystemExit) as analyze_exit:
            runpy.run_path(str(SKILL_DIR / "scripts" / "analyze_agent_body.py"), run_name="__main__")
    assert analyze_exit.value.code == 0
    payload = json.loads(stream.getvalue())
    assert payload["body_lines"] > 0


def test_skill_assets_exist():
    assert (SKILL_DIR / "evals" / "evals.json").is_file()
    assert (SKILL_DIR / "datasets" / "train.jsonl").is_file()
    assert (SKILL_DIR / "datasets" / "val.jsonl").is_file()
