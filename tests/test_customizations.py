from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_SKILLS_MODULE_PATH = REPO_ROOT / "tools" / "agent-skills-mcp" / "agent_skills_mcp.py"
AGENT_SKILLS_UVX_BOOTSTRAP = (
    "python -m pip install --quiet --disable-pip-version-check --no-cache-dir uv "
    "&& exec uvx --from "
    "git+https://github.com/Tyler-R-Kendrick/copilot-apo#subdirectory=tools/agent-skills-mcp "
    "agent-skills-mcp"
)
SKILL_LINKS_MODULE_PATH = REPO_ROOT / ".github" / "hooks" / "sync-skill-links.py"
PLUGIN_LINKS_MODULE_PATH = REPO_ROOT / ".github" / "hooks" / "sync-plugin-links.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _markdown_section(text: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = text.index(marker) + len(marker)
    remainder = text[start:]
    next_heading = remainder.find("\n## ")
    if next_heading == -1:
        return remainder.strip()
    return remainder[:next_heading].strip()


def _markdown_bullets(text: str) -> list[str]:
    return [line[2:].strip() for line in text.splitlines() if line.startswith("- ")]


def _markdown_numbered_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        match = re.match(r"\d+\.\s+(.*)", line.strip())
        if match:
            items.append(match.group(1).strip())
    return items


def _gh_aw_glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Mirror gh-aw's glob_pattern_helpers.cjs path-mode glob behavior."""
    escaped = pattern.replace("\\", "\\\\")
    escaped = escaped.replace(".", r"\.")
    escaped = re.sub(r"([+?^${}()|\[\]])", r"\\\1", escaped)
    escaped = escaped.replace("**", "<!DOUBLESTAR>")
    escaped = escaped.replace("*", "[^/]*")
    escaped = escaped.replace("<!DOUBLESTAR>", ".*")
    return re.compile(f"^{escaped}$")


def _matches_gh_aw_allowed_files(path: str, patterns: list[str]) -> bool:
    return any(_gh_aw_glob_to_regex(pattern).match(path) for pattern in patterns)


def _load_agent_skills_module():
    spec = importlib.util.spec_from_file_location("agent_skills_mcp_customizations", AGENT_SKILLS_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("agent_skills_mcp_customizations", module)
    spec.loader.exec_module(module)
    return module


def _load_skill_links_module():
    spec = importlib.util.spec_from_file_location("sync_skill_links_customizations", SKILL_LINKS_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("sync_skill_links_customizations", module)
    spec.loader.exec_module(module)
    return module


def _load_plugin_links_module():
    spec = importlib.util.spec_from_file_location("sync_plugin_links_customizations", PLUGIN_LINKS_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("sync_plugin_links_customizations", module)
    spec.loader.exec_module(module)
    return module


def _run_python_script(script_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(REPO_ROOT / ".venv" / "bin" / "python"), str(script_path), *args],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _run_shell_script(
    script_path: Path,
    *args: str,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(script_path), *args],
        check=check,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, **env} if env else None,
    )


class TestAgentCustomizations:
    def test_trainer_agent_exists(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "trainer.agent.md"
        text = _read(agent_path)

        assert 'tools:' in text
        assert 'read' in text
        assert 'edit' in text
        assert 'search' in text
        assert 'execute' in text
        assert 'todo' in text
        assert 'agent' in text
        assert 'agent-skills/*' in text
        assert 'agents: ["teacher", "student", "judge", "adversary"]' in text
        assert 'name: "trainer"' in text
        assert 'Treat this agent as the canonical orchestration contract for trainer-led optimization work.' in text
        assert 'Manage all `trainer-*` skill usage yourself' in text
        assert 'Use the `agent-skills` MCP server as the execution path for the `trainer-research`, `trainer-synthesize`, `trainer-optimize`, and optional `trainer-election` skills.' in text
        assert 'handoffs:' in text
        assert '- label: "Request Teacher Guidance"' in text
        assert 'agent: "teacher"' in text
        assert '- label: "Request Student Revision"' in text
        assert '- label: "Score Candidates"' in text
        assert '- label: "Run Adversarial Review"' in text
        assert '## Workspace Contract' in text
        assert '## MCP Execution Contract' in text
        assert '## Teacher Collaboration Contract' in text

    def test_teacher_agent_contract_structure(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "teacher.agent.md"
        text = _read(agent_path)
        frontmatter_end = text.index('---', 4)
        frontmatter = text[:frontmatter_end]

        assert 'name: "teacher"' in text
        assert 'description: "Use when reviewing optimization artifacts or user-supplied context' in text
        assert 'tools:' in frontmatter
        assert 'read' in frontmatter
        assert 'search' in frontmatter
        assert 'agent' in frontmatter
        assert 'agent/runSubagent' in frontmatter
        assert 'agents: ["student", "engineer", "judge"]' in text
        assert '- label: "Request Engineer Guidance"' in text
        assert '- label: "Request Judge Review"' in text
        assert '- label: "Request Student Response"' in text
        assert 'edit' not in frontmatter
        assert 'execute' not in frontmatter
        assert 'todo' not in frontmatter
        assert 'agent-skills/*' not in frontmatter
        assert 'The `trainer` agent owns trainer-skill usage, workspace coordination, iteration planning, and any handoffs to `student`, `judge`, or `adversary`.' in text
        assert 'Do not run `trainer-*` skills, do not orchestrate the loop, and do not take over candidate editing.' in text
        assert 'Treat any supplied workspace steering as read-only evidence.' in text
        assert 'Forecast likely student mistakes yourself before you ask the `student` for anything.' in text
        assert '`optimize-report.json`' in text
        assert '`manual-followup-report.json`' in text
        assert '`optimized-prompt.md`' in text
        assert '`steering/<agent>/summary.md`' in text
        assert 'State the strongest improvement recommendation.' in text

    def test_student_agent_contract_structure(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "student.agent.md"
        text = _read(agent_path)

        assert 'name: "student"' in text
        assert 'description: "Use when drafting or revising prompt candidates from teacher guidance inside trainer-led optimization loops, with explicit reasoning trajectory for the teacher."' in text
        assert 'tools:' in text
        assert 'read' in text
        assert 'edit' in text
        assert 'search' in text
        assert 'execute' in text
        assert 'todo' in text
        assert 'agent-skills/*' not in text
        assert 'agents: ["teacher", "engineer"]' in text
        assert '- label: "Request Teacher Guidance"' in text
        assert '- label: "Request Engineer Guidance"' in text
        assert 'Do not take over judging, adversarial review, or trainer-loop orchestration.' in text
        assert 'Do not use `engineer-prompt`, `engineer-code`, or any other engineer skills directly.' in text
        assert 'You are a specialist in teacher-guided candidate revision.' in text
        assert 'Use the `teacher` handoff whenever the critique is incomplete' in text
        assert 'Use the `engineer` handoff to format your reasoning trajectory and solution plan into a clearer teacher-ready explanation' in text
        assert 'Implement the smallest defensible candidate revision' in text
        assert "Treat turn-scoped `steering/<agent>/turn-N/STEERING.md` artifacts and the active iteration's per-agent `steering/<agent>/summary.md` files as the guidance record" in text
        assert 'pre-emptively predict whether the `teacher` would approve the revision' in text
        assert 'Do not return answer-only output; expose the plan, reasoning trajectory, tradeoffs, and uncertainty' in text
        assert 'chain-of-thought, tree-of-thought, chain-of-uncertainty-thought, sketch-of-thought' in text

    def test_adversary_agent_contract_structure(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "adversary.agent.md"
        text = _read(agent_path)

        assert 'name: "adversary"' in text
        assert 'description: "Use when stress-testing prompt, dataset, or evaluator changes by producing exploit artifacts intended to trick the judge before finalization."' in text
        assert 'tools: [read, search]' in text
        assert 'user-invocable: true' in text
        assert 'DO NOT edit files.' in text
        assert 'DO NOT rerun the full optimization loop yourself.' in text
        assert 'build artifact-ready exploit attempts and judge-gaming candidates' in text
        assert '`candidate.md`' in text
        assert '`predicted-judge-response.md`' in text
        assert 'hidden assumptions' in text
        assert 'unsupported workflow behavior' in text

    def test_engineer_agent_exists_and_routes_prompt_work_through_engineer_skill(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "engineer.agent.md"
        text = _read(agent_path)

        assert 'name: "engineer"' in text
        assert 'tools:' in text
        assert 'read' in text
        assert 'edit' in text
        assert 'search' in text
        assert 'execute' in text
        assert 'todo' in text
        assert 'agent-skills/*' in text
        assert 'Use when writing, benchmarking, or improving LLM/ML prompt and context systems' in text
        assert 'formatting student reasoning and solution plans for teacher review' in text
        assert 'Use the `agent-skills` MCP server as the execution path for the `engineer-prompt` skill' in text
        assert 'Use the `agent-skills` MCP server as the execution path for the `engineer-code` skill' in text
        assert 'Call `find_agent_skill` to discover the exact `engineer-prompt` skill before doing prompt-engineering work.' in text
        assert 'Call `load_agent_skill` before first use so the loaded skill contract and bundled assets guide the task.' in text
        assert 'Call `run_agent_skill` only when the `engineer-prompt` skill exposes a runnable helper under `scripts/`' in text
        assert 'Call `find_agent_skill` to discover the exact `engineer-code` skill before giving Microsoft Trace or `trace-opt` code-optimization guidance.' in text
        assert 'Call `load_agent_skill` before first use so the loaded `engineer-code` contract and bundled references guide the task.' in text
        assert 'Call `run_agent_skill` only when the `engineer-code` skill later exposes a runnable helper under `scripts/`' in text
        assert 'DO NOT claim a performance or quality improvement without running the available benchmark, eval, test, or deterministic check.' in text
        assert 'Microsoft Trace and `trace-opt` code optimization for Python behavior' in text

        prompt_find_idx = text.index('Call `find_agent_skill` to discover the exact `engineer-prompt` skill before doing prompt-engineering work.')
        prompt_load_idx = text.index('Call `load_agent_skill` before first use so the loaded skill contract and bundled assets guide the task.')
        prompt_run_idx = text.index('Call `run_agent_skill` only when the `engineer-prompt` skill exposes a runnable helper under `scripts/`')
        code_find_idx = text.index('Call `find_agent_skill` to discover the exact `engineer-code` skill before giving Microsoft Trace or `trace-opt` code-optimization guidance.')
        code_load_idx = text.index('Call `load_agent_skill` before first use so the loaded `engineer-code` contract and bundled references guide the task.')
        code_run_idx = text.index('Call `run_agent_skill` only when the `engineer-code` skill later exposes a runnable helper under `scripts/`')

        assert prompt_find_idx < prompt_load_idx < prompt_run_idx
        assert code_find_idx < code_load_idx < code_run_idx

    def test_engineer_agent_contract_matches_discoverable_engineer_prompt_skill(self, monkeypatch):
        agent_skills_module = _load_agent_skills_module()
        monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(REPO_ROOT))

        agent_text = _read(REPO_ROOT / ".github" / "agents" / "engineer.agent.md")
        skill = agent_skills_module._find_skill_by_name("engineer-prompt")
        payload = agent_skills_module.load_agent_skill("engineer-prompt")

        assert Path(skill.dir).resolve() == (REPO_ROOT / "skills" / "engineer-prompt").resolve()
        assert "Name: engineer-prompt" in payload
        assert "The user wants to improve a prompt." in payload
        assert "Reserved for deterministic helpers if the engineer-prompt skill later needs" in payload
        assert 'Call `run_agent_skill` only when the `engineer-prompt` skill exposes a runnable helper under `scripts/`' in agent_text

        with pytest.raises(agent_skills_module.SkillError, match="has no runnable Python scripts"):
            agent_skills_module.run_agent_skill("engineer-prompt")

    def test_engineer_agent_contract_matches_discoverable_engineer_code_skill(self, monkeypatch):
        agent_skills_module = _load_agent_skills_module()
        monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(REPO_ROOT))

        agent_text = _read(REPO_ROOT / ".github" / "agents" / "engineer.agent.md")
        skill = agent_skills_module._find_skill_by_name("engineer-code")
        payload = agent_skills_module.load_agent_skill("engineer-code")

        assert Path(skill.dir).resolve() == (REPO_ROOT / "skills" / "engineer-code").resolve()
        assert "Name: engineer-code" in payload
        assert "Microsoft Trace" in payload
        assert "trace-opt" in payload
        assert "Reserved for deterministic helpers if the engineer-code skill later needs" in payload
        assert 'Call `run_agent_skill` only when the `engineer-code` skill later exposes a runnable helper under `scripts/`' in agent_text

        with pytest.raises(agent_skills_module.SkillError, match="has no runnable Python scripts"):
            agent_skills_module.run_agent_skill("engineer-code")

    def test_trainer_election_mirror_skill_stays_aligned_with_canonical_contract(self):
        mirrored_root = REPO_ROOT / ".agents" / "skills" / "trainer-election"
        canonical_path = REPO_ROOT / "skills" / "trainer-election" / "SKILL.md"
        mirrored_path = mirrored_root / "SKILL.md"

        assert mirrored_root.is_symlink()
        assert mirrored_path.resolve() == canonical_path.resolve()
        assert _read(canonical_path) == _read(mirrored_path)

    def test_trainer_synthesize_mirror_assets_stay_aligned_with_canonical_contract(self):
        canonical_root = REPO_ROOT / "skills" / "trainer-synthesize"
        mirrored_root = REPO_ROOT / ".agents" / "skills" / "trainer-synthesize"

        for relative_path in (
            "SKILL.md",
            "references/data-generation.md",
            "scripts/run_synthesize.py",
        ):
            assert _read(canonical_root / relative_path) == _read(mirrored_root / relative_path)

    def test_trainer_agent_declares_mcp_tool_sequence_and_loop_order(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "trainer.agent.md"
        text = _read(agent_path)

        find_idx = text.index('Call `find_agent_skill`')
        load_idx = text.index('Call `load_agent_skill`')
        run_idx = text.index('Call `run_agent_skill`')
        research_idx = text.index('`trainer-research` -> `trainer-synthesize` -> `trainer-optimize`')

        assert find_idx < load_idx < run_idx < research_idx

    def test_trainer_agent_declares_frontmatter_handoffs_for_teacher_student_judge_and_adversary(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        frontmatter_end = text.index('---', 4)
        frontmatter = text[:frontmatter_end]

        handoffs_idx = frontmatter.index('handoffs:')
        teacher_idx = frontmatter.index('- label: "Request Teacher Guidance"')
        teacher_agent_idx = frontmatter.index('agent: "teacher"', teacher_idx)
        student_idx = frontmatter.index('- label: "Request Student Revision"')
        student_agent_idx = frontmatter.index('agent: "student"', student_idx)
        judge_idx = frontmatter.index('- label: "Score Candidates"')
        judge_agent_idx = frontmatter.index('agent: "judge"', judge_idx)
        adversary_idx = frontmatter.index('- label: "Run Adversarial Review"')
        adversary_agent_idx = frontmatter.index('agent: "adversary"', adversary_idx)

        assert (
            handoffs_idx
            < teacher_idx
            < teacher_agent_idx
            < student_idx
            < student_agent_idx
            < judge_idx
            < judge_agent_idx
            < adversary_idx
            < adversary_agent_idx
        )
        assert '## Subagent Handoffs' not in text

    def test_teacher_agent_handoffs_structure(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "teacher.agent.md")

        frontmatter_end = text.index('---', 4)
        frontmatter = text[:frontmatter_end]

        handoffs_idx = frontmatter.index('handoffs:')
        engineer_idx = frontmatter.index('- label: "Request Engineer Guidance"')
        engineer_agent_idx = frontmatter.index('agent: "engineer"', engineer_idx)
        judge_idx = frontmatter.index('- label: "Request Judge Review"')
        judge_agent_idx = frontmatter.index('agent: "judge"', judge_idx)
        student_idx = frontmatter.index('- label: "Request Student Response"')
        student_agent_idx = frontmatter.index('agent: "student"', student_idx)

        assert 'agents: ["student", "engineer", "judge"]' in frontmatter
        assert handoffs_idx < engineer_idx < engineer_agent_idx < judge_idx < judge_agent_idx < student_idx < student_agent_idx

    def test_trainer_agent_optimize_contract_matches_single_shot_runtime(self):
        agent_text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")
        optimize_text = _read(REPO_ROOT / "skills" / "trainer-optimize" / "SKILL.md")

        assert 'performs leader election or baseline comparison internally' in agent_text
        assert 'The runtime is single-shot' in optimize_text

    def test_trainer_loop_contract_routes_steering_through_local_workspace_bundles(self):
        text = _read(REPO_ROOT / ".github" / "workflows" / "shared" / "trainer-loop-contract.md")

        assert "## Judge Steering Contract" in text
        assert "## Collaboration Contract" in text
        assert "The `trainer` agent owns trainer-skill execution, workspace coordination, and the sequencing of any teacher/student/adversary loop work." in text
        assert "The `teacher` agent only reviews supplied optimization artifacts or user-provided context to recommend what should improve next, and must forecast likely student mistakes itself before using any student handoff." in text
        assert "The `teacher` and `student` agents may hand off to each other in a bounded multi-turn loop, but within a teacher turn the teacher should finalize steering first and use any student handoff only at the end to elicit a concrete response or solution." in text
        assert "Keep Judge-owned agent files, skill contracts, scripts, templates, and local references (including any `references/` trees) immutable during trainer runs." in text
        assert "When the selected target is not `.github/agents/judge.agent.md`, do not write trainer output into `.github/agents/judge.agent.md`, `skills/judge-*/`, or any path under `.github/agents/.trainer-workspace/judge.agent/`." in text
        assert "Publish iteration-scoped steering under the selected target's local `.trainer-workspace/<prompt-name>/iterations/iteration-N/steering/<agent>/turn-N/STEERING.md` path" in text
        assert "Treat `required_artifacts.latest_iteration_dir` plus the active iteration's `steering/`, `optimize/`, `election/`, and `validation/` outputs as the iteration steering bundle." in text
        assert "Treat workspace-root `decision.md`, optional `benchmark.json`, `benchmark.md`, and `review.html` as the cross-run rollup steering bundle." in text
        assert "Populate `iterations/iteration-N/candidates/` with judge-ready entries for `original`, `student`, and `adversary`" in text
        assert "If an adversary candidate wins or reveals a credible exploit, add extra steering guidance for later judge turns" in text
        assert "If the old prompt wins, add extra steering guidance for the teacher" in text
        assert "Judge agents and judge skills must read those steering bundles as external, read-only inputs at runtime." in text

    def test_teacher_agent_stays_evidence_only_and_defers_orchestration(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "teacher.agent.md")

        assert "The `trainer` agent owns trainer-skill usage, workspace coordination, iteration planning, and any handoffs to `student`, `judge`, or `adversary`." in text
        assert "Do not run `trainer-*` skills, do not orchestrate the loop, and do not take over candidate editing." in text
        assert "Treat any supplied workspace steering as read-only evidence." in text
        assert "DO NOT edit files, mutate workspace artifacts, or claim that you ran validation yourself." in text
        assert "forecast how the `student` would likely misunderstand" in text

    def test_trainer_agent_missing_data_flow_runs_research_before_optimize(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        research_idx = text.index('run the `trainer-research` skill through MCP')
        synth_idx = text.index('Use the `trainer-synthesize` skill through MCP')
        optimize_idx = text.index('Run the `trainer-optimize` skill through MCP')

        assert research_idx < synth_idx < optimize_idx

    def test_trainer_agent_selects_llm_judge_for_reference_criteria_datasets(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        infer_idx = text.index('Inspect representative dataset rows before optimization and choose `judge_mode` from the scoring shape.')
        llm_idx = text.index('Rows that use `reference` and `criteria`, or otherwise declare `scoring: "llm_judge"`, must run with `judge_mode=llm_judge` rather than the deterministic default.')
        optimize_idx = text.index('Run the `trainer-optimize` skill through MCP against the target file')

        assert llm_idx < optimize_idx
        assert infer_idx < optimize_idx

    def test_trainer_agent_selects_custom_for_expected_json_and_custom_scoring_rows(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        custom_idx = text.index('Rows that use `expected_json`, or row-level scoring such as `normalized_match`, `json_schema`, or `custom_python`, must run with `judge_mode=custom`.')
        deterministic_idx = text.index('Keep `judge_mode=deterministic` only for rows that are genuinely exact-match `expected` tasks with no dataset shape that requires a richer scorer.')
        optimize_idx = text.index('Run the `trainer-optimize` skill through MCP against the target file')

        assert custom_idx < optimize_idx
        assert deterministic_idx < optimize_idx

    def test_old_loop_agent_file_is_absent(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "prompt-optimization-loop.agent.md"
        assert not agent_path.exists()

    def test_judge_agent_exists_and_is_user_invocable(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "judge.agent.md"
        text = _read(agent_path)

        assert 'name: "judge"' in text
        assert 'user-invocable: true' in text
        assert 'description: "Use when scoring prompt candidates' in text
        assert 'write concise candidate summaries' in text

    def test_judge_agent_routes_through_judge_skills_when_available(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "judge.agent.md")

        assert "agent-skills/*" in text
        assert 'Use the `agent-skills` MCP server as the execution path for the `judge-rubric`, `judge-trajectory`, and `judge-outcome` skills' in text
        rubric_idx = text.index('Call `find_agent_skill` to discover the exact `judge-rubric` skill')
        trajectory_idx = text.index('Call `find_agent_skill` to discover the exact `judge-trajectory` skill')
        outcome_idx = text.index('Call `find_agent_skill` to discover the exact `judge-outcome` skill')
        load_idx = text.index('Call `load_agent_skill` before first use')
        run_idx = text.index('Call `run_agent_skill` only when the chosen skill later exposes a deterministic helper under `scripts/`')

        assert rubric_idx < load_idx < run_idx
        assert trajectory_idx < load_idx < run_idx
        assert outcome_idx < load_idx < run_idx

    def test_judge_agent_treats_workspace_steering_as_read_only_external_input(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "judge.agent.md")

        assert "Treat any trainer-produced steering bundle as external evidence, not as Judge-owned state." in text
        assert "Read the selected target's local `.trainer-workspace/<prompt-name>/` artifacts when they are supplied, including turn-scoped `steering/<agent>/turn-N/STEERING.md` files and per-agent `steering/<agent>/summary.md` files under the active iteration, but do not rewrite them." in text
        assert "Use `required_artifacts.latest_iteration_dir` plus `steering/`, `optimize/`, `election/`, and `validation/` outputs as the iteration steering bundle." in text
        assert "Use workspace-root `decision.md`, optional `benchmark.json`, `benchmark.md`, and `review.html` as the cross-run rollup steering bundle." in text
        assert "Judge skills must remain independently runnable even when no steering bundle is present; treat steering as optional evidence rather than a hidden dependency." in text

    def test_judge_agent_contract_matches_discoverable_judge_skills(self, monkeypatch):
        agent_skills_module = _load_agent_skills_module()
        monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(REPO_ROOT))

        for skill_name in ("judge-rubric", "judge-trajectory", "judge-outcome"):
            skill = agent_skills_module._find_skill_by_name(skill_name)
            payload = agent_skills_module.load_agent_skill(skill_name)

            assert skill.dir == (REPO_ROOT / "skills" / skill_name).resolve().as_posix()
            assert f"Name: {skill_name}" in payload

        rubric_result = agent_skills_module.run_agent_skill(
            "judge-rubric",
            argv=[
                "--input-file",
                str(REPO_ROOT / "skills" / "judge-rubric" / "assets" / "sample-contract.json"),
            ],
        )
        assert rubric_result["exit_code"] == 0
        assert "# Rubric Package" in rubric_result["stdout"]
        assert "## Locked Rubric" in rubric_result["stdout"]

        with pytest.raises(agent_skills_module.SkillError, match="has no runnable Python scripts"):
            agent_skills_module.run_agent_skill("judge-outcome")

    def test_judge_agent_operational_flow_requires_rubric_then_evidence_then_comparison(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "judge.agent.md")

        operational_items = _markdown_numbered_items(_markdown_section(text, "Operational Instructions"))
        approach_items = _markdown_numbered_items(_markdown_section(text, "Approach"))

        assert len(operational_items) >= 8
        assert "judging skill" in operational_items[0].lower()
        assert "task-specific rubric" in operational_items[1].lower()
        assert "evidence ledger" in operational_items[2].lower()

        runtime_idx = next(i for i, item in enumerate(operational_items) if "runtime failure" in item.lower())
        robustness_idx = next(i for i, item in enumerate(operational_items) if "robustness checks" in item.lower())
        confidence_idx = next(i for i, item in enumerate(operational_items) if "lower confidence" in item.lower() or "confidence" in item.lower())

        assert runtime_idx > 2
        assert robustness_idx > runtime_idx
        assert confidence_idx >= robustness_idx

        skill_idx = next(i for i, item in enumerate(approach_items) if "judging skill" in item.lower())
        rubric_idx = next(i for i, item in enumerate(approach_items) if "lock the rubric" in item.lower())
        evidence_idx = next(i for i, item in enumerate(approach_items) if "collect the available evidence" in item.lower())
        tie_break_idx = next(i for i, item in enumerate(approach_items) if "tie-breakers" in item.lower())

        assert skill_idx < rubric_idx <= evidence_idx < tie_break_idx

    def test_judge_agent_output_contract_matches_evidence_first_claims(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "judge.agent.md")

        constraints = _markdown_bullets(_markdown_section(text, "Constraints"))
        scope = _markdown_bullets(_markdown_section(text, "Scope"))
        focus_areas = _markdown_bullets(_markdown_section(text, "Focus Areas"))
        output = _markdown_bullets(_markdown_section(text, "Output Format"))

        assert any("unsupported chain-of-thought" in item.lower() for item in constraints)
        assert any("invent benchmark claims" in item.lower() or "unseen evidence" in item.lower() for item in constraints)
        assert any("optimize-report.json" in item for item in scope)
        assert len(focus_areas) <= 4
        assert any(
            "judge-rubric" in item.lower()
            and "judge-trajectory" in item.lower()
            and "judge-outcome" in item.lower()
            for item in focus_areas
        )
        assert any("decision utility" in item.lower() for item in focus_areas)
        assert any("evidence" in item.lower() for item in output)
        assert any("confidence" in item.lower() or "uncertainty" in item.lower() for item in output)

    def test_judge_agent_operational_instructions_cover_reference_technique_families(self):
        prompt_text = _read(REPO_ROOT / ".github" / "agents" / "judge.agent.md").lower()
        reference_text = _read(
            REPO_ROOT / ".github" / "agents" / ".trainer-workspace" / "judge.agent" / "references" / "judging-techniques.md"
        ).lower()

        technique_families = {
            "locked_rubrics": (("rulers", "autorubric"), ("task-specific rubric", "locked rubric")),
            "task_adaptive": (("adarubric", "rubricrag"), ("task-adaptive", "reweight or rename dimensions")),
            "trajectory_process": (("agent-as-a-judge", "trajector"), ("process evidence", "intermediate artifacts")),
            "evidence_verification": (("verifiagent", "optimize-report.json"), ("evidence ledger", "observable evidence")),
            "order_robustness": (("pcfjudge", "position bias"), ("robustness checks", "order-robustness")),
            "cot_skepticism": (("gaming the judge", "chain-of-thought"), ("low-trust evidence", "unsupported chain-of-thought")),
            "calibration": (("judgment distribution", "bias-bounded"), ("confidence", "lower confidence")),
        }

        for reference_markers, prompt_markers in technique_families.values():
            assert all(marker in reference_text for marker in reference_markers)
            assert any(marker in prompt_text for marker in prompt_markers)

    def test_judge_agent_workspace_exists_with_local_judging_reference(self):
        workspace_root = REPO_ROOT / ".github" / "agents" / ".trainer-workspace" / "judge.agent"
        reference_path = workspace_root / "references" / "judging-techniques.md"

        assert workspace_root.is_dir()
        assert reference_path.is_file()

    def test_judge_agent_local_judging_reference_tracks_benchmarks_and_usage_rules(self):
        reference_path = REPO_ROOT / ".github" / "agents" / ".trainer-workspace" / "judge.agent" / "references" / "judging-techniques.md"
        text = _read(reference_path)

        assert 'JudgeBench' in text
        assert 'arXiv:2410.12784' in text
        assert 'RewardBench 2' in text
        assert 'RULERS' in text
        assert 'arXiv:2601.08654' in text
        assert 'AdaRubric' in text
        assert 'arXiv:2603.21362' in text
        assert 'RubricRAG' in text
        assert 'Agent-as-a-Judge survey' in text
        assert 'arXiv:2601.05111' in text
        assert 'Gaming the Judge' in text
        assert 'arXiv:2601.14691' in text
        assert 'Keep runtime scoring prompts concise.' in text

    def test_trainer_optimize_dataset_format_points_llm_judge_workflows_to_judging_reference(self):
        text = _read(REPO_ROOT / "skills" / "trainer-optimize" / "references" / "dataset-format.md")

        assert '[.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md](../../../.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md)' in text
        assert 'When `judge_mode=llm_judge` is used to optimize a judge prompt or other rubric-heavy evaluator, consult [.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md](../../../.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md) before changing the scoring prompt.' in text

    def test_default_judge_prompt_distinguishes_runtime_prompt_from_reference_brief(self):
        text = _read(REPO_ROOT / "skills" / "trainer-optimize" / "assets" / "judge-default.md")

        assert 'This file is the runtime scoring prompt, not the canonical literature review for judge design.' in text
        assert '[.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md](../../../.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md)' in text

    def test_judge_skills_have_eval_manifests(self):
        for skill_name in ("judge-rubric", "judge-trajectory", "judge-outcome"):
            manifest_path = REPO_ROOT / "skills" / skill_name / "evals" / "evals.json"
            payload = json.loads(_read(manifest_path))

            assert payload["skill_name"] == skill_name
            assert len(payload["evals"]) >= 3
            assert all("prompt" in case for case in payload["evals"])
            assert all("expected_output" in case for case in payload["evals"])
            assert all(case.get("assertions") for case in payload["evals"])

    def test_conservator_agent_exists_and_is_user_invocable(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "conservator.agent.md"
        text = _read(agent_path)

        assert 'user-invocable: true' in text
        assert 'name: "conservator"' in text
        assert 'Use when reviewing prompt, dataset, or evaluator changes for likely regressions' in text
        assert 'required MCP skill-routing' in text
        assert 'accidental reintroduction of internal leader-election behavior into single-shot optimize flows' in text
        assert 'find_agent_skill' in text
        assert 'load_agent_skill' in text
        assert 'run_agent_skill' in text
        assert 'single-shot optimize workflow unexpectedly depends on external selection behavior' in text
        assert 'what authored eval manifests support' in text
        assert 'explicit `train.jsonl` or `val.jsonl` inputs are blurred together with authored `evals/evals.json` artifacts' in text


class TestInstructionCustomization:
    def test_workspace_instruction_exists_with_repo_specific_guidance(self):
        instructions_path = REPO_ROOT / ".github" / "copilot-instructions.md"
        text = _read(instructions_path)

        assert '# Project Guidelines' in text
        assert 'python -m pytest -q' in text
        assert 'skill contracts live in `skills/*/SKILL.md`, authored evals live in adjacent `evals/evals.json`, and executable code belongs under `skills/*/scripts/`.' in text
        assert '`trainer-optimize` is a single-shot optimizer.' in text
        assert '[instructions/prompt-optimization.instructions.md](instructions/prompt-optimization.instructions.md)' in text
        assert '`trainer-optimize` requires explicit `train.jsonl` and `val.jsonl` inputs' in text

    def test_prompt_file_instruction_exists_with_scalar_applyto(self):
        instructions_path = REPO_ROOT / ".github" / "instructions" / "prompt-optimization.instructions.md"
        text = _read(instructions_path)

        assert 'applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"' in text
        assert 'Use the `trainer-optimize` skill for single-shot optimization, `trainer-election` only for external leader selection' in text

    def test_evals_dataset_instruction_exists(self):
        instructions_path = REPO_ROOT / ".github" / "instructions" / "evals-dataset.instructions.md"
        text = _read(instructions_path)

        assert 'applyTo: "**/evals/evals.json"' in text
        assert 'Keep the manifest root as a JSON object with `skill_name` and an `evals` array.' in text
        assert 'Keep `files` paths relative and prefer assets under `evals/files/`.' in text

    def test_gitignore_keeps_generic_workspace_glob_and_ignores_trainer_workspace(self):
        text = _read(REPO_ROOT / ".gitignore")

        assert "**/*-workspace/" in text
        assert "**/.trainer-workspace/" in text


class TestHookCustomization:
    def test_agentic_workflow_validation_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "agentic-workflow-validation.json"
        hook = json.loads(_read(hook_path))

        stop_hooks = hook["hooks"]["Stop"]
        post_tool_use = hook["hooks"]["PostToolUse"]
        assert stop_hooks
        assert all("/workspaces/" not in entry["command"] for entry in stop_hooks)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in stop_hooks)
        assert any("validate-agentic-workflow-compilation.sh --enforce" in entry["command"] for entry in stop_hooks)
        assert post_tool_use
        assert any(entry.get("matcher") == "Write|Edit|MultiEdit|ApplyPatch" for entry in post_tool_use)
        assert all("/workspaces/" not in entry["command"] for entry in post_tool_use)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in post_tool_use)
        assert any("validate-agentic-workflow-compilation.sh" in entry["command"] for entry in post_tool_use)

    def test_agentic_workflow_validation_script_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-agentic-workflow-compilation.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert ".github/workflows/*.md" in text
        assert "gh aw compile" in text
        assert ".git/copilot-agentic-workflows.txt" in text
        assert "collect_git_changed_targets" in text
        assert "origin/main" in text
        assert "normalize_lockfile_writeback_tokens" in text

    def test_agents_memory_records_workflow_compile_rule(self):
        memory_path = REPO_ROOT / ".agents" / "MEMORY.md"
        text = _read(memory_path)

        assert "`.github/workflows/*.md`" in text
        assert "`gh aw compile <workflow-name>`" in text
        assert "`agentic-workflow-validation`" in text
        assert "patch-based edits" in text

    def test_agentic_workflow_validation_script_records_changed_workflows(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-agentic-workflow-compilation.sh"
        workflow_path = REPO_ROOT / ".github" / "workflows" / "train-prompt.md"
        state_path = REPO_ROOT / ".git" / "copilot-agentic-workflows.txt"
        if state_path.exists():
            state_path.unlink()

        result = _run_shell_script(script_path, str(workflow_path))
        payload = json.loads(result.stdout)

        assert payload["continue"] is True
        assert "train-prompt.md" in payload["systemMessage"]
        assert state_path.read_text(encoding="utf-8").strip() == ".github/workflows/train-prompt.md"

        state_path.unlink(missing_ok=True)

    def test_agentic_workflow_validation_script_blocks_when_compile_updates_lockfile(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-agentic-workflow-compilation.sh"
        workflow_path = REPO_ROOT / ".github" / "workflows" / "train-prompt.md"
        state_path = REPO_ROOT / ".git" / "copilot-agentic-workflows.txt"
        state_path.write_text(".github/workflows/train-prompt.md\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            gh_path = temp_root / "gh"
            gh_path.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "aw" && "${2:-}" == "--help" ]]; then
  exit 0
fi
if [[ "${1:-}" == "aw" && "${2:-}" == "compile" ]]; then
  cat <<'EOF' > "$PWD/.github/workflows/train-prompt.lock.yml"
compiled by hook
EOF
  exit 0
fi
exit 1
""",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            original_lock = (REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml").read_text(encoding="utf-8")
            env = {"PATH": f"{temp_root}:{os.environ['PATH']}"}
            try:
                blocked = _run_shell_script(script_path, "--enforce", check=False, env=env)
                payload = json.loads(blocked.stdout)
                assert blocked.returncode == 0
                assert payload["continue"] is False
                assert "required recompilation" in payload["stopReason"]
                assert "train-prompt.lock.yml" in payload["stopReason"]
            finally:
                (REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml").write_text(
                    original_lock,
                    encoding="utf-8",
                )
                state_path.unlink(missing_ok=True)

    def test_agentic_workflow_validation_script_normalizes_writeback_token_fallback(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-agentic-workflow-compilation.sh"
        state_path = REPO_ROOT / ".git" / "copilot-agentic-workflows.txt"
        state_path.write_text(".github/workflows/train-prompt.md\n", encoding="utf-8")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            gh_path = temp_root / "gh"
            gh_path.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "aw" && "${2:-}" == "--help" ]]; then
  exit 0
fi
if [[ "${1:-}" == "aw" && "${2:-}" == "compile" ]]; then
  cat <<'EOF' > "$PWD/.github/workflows/train-prompt.lock.yml"
jobs:
  safe_outputs:
    steps:
      - name: Process Safe Outputs
        with:
          github-token: ${{ secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}
EOF
  exit 0
fi
exit 1
""",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)
            lock_path = REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml"
            original_lock = lock_path.read_text(encoding="utf-8")
            env = {"PATH": f"{temp_root}:{os.environ['PATH']}"}
            try:
                blocked = _run_shell_script(script_path, "--enforce", check=False, env=env)
                payload = json.loads(blocked.stdout)
                assert blocked.returncode == 0
                assert payload["continue"] is False
                assert (
                    "github-token: ${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}"
                    in lock_path.read_text(encoding="utf-8")
                )
            finally:
                lock_path.write_text(original_lock, encoding="utf-8")
                state_path.unlink(missing_ok=True)

    def test_agentic_workflow_validation_script_enforces_branch_workflow_changes_without_state(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-agentic-workflow-compilation.sh"
        state_path = REPO_ROOT / ".git" / "copilot-agentic-workflows.txt"
        state_path.unlink(missing_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            gh_path = temp_root / "gh"
            gh_path.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "aw" && "${2:-}" == "--help" ]]; then
  exit 0
fi
if [[ "${1:-}" == "aw" && "${2:-}" == "compile" ]]; then
  cat <<'EOF' > "$PWD/.github/workflows/train-prompt.lock.yml"
compiled by hook
EOF
  exit 0
fi
exit 1
""",
                encoding="utf-8",
            )
            gh_path.chmod(0o755)

            git_path = temp_root / "git"
            git_path.write_text(
                f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "$#" -ge 3 && "${{1:-}}" == "show-ref" && "${{2:-}}" == "--verify" && "${{3:-}}" == "--quiet" ]]; then
  case "${{4:-}}" in
    refs/remotes/origin/HEAD|refs/remotes/origin/main)
      exit 0
      ;;
  esac
fi
if [[ "$#" -ge 4 && "${{1:-}}" == "symbolic-ref" && "${{2:-}}" == "--quiet" && "${{3:-}}" == "--short" && "${{4:-}}" == "refs/remotes/origin/HEAD" ]]; then
  echo origin/main
  exit 0
fi
if [[ "$#" -ge 3 && "${{1:-}}" == "merge-base" && "${{2:-}}" == "HEAD" && "${{3:-}}" == "origin/main" ]]; then
  echo test-merge-base
  exit 0
fi
if [[ "$#" -ge 4 && "${{1:-}}" == "diff" && "${{2:-}}" == "--name-only" && "${{3:-}}" == "test-merge-base...HEAD" ]]; then
  echo .github/workflows/train-prompt.md
  exit 0
fi
if [[ "$#" -ge 4 && "${{1:-}}" == "diff" && "${{2:-}}" == "--quiet" && "${{4:-}}" == ".github/workflows/train-prompt.lock.yml" ]]; then
  exit 1
fi
if [[ "$#" -ge 5 && "${{1:-}}" == "diff" && "${{2:-}}" == "--cached" && "${{3:-}}" == "--quiet" && "${{5:-}}" == ".github/workflows/train-prompt.lock.yml" ]]; then
  exit 0
fi
exec {shlex.quote(shutil.which("git") or "git")} "$@"
""",
                encoding="utf-8",
            )
            git_path.chmod(0o755)

            lock_path = REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml"
            original_lock = lock_path.read_text(encoding="utf-8")
            env = {"PATH": f"{temp_root}:{os.environ['PATH']}"}
            try:
                blocked = _run_shell_script(script_path, "--enforce", check=False, env=env)
                payload = json.loads(blocked.stdout)
                assert blocked.returncode == 0
                assert payload["continue"] is False
                assert "required recompilation" in payload["stopReason"]
                assert "train-prompt.lock.yml" in payload["stopReason"]
            finally:
                lock_path.write_text(original_lock, encoding="utf-8")
                state_path.unlink(missing_ok=True)

    def test_prompt_validation_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "prompt-optimization-validation.json"
        hook = json.loads(_read(hook_path))

        post_tool_use = hook["hooks"]["PostToolUse"]
        assert post_tool_use
        assert all("/workspaces/" not in entry["command"] for entry in post_tool_use)
        assert any("validate-prompt-optimization.sh" in entry["command"] for entry in post_tool_use)
        assert any(entry["command"].startswith("bash .github/hooks/") for entry in post_tool_use)

    def test_prompt_validation_script_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-prompt-optimization.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert '.venv/bin/python' in text
        assert "/evals/" in text
        assert '"$python_bin" -m pytest -q tests/test_customizations.py' in text

    def test_skill_isolation_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "skill-isolation-validation.json"
        hook = json.loads(_read(hook_path))

        stop_hooks = hook["hooks"]["Stop"]
        post_tool_use = hook["hooks"]["PostToolUse"]
        assert stop_hooks
        assert all("/workspaces/" not in entry["command"] for entry in stop_hooks)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in stop_hooks)
        assert any("validate-skill-isolation.sh --all" in entry["command"] for entry in stop_hooks)
        assert post_tool_use
        assert any(entry.get("matcher") == "Write|Edit|MultiEdit" for entry in post_tool_use)
        assert all("/workspaces/" not in entry["command"] for entry in post_tool_use)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in post_tool_use)
        assert any("validate-skill-isolation.sh" in entry["command"] for entry in post_tool_use)

    def test_skill_isolation_script_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-skill-isolation.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "skills/*/SKILL.md" in text
        assert "continue" in text
        assert "stopReason" in text

    def test_skill_isolation_script_blocks_cross_skill_reference(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-skill-isolation.sh"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            temp_root = Path(temp_dir)
            skill_path = temp_root / "SKILL.md"
            skill_path.write_text(
                "---\nname: temp-skill\ndescription: temp\n---\n\n# Temp\n\nUse `judge-outcome` when final outputs matter.\n",
                encoding="utf-8",
            )

            blocked = _run_shell_script(script_path, str(skill_path), check=False)
            payload = json.loads(blocked.stdout)

            assert blocked.returncode == 0
            assert payload["continue"] is False
            assert "judge-outcome" in payload["stopReason"]
            assert str(skill_path.relative_to(REPO_ROOT)) in payload["stopReason"]

    def test_prompt_workflow_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "prompt-workflow-reminder.json"
        hook = json.loads(_read(hook_path))

        stop_hooks = hook["hooks"]["Stop"]
        post_tool_use = hook["hooks"]["PostToolUse"]
        assert stop_hooks
        assert all("/workspaces/" not in entry["command"] for entry in stop_hooks)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in stop_hooks)
        assert any("block-incomplete-prompt-workflows.sh" in entry["command"] for entry in stop_hooks)
        assert post_tool_use
        assert any(entry.get("matcher") == "Write|Edit|MultiEdit" for entry in post_tool_use)
        assert all("/workspaces/" not in entry["command"] for entry in post_tool_use)
        assert all(entry["command"].startswith("bash .github/hooks/") for entry in post_tool_use)
        assert any("prompt-workflow-reminder.sh" in entry["command"] for entry in post_tool_use)
        assert any("ensure-skill-link-watcher.sh" in entry["command"] for entry in post_tool_use)
        assert any("ensure-plugin-link-watcher.sh" in entry["command"] for entry in post_tool_use)

    def test_skill_link_watcher_launcher_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "ensure-skill-link-watcher.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "sync-skill-links.py" in text
        assert "--watch" in text
        assert 'pgrep -u "$UID" -f "$sync_helper .*--watch"' in text
        assert "$HOME/skills" in text
        assert "$HOME/.agents/skills" in text

    def test_plugin_link_watcher_launcher_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "ensure-plugin-link-watcher.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "sync-plugin-links.py" in text
        assert "--watch" in text
        assert 'pgrep -u "$UID" -f "$sync_helper .*--watch"' in text
        assert "copilot-training-plugin-link-watcher" in text

    def test_skill_link_sync_helper_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "sync-skill-links.py"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env python3")
        assert ".agents/skills" in text
        assert "~/skills" in text
        assert "--check" in text
        assert "--watch" in text
        assert "symlink_to" in text

    def test_plugin_link_sync_helper_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "sync-plugin-links.py"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env python3")
        assert "plugin-sources.json" in text
        assert "marketplace.json" in text
        assert "--check" in text
        assert "--watch" in text
        assert "symlink_to" in text

    def test_skill_link_sync_helper_normalizes_repo_and_external_skill_roots(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "sync-skill-links.py"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            repo_skill = temp_root / "skills" / "repo-skill"
            repo_skill.mkdir(parents=True)
            (repo_skill / "SKILL.md").write_text("---\nname: repo-skill\ndescription: repo\n---\n", encoding="utf-8")

            agent_skill = temp_root / ".agents" / "skills" / "agent-skill"
            agent_skill.mkdir(parents=True)
            (agent_skill / "SKILL.md").write_text("---\nname: agent-skill\ndescription: agent\n---\n", encoding="utf-8")

            external_root = temp_root / "home-skills"
            external_skill = external_root / "external-skill"
            external_skill.mkdir(parents=True)
            (external_skill / "SKILL.md").write_text("---\nname: external-skill\ndescription: external\n---\n", encoding="utf-8")

            mirror_root = temp_root / ".agents" / "skills"
            stale_copy = mirror_root / "repo-skill"
            stale_copy.mkdir(parents=True)
            (stale_copy / "SKILL.md").write_text("stale copy\n", encoding="utf-8")
            stale_link = mirror_root / "stale-skill"
            stale_link.symlink_to(repo_skill, target_is_directory=True)

            result = _run_python_script(
                helper_path,
                "--repo-root",
                str(temp_root),
                "--mirror-root",
                str(mirror_root),
                "--external-root",
                str(external_root),
            )
            payload = json.loads(result.stdout)

            assert "repo-skill" in payload["updated"]
            assert "agent-skill" in payload["unchanged"]
            assert "external-skill" in payload["created"]
            assert "stale-skill" in payload["removed"]

            repo_link = mirror_root / "repo-skill"
            agent_link = mirror_root / "agent-skill"
            external_link = mirror_root / "external-skill"
            assert repo_link.is_symlink()
            assert not agent_link.is_symlink()
            assert external_link.is_symlink()
            assert repo_link.resolve() == repo_skill.resolve()
            assert agent_link.resolve() == agent_skill.resolve()
            assert external_link.resolve() == external_skill.resolve()
            assert os.readlink(repo_link) == "../../skills/repo-skill"
            assert os.readlink(external_link)

            gitignore_text = _read(mirror_root / ".gitignore")
            assert "!repo-skill" in gitignore_text
            assert "!agent-skill/" in gitignore_text
            assert "!external-skill" not in gitignore_text

    def test_skill_link_sync_helper_check_detects_drift(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "sync-skill-links.py"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            repo_skill = temp_root / "skills" / "repo-skill"
            repo_skill.mkdir(parents=True)
            (repo_skill / "SKILL.md").write_text("---\nname: repo-skill\ndescription: repo\n---\n", encoding="utf-8")

            _run_python_script(helper_path, "--repo-root", str(temp_root))

            clean = subprocess.run(
                [str(REPO_ROOT / ".venv" / "bin" / "python"), str(helper_path), "--repo-root", str(temp_root), "--mirror-root", str(temp_root / ".agents" / "skills"), "--check"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            assert clean.returncode == 0
            clean_payload = json.loads(clean.stdout)
            assert clean_payload["status"] == "ok"

            broken_link = temp_root / ".agents" / "skills" / "repo-skill"
            broken_link.unlink()
            broken_link.mkdir()
            (broken_link / "SKILL.md").write_text("stale copy\n", encoding="utf-8")

            drift = subprocess.run(
                [str(REPO_ROOT / ".venv" / "bin" / "python"), str(helper_path), "--repo-root", str(temp_root), "--mirror-root", str(temp_root / ".agents" / "skills"), "--check"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            assert drift.returncode == 1
            drift_payload = json.loads(drift.stdout)
            assert drift_payload["status"] == "drift"
            assert "repo-skill" in drift_payload["non_symlink"]

    def test_plugin_link_sync_helper_normalizes_plugin_components_and_marketplace(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "sync-plugin-links.py"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            plugin_root = temp_root / "plugins" / "demo-plugin"
            plugin_root.mkdir(parents=True)
            (plugin_root / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "demo-plugin",
                        "description": "Demo plugin.",
                        "version": "1.2.3",
                        "license": "MIT",
                        "repository": "https://example.invalid/repo",
                    }
                ) + "\n",
                encoding="utf-8",
            )

            skill_root = temp_root / "skills" / "demo-skill"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n", encoding="utf-8")

            agent_root = temp_root / ".github" / "agents"
            agent_root.mkdir(parents=True)
            agent_file = agent_root / "demo.agent.md"
            agent_file.write_text("---\nname: demo\n---\n", encoding="utf-8")

            hook_root = temp_root / ".github" / "hooks"
            hook_root.mkdir(parents=True, exist_ok=True)
            hook_file = hook_root / "demo-hook.sh"
            hook_file.write_text("#!/usr/bin/env bash\n", encoding="utf-8")
            (hook_root / "__pycache__").mkdir()

            mcp_root = temp_root / "tools" / "demo-mcp"
            mcp_root.mkdir(parents=True)
            (mcp_root / "server.py").write_text("print('ok')\n", encoding="utf-8")

            obsolete_plugin_root = temp_root / "plugins" / "obsolete-plugin"
            obsolete_plugin_root.mkdir(parents=True)

            plugin_config = {
                "marketplace": {
                    "name": "demo-marketplace",
                    "owner": {"name": "Demo Owner"},
                    "metadata": {"description": "Demo marketplace.", "version": "9.9.9"},
                },
                "plugin": {
                    "name": "demo-plugin",
                    "directory": "plugins/demo-plugin",
                    "components": {
                        "skills": [{"root": "skills"}],
                        "agents": [{"root": ".github/agents"}],
                        "mcps": ["tools/demo-mcp"],
                        "hooks": [{"root": ".github/hooks", "exclude": ["__pycache__"]}],
                    },
                },
            }
            plugin_config_path = temp_root / ".github" / "plugin" / "plugin-sources.json"
            plugin_config_path.parent.mkdir(parents=True, exist_ok=True)
            plugin_config_path.write_text(json.dumps(plugin_config, indent=2) + "\n", encoding="utf-8")

            result = _run_python_script(helper_path, "--repo-root", str(temp_root))
            payload = json.loads(result.stdout)

            assert "demo-plugin:skills/demo-skill" in payload["created"]
            assert "demo-plugin:agents/demo.agent.md" in payload["created"]
            assert "demo-plugin:mcps/demo-mcp" in payload["created"]
            assert "demo-plugin:hooks/demo-hook.sh" in payload["created"]
            assert payload["marketplace_updated"] is True
            assert "obsolete-plugin" in payload["removed"]

            assert (plugin_root / "skills" / "demo-skill").is_symlink()
            assert (plugin_root / "agents" / "demo.agent.md").is_symlink()
            assert (plugin_root / "mcps" / "demo-mcp").is_symlink()
            assert (plugin_root / "hooks" / "demo-hook.sh").is_symlink()
            assert (plugin_root / "skills" / "demo-skill").resolve() == skill_root.resolve()
            assert (plugin_root / "agents" / "demo.agent.md").resolve() == agent_file.resolve()
            assert (plugin_root / "mcps" / "demo-mcp").resolve() == mcp_root.resolve()
            assert (plugin_root / "hooks" / "demo-hook.sh").resolve() == hook_file.resolve()
            assert not (plugin_root / "hooks" / "__pycache__").exists()
            assert not obsolete_plugin_root.exists()

            marketplace_payload = json.loads((temp_root / ".github" / "plugin" / "marketplace.json").read_text(encoding="utf-8"))
            assert marketplace_payload == {
                "name": "demo-marketplace",
                "owner": {"name": "Demo Owner"},
                "metadata": {"description": "Demo marketplace.", "version": "9.9.9"},
                "plugins": [
                    {
                        "name": "demo-plugin",
                        "description": "Demo plugin.",
                        "version": "1.2.3",
                        "source": "plugins/demo-plugin",
                    }
                ],
            }

    def test_plugin_link_sync_helper_check_detects_drift(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "sync-plugin-links.py"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            skill_root = temp_root / "skills" / "demo-skill"
            skill_root.mkdir(parents=True)
            (skill_root / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n", encoding="utf-8")

            plugin_root = temp_root / "plugins" / "demo-plugin"
            plugin_root.mkdir(parents=True)
            (plugin_root / "plugin.json").write_text(
                json.dumps(
                    {
                        "name": "demo-plugin",
                        "description": "Demo plugin.",
                        "version": "1.0.0",
                        "license": "MIT",
                        "repository": "https://example.invalid/repo",
                    }
                ) + "\n",
                encoding="utf-8",
            )

            plugin_config_path = temp_root / ".github" / "plugin" / "plugin-sources.json"
            plugin_config_path.parent.mkdir(parents=True, exist_ok=True)
            plugin_config_path.write_text(
                json.dumps(
                    {
                        "marketplace": {
                            "name": "demo-marketplace",
                            "owner": {"name": "Demo Owner"},
                            "metadata": {"description": "Demo marketplace.", "version": "1.0.0"},
                        },
                        "plugin": {
                            "name": "demo-plugin",
                            "directory": "plugins/demo-plugin",
                            "components": {
                                "skills": ["skills/demo-skill"],
                                "agents": [],
                                "mcps": [],
                                "hooks": [],
                            },
                        },
                    },
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )

            _run_python_script(helper_path, "--repo-root", str(temp_root))

            clean = subprocess.run(
                [str(REPO_ROOT / ".venv" / "bin" / "python"), str(helper_path), "--repo-root", str(temp_root), "--check"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            assert clean.returncode == 0
            clean_payload = json.loads(clean.stdout)
            assert clean_payload["status"] == "ok"

            broken_link = temp_root / "plugins" / "demo-plugin" / "skills" / "demo-skill"
            broken_link.unlink()
            broken_link.mkdir()
            (broken_link / "SKILL.md").write_text("stale copy\n", encoding="utf-8")

            drift = subprocess.run(
                [str(REPO_ROOT / ".venv" / "bin" / "python"), str(helper_path), "--repo-root", str(temp_root), "--check"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            assert drift.returncode == 1
            drift_payload = json.loads(drift.stdout)
            assert drift_payload["status"] == "drift"
            assert "demo-plugin:skills/demo-skill" in drift_payload["non_symlink"]

    def test_agents_skill_directory_matches_managed_links(self):
        skill_links_module = _load_skill_links_module()
        mirror_root = REPO_ROOT / ".agents" / "skills"
        skill_links = sorted(child for child in mirror_root.iterdir() if not child.name.startswith("."))
        expected_links, duplicates, _ = skill_links_module.desired_skill_links(REPO_ROOT, [], mirror_root=mirror_root)
        actual_links = {child.name: child for child in skill_links}

        assert skill_links
        assert duplicates == {}
        assert all(child.is_symlink() or child.name == "skill-creator" for child in skill_links)
        assert all((child.resolve() / "SKILL.md").is_file() for child in skill_links)
        assert set(expected_links).issubset(actual_links)
        assert all(actual_links[name].resolve() == target.resolve() for name, target in expected_links.items())

    def test_agents_skill_directory_gitignore_hides_local_external_links(self):
        gitignore_path = REPO_ROOT / ".agents" / "skills" / ".gitignore"
        text = _read(gitignore_path)

        assert "Managed by .github/hooks/sync-skill-links.py" in text
        assert "*" in text
        assert "!.gitignore" in text
        assert "!skill-creator/" in text

    def test_prompt_workflow_script_injects_engineer_prompt_and_trainer(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "prompt-workflow-reminder.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "*.prompt.md" in text
        assert "copilot-instructions.md" in text
        assert "/engineer-prompt" in text
        assert "@trainer" in text
        assert ".trainer-workspace" in text
        assert "inputs/source" in text
        assert "steering/<agent>/summary.md" in text
        assert "decision.md" in text
        assert "systemMessage" in text

    def test_prompt_workflow_block_script_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "block-incomplete-prompt-workflows.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "workflow-status.json" in text
        assert ".trainer-workspace" in text
        assert "/engineer-prompt" in text
        assert "@trainer" in text

    def test_trainer_workspace_helper_init_and_update_behaves_correctly(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "trainer-workspace.py"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            prompt_dir = temp_root / "skills" / "demo-skill"
            prompt_dir.mkdir(parents=True)
            prompt_file = prompt_dir / "SKILL.md"
            prompt_file.write_text("# Demo\n", encoding="utf-8")
            rel_prompt = str(prompt_file.relative_to(REPO_ROOT))

            init_result = _run_python_script(
                helper_path,
                "init",
                "--repo-root",
                str(REPO_ROOT),
                "--target-file",
                rel_prompt,
            )
            init_payload = json.loads(init_result.stdout)

            workspace_root = prompt_dir / ".trainer-workspace" / "SKILL"
            status_path = workspace_root / "workflow-status.json"
            assert init_payload["workspace_root"].endswith("skills/demo-skill/.trainer-workspace/SKILL")
            assert workspace_root.is_dir()
            assert (workspace_root / "engineer-prompt").is_dir()
            assert (workspace_root / "inputs" / "source" / "SKILL.md").read_text(encoding="utf-8") == "# Demo\n"
            assert (workspace_root / "iterations").is_dir()

            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            assert status_payload["workflow_state"] == "pending_engineer_prompt"
            assert status_payload["required_artifacts"]["source_snapshot"].endswith("inputs/source/SKILL.md")
            assert "candidate descriptions, predicted judge responses, and reflection artifacts" in status_payload["artifact_contract"]["candidates"]
            assert "iteration steering bundle" in status_payload["artifact_contract"]["steering"]
            assert "cross-run rollup steering bundle" in status_payload["artifact_contract"]["steering"]
            assert status_payload["required_artifacts"]["candidate_dir"] is None
            assert status_payload["required_artifacts"]["steering_summary_dir"] is None
            assert "Do not write trainer output into Judge-owned files" in status_payload["notes"]

            review_path = workspace_root / "engineer-prompt" / "review.md"
            review_path.write_text("# Review\n", encoding="utf-8")

            manual_followup_path = workspace_root / "iterations" / "iteration-1" / "optimize" / "manual-followup-report.json"
            manual_followup_path.parent.mkdir(parents=True, exist_ok=True)
            manual_followup_path.write_text("{}\n", encoding="utf-8")
            candidate_manifest_path = workspace_root / "iterations" / "iteration-1" / "candidates" / "candidates.json"
            candidate_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            candidate_manifest_path.write_text("{}\n", encoding="utf-8")
            steering_turn_path = workspace_root / "iterations" / "iteration-1" / "steering" / "teacher" / "turn-2" / "STEERING.md"
            steering_turn_path.parent.mkdir(parents=True, exist_ok=True)
            steering_turn_path.write_text("# Steering\n", encoding="utf-8")

            update_result = _run_python_script(
                helper_path,
                "update",
                "--repo-root",
                str(REPO_ROOT),
                "--workspace-root",
                str(workspace_root.relative_to(REPO_ROOT)),
                "--state",
                "training",
                "--iteration",
                "iteration-1",
                "--create-iteration-layout",
                "--engineer-prompt-review",
                str(review_path.relative_to(REPO_ROOT)),
                "--train-dataset",
                str((workspace_root / "inputs" / "train.jsonl").relative_to(REPO_ROOT)),
                "--val-dataset",
                str((workspace_root / "inputs" / "val.jsonl").relative_to(REPO_ROOT)),
                "--eval-manifest",
                str((workspace_root / "inputs" / "evals.json").relative_to(REPO_ROOT)),
                "--validation-log",
                str((workspace_root / "iterations" / "iteration-1" / "validation" / "pytest.txt").relative_to(REPO_ROOT)),
                "--decision-summary",
                str((workspace_root / "decision.md").relative_to(REPO_ROOT)),
            )
            update_payload = json.loads(update_result.stdout)

            assert update_payload["workflow_state"] == "training"
            assert (workspace_root / "iterations" / "iteration-1" / "research").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "synthesize").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "optimize").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "election").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "candidates").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "candidates" / "original").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "candidates" / "student").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "candidates" / "adversary").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "steering").is_dir()
            assert (workspace_root / "iterations" / "iteration-1" / "validation").is_dir()

            updated_status = json.loads(status_path.read_text(encoding="utf-8"))
            assert updated_status["required_artifacts"]["engineer_prompt_review"].endswith("engineer-prompt/review.md")
            assert updated_status["required_artifacts"]["latest_iteration_dir"].endswith("iterations/iteration-1")
            assert updated_status["required_artifacts"]["train_dataset"].endswith("inputs/train.jsonl")
            assert updated_status["required_artifacts"]["optimize_report"].endswith("iterations/iteration-1/optimize/manual-followup-report.json")
            assert updated_status["required_artifacts"]["candidate_dir"].endswith("iterations/iteration-1/candidates")
            assert updated_status["required_artifacts"]["candidate_manifest"].endswith("iterations/iteration-1/candidates/candidates.json")
            assert updated_status["required_artifacts"]["latest_steering_turn"].endswith("iterations/iteration-1/steering/teacher/turn-2/STEERING.md")
            assert updated_status["required_artifacts"]["steering_summary_dir"].endswith("iterations/iteration-1/steering")
            assert updated_status["required_artifacts"]["validation_log"].endswith("iterations/iteration-1/validation/pytest.txt")

            complete_result = _run_python_script(
                helper_path,
                "update",
                "--repo-root",
                str(REPO_ROOT),
                "--workspace-root",
                str(workspace_root.relative_to(REPO_ROOT)),
                "--state",
                "complete",
            )
            complete_payload = json.loads(complete_result.stdout)
            assert complete_payload["workflow_state"] == "complete"
            assert complete_payload["required_artifacts"]["optimize_report"].endswith("iterations/iteration-1/optimize/manual-followup-report.json")

    def test_prompt_workflow_hook_creates_workspace_status_for_prompt_like_file(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "prompt-workflow-reminder.sh"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            prompt_dir = temp_root / "prompts"
            prompt_dir.mkdir(parents=True)
            prompt_file = prompt_dir / "example.prompt.md"
            prompt_file.write_text("Prompt body\n", encoding="utf-8")

            result = _run_shell_script(script_path, str(prompt_file))
            payload = json.loads(result.stdout)
            workspace_root = prompt_dir / ".trainer-workspace" / "example.prompt"
            status_path = workspace_root / "workflow-status.json"

            assert payload["continue"] is True
            assert "/engineer-prompt" in payload["systemMessage"]
            assert "@trainer" in payload["systemMessage"]
            assert "candidates/<source>/" in payload["systemMessage"]
            assert workspace_root.is_dir()
            assert status_path.is_file()

            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            assert status_payload["workflow_state"] == "pending_engineer_prompt"
            assert status_payload["required_artifacts"]["steering_summary_dir"] is None
            assert status_payload["required_artifacts"]["decision_summary"].endswith("decision.md")

    def test_prompt_workflow_block_script_blocks_incomplete_and_allows_complete(self):
        helper_path = REPO_ROOT / ".github" / "hooks" / "trainer-workspace.py"
        block_path = REPO_ROOT / ".github" / "hooks" / "block-incomplete-prompt-workflows.sh"

        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            temp_root = Path(temp_dir)
            prompt_dir = temp_root / "instructions"
            prompt_dir.mkdir(parents=True)
            prompt_file = prompt_dir / "demo.instructions.md"
            prompt_file.write_text("Use this instruction\n", encoding="utf-8")
            rel_prompt = str(prompt_file.relative_to(REPO_ROOT))

            _run_python_script(
                helper_path,
                "init",
                "--repo-root",
                str(REPO_ROOT),
                "--target-file",
                rel_prompt,
            )

            scoped_env = {"PROMPT_WORKFLOW_SCAN_ROOT": str(temp_root)}

            blocked = _run_shell_script(block_path, check=False, env=scoped_env)
            blocked_payload = json.loads(blocked.stdout)
            assert blocked.returncode == 0
            assert blocked_payload["continue"] is False
            assert rel_prompt in blocked_payload["stopReason"]

            workspace_root = prompt_dir / ".trainer-workspace" / "demo.instructions"
            _run_python_script(
                helper_path,
                "update",
                "--repo-root",
                str(REPO_ROOT),
                "--workspace-root",
                str(workspace_root.relative_to(REPO_ROOT)),
                "--state",
                "complete",
            )

            allowed = _run_shell_script(block_path, env=scoped_env)
            assert allowed.stdout == ""


class TestTrainPromptWorkflow:
    """Validate the Train Prompt workflow safe-outputs configuration."""

    WORKFLOW_MD = REPO_ROOT / ".github" / "workflows" / "train-prompt.md"
    WORKFLOW_LOCK = REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml"
    AGENT_SKILLS_RUNTIME = REPO_ROOT / ".github" / "workflows" / "shared" / "agent-skills-runtime.md"

    def _parse_frontmatter_yaml(self, text: str) -> str:
        """Return the raw YAML block from a frontmatter-delimited file."""
        assert text.startswith("---"), "Expected frontmatter starting with ---"
        # Search for closing delimiter on its own line to avoid false positives
        closing = text.find("\n---", 3)
        assert closing != -1, "Expected closing --- in frontmatter"
        return text[3:closing]

    def _lock_safe_outputs_configs(self) -> list[dict]:
        """Extract both safe-outputs JSON config blobs from the lock file."""
        text = _read(self.WORKFLOW_LOCK)
        configs: list[dict] = []
        for line in text.splitlines():
            stripped = line.strip()
            # The config appears in two forms:
            # 1. Bare JSON object on its own line (the config.json heredoc)
            # 2. An escaped JSON string as a YAML env-var value
            if "create_pull_request" not in stripped:
                continue
            if stripped.startswith("GH_AW_SAFE_OUTPUTS_HANDLER_CONFIG:"):
                # Env-var form: value is a JSON-escaped string (use json.loads for
                # proper handling of all escape sequences, not just \")
                raw_yaml_value = stripped.split(":", 1)[1].strip()
                inner_json = json.loads(raw_yaml_value)  # decode outer JSON string escapes
                configs.append(json.loads(inner_json))   # decode the inner JSON object
            else:
                try:
                    candidate = json.loads(stripped)
                    if isinstance(candidate, dict) and "create_pull_request" in candidate:
                        configs.append(candidate)
                except json.JSONDecodeError:
                    pass  # skip lines that match keyword filters but aren't valid JSON
        return configs

    def _lock_text(self) -> str:
        return _read(self.WORKFLOW_LOCK)

    def _lock_yaml(self) -> dict:
        parsed = yaml.safe_load(self._lock_text())
        assert isinstance(parsed, dict), "Expected train-prompt.lock.yml to parse as a YAML mapping"
        return parsed

    def _source_agent_skills_runtime(self) -> dict:
        text = _read(self.AGENT_SKILLS_RUNTIME)
        frontmatter = self._parse_frontmatter_yaml(text)
        parsed = yaml.safe_load(frontmatter)
        return parsed["mcp-servers"]["agent-skills"]

    def test_workflow_source_exists(self):
        assert self.WORKFLOW_MD.is_file(), f"train-prompt.md not found: {self.WORKFLOW_MD}"

    def test_workflow_lock_exists(self):
        assert self.WORKFLOW_LOCK.is_file(), f"train-prompt.lock.yml not found: {self.WORKFLOW_LOCK}"

    def _source_create_pull_request_config(self) -> dict:
        text = _read(self.WORKFLOW_MD)
        frontmatter = self._parse_frontmatter_yaml(text)
        parsed = yaml.safe_load(frontmatter)
        config = parsed["safe-outputs"]["create-pull-request"]
        assert isinstance(config, dict), "Expected create-pull-request safe output config to be a YAML mapping"
        return config

    def _source_safe_outputs(self) -> dict:
        text = _read(self.WORKFLOW_MD)
        frontmatter = self._parse_frontmatter_yaml(text)
        parsed = yaml.safe_load(frontmatter)
        safe_outputs = parsed["safe-outputs"]
        assert isinstance(safe_outputs, dict), "Expected safe-outputs to be a YAML mapping"
        return safe_outputs

    def _source_steps(self, text: str | None = None) -> list[dict]:
        text = _read(self.WORKFLOW_MD) if text is None else text
        frontmatter = self._parse_frontmatter_yaml(text)
        parsed = yaml.safe_load(frontmatter)
        assert isinstance(parsed, dict), "Expected workflow frontmatter to parse as a YAML mapping"
        assert "steps" in parsed, "Expected workflow frontmatter to define steps"
        steps = parsed["steps"]
        assert isinstance(steps, list), "Expected steps to be a YAML list"
        return steps

    def test_source_create_pull_request_has_no_allowed_files_restriction(self):
        config = self._source_create_pull_request_config()
        assert "allowed-files" not in config, (
            "train-prompt.md should not define allowed-files for create-pull-request; "
            f"got {config.get('allowed-files')!r}"
        )

    def test_source_create_pull_request_explicitly_allows_protected_prompt_paths(self):
        config = self._source_create_pull_request_config()
        assert config.get("protected-files") == "allowed", (
            "train-prompt.md should set protected-files: allowed so gh aw's default "
            "protected path prefixes do not block prompt updates under .github/ or .agents/."
        )

    def test_source_create_pull_request_explicitly_sets_github_token_fallback(self):
        config = self._source_create_pull_request_config()
        expected_token_fallback = "${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}"
        assert config.get("github-token") == expected_token_fallback, (
            "train-prompt.md should explicitly set create-pull-request github-token "
            "to prefer COPILOT_GITHUB_TOKEN before GH_AW_GITHUB_TOKEN so PR creation "
            "does not stop on a PAT that can push but cannot open pull requests."
        )

    def test_source_does_not_request_reviewers(self):
        safe_outputs = self._source_safe_outputs()
        assert "add-reviewer" not in safe_outputs, (
            "train-prompt.md should not configure add-reviewer because create_pull_request "
            "can fall back to an issue and reviewer automation has no PR context then."
        )
        text = _read(self.WORKFLOW_MD)
        assert "add-reviewer" not in text, (
            "train-prompt.md should not instruct the agent to use add-reviewer."
        )
        reviewer_phrases = [
            "request copilot as a reviewer",
            "request a reviewer using",
            "use the `add-reviewer` safe output",
        ]
        assert not any(phrase in text.lower() for phrase in reviewer_phrases), (
            "train-prompt.md should not instruct automatic reviewer behavior in natural language."
        )

    def test_source_requires_stage_checkpointable_workspace_artifacts(self):
        text = _read(self.WORKFLOW_MD)
        assert "workflow can upload GitHub artifact checkpoints even when a later stage fails" in text, (
            "train-prompt.md should require keeping workflow-status.json and iteration directories "
            "current so the workflow can checkpoint interrupted training runs."
        )
        assert "staged `candidates/<source>/` entries" in text
        assert "`steering/<agent>/turn-N/STEERING.md` artifacts and per-agent `steering/<agent>/summary.md` files" in text
        assert "upload separate GitHub artifact checkpoints for workspace state plus research, synthesize, optimize, election, candidates, steering, and validation outputs" in text, (
            "train-prompt.md guardrails should explicitly preserve stage outputs for GitHub artifact uploads."
        )

    def test_source_limits_repo_analysis_to_tracked_checkout_files(self):
        text = _read(self.WORKFLOW_MD)
        assert "Build the candidate list only from git-tracked files under `${{ github.workspace }}`." in text, (
            "train-prompt.md should constrain candidate discovery to tracked files in the checked-out repository."
        )
        assert "Do not scan parent directories, `/tmp/**`, `/tmp/gh-aw/**`, sandbox firewall logs or audit directories" in text, (
            "train-prompt.md should explicitly forbid scanning restricted runtime-owned paths that are outside the repository checkout."
        )

    def test_source_excludes_training_workspace_artifacts_from_candidate_analysis(self):
        text = _read(self.WORKFLOW_MD)
        assert "Treat trainer workspace contents as generated artifacts, not source candidates." in text, (
            "train-prompt.md should tell the agent not to treat trainer workspace contents as source files to optimize."
        )
        assert "`inputs/`, `iterations/`, `research/`, `synthesize/`, `optimize/`, `election/`, `validation/`, `candidates/`, and `steering/`" in text, (
            "train-prompt.md should explicitly name trainer workspace stage directories that must be ignored during candidate analysis."
        )

    def test_source_requires_compile_loop_for_selected_workflow_targets(self):
        text = _read(self.WORKFLOW_MD)
        assert "If the selected target is a workflow source under `.github/workflows/*.md`, treat compilation as mandatory workflow maintenance:" in text, (
            "train-prompt.md should explicitly require gh aw compilation when it optimizes a workflow source file."
        )

    def test_source_distinguishes_target_compile_loop_from_self_check(self):
        text = _read(self.WORKFLOW_MD)
        assert "target-specific compile loop that is separate from the workflow's own pre-activation `gh aw compile train-prompt` safeguard" in text, (
            "train-prompt.md should distinguish workflow-target compilation from the workflow's own pre-activation compile check."
        )
        assert "including `train-prompt.md`; the pre-activation self-check only establishes a clean starting lockfile, and the target-specific compile loop still must run again after edits and again before validation" in text, (
            "train-prompt.md should clarify that when train-prompt itself is the selected workflow target, the later target-specific compile loop still applies after the initial self-check."
        )

    def test_source_requires_selected_workflow_targets_to_recompile_before_validation(self):
        text = _read(self.WORKFLOW_MD)
        assert "run `gh aw compile <workflow-name>` after editing that workflow source and again before final validation" in text, (
            "train-prompt.md should require running gh aw compile before validation for selected workflow sources."
        )
        assert "confirm the corresponding `.lock.yml` is present and in sync with no remaining diff after that final compile" in text, (
            "train-prompt.md should require the final workflow-target validation compile to leave no remaining lockfile diff."
        )

    def test_source_requires_selected_workflow_targets_to_include_lockfile(self):
        text = _read(self.WORKFLOW_MD)
        assert "keep the generated `.github/workflows/<workflow-name>.lock.yml` in sync with the source file and include it in the change set" in text, (
            "train-prompt.md should require including the compiled lock file alongside workflow source edits."
        )

    def test_source_blocks_pr_when_selected_workflow_target_compile_fails(self):
        text = _read(self.WORKFLOW_MD)
        assert "if compilation fails or the lock file still differs from the compiled output, record the command output in the selected local workspace validation artifacts and stop instead of opening a pull request" in text, (
            "train-prompt.md should block PR creation when an edited workflow target cannot be recompiled cleanly."
        )

    def test_source_adds_pre_activation_compile_step_for_train_prompt(self):
        steps = self._source_steps()
        pre_activation_compile_step = next((step for step in steps if step.get("name") == "Verify train-prompt workflow compile state"), None)
        assert pre_activation_compile_step is not None, (
            "train-prompt.md should define a deterministic pre-activation step that recompiles the trainer workflow."
        )
        assert pre_activation_compile_step.get("env", {}).get("GH_TOKEN") == "${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}", (
            "train-prompt.md should use the COPILOT_GITHUB_TOKEN fallback chain when running the pre-activation compile step."
        )
        run = pre_activation_compile_step.get("run", "")
        assert run.strip().splitlines() == [
            "gh aw --help >/dev/null 2>&1 || gh extension install github/gh-aw",
            "gh aw compile train-prompt",
        ], (
            "train-prompt.md should refresh train-prompt.lock.yml by compiling the workflow without adding a separate diff-based failure gate."
        )
        assert "git diff --exit-code -- .github/workflows/train-prompt.lock.yml" not in run, (
            "train-prompt.md should refresh train-prompt.lock.yml when stale instead of failing on lockfile drift."
        )

    def test_source_agent_skills_runtime_bootstraps_uv_in_python_container(self):
        runtime = self._source_agent_skills_runtime()
        assert runtime.get("command") == "/bin/sh", (
            "agent-skills-runtime.md should use a shell entrypoint that exists in python:alpine "
            "instead of invoking uvx directly."
        )
        assert runtime.get("args") == [
            "-lc",
            AGENT_SKILLS_UVX_BOOTSTRAP,
        ], (
            "agent-skills-runtime.md should bootstrap uv inside python:alpine before launching the "
            "agent-skills MCP server so the container does not fail with a missing uvx executable."
        )

    def test_lock_config_create_pull_request_has_no_allowed_files_restriction(self):
        configs = self._lock_safe_outputs_configs()
        assert configs, "Could not find safe-outputs config JSON blocks in train-prompt.lock.yml"
        for config in configs:
            create_pr = config.get("create_pull_request", {})
            assert "allowed_files" not in create_pr, (
                "train-prompt.lock.yml should not define allowed_files for create_pull_request; "
                f"got {create_pr.get('allowed_files')!r}"
            )

    def test_lock_config_allows_protected_files_policy(self):
        """Compiler defaults may add protected_path_prefixes, so policy must explicitly allow them."""
        configs = self._lock_safe_outputs_configs()
        assert configs, "Could not find safe-outputs config JSON blocks in train-prompt.lock.yml"
        for config in configs:
            create_pr = config.get("create_pull_request", {})
            assert create_pr.get("protected_files_policy") == "allowed", (
                "train-prompt.lock.yml should compile create_pull_request with "
                "protected_files_policy=allowed so prompt updates under compiler-default "
                "protected path prefixes remain reviewable."
            )

    def test_lock_configs_are_consistent_with_each_other(self):
        configs = self._lock_safe_outputs_configs()
        assert len(configs) == 2, (
            f"Expected exactly 2 safe-outputs config blocks in train-prompt.lock.yml, "
            f"found {len(configs)}."
        )
        first_allowed = configs[0].get("create_pull_request", {}).get("allowed_files")
        second_allowed = configs[1].get("create_pull_request", {}).get("allowed_files")
        assert first_allowed is None and second_allowed is None, (
            "Both safe-outputs config blocks in train-prompt.lock.yml must omit "
            f"allowed_files. Got:\n  block 1: {first_allowed}\n  block 2: {second_allowed}"
        )
        first_pr = configs[0].get("create_pull_request", {})
        second_pr = configs[1].get("create_pull_request", {})
        assert first_pr.get("protected_files_policy") == second_pr.get("protected_files_policy"), (
            "Both safe-outputs config blocks in train-prompt.lock.yml must have "
            "identical protected_files_policy values."
        )
        assert first_pr.get("github-token") == second_pr.get("github-token"), (
            "Both safe-outputs config blocks in train-prompt.lock.yml must have "
            "identical create_pull_request github-token overrides."
        )

    def test_lock_does_not_configure_add_reviewer(self):
        text = self._lock_text()
        assert "add_reviewer" not in text, (
            "train-prompt.lock.yml should not configure add_reviewer because fallback "
            "issue creation leaves no pull request context for reviewer automation."
        )

    def test_lock_runs_pre_activation_compile_for_train_prompt(self):
        agent_steps = self._lock_yaml()["jobs"]["agent"]["steps"]
        pre_activation_compile_step = next((step for step in agent_steps if step.get("name") == "Verify train-prompt workflow compile state"), None)
        assert pre_activation_compile_step is not None, (
            "train-prompt.lock.yml should run a pre-activation compile check for the trainer workflow."
        )
        assert pre_activation_compile_step.get("env", {}).get("GH_TOKEN") == "${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}", (
            "train-prompt.lock.yml should preserve the COPILOT_GITHUB_TOKEN fallback chain for the pre-activation compile step."
        )
        run = pre_activation_compile_step.get("run", "")
        assert run.strip().splitlines() == [
            "gh aw --help >/dev/null 2>&1 || gh extension install github/gh-aw",
            "gh aw compile train-prompt",
        ], (
            "train-prompt.lock.yml should refresh the checked-in lock file by compiling the workflow without a separate diff-based failure gate."
        )
        assert "git diff --exit-code -- .github/workflows/train-prompt.lock.yml" not in run, (
            "train-prompt.lock.yml should refresh the checked-in lock file when pre-activation compilation detects drift."
        )

    def test_source_steps_helper_rejects_missing_steps_key(self):
        with pytest.raises(AssertionError, match="Expected workflow frontmatter to define steps"):
            self._source_steps("---\nname: Missing steps\n---\nBody\n")

    def test_source_steps_helper_rejects_malformed_yaml(self):
        with pytest.raises(yaml.YAMLError):
            self._source_steps("---\nsteps: [\n---\nBody\n")

    def test_lock_agent_skills_gateway_bootstraps_uv_in_python_container(self):
        text = self._lock_text()
        assert '"container": "python:alpine"' in text
        assert '"entrypoint": "/bin/sh"' in text, (
            "train-prompt.lock.yml should start the agent-skills MCP container with /bin/sh so "
            "the entrypoint exists in python:alpine."
        )
        expected_bootstrap = f'"{AGENT_SKILLS_UVX_BOOTSTRAP}"'
        assert expected_bootstrap in text, (
            "train-prompt.lock.yml should bootstrap uv inside the python:alpine agent-skills "
            "container before invoking uvx so the MCP gateway can start reliably."
        )

    def test_lock_uploads_trainer_workspace_checkpoint_artifacts(self):
        text = self._lock_text()
        assert "Collect trainer workspace checkpoints" in text, (
            "train-prompt.lock.yml should collect changed .trainer-workspace checkpoints after the agent run."
        )
        expected_artifacts = (
            "trainer-workspace-state",
            "trainer-stage-research",
            "trainer-stage-synthesize",
            "trainer-stage-optimize",
            "trainer-stage-election",
            "trainer-stage-validation",
        )
        for artifact_name in expected_artifacts:
            assert f"name: {artifact_name}" in text, (
                "train-prompt.lock.yml should upload GitHub artifacts for each trainer stage "
                f"checkpoint, missing {artifact_name!r}."
            )
        for staged_path in (
            "/tmp/gh-aw/trainer-workspace/*/research/",
            "/tmp/gh-aw/trainer-workspace/*/synthesize/",
            "/tmp/gh-aw/trainer-workspace/*/optimize/",
            "/tmp/gh-aw/trainer-workspace/*/election/",
            "/tmp/gh-aw/trainer-workspace/*/validation/",
        ):
            assert staged_path in text, (
                "train-prompt.lock.yml should upload the exported trainer workspace stage "
                f"directory {staged_path!r}."
            )
        assert "Download trainer workspace state artifact" in text, (
            "train-prompt.lock.yml should make the workspace checkpoint metadata available "
            "to downstream jobs from its dedicated GitHub artifact."
        )
        assert "Download trainer stage checkpoint artifacts" in text, (
            "train-prompt.lock.yml should download dedicated trainer stage checkpoint artifacts "
            "for downstream jobs instead of relying on the generic agent bundle."
        )
        assert "pattern: trainer-stage-*" in text, (
            "train-prompt.lock.yml should download all trainer stage checkpoint artifacts with "
            "a dedicated artifact pattern."
        )
        assert "merge-multiple: false" in text, (
            "train-prompt.lock.yml should preserve per-artifact directories when downloading "
            "trainer stage checkpoints for later inspection."
        )

    def test_lock_writeback_steps_prefer_copilot_token_before_gh_aw_token(self):
        text = self._lock_text()
        expected_fallback = (
            "secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN"
        )
        assert expected_fallback in text, (
            "train-prompt.lock.yml write-back steps should prefer COPILOT_GITHUB_TOKEN "
            "before GH_AW_GITHUB_TOKEN so the workflow reaches a token that can open "
            "pull requests instead of stopping at a push-only PAT."
        )
        assert "token: ${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}" in text, (
            "train-prompt.lock.yml checkout for create_pull_request should preserve "
            "the COPILOT_GITHUB_TOKEN fallback."
        )
        assert "GIT_TOKEN: ${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}" in text, (
            "train-prompt.lock.yml git credential setup for create_pull_request "
            "should preserve the COPILOT_GITHUB_TOKEN fallback."
        )
        assert "\"github-token\":\"${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}\"" in text, (
            "train-prompt.lock.yml create_pull_request safe-output config should preserve "
            "the COPILOT_GITHUB_TOKEN fallback even if some auxiliary reporting steps use "
            "the default GH_AW_GITHUB_TOKEN || GITHUB_TOKEN fallback."
        )
        safe_outputs_steps = self._lock_yaml()["jobs"]["safe_outputs"]["steps"]
        process_safe_outputs = next(
            (step for step in safe_outputs_steps if step.get("name") == "Process Safe Outputs"),
            None,
        )
        assert process_safe_outputs is not None, "Expected Process Safe Outputs step in train-prompt.lock.yml"
        assert process_safe_outputs["with"]["github-token"] == "${{ secrets.COPILOT_GITHUB_TOKEN || secrets.GH_AW_GITHUB_TOKEN || secrets.GITHUB_TOKEN }}", (
            "train-prompt.lock.yml should pass the COPILOT_GITHUB_TOKEN fallback into the "
            "Process Safe Outputs github-script step so create_pull_request does not fall "
            "back to a token that cannot open pull requests."
        )
