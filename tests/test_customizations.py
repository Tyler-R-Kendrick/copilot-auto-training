from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_SKILLS_MODULE_PATH = REPO_ROOT / "tools" / "agent-skills-mcp" / "agent_skills_mcp.py"
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
        assert 'agents: ["engineer", "judge", "conservator"]' in text
        assert 'name: "trainer"' in text
        assert 'orchestrate repeated loops across the `trainer-optimize`, `trainer-research`, `trainer-synthesize`, and optional `trainer-election` skills' in text
        assert 'Use the `agent-skills` MCP server as the execution path for those skills.' in text
        assert 'Do not involve the `skill-creator` skill or its helper scripts in the `@trainer` workflow.' in text
        assert 'Do not write trainer artifacts under a sibling `*-workspace/` directory or any repo-root `**/*-workspace/` tree; that naming is reserved for other workflows.' in text
        assert 'Call `find_agent_skill` to discover the exact `trainer-*` skill before each stage of the workflow.' in text
        assert 'Call `load_agent_skill` before first use of a discovered skill' in text
        assert 'Call `run_agent_skill` to execute the discovered skill runtime' in text
        assert 'the default loop order is `trainer-research` -> `trainer-synthesize` -> `trainer-optimize`.' in text
        assert 'you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Run a minimum of 3 candidate-generation iterations unless the user explicitly requests a different iteration count.' in text
        assert 'If any required training data, validation data, or authored eval assets are missing from the supporting directory, and the user has not supplied the missing pieces directly, you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Use the `trainer-synthesize` skill through MCP to convert source material, user examples, or simulated edge cases into official `evals/evals.json` content plus any supporting `evals/files/` assets, then ensure the explicit `train.jsonl` and `val.jsonl` datasets required by `trainer-optimize` are present.' in text
        assert 'When optimizing a judge prompt or any rubric-heavy `llm_judge` workflow, consult `.github/agents/.trainer-workspace/judge.agent/references/judging-techniques.md`' in text
        assert 'Infer `judge_mode` from the dataset row shape before calling `trainer-optimize`, and pass the selected mode explicitly instead of relying on the runtime default.' in text
        assert 'Rows that use `reference` and `criteria`, or otherwise declare `scoring: "llm_judge"`, must run with `judge_mode=llm_judge` rather than the deterministic default.' in text
        assert 'Rows that use `expected_json`, or row-level scoring such as `normalized_match`, `json_schema`, or `custom_python`, must run with `judge_mode=custom`.' in text
        assert 'Keep `judge_mode=deterministic` only for rows that are genuinely exact-match `expected` tasks with no dataset shape that requires a richer scorer.' in text
        assert 'Inspect representative dataset rows before optimization and choose `judge_mode` from the scoring shape.' in text
        assert 'Do not assume `trainer-optimize` performs leader election or baseline comparison internally.' in text
        assert 'If the workflow explicitly needs comparison across multiple optimize outputs, run the `trainer-election` skill through MCP as a separate selection step' in text
        assert 'Keep stable cross-iteration inputs under `inputs/`.' in text
        assert '`iterations/iteration-N/optimize/`' in text
        assert '`optimized-prompt.md`' in text
        assert '`optimize-report.json`' in text
        assert '`manual-followup-report.json`' in text
        assert '`operator-followup.md`' in text
        assert '`decision.md`' in text
        assert 'If `trainer-optimize` returns `mode=manual_followup`' in text
        assert 'the current `@trainer` agent becomes the inference step' in text
        assert 'answer the payload\'s `model_prompt` with the current `@trainer` agent' in text
        assert 'Treat the agent-authored `optimized-prompt.md` from a `manual_followup` run as the optimize-stage candidate' in text
        assert 'let the helper auto-record whichever optimize artifact exists when `--optimize-report` is omitted' in text
        assert 'Do not copy a generic `with_skill` / `without_skill` tree unless the workflow actually runs comparative evals.' in text
        assert 'DO NOT route any part of the `@trainer` workflow through `skill-creator`, its scripts, or its benchmark layout.' in text
        assert 'handoffs:' in text
        assert '- label: "Request Engineer Review"' in text
        assert 'prompt: "Review the current target prompt, workspace artifacts, and optimization goal. Return a concise prompt-engineering assessment with rewrite hypotheses and metric framing for the next trainer iteration."' in text
        assert '- label: "Score Candidates"' in text
        assert 'prompt: "Compare the current prompt candidates or optimizer outputs and return a concise scoring summary with the strongest option and key tradeoffs."' in text
        assert '- label: "Run Regression Review"' in text
        assert 'prompt: "Review the pending prompt, dataset, evaluator, and scoring changes for regressions, contract drift, or unsupported workflow assumptions before finalization."' in text
        assert '## Subagent Handoffs' not in text

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
        assert 'Use the `agent-skills` MCP server as the execution path for the `engineer-prompt` skill' in text
        assert 'Call `find_agent_skill` to discover the exact `engineer-prompt` skill before doing prompt-engineering work.' in text
        assert 'Call `load_agent_skill` before first use so the loaded skill contract and bundled assets guide the task.' in text
        assert 'Call `run_agent_skill` only when the `engineer-prompt` skill exposes a runnable helper under `scripts/`' in text
        assert 'DO NOT claim a performance or quality improvement without running the available benchmark, eval, test, or deterministic check.' in text

        find_idx = text.index('Call `find_agent_skill`')
        load_idx = text.index('Call `load_agent_skill`')
        run_idx = text.index('Call `run_agent_skill`')

        assert find_idx < load_idx < run_idx

    def test_engineer_agent_contract_matches_discoverable_engineer_prompt_skill(self, monkeypatch):
        agent_skills_module = _load_agent_skills_module()
        monkeypatch.setenv("AGENT_SKILLS_REPO_ROOT", str(REPO_ROOT))

        agent_text = _read(REPO_ROOT / ".github" / "agents" / "engineer.agent.md")
        skill = agent_skills_module._find_skill_by_name("engineer-prompt")
        payload = agent_skills_module.load_agent_skill("engineer-prompt")

        assert skill.dir == (REPO_ROOT / "skills" / "engineer-prompt").resolve().as_posix()
        assert "Name: engineer-prompt" in payload
        assert "The user wants to improve a prompt." in payload
        assert "Reserved for deterministic helpers if the engineer-prompt skill later needs" in payload
        assert 'Call `run_agent_skill` only when the `engineer-prompt` skill exposes a runnable helper under `scripts/`' in agent_text

        with pytest.raises(agent_skills_module.SkillError, match="has no runnable Python scripts"):
            agent_skills_module.run_agent_skill("engineer-prompt")

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

    def test_trainer_agent_declares_frontmatter_handoffs_for_engineer_judge_and_conservator(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        frontmatter_end = text.index('---', 4)
        frontmatter = text[:frontmatter_end]

        handoffs_idx = frontmatter.index('handoffs:')
        engineer_idx = frontmatter.index('- label: "Request Engineer Review"')
        engineer_agent_idx = frontmatter.index('agent: "engineer"', engineer_idx)
        judge_idx = frontmatter.index('- label: "Score Candidates"')
        judge_agent_idx = frontmatter.index('agent: "judge"', judge_idx)
        conservator_idx = frontmatter.index('- label: "Run Regression Review"')
        conservator_agent_idx = frontmatter.index('agent: "conservator"', conservator_idx)

        assert handoffs_idx < engineer_idx < engineer_agent_idx < judge_idx < judge_agent_idx < conservator_idx < conservator_agent_idx
        assert '## Subagent Handoffs' not in text

    def test_trainer_agent_optimize_contract_matches_single_shot_runtime(self):
        agent_text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")
        optimize_text = _read(REPO_ROOT / "skills" / "trainer-optimize" / "SKILL.md")

        assert 'performs leader election or baseline comparison internally' in agent_text
        assert 'The runtime is single-shot' in optimize_text

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
    def test_prompt_validation_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "prompt-optimization-validation.json"
        hook = json.loads(_read(hook_path))

        post_tool_use = hook["hooks"]["PostToolUse"]
        assert post_tool_use
        assert any("validate-prompt-optimization.sh" in entry["command"] for entry in post_tool_use)

    def test_prompt_validation_script_exists(self):
        script_path = REPO_ROOT / ".github" / "hooks" / "validate-prompt-optimization.sh"
        text = _read(script_path)

        assert text.startswith("#!/usr/bin/env bash")
        assert "/evals/" in text
        assert "python -m pytest -q" in text

    def test_skill_isolation_hook_exists(self):
        hook_path = REPO_ROOT / ".github" / "hooks" / "skill-isolation-validation.json"
        hook = json.loads(_read(hook_path))

        stop_hooks = hook["hooks"]["Stop"]
        post_tool_use = hook["hooks"]["PostToolUse"]
        assert stop_hooks
        assert any("validate-skill-isolation.sh --all" in entry["command"] for entry in stop_hooks)
        assert post_tool_use
        assert any(entry.get("matcher") == "Write|Edit|MultiEdit" for entry in post_tool_use)
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
        assert any("block-incomplete-prompt-workflows.sh" in entry["command"] for entry in stop_hooks)
        assert post_tool_use
        assert any(entry.get("matcher") == "Write|Edit|MultiEdit" for entry in post_tool_use)
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

            review_path = workspace_root / "engineer-prompt" / "review.md"
            review_path.write_text("# Review\n", encoding="utf-8")

            manual_followup_path = workspace_root / "iterations" / "iteration-1" / "optimize" / "manual-followup-report.json"
            manual_followup_path.parent.mkdir(parents=True, exist_ok=True)
            manual_followup_path.write_text("{}\n", encoding="utf-8")

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
            assert (workspace_root / "iterations" / "iteration-1" / "validation").is_dir()

            updated_status = json.loads(status_path.read_text(encoding="utf-8"))
            assert updated_status["required_artifacts"]["engineer_prompt_review"].endswith("engineer-prompt/review.md")
            assert updated_status["required_artifacts"]["latest_iteration_dir"].endswith("iterations/iteration-1")
            assert updated_status["required_artifacts"]["train_dataset"].endswith("inputs/train.jsonl")
            assert updated_status["required_artifacts"]["optimize_report"].endswith("iterations/iteration-1/optimize/manual-followup-report.json")
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
            assert workspace_root.is_dir()
            assert status_path.is_file()

            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            assert status_payload["workflow_state"] == "pending_engineer_prompt"
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
    """Validate that the train-prompt workflow safe-outputs configuration allows
    the trainer to modify files under .github/instructions/ via pull requests."""

    WORKFLOW_MD = REPO_ROOT / ".github" / "workflows" / "train-prompt.md"
    WORKFLOW_LOCK = REPO_ROOT / ".github" / "workflows" / "train-prompt.lock.yml"

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
            if "create_pull_request" not in stripped or "allowed_files" not in stripped:
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

    def test_workflow_source_exists(self):
        assert self.WORKFLOW_MD.is_file(), f"train-prompt.md not found: {self.WORKFLOW_MD}"

    def test_workflow_lock_exists(self):
        assert self.WORKFLOW_LOCK.is_file(), f"train-prompt.lock.yml not found: {self.WORKFLOW_LOCK}"

    def test_source_allowed_files_includes_github_prefix(self):
        """The trainer modifies files across many sub-paths of .github/ (not just
        instructions/), so the broad '.github/' prefix must appear in allowed-files.
        '.github/' is only usable as an allowed-files entry once it is removed from
        protected_path_prefixes in the lock file."""
        text = _read(self.WORKFLOW_MD)
        frontmatter = self._parse_frontmatter_yaml(text)
        lines = [ln.strip() for ln in frontmatter.splitlines()]
        assert '- ".github/"' in lines, (
            "train-prompt.md allowed-files must include '.github/' so the trainer "
            "can create pull requests modifying any file under .github/."
        )

    def test_lock_config_json_includes_github_in_allowed_files(self):
        configs = self._lock_safe_outputs_configs()
        assert configs, "Could not find safe-outputs config JSON blocks in train-prompt.lock.yml"
        for config in configs:
            allowed = config.get("create_pull_request", {}).get("allowed_files", [])
            assert ".github/" in allowed, (
                f"train-prompt.lock.yml safe-outputs config must include "
                f"'.github/' in allowed_files, got: {allowed}"
            )

    def test_lock_config_no_protected_path_prefixes(self):
        """protected_path_prefixes must be empty so the trainer can create pull
        requests modifying any prompt file — including those under .github/ and
        .agents/ — without being blocked."""
        configs = self._lock_safe_outputs_configs()
        assert configs, "Could not find safe-outputs config JSON blocks in train-prompt.lock.yml"
        for config in configs:
            prefixes = config.get("create_pull_request", {}).get("protected_path_prefixes", [])
            assert prefixes == [], (
                f"protected_path_prefixes must be empty so any prompt file can be "
                f"modified. Got: {prefixes}"
            )

    def test_lock_configs_are_consistent_with_each_other(self):
        configs = self._lock_safe_outputs_configs()
        assert len(configs) == 2, (
            f"Expected exactly 2 safe-outputs config blocks in train-prompt.lock.yml, "
            f"found {len(configs)}."
        )
        first_allowed = configs[0].get("create_pull_request", {}).get("allowed_files", [])
        second_allowed = configs[1].get("create_pull_request", {}).get("allowed_files", [])
        assert first_allowed == second_allowed, (
            "Both safe-outputs config blocks in train-prompt.lock.yml must have "
            f"identical allowed_files. Got:\n  block 1: {first_allowed}\n  block 2: {second_allowed}"
        )
        first_pp = configs[0].get("create_pull_request", {}).get("protected_path_prefixes", [])
        second_pp = configs[1].get("create_pull_request", {}).get("protected_path_prefixes", [])
        assert first_pp == second_pp, (
            "Both safe-outputs config blocks in train-prompt.lock.yml must have "
            f"identical protected_path_prefixes. Got:\n  block 1: {first_pp}\n  block 2: {second_pp}"
        )

    def test_trainer_workspace_files_covered_by_allowed_prefix(self):
        """Spot-check that the specific paths blocked in the reported failures
        (issues #6 and #8) are covered by the '.github/' or '.agents/' allowed prefix."""
        covered_prefixes = (".github/", ".agents/")
        blocked_files = [
            ".github/instructions/.trainer-workspace/evals-dataset.instructions/decision.md",
            ".github/instructions/.trainer-workspace/evals-dataset.instructions/iterations/iteration-1/optimize/candidate-1.md",
            ".github/instructions/datasets/train.jsonl",
            ".github/instructions/datasets/val.jsonl",
            ".github/instructions/evals-dataset.instructions.md",
            ".github/instructions/evals/evals.json",
            ".github/agents/trainer.agent.md",
            ".agents/skills/trainer-optimize/SKILL.md",
        ]
        for path in blocked_files:
            assert any(path.startswith(p) for p in covered_prefixes), (
                f"'{path}' is not covered by any of the allowed prefixes {covered_prefixes}"
            )
