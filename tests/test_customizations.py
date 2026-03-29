from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _run_python_script(script_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(REPO_ROOT / ".venv" / "bin" / "python"), str(script_path), *args],
        check=True,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def _run_shell_script(script_path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(script_path), *args],
        check=check,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
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
        assert 'agents: ["judge", "conservator"]' in text
        assert 'name: "trainer"' in text
        assert 'orchestrate repeated loops across the `trainer-optimize`, `trainer-research`, `trainer-synthesize`, and optional `trainer-election` skills' in text
        assert 'Use the `agent-skills` MCP server as the execution path for those skills.' in text
        assert 'Call `find_agent_skill` to discover the exact `trainer-*` skill before each stage of the workflow.' in text
        assert 'Call `load_agent_skill` before first use of a discovered skill' in text
        assert 'Call `run_agent_skill` to execute the discovered skill runtime' in text
        assert 'the default loop order is `trainer-research` -> `trainer-synthesize` -> `trainer-optimize`.' in text
        assert 'you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Run a minimum of 3 candidate-generation iterations unless the user explicitly requests a different iteration count.' in text
        assert 'If any required training data, validation data, or authored eval assets are missing from the supporting directory, and the user has not supplied the missing pieces directly, you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Use the `trainer-synthesize` skill through MCP to convert source material, user examples, or simulated edge cases into official `evals/evals.json` content plus any supporting `evals/files/` assets, then ensure the explicit `train.jsonl` and `val.jsonl` datasets required by `trainer-optimize` are present.' in text
        assert 'Do not assume `trainer-optimize` performs leader election or baseline comparison internally.' in text
        assert 'If the workflow explicitly needs comparison across multiple optimize outputs, run the `trainer-election` skill through MCP as a separate selection step' in text
        assert 'Keep stable cross-iteration inputs under `inputs/`.' in text
        assert '`iteration-N/optimize/`' in text
        assert '`optimized-prompt.md`' in text
        assert '`optimize-report.json`' in text
        assert '`decision.md`' in text
        assert 'Do not copy a generic `with_skill` / `without_skill` tree unless the workflow actually runs comparative evals.' in text

    def test_trainer_election_mirror_skill_stays_aligned_with_canonical_contract(self):
        canonical_path = REPO_ROOT / "skills" / "trainer-election" / "SKILL.md"
        mirrored_path = REPO_ROOT / ".github" / "skills" / "trainer-election" / "SKILL.md"

        canonical = _read(canonical_path).replace(
            "[skills/trainer-election/references/leader-election.md](./references/leader-election.md)",
            "[skills/trainer-election/references/leader-election.md](REFERENCE_LINK)",
        )
        mirrored = _read(mirrored_path).replace(
            "[skills/trainer-election/references/leader-election.md](../../../skills/trainer-election/references/leader-election.md)",
            "[skills/trainer-election/references/leader-election.md](REFERENCE_LINK)",
        )

        assert canonical == mirrored

    def test_trainer_synthesize_mirror_assets_stay_aligned_with_canonical_contract(self):
        canonical_root = REPO_ROOT / "skills" / "trainer-synthesize"
        mirrored_root = REPO_ROOT / ".github" / "skills" / "trainer-synthesize"

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

    def test_old_loop_agent_file_is_absent(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "prompt-optimization-loop.agent.md"
        assert not agent_path.exists()

    def test_judge_agent_exists_and_is_subagent_only(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "judge.agent.md"
        text = _read(agent_path)

        assert 'name: "judge"' in text
        assert 'user-invocable: false' in text
        assert 'description: "Use when scoring prompt candidates' in text
        assert 'write concise candidate summaries' in text

    def test_conservator_agent_exists_and_is_subagent_only(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "conservator.agent.md"
        text = _read(agent_path)

        assert 'user-invocable: false' in text
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
            assert (workspace_root / "validation").is_dir()
            assert (workspace_root / "inputs" / "source" / "SKILL.md").read_text(encoding="utf-8") == "# Demo\n"

            status_payload = json.loads(status_path.read_text(encoding="utf-8"))
            assert status_payload["workflow_state"] == "pending_engineer_prompt"
            assert status_payload["required_artifacts"]["source_snapshot"].endswith("inputs/source/SKILL.md")

            review_path = workspace_root / "engineer-prompt" / "review.md"
            review_path.write_text("# Review\n", encoding="utf-8")

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
                "--optimize-report",
                str((workspace_root / "iteration-1" / "optimize" / "optimize-report.json").relative_to(REPO_ROOT)),
                "--validation-log",
                str((workspace_root / "validation" / "pytest.txt").relative_to(REPO_ROOT)),
                "--decision-summary",
                str((workspace_root / "decision.md").relative_to(REPO_ROOT)),
            )
            update_payload = json.loads(update_result.stdout)

            assert update_payload["workflow_state"] == "training"
            assert (workspace_root / "iteration-1" / "research").is_dir()
            assert (workspace_root / "iteration-1" / "synthesize").is_dir()
            assert (workspace_root / "iteration-1" / "optimize").is_dir()
            assert (workspace_root / "iteration-1" / "election").is_dir()
            assert (workspace_root / "iteration-1" / "validation").is_dir()

            updated_status = json.loads(status_path.read_text(encoding="utf-8"))
            assert updated_status["required_artifacts"]["engineer_prompt_review"].endswith("engineer-prompt/review.md")
            assert updated_status["required_artifacts"]["latest_iteration_dir"].endswith("iteration-1")
            assert updated_status["required_artifacts"]["train_dataset"].endswith("inputs/train.jsonl")
            assert updated_status["required_artifacts"]["optimize_report"].endswith("iteration-1/optimize/optimize-report.json")

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

            blocked = _run_shell_script(block_path, check=False)
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

            allowed = _run_shell_script(block_path)
            assert allowed.stdout == ""