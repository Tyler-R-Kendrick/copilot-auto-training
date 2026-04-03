from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "skills" / "engineer-prompt" / "scripts" / "export_skill_prompt.py"


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


def _write_prompt(path: Path) -> Path:
    path.write_text(
        "---\n"
        "title: Example Prompt\n"
        "owner: tests\n"
        "---\n\n"
        "# Support Prompt\n\n"
        "Answer the request using `${context}`.\n"
        "Return exactly three bullets and keep the wording concise.\n",
        encoding="utf-8",
    )
    return path


def test_build_prompt_task_extracts_generic_prompt_fields(tmp_path: Path, engineer_prompt_export_module):
    prompt_path = _write_prompt(tmp_path / "prompt.md")
    context_path = tmp_path / "context.md"
    context_path.write_text("Reference material for the prompt rewrite.", encoding="utf-8")

    task = engineer_prompt_export_module.build_prompt_task(
        str(prompt_path),
        goal="Make the prompt clearer.",
        context_files=[str(context_path)],
        required_text=["three bullets"],
        forbidden_text=["DSPy"],
        min_body_length=20,
    )

    assert task.prompt_path == prompt_path.resolve()
    assert task.frontmatter["title"] == "Example Prompt"
    assert "`${context}`" in task.prompt_body
    assert task.optimization_goal == "Make the prompt clearer."
    assert task.required_text == ("three bullets",)
    assert task.forbidden_text == ("DSPy",)
    assert task.placeholders == ("${context}",)
    assert str(context_path.resolve()) in task.supporting_context
    assert "Reference material for the prompt rewrite." in task.supporting_context


def test_build_prompt_task_raises_for_missing_context_file(tmp_path: Path, engineer_prompt_export_module):
    prompt_path = _write_prompt(tmp_path / "prompt.md")

    with pytest.raises(FileNotFoundError):
        engineer_prompt_export_module.build_prompt_task(
            str(prompt_path),
            context_files=[str(tmp_path / "missing-context.md")],
        )


def test_validate_prompt_markdown_accepts_generic_prompt(engineer_prompt_export_module):
    markdown = (
        "# Prompt\n\n"
        "Use `${context}` to answer the user.\n"
        "Return exactly three bullets.\n"
    )

    summary = engineer_prompt_export_module.validate_prompt_markdown(
        markdown,
        expected_placeholders=("${context}",),
        required_text=("three bullets",),
        forbidden_text=("DSPy",),
        min_body_length=20,
    )

    assert summary["valid"] is True
    assert summary["missing_placeholders"] == []
    assert summary["missing_required_text"] == []
    assert summary["forbidden_text_present"] == []


def test_compile_prompt_uses_dspy_optimizer(monkeypatch, tmp_path: Path, engineer_prompt_export_module):
    dspy_call_trace: dict[str, object] = {}
    optimized_prompt = """# Better Prompt

Use `${context}` to answer the request.
Return exactly three bullets.
Keep the wording concise.
"""

    class FakeExample:
        def __init__(self, **kwargs):
            self._data = dict(kwargs)
            for key, value in kwargs.items():
                setattr(self, key, value)

        def with_inputs(self, *keys):
            self.input_keys = keys
            return self

        def get(self, key, default=None):
            return self._data.get(key, default)

    class FakePredict:
        def __init__(self, signature):
            dspy_call_trace["signature"] = signature

        def __call__(self, **kwargs):
            dspy_call_trace["prediction_kwargs"] = kwargs
            return SimpleNamespace(optimized_prompt=optimized_prompt)

    class FakeModule:
        def __call__(self, *args, **kwargs):
            return self.forward(*args, **kwargs)

        def save(self, path, save_program=False, modules_to_serialize=None):
            Path(path).write_text(json.dumps({"saved": save_program}), encoding="utf-8")

    class FakeMIPROv2:
        def __init__(self, **kwargs):
            dspy_call_trace["optimizer_kwargs"] = kwargs

        def compile(self, student, **kwargs):
            dspy_call_trace["compile_kwargs"] = kwargs
            return student

    class FakeLM:
        def __init__(self, model, **kwargs):
            dspy_call_trace["lm"] = {"model": model, **kwargs}

    fake_dspy = SimpleNamespace(
        Signature=type("Signature", (), {}),
        Module=FakeModule,
        Predict=FakePredict,
        Example=FakeExample,
        InputField=lambda **kwargs: kwargs,
        OutputField=lambda **kwargs: kwargs,
        MIPROv2=FakeMIPROv2,
        LM=FakeLM,
        configure=lambda **kwargs: dspy_call_trace.setdefault("configure", kwargs),
    )

    monkeypatch.setattr(engineer_prompt_export_module, "_load_dspy", lambda: fake_dspy)
    prompt_path = _write_prompt(tmp_path / "prompt.md")
    task = engineer_prompt_export_module.build_prompt_task(
        str(prompt_path),
        goal="Make the prompt clearer.",
        required_text=["three bullets"],
        forbidden_text=["DSPy"],
        min_body_length=20,
    )
    body, _compiled = engineer_prompt_export_module.compile_prompt(
        task,
        program_file=tmp_path / "program.json",
        model="openai/gpt-4o-mini",
    )

    assert "`${context}`" in body
    assert "three bullets" in body
    assert all(example.input_keys for example in dspy_call_trace["compile_kwargs"]["trainset"])
    assert dspy_call_trace["optimizer_kwargs"]["max_bootstrapped_demos"] == 0
    assert dspy_call_trace["optimizer_kwargs"]["max_labeled_demos"] == 0
    assert dspy_call_trace["compile_kwargs"]["requires_permission_to_run"] is False
    assert dspy_call_trace["lm"]["model"] == "openai/gpt-4o-mini"
    assert (tmp_path / "program.json").is_file()


def test_validate_only_cli_emits_json_summary(tmp_path: Path):
    prompt_path = _write_prompt(tmp_path / "prompt.md")
    output = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--validate-only",
            "--prompt-file",
            str(prompt_path),
            "--required-text",
            "three bullets",
            "--forbidden-text",
            "DSPy",
            "--min-body-length",
            "20",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(output.stdout)
    assert payload["valid"] is True
    assert payload["missing_placeholders"] == []
    assert payload["forbidden_text_present"] == []
    assert payload["prompt_file"] == str(prompt_path.resolve())


def test_validate_only_cli_reports_missing_prompt_file(tmp_path: Path):
    missing_prompt = tmp_path / "missing.md"
    output = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            "--validate-only",
            "--prompt-file",
            str(missing_prompt),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert output.returncode == 1
    assert str(missing_prompt.resolve()) in output.stderr


def test_exporter_script_exists():
    assert MODULE_PATH.is_file()
