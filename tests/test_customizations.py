from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


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
        assert 'agents: ["Prompt Evaluator", "Regression Review"]' in text
        assert 'name: "trainer"' in text
        assert 'orchestrate repeated loops across the `trainer-optimize`, `trainer-election`, `trainer-research`, and `trainer-synthesize` skills' in text

    def test_old_loop_agent_file_is_absent(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "prompt-optimization-loop.agent.md"
        assert not agent_path.exists()

    def test_prompt_evaluator_agent_exists_and_is_subagent_only(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "prompt-evaluator.agent.md"
        text = _read(agent_path)

        assert 'name: "Prompt Evaluator"' in text
        assert 'user-invocable: false' in text
        assert 'description: "Use when scoring prompt candidates' in text
        assert 'write concise candidate summaries' in text

    def test_regression_review_agent_exists_and_is_subagent_only(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "regression-review.agent.md"
        text = _read(agent_path)

        assert 'user-invocable: false' in text
        assert 'name: "Regression Review"' in text
        assert 'Use when reviewing prompt, dataset, or evaluator changes for likely regressions' in text


class TestInstructionCustomization:
    def test_prompt_file_instruction_exists_with_scalar_applyto(self):
        instructions_path = REPO_ROOT / ".github" / "instructions" / "prompt-optimization.instructions.md"
        text = _read(instructions_path)

        assert 'applyTo: "**/{*.prompt.md,*.prompty,*.instructions.md,SKILL.md,AGENTS.md,*.agent.md}"' in text
        assert 'Use the `trainer-optimize` skill for optimization, `trainer-election` for leader selection, `trainer-research` for public-source discovery' in text

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