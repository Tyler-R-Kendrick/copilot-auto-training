from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "skills" / "engineer-prompt" / "scripts" / "export_skill_prompt.py"
SKILL_DIR = REPO_ROOT / "skills" / "engineer-prompt"


def _load_module():
    spec = importlib.util.spec_from_file_location("engineer_prompt_export", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules.setdefault("engineer_prompt_export", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def engineer_prompt_export_module():
    return _load_module()


def test_render_skill_markdown_preserves_general_prompt_contract(engineer_prompt_export_module):
    contract = engineer_prompt_export_module.build_default_contract(SKILL_DIR)

    markdown = engineer_prompt_export_module.render_skill_markdown(
        contract.seed_instruction_body,
        frontmatter=contract.frontmatter,
    )

    assert markdown.startswith("---\n")
    assert "# Engineer Prompt" in markdown
    assert "The user wants to improve a prompt." in markdown
    assert "references/token-efficient-patterns.md" in markdown
    assert "dspy" not in markdown.lower()


def test_validate_skill_markdown_accepts_current_skill(engineer_prompt_export_module):
    markdown = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

    summary = engineer_prompt_export_module.validate_skill_markdown(markdown)

    assert summary["valid"] is True
    assert summary["missing_sections"] == []
    assert summary["missing_guardrails"] == []
    assert summary["banned_terms_present"] == []


def test_compile_instruction_body_uses_dspy_optimizer(monkeypatch, tmp_path: Path, engineer_prompt_export_module):
    captured: dict[str, object] = {}

    class FakeExample(dict):
        def with_inputs(self, *keys):
            self["_input_keys"] = keys
            return self

    class FakePredict:
        def __init__(self, signature):
            captured["signature"] = signature

        def __call__(self, **kwargs):
            captured["prediction_kwargs"] = kwargs
            return SimpleNamespace(
                instruction_body="# Engineer Prompt\n\n## When to use this skill\n\n- The user wants to improve a prompt.\n\n## Core workflow\n\n1. Diagnose the task shape and failure mode.\n\n## Output contract\n\n1. `Task shape`: what the model is being asked to do\n\n## Diagnose first\n\nPrompt engineering is not just naming a technique.\n\n## Default selection heuristic\n\nUse structured output, grounding, and prompt chaining only when they fit.\n\n## Token-budget guidance\n\nRead `references/token-efficient-patterns.md` when token pressure matters.\n\n## Final rule\n\nIf retrieval is stale, prompt changes are secondary."
            )

    class FakeModule:
        def __call__(self, *args, **kwargs):
            return self.forward(*args, **kwargs)

        def save(self, path, save_program=False, modules_to_serialize=None):
            Path(path).write_text(json.dumps({"saved": save_program}), encoding="utf-8")

    class FakeMIPROv2:
        def __init__(self, **kwargs):
            captured["optimizer_kwargs"] = kwargs

        def compile(self, student, **kwargs):
            captured["compile_kwargs"] = kwargs
            return student

    class FakeLM:
        def __init__(self, model, **kwargs):
            captured["lm"] = {"model": model, **kwargs}

    fake_dspy = SimpleNamespace(
        Signature=type("Signature", (), {}),
        Module=FakeModule,
        Predict=FakePredict,
        Example=FakeExample,
        InputField=lambda **kwargs: kwargs,
        OutputField=lambda **kwargs: kwargs,
        MIPROv2=FakeMIPROv2,
        LM=FakeLM,
        configure=lambda **kwargs: captured.setdefault("configure", kwargs),
    )

    monkeypatch.setattr(engineer_prompt_export_module, "_load_dspy", lambda: fake_dspy)
    contract = engineer_prompt_export_module.build_default_contract(SKILL_DIR)
    body, _compiled = engineer_prompt_export_module.compile_instruction_body(
        contract,
        program_file=tmp_path / "program.json",
        model="openai/gpt-4o-mini",
    )

    assert "The user wants to improve a prompt." in body
    assert captured["optimizer_kwargs"]["max_bootstrapped_demos"] == 0
    assert captured["optimizer_kwargs"]["max_labeled_demos"] == 0
    assert captured["compile_kwargs"]["requires_permission_to_run"] is False
    assert captured["lm"]["model"] == "openai/gpt-4o-mini"
    assert (tmp_path / "program.json").is_file()


def test_validate_only_cli_emits_json_summary():
    output = __import__("subprocess").run(
        [sys.executable, str(MODULE_PATH), "--validate-only"],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(output.stdout)
    assert payload["valid"] is True
    assert payload["banned_terms_present"] == []
