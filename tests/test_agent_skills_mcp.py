from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import types

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "tools" / "agent-skills-mcp" / "agent_skills_mcp.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("agent_skills_mcp", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("agent_skills_mcp", module)
    spec.loader.exec_module(module)
    return module


def _write_skill(root: Path, name: str, *, description: str = "skill description", version: str = "0.1.0", body: str = "# Body\n- step\n", extra_files: dict[str, str | bytes] | None = None) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    header = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "metadata:",
        f"  version: \"{version}\"",
    ]
    header.extend(["---", "", body])
    (skill_dir / "SKILL.md").write_text("\n".join(header), encoding="utf-8")
    if extra_files:
        for rel_path, content in extra_files.items():
            file_path = skill_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                file_path.write_text(content, encoding="utf-8")
    return skill_dir


def _write_skill_with_frontmatter(root: Path, name: str, *, frontmatter_lines: list[str], body: str = "# Body\n- step\n", extra_files: dict[str, str | bytes] | None = None) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("\n".join(["---", *frontmatter_lines, "---", "", body]), encoding="utf-8")
    if extra_files:
        for rel_path, content in extra_files.items():
            file_path = skill_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                file_path.write_bytes(content)
            else:
                file_path.write_text(content, encoding="utf-8")
    return skill_dir


def _make_skill_record(agent_skills_module, *, name: str = "skill", dir_path: str = "/tmp/skill", description: str = "desc", body: str = "body", source_root: str = "skills", assets: dict[str, str] | None = None, version_key: tuple[int, ...] = (), freshness_key: tuple[object, ...] = (), identity_key: tuple[object, ...] = ()):
    return agent_skills_module.SkillRecord(
        name=name,
        description=description,
        dir=dir_path,
        skill_md=f"{dir_path}/SKILL.md",
        source_root=source_root,
        body=body,
        assets=assets or {},
        frontmatter={},
        model_invocation_disabled=False,
        version_key=version_key,
        freshness_key=freshness_key,
        identity_key=identity_key,
    )


@pytest.fixture
def agent_skills_module():
    return _load_module()


def test_candidate_skill_roots_preserve_supported_order(tmp_path, monkeypatch, agent_skills_module):
    (tmp_path / ".agents" / "skills").mkdir(parents=True)
    (tmp_path / ".github" / "skills").mkdir(parents=True)
    (tmp_path / "skills").mkdir()
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    roots = agent_skills_module._candidate_skill_roots()

    assert [label for label, _ in roots] == ["skills", ".agents/skills", ".github/skills"]


def test_repository_root_defaults_to_repo_root_when_env_is_unset(monkeypatch, agent_skills_module):
    monkeypatch.delenv("AGENT_SKILLS_REPO_ROOT", raising=False)

    assert agent_skills_module._repository_root() == REPO_ROOT


def test_candidate_skill_roots_override_filters_blank_missing_and_external_paths(tmp_path, monkeypatch, agent_skills_module):
    (tmp_path / "skills").mkdir()
    github_root = tmp_path / ".github" / "skills"
    github_root.mkdir(parents=True)
    outside_root = tmp_path.parent / "external-roots"
    outside_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv(
        "AGENT_SKILLS_ROOTS",
        os.pathsep.join(["", "skills", str(github_root), str(outside_root), "missing-root"]),
    )

    roots = agent_skills_module._candidate_skill_roots()

    assert [label for label, _ in roots] == ["skills", ".github/skills"]


def test_candidate_skill_roots_falls_back_to_absolute_label_when_relative_to_raises(tmp_path, monkeypatch, agent_skills_module):
    github_root = tmp_path / ".github" / "skills"
    github_root.mkdir(parents=True)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("AGENT_SKILLS_ROOTS", str(github_root))
    original_relative_to = agent_skills_module.Path.relative_to
    call_count = {"count": 0}

    def flaky_relative_to(self, *other):
        if self == github_root.resolve():
            call_count["count"] += 1
            if call_count["count"] == 2:
                raise ValueError("forced label fallback")
        return original_relative_to(self, *other)

    monkeypatch.setattr(agent_skills_module.Path, "relative_to", flaky_relative_to)

    roots = agent_skills_module._candidate_skill_roots()

    assert roots == [(github_root.resolve().as_posix(), github_root.resolve())]


def test_extract_frontmatter_returns_body_when_text_has_no_frontmatter(agent_skills_module):
    frontmatter, body = agent_skills_module._extract_frontmatter("plain text\n")

    assert frontmatter == {}
    assert body == "plain text"


def test_extract_frontmatter_returns_body_when_opening_line_is_not_exact_delimiter(agent_skills_module):
    frontmatter, body = agent_skills_module._extract_frontmatter("---not-frontmatter\nbody\n")

    assert frontmatter == {}
    assert body == "---not-frontmatter\nbody"


def test_extract_frontmatter_requires_closing_delimiter(agent_skills_module):
    with pytest.raises(agent_skills_module.SkillError, match="missing a closing"):
        agent_skills_module._extract_frontmatter("---\nname: broken\nbody")


def test_extract_frontmatter_rejects_malformed_yaml(agent_skills_module):
    with pytest.raises(agent_skills_module.SkillError, match="Malformed SKILL.md frontmatter"):
        agent_skills_module._extract_frontmatter("---\nname: [broken\n---\nbody")


def test_extract_frontmatter_requires_mapping(agent_skills_module):
    with pytest.raises(agent_skills_module.SkillError, match="must be a YAML mapping"):
        agent_skills_module._extract_frontmatter("---\n- one\n- two\n---\nbody")


def test_version_key_supports_top_level_and_missing_metadata(agent_skills_module):
    assert agent_skills_module._version_key({"version": "2.4.6"}) == (2, 4, 6)
    assert agent_skills_module._version_key({"metadata": "invalid"}) == ()
    assert agent_skills_module._version_key({"metadata": {}}) == ()


def test_model_invocation_disabled_accepts_top_level_and_metadata_flags(agent_skills_module):
    assert agent_skills_module._model_invocation_disabled({"disable-model-invocation": True}) is True
    assert agent_skills_module._model_invocation_disabled({"metadata": {"disable_model_invocation": "yes"}}) is True
    assert agent_skills_module._model_invocation_disabled({"metadata": {"disable-model-invocation": "false"}}) is False


def test_is_truthy_flag_handles_numeric_and_unknown_values(agent_skills_module):
    assert agent_skills_module._is_truthy_flag(1) is True
    assert agent_skills_module._is_truthy_flag(0) is False
    assert agent_skills_module._is_truthy_flag(["true"]) is False


def test_iter_skill_files_skips_unresolvable_and_external_paths(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    valid_file = skill_dir / "valid.txt"
    valid_file.write_text("ok", encoding="utf-8")
    failing_file = skill_dir / "failing.txt"
    failing_file.write_text("bad", encoding="utf-8")
    outside_file = tmp_path.parent / "outside.txt"
    outside_file.write_text("outside", encoding="utf-8")
    (skill_dir / "external.txt").symlink_to(outside_file)
    original_resolve = agent_skills_module.Path.resolve

    def fake_resolve(self, strict=False):
        if self == failing_file:
            raise OSError("cannot resolve")
        return original_resolve(self, strict=strict)

    monkeypatch.setattr(agent_skills_module.Path, "resolve", fake_resolve)

    files = agent_skills_module._iter_skill_files(skill_dir)

    assert files == [valid_file]


def test_load_text_assets_skips_unreadable_and_binary_text_extensions(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(
        tmp_path,
        "asset-filter-skill",
        extra_files={
            "assets/readme.md": "visible",
            "assets/binary.txt": b"\xff\xfe",
            "assets/failing.sh": "echo nope\n",
        },
    )
    failing_file = skill_dir / "assets" / "failing.sh"
    original_read_text = agent_skills_module.Path.read_text

    def fake_read_text(self, *args, **kwargs):
        if self == failing_file:
            raise OSError("cannot read")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(agent_skills_module.Path, "read_text", fake_read_text)

    assets = agent_skills_module._load_text_assets(skill_dir)

    assert assets == {"assets/readme.md": "visible"}


def test_iter_script_files_only_returns_runnable_python_scripts(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(
        tmp_path,
        "script-skill",
        extra_files={
            "scripts/run.py": "print('run')\n",
            "scripts/tool.sh": "echo no\n",
            "scripts/__pycache__/cached.py": "print('ignore')\n",
            "notes.py": "print('ignore')\n",
        },
    )

    script_files = agent_skills_module._iter_script_files(skill_dir)

    assert script_files == [skill_dir / "scripts" / "run.py"]


def test_skill_identity_and_freshness_skip_stat_failures(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(tmp_path, "stat-skill", extra_files={"assets/ok.txt": "ok"})
    good_file = skill_dir / "assets" / "ok.txt"

    class BrokenPath:
        def stat(self):
            raise OSError("cannot stat")

        def relative_to(self, _other):
            return Path("assets/failing.txt")

    monkeypatch.setattr(agent_skills_module, "_iter_skill_files", lambda _skill_dir: [good_file, BrokenPath()])

    identity = agent_skills_module._skill_identity_key(skill_dir)
    freshness = agent_skills_module._freshness_key(skill_dir, {"metadata": {"version": "1.2.3"}}, 2)

    assert identity == (("assets/ok.txt", good_file.stat().st_dev, good_file.stat().st_ino, good_file.stat().st_size),)
    assert freshness[0] == (1, 2, 3)
    assert freshness[2] == 1


def test_read_skill_dir_requires_skill_md(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = tmp_path / "missing-skill-md"
    skill_dir.mkdir()
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="SKILL.md is missing"):
        agent_skills_module._read_skill_dir(skill_dir, "skills", 0)


def test_read_skill_dir_falls_back_to_directory_name_when_frontmatter_name_is_blank(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = tmp_path / "skills" / "fallback-name"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: ''\ndescription: hello\n---\nbody\n", encoding="utf-8")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._read_skill_dir(skill_dir, "skills", 0)

    assert skill.name == "fallback-name"
    assert skill.description == "hello"


def test_better_skill_prefers_existing_when_candidate_is_not_newer(agent_skills_module):
    existing = _make_skill_record(
        agent_skills_module,
        dir_path="/repo/alpha",
        freshness_key=((1,), 10, 2, 0, "/repo/alpha"),
        identity_key=(("a", 1, 1, 1),),
    )
    candidate = _make_skill_record(
        agent_skills_module,
        dir_path="/repo/beta",
        freshness_key=((1,), 9, 2, 0, "/repo/beta"),
        identity_key=(("b", 1, 2, 1),),
    )

    assert agent_skills_module._better_skill(existing, candidate) is existing


def test_better_skill_uses_lexicographically_earlier_path_for_identical_skills(agent_skills_module):
    existing = _make_skill_record(
        agent_skills_module,
        dir_path="/repo/zeta",
        identity_key=(("same", 1, 1, 1),),
    )
    candidate = _make_skill_record(
        agent_skills_module,
        dir_path="/repo/alpha",
        identity_key=(("same", 1, 1, 1),),
    )

    assert agent_skills_module._better_skill(existing, candidate) is candidate


def test_all_skills_skips_non_directories_and_invalid_skill_dirs(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    (skills_root / "README.txt").write_text("not a skill", encoding="utf-8")
    (skills_root / "broken-skill").mkdir()
    _write_skill(skills_root, "valid-skill")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    warnings: list[tuple[object, ...]] = []

    def fake_warning(*args):
        warnings.append(args)

    monkeypatch.setattr(agent_skills_module.LOGGER, "warning", fake_warning)

    skills = agent_skills_module._all_skills()

    assert [skill.name for skill in skills] == ["valid-skill"]
    assert warnings
    assert warnings[0][0] == "Skipping invalid skill at %s: %s"


def test_find_skill_by_name_skips_non_matching_skills_before_match(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(skills_root, "alpha")
    target_dir = _write_skill(skills_root, "beta")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("beta")

    assert skill.dir == target_dir.resolve().as_posix()


def test_find_skill_by_name_reports_missing_skill_md_for_named_directory(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    named_dir = skills_root / "named-skill"
    named_dir.mkdir(parents=True)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="SKILL.md is missing"):
        agent_skills_module._find_skill_by_name("named-skill")


def test_find_skill_by_name_reports_invalid_named_directory(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    skill_dir = skills_root / "invalid-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: [broken\n---\nbody\n", encoding="utf-8")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="Skill 'invalid-skill' is invalid"):
        agent_skills_module._find_skill_by_name("invalid-skill")


def test_find_skill_by_name_reports_missing_skill(tmp_path, monkeypatch, agent_skills_module):
    (tmp_path / "skills").mkdir()
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="was not found"):
        agent_skills_module._find_skill_by_name("missing")


def test_score_skill_ignores_cwd_when_no_cwd_tokens(agent_skills_module):
    skill = _make_skill_record(
        agent_skills_module,
        name="trainer-optimize",
        description="improve prompts",
        body="prompt tuning guide",
        dir_path="/repo/skills/trainer-optimize",
    )

    score = agent_skills_module._score_skill(skill, {"trainer", "optimize", "prompt"}, set())

    assert score == 9


def test_resolve_entrypoint_requires_at_least_one_scripts_python_file(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(tmp_path / "skills", "no-script-skill")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    skill = agent_skills_module._read_skill_dir(skill_dir, "skills", 0)

    with pytest.raises(agent_skills_module.SkillError, match="has no runnable Python scripts"):
        agent_skills_module._resolve_entrypoint(skill)


def test_resolve_script_path_rejects_escape_paths(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(tmp_path / "skills", "escape-skill", extra_files={"scripts/run.py": "print('ok')\n"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    skill = agent_skills_module._read_skill_dir(skill_dir, "skills", 0)

    with pytest.raises(agent_skills_module.SkillError, match="escapes skill"):
        agent_skills_module._resolve_script_path(skill, "../outside.py")


def test_resolve_script_path_requires_existing_python_file(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(tmp_path / "skills", "missing-script-skill", extra_files={"scripts/run.py": "print('ok')\n"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    skill = agent_skills_module._read_skill_dir(skill_dir, "skills", 0)

    with pytest.raises(agent_skills_module.SkillError, match="was not found as a Python file"):
        agent_skills_module._resolve_script_path(skill, "scripts/missing.sh")


def test_resolve_script_path_rejects_pycache_files(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(
        tmp_path / "skills",
        "pycache-skill",
        extra_files={"scripts/__pycache__/run.py": "print('no')\n"},
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    skill = agent_skills_module._read_skill_dir(skill_dir, "skills", 0)

    with pytest.raises(agent_skills_module.SkillError, match="is not runnable"):
        agent_skills_module._resolve_script_path(skill, "scripts/__pycache__/run.py")


def test_normalize_argv_rejects_non_string_lists(agent_skills_module):
    with pytest.raises(agent_skills_module.SkillError, match="argv must be a JSON array of strings"):
        agent_skills_module._normalize_argv(["ok", 1])


def test_resolve_python_executable_prefers_override(agent_skills_module, monkeypatch):
    monkeypatch.setenv("AGENT_SKILLS_PYTHON", "/custom/python")

    assert agent_skills_module._resolve_python_executable() == "/custom/python"


def test_resolve_python_executable_prefers_repo_venv_when_present(tmp_path, monkeypatch, agent_skills_module):
    python_path = tmp_path / ".venv" / "bin" / "python"
    python_path.parent.mkdir(parents=True)
    python_path.write_text("#!/usr/bin/env python\n", encoding="utf-8")
    monkeypatch.delenv("AGENT_SKILLS_PYTHON", raising=False)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(agent_skills_module.sys, "executable", "/fallback/python")

    assert agent_skills_module._resolve_python_executable() == str(python_path)


def test_resolve_python_executable_falls_back_to_current_interpreter(tmp_path, monkeypatch, agent_skills_module):
    monkeypatch.delenv("AGENT_SKILLS_PYTHON", raising=False)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    monkeypatch.setattr(agent_skills_module.sys, "executable", "/fallback/python")

    assert agent_skills_module._resolve_python_executable() == "/fallback/python"


def test_skill_directory_tree_skips_the_root_entry(tmp_path, monkeypatch, agent_skills_module):
    skill_dir = _write_skill(tmp_path, "tree-skill")
    original_rglob = agent_skills_module.Path.rglob

    def fake_rglob(self, pattern):
        if self == skill_dir:
            return [skill_dir, skill_dir / "SKILL.md"]
        return original_rglob(self, pattern)

    monkeypatch.setattr(agent_skills_module.Path, "rglob", fake_rglob)

    tree = agent_skills_module._skill_directory_tree(skill_dir)

    assert tree.count("SKILL.md") == 1
    assert tree.splitlines()[0].startswith("Skill Directory:")


def test_read_skill_resource_rejects_escape_and_missing_paths(tmp_path, monkeypatch, agent_skills_module):
    _write_skill(tmp_path / "skills", "resource-guard-skill", extra_files={"nested/info.txt": "hello"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="escapes skill directory"):
        agent_skills_module.read_skill_resource("resource-guard-skill", "../secret.txt")

    with pytest.raises(agent_skills_module.SkillError, match="was not found"):
        agent_skills_module.read_skill_resource("resource-guard-skill", "nested/missing.txt")


def test_read_skill_resource_returns_binary_for_non_utf8_files(tmp_path, monkeypatch, agent_skills_module):
    _write_skill(tmp_path / "skills", "binary-resource-skill", extra_files={"assets/raw.bin": b"\xff\xfe"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    resource = agent_skills_module.read_skill_resource("binary-resource-skill", "assets/raw.bin")

    assert resource == b"\xff\xfe"


def test_find_agent_skill_requires_at_least_one_valid_skill_root(tmp_path, monkeypatch, agent_skills_module):
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="No supported skill roots were found"):
        agent_skills_module.find_agent_skill("anything")


def test_load_agent_skill_shows_none_when_no_assets_exist(tmp_path, monkeypatch, agent_skills_module):
    _write_skill(tmp_path / "skills", "assetless-skill")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    payload = agent_skills_module.load_agent_skill("assetless-skill")

    assert "Bundled Assets:\n<none>" in payload


def test_run_agent_skill_returns_stderr_and_exit_code(tmp_path, monkeypatch, agent_skills_module):
    _write_skill(
        tmp_path / "skills",
        "stderr-skill",
        extra_files={
            "scripts/run.py": (
                "from __future__ import annotations\n"
                "import sys\n"
                "sys.stderr.write('bad\\n')\n"
                "raise SystemExit(3)\n"
            )
        },
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    result = agent_skills_module.run_agent_skill("stderr-skill")

    assert result == {"exit_code": 3, "stdout": "", "stderr": "bad\n"}


def test_run_agent_skill_uses_resolved_python_executable(tmp_path, monkeypatch, agent_skills_module):
    _write_skill(
        tmp_path / "skills",
        "python-select-skill",
        extra_files={"scripts/run.py": "print('ok')\n"},
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))
    calls: dict[str, object] = {}

    def fake_run(command, **kwargs):
        calls["command"] = command
        calls["kwargs"] = kwargs
        return types.SimpleNamespace(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(agent_skills_module, "_resolve_python_executable", lambda: "/chosen/python")
    monkeypatch.setattr(agent_skills_module.subprocess, "run", fake_run)

    result = agent_skills_module.run_agent_skill("python-select-skill")

    assert result == {"exit_code": 0, "stdout": "ok\n", "stderr": ""}
    assert calls["command"][0] == "/chosen/python"


def test_build_mcp_registers_tools_and_resources(monkeypatch, agent_skills_module):
    class FakeFastMCP:
        def __init__(self, name):
            self.name = name
            self.tools = {}
            self.resources = {}

        def tool(self, *, name):
            def decorator(func):
                self.tools[name] = func
                return func

            return decorator

        def resource(self, uri):
            def decorator(func):
                self.resources[uri] = func
                return func

            return decorator

    fake_module = types.ModuleType("mcp.server.fastmcp")
    fake_module.FastMCP = FakeFastMCP
    monkeypatch.setitem(sys.modules, "mcp.server.fastmcp", fake_module)
    monkeypatch.setattr(agent_skills_module, "find_agent_skill", lambda query, cwd="": [{"name": query, "cwd": cwd}])
    monkeypatch.setattr(agent_skills_module, "load_agent_skill", lambda name: f"loaded:{name}")
    monkeypatch.setattr(
        agent_skills_module,
        "run_agent_skill",
        lambda name, script_path="", argv=None: {"name": name, "script_path": script_path, "argv": argv or []},
    )

    def fake_read_skill_resource(name, relative_path=""):
        if not relative_path:
            return b"directory bytes"
        return f"file:{name}:{relative_path}"

    monkeypatch.setattr(agent_skills_module, "read_skill_resource", fake_read_skill_resource)

    mcp = agent_skills_module.build_mcp()

    assert mcp.name == "agent-skills"
    assert sorted(mcp.tools) == ["find_agent_skill", "load_agent_skill", "run_agent_skill"]
    assert sorted(mcp.resources) == ["skill-file://{name}/{encoded_path}", "skill://{name}"]
    assert mcp.tools["find_agent_skill"]("query", cwd="here") == [{"name": "query", "cwd": "here"}]
    assert mcp.tools["load_agent_skill"]("skill") == "loaded:skill"
    assert mcp.tools["run_agent_skill"]("skill", script_path="scripts/run.py", argv=["--x"]) == {
        "name": "skill",
        "script_path": "scripts/run.py",
        "argv": ["--x"],
    }
    assert mcp.resources["skill://{name}"]("skill") == "directory bytes"
    assert mcp.resources["skill-file://{name}/{encoded_path}"]("skill", "nested%2Ffile.txt") == "file:skill:nested%2Ffile.txt"


def test_all_skills_hotload_skill_edits(tmp_path, monkeypatch, agent_skills_module):
    skill_root = tmp_path / "skills"
    _write_skill(skill_root, "fresh-skill", description="first pass")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    first = agent_skills_module._find_skill_by_name("fresh-skill")
    _write_skill(skill_root, "fresh-skill", description="second pass")
    second = agent_skills_module._find_skill_by_name("fresh-skill")

    assert first.description == "first pass"
    assert second.description == "second pass"


def test_duplicate_name_prefers_higher_version_then_newer_files(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    github_root = tmp_path / ".github" / "skills"
    older = _write_skill(skills_root, "shared-skill", description="older", version="0.1.0")
    newer = _write_skill(github_root, "shared-skill", description="newer", version="0.2.0")
    os.utime(older / "SKILL.md", ns=(1, 1))
    os.utime(newer / "SKILL.md", ns=(2, 2))
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("shared-skill")

    assert skill.description == "newer"
    assert skill.dir == newer.resolve().as_posix()


def test_symlink_duplicate_uses_origin_skill(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    github_root = tmp_path / ".github" / "skills"
    origin = _write_skill(skills_root, "linked-skill", description="origin skill")
    github_root.mkdir(parents=True, exist_ok=True)
    (github_root / "linked-skill").symlink_to(origin, target_is_directory=True)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("linked-skill")

    assert skill.dir == origin.resolve().as_posix()
    assert skill.source_root == "skills"


def test_out_of_repo_symlinked_skill_is_ignored(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    outside_root = tmp_path.parent / "external-skill-home"
    outside_root.mkdir(parents=True, exist_ok=True)
    origin = _write_skill(outside_root, "outside-skill", description="external")
    skills_root.mkdir(parents=True, exist_ok=True)
    (skills_root / "outside-skill").symlink_to(origin, target_is_directory=True)
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError):
        agent_skills_module._find_skill_by_name("outside-skill")


def test_find_agent_skill_scores_best_match_first(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(skills_root, "trainer-optimize", description="Improve a markdown prompt file")
    _write_skill(skills_root, "researcher-research", description="Research public datasets")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    matches = agent_skills_module.find_agent_skill("optimize a markdown prompt", cwd="/repo/prompts")

    assert matches[0]["name"] == "trainer-optimize"
    assert matches[0]["score"] >= matches[1]["score"]


def test_find_agent_skill_hides_model_invocation_disabled_skills(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill_with_frontmatter(
        skills_root,
        "hidden-skill",
        frontmatter_lines=[
            "name: hidden-skill",
            "description: Hidden from model invocation",
            "disable-model-invocation: true",
        ],
    )
    _write_skill(skills_root, "visible-skill", description="Visible skill")
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    matches = agent_skills_module.find_agent_skill("skill")

    assert [match["name"] for match in matches] == ["visible-skill"]


def test_public_lookup_uses_visible_duplicate_when_hidden_duplicate_exists(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    github_root = tmp_path / ".github" / "skills"
    _write_skill(skills_root, "shared-skill", description="visible", version="0.1.0")
    _write_skill_with_frontmatter(
        github_root,
        "shared-skill",
        frontmatter_lines=[
            "name: shared-skill",
            "description: hidden",
            "metadata:",
            "  version: \"9.9.9\"",
            "  disable-model-invocation: true",
        ],
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("shared-skill")

    assert skill.description == "visible"


def test_load_and_run_agent_skill_reject_model_invocation_disabled_skills(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill_with_frontmatter(
        skills_root,
        "hidden-runner",
        frontmatter_lines=[
            "name: hidden-runner",
            "description: Hidden from model invocation",
            "metadata:",
            "  disable-model-invocation: true",
        ],
        extra_files={"scripts/run.py": "print('hidden')\n"},
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError, match="was not found"):
        agent_skills_module.load_agent_skill("hidden-runner")

    with pytest.raises(agent_skills_module.SkillError, match="was not found"):
        agent_skills_module.run_agent_skill("hidden-runner")

    with pytest.raises(agent_skills_module.SkillError, match="was not found"):
        agent_skills_module.read_skill_resource("hidden-runner")


def test_internal_lookup_can_include_model_invocation_disabled_skills(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill_with_frontmatter(
        skills_root,
        "hidden-direct",
        frontmatter_lines=[
            "name: hidden-direct",
            "description: Hidden from model invocation",
            "disable_model_invocation: true",
        ],
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("hidden-direct", include_model_invocation_disabled=True)

    assert skill.name == "hidden-direct"
    assert skill.model_invocation_disabled is True


def test_find_skill_by_name_can_resolve_exact_directory_name_when_frontmatter_name_differs(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill_with_frontmatter(
        skills_root,
        "directory-name",
        frontmatter_lines=[
            "name: canonical-name",
            "description: Uses a different frontmatter name",
        ],
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    skill = agent_skills_module._find_skill_by_name("directory-name")

    assert skill.name == "canonical-name"


def test_load_agent_skill_returns_body_and_text_assets(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(
        skills_root,
        "asset-skill",
        extra_files={
            "assets/example.md": "example text",
            "assets/raw.bin": b"\x00\x01",
            "notes.txt": "plain text",
        },
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    payload = agent_skills_module.load_agent_skill("asset-skill")

    assert "Name: asset-skill" in payload
    assert "--- assets/example.md ---" in payload
    assert "example text" in payload
    assert "--- notes.txt ---" in payload
    assert "raw.bin" not in payload


def test_run_agent_skill_executes_existing_scripts_file(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(
        skills_root,
        "runner-skill",
        extra_files={
            "scripts/run_skill.py": (
                "from __future__ import annotations\n"
                "import argparse\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--flag')\n"
                "args = parser.parse_args()\n"
                "print(args.flag)\n"
            )
        },
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    result = agent_skills_module.run_agent_skill(
        "runner-skill",
        script_path="scripts/run_skill.py",
        argv=["--flag", "ok"],
    )

    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "ok"


def test_run_agent_skill_rejects_script_outside_scripts_dir(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(skills_root, "unsafe-skill", extra_files={"tool.py": "print('bad')\n"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError):
        agent_skills_module.run_agent_skill("unsafe-skill", script_path="tool.py")


def test_run_agent_skill_uses_single_scripts_file_by_default(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(
        skills_root,
        "single-script-skill",
        extra_files={
            "scripts/run_skill.py": (
                "from __future__ import annotations\n"
                "print('single')\n"
            )
        },
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    result = agent_skills_module.run_agent_skill("single-script-skill")

    assert result["exit_code"] == 0
    assert result["stdout"].strip() == "single"


def test_run_agent_skill_requires_explicit_script_when_multiple_exist(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(
        skills_root,
        "multi-script-skill",
        extra_files={
            "scripts/a.py": "print('a')\n",
            "scripts/b.py": "print('b')\n",
        },
    )
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    with pytest.raises(agent_skills_module.SkillError):
        agent_skills_module.run_agent_skill("multi-script-skill")


def test_read_skill_resource_exposes_directory_and_nested_files(tmp_path, monkeypatch, agent_skills_module):
    skills_root = tmp_path / "skills"
    _write_skill(skills_root, "resource-skill", extra_files={"nested/info.txt": "hello"})
    monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(tmp_path))

    directory_view = agent_skills_module.read_skill_resource("resource-skill")
    nested_file = agent_skills_module.read_skill_resource("resource-skill", "nested/info.txt")

    assert "nested/info.txt" in directory_view
    assert nested_file == "hello"


def test_repo_skills_are_not_mutated_with_runner_wrappers():
    assert not (REPO_ROOT / "skills" / "trainer-optimize" / "run.py").exists()
    assert not (REPO_ROOT / "skills" / "trainer-election" / "run.py").exists()
    assert not (REPO_ROOT / "skills" / "researcher-research" / "run.py").exists()
    assert not (REPO_ROOT / "skills" / "trainer-synthesize" / "run.py").exists()


def test_vscode_mcp_config_contains_agent_skills_server():
    config = json.loads((REPO_ROOT / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
    server = config["servers"]["agent-skills"]

    assert server["type"] == "stdio"
    assert server["command"].endswith("/.venv/bin/python")
    assert any(arg.endswith("tools/agent-skills-mcp/server.py") for arg in server["args"])


def test_devcontainer_post_start_syncs_agent_skills_project():
    text = (REPO_ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8")
    script = (REPO_ROOT / ".devcontainer" / "post-start.sh").read_text(encoding="utf-8")

    assert "postStartCommand" in text
    assert ".devcontainer/post-start.sh" in text
    assert "tools/agent-skills-mcp" in script
    assert "uv sync --directory" in script


def test_copilot_setup_workflow_reuses_devcontainer_bootstrap():
    workflow_text = (REPO_ROOT / ".github" / "workflows" / "copilot-setup-steps.yml").read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)
    workflow_on = workflow.get("on", workflow.get(True))

    assert "workflow_dispatch" in workflow_on
    job = workflow["jobs"]["copilot-setup-steps"]
    assert job["permissions"]["contents"] == "read"

    steps = job["steps"]
    assert any(step.get("uses") == "actions/checkout@v5" for step in steps)
    assert any(".devcontainer/post-start.sh" in step.get("run", "") for step in steps)
    assert any("gh aw --help" in step.get("run", "") for step in steps)
