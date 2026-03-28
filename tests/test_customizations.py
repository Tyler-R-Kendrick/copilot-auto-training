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
        assert 'agent-skills/*' in text
        assert 'agents: ["judge", "conservator"]' in text
        assert 'name: "trainer"' in text
        assert 'orchestrate repeated loops across the `trainer-optimize`, `trainer-election`, `trainer-research`, and `trainer-synthesize` skills' in text
        assert 'Use the `agent-skills` MCP server as the execution path for those skills.' in text
        assert 'Call `find_agent_skill` to discover the exact `trainer-*` skill before each stage of the workflow.' in text
        assert 'Call `load_agent_skill` before first use of a discovered skill' in text
        assert 'Call `run_agent_skill` to execute the discovered skill runtime' in text
        assert 'the default loop order is `trainer-research` -> `trainer-synthesize` -> `trainer-optimize` -> `trainer-election`.' in text
        assert 'you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Run a minimum of 3 candidate-generation iterations unless the user explicitly requests a different iteration count.' in text
        assert 'If any required training data, validation data, or authored eval assets are missing from the supporting directory, and the user has not supplied the missing pieces directly, you MUST begin with the `trainer-research` skill before attempting synthesis or optimization.' in text
        assert 'Use the `trainer-synthesize` skill through MCP to convert source material, user examples, or simulated edge cases into official `evals/evals.json` content plus any supporting `evals/files/` assets, then ensure the explicit `train.jsonl` and `val.jsonl` datasets required by `trainer-optimize` are present.' in text
        assert 'You MUST run `trainer-election` on the generated candidates plus the current prompt as a baseline candidate, elect the leader using the validation dataset and available eval artifacts, and apply the elected leader to the target file before finalizing.' in text
        assert 'Run the `trainer-election` skill through MCP on the resulting candidate set plus the current prompt as a baseline candidate, using the validation dataset as the primary election input and authored evals as supporting validation when available.' in text

    def test_trainer_agent_declares_mcp_tool_sequence_and_loop_order(self):
        agent_path = REPO_ROOT / ".github" / "agents" / "trainer.agent.md"
        text = _read(agent_path)

        find_idx = text.index('Call `find_agent_skill`')
        load_idx = text.index('Call `load_agent_skill`')
        run_idx = text.index('Call `run_agent_skill`')
        research_idx = text.index('`trainer-research` -> `trainer-synthesize` -> `trainer-optimize` -> `trainer-election`')

        assert find_idx < load_idx < run_idx < research_idx

    def test_trainer_agent_baseline_rule_matches_optimize_contract(self):
        agent_text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")
        optimize_text = _read(REPO_ROOT / "skills" / "trainer-optimize" / "SKILL.md")

        assert 'plus the current prompt as a baseline candidate' in agent_text
        assert 'includes the original prompt as a baseline' in optimize_text

    def test_trainer_agent_missing_data_flow_uses_all_trainer_skills(self):
        text = _read(REPO_ROOT / ".github" / "agents" / "trainer.agent.md")

        research_idx = text.index('run the `trainer-research` skill through MCP')
        synth_idx = text.index('Use the `trainer-synthesize` skill through MCP')
        optimize_idx = text.index('Run the `trainer-optimize` skill through MCP')
        election_idx = text.index('Run the `trainer-election` skill through MCP')

        assert research_idx < synth_idx < optimize_idx < election_idx

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
        assert 'baseline-candidate preservation during leader election' in text
        assert 'find_agent_skill' in text
        assert 'load_agent_skill' in text
        assert 'run_agent_skill' in text
        assert 'current prompt as a baseline candidate' in text
        assert 'what authored eval manifests support' in text
        assert 'explicit `train.jsonl` or `val.jsonl` inputs are blurred together with authored `evals/evals.json` artifacts' in text


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