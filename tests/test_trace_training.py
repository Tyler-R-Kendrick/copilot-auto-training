from __future__ import annotations

import json
from pathlib import Path
import runpy
import sys
import types

import pytest

import train as trace_train
from run_optimize import TraceSelfOptimizationPolicy, build_trace_case_summary, parse_trace_search_budget


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")


def test_trace_policy_returns_supported_algorithm_and_budget_shapes():
    policy = TraceSelfOptimizationPolicy()

    algorithm = policy.choose_algorithm(8, 4, 1, "deterministic")
    budget = policy.choose_search_budget(8, 4, 1, "deterministic")

    assert algorithm.data in {"apo", "verl"}
    parsed_budget = json.loads(budget.data)
    assert set(parsed_budget) == {"iterations", "beam_width", "branch_factor", "n_runners"}
    assert all(int(value) >= 1 for value in parsed_budget.values())


def test_trace_policy_prefers_verl_for_large_or_complex_cases():
    policy = TraceSelfOptimizationPolicy()

    assert policy.choose_algorithm(8, 4, 1, "llm_judge").data == "verl"
    assert policy.choose_algorithm(64, 8, 1, "deterministic").data == "verl"
    assert policy.choose_algorithm(8, 4, 4, "deterministic").data == "verl"

    parsed_budget = json.loads(policy.choose_search_budget(96, 8, 4, "deterministic").data)
    assert parsed_budget == {
        "iterations": 4,
        "beam_width": 6,
        "branch_factor": 5,
        "n_runners": 6,
    }


def test_build_trace_case_summary_includes_case_shape():
    summary = build_trace_case_summary(
        "Answer: {input}\n",
        [{"input": "ping", "expected": "pong"}],
        [{"input": "foo", "expected": "bar"}],
        "deterministic",
        prompt_file="examples/prompt.md",
    )

    assert "prompt_file: examples/prompt.md" in summary
    assert "train_size: 1" in summary
    assert "val_size: 1" in summary
    assert "judge_mode: deterministic" in summary
    assert "placeholders: input" in summary


def test_build_trace_case_summary_handles_empty_prompt_without_placeholders():
    summary = build_trace_case_summary("", [], [], "custom")

    assert "prompt_file: <memory>" in summary
    assert "placeholders: <none>" in summary
    assert "<empty>" in summary


def test_parse_trace_search_budget_defaults_and_clamps_values():
    parsed = parse_trace_search_budget(
        '{"algorithm": "verl", "iterations": 0, "beam_width": "6", "branch_factor": -2, "n_runners": 3}',
        default_algorithm="apo",
    )

    assert parsed == {
        "algorithm": "verl",
        "iterations": 1,
        "beam_width": 6,
        "branch_factor": 1,
        "n_runners": 3,
    }


def test_parse_trace_search_budget_supports_trace_nodes_and_invalid_payloads():
    parsed = parse_trace_search_budget(types.SimpleNamespace(data="not-json"), default_algorithm="bogus")

    assert parsed == {
        "algorithm": "apo",
        "iterations": 3,
        "beam_width": 4,
        "branch_factor": 4,
        "n_runners": 4,
    }


def test_normalize_training_case_requires_required_fields():
    with pytest.raises(ValueError, match="missing required fields"):
        trace_train.normalize_training_case({"prompt_file": "prompt.md"})


def test_normalize_training_case_preserves_optional_judge_prompt_file():
    normalized = trace_train.normalize_training_case(
        {
            "prompt_file": "prompt.md",
            "train_file": "train.jsonl",
            "val_file": "val.jsonl",
            "judge_mode": "llm_judge",
            "judge_prompt_file": "judge.md",
        }
    )

    assert normalized["judge_prompt_file"] == "judge.md"


def test_load_training_cases_supports_jsonl_cases_file(tmp_path):
    cases_path = tmp_path / "cases.jsonl"
    _write_jsonl(
        cases_path,
        [
            {
                "prompt_file": "prompt.md",
                "train_file": "train.jsonl",
                "val_file": "val.jsonl",
                "judge_mode": "custom",
            }
        ],
    )

    cases = trace_train.load_training_cases(cases_file=str(cases_path))

    assert cases == [
        {
            "prompt_file": "prompt.md",
            "train_file": "train.jsonl",
            "val_file": "val.jsonl",
            "judge_mode": "custom",
        }
    ]


def test_load_training_cases_rejects_mixed_sources():
    with pytest.raises(ValueError, match="either --cases-file or"):
        trace_train.load_training_cases(
            cases_file="cases.jsonl",
            prompt_file="prompt.md",
            train_file="train.jsonl",
            val_file="val.jsonl",
        )


def test_load_training_cases_supports_single_explicit_case():
    cases = trace_train.load_training_cases(
        prompt_file="prompt.md",
        train_file="train.jsonl",
        val_file="val.jsonl",
        judge_mode="llm_judge",
        judge_prompt_file="judge.md",
    )

    assert cases == [
        {
            "prompt_file": "prompt.md",
            "train_file": "train.jsonl",
            "val_file": "val.jsonl",
            "judge_mode": "llm_judge",
            "judge_prompt_file": "judge.md",
        }
    ]


def test_load_training_cases_requires_complete_input():
    with pytest.raises(ValueError, match="Provide --cases-file"):
        trace_train.load_training_cases(prompt_file="prompt.md", train_file="train.jsonl")


def test_configure_trace_environment_exports_resolved_model_settings(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)
    monkeypatch.delenv("TRACE_LITELLM_MODEL", raising=False)

    monkeypatch.setattr(
        trace_train,
        "resolve_model_settings",
        lambda prompt_file: {
            "provider": "github",
            "api_key": "token",
            "base_url": "https://models.github.ai/inference",
            "inference_model": "openai/gpt-4.1-mini",
        },
    )

    settings = trace_train.configure_trace_environment("prompt.md")

    assert settings["provider"] == "github"
    assert settings["inference_model"] == "openai/gpt-4.1-mini"
    assert trace_train.os.environ["OPENAI_API_KEY"] == "token"
    assert trace_train.os.environ["OPENAI_BASE_URL"] == "https://models.github.ai/inference"
    assert trace_train.os.environ["OPENAI_API_BASE"] == "https://models.github.ai/inference"
    assert trace_train.os.environ["TRACE_LITELLM_MODEL"] == "openai/gpt-4.1-mini"


@pytest.mark.asyncio
async def test_score_prompt_text_requires_inference_model(monkeypatch):
    monkeypatch.setattr(trace_train, "create_openai_client", lambda prompt_file: (object(), {"inference_model": None}))

    with pytest.raises(ValueError, match="requires GITHUB_MODELS_MODEL or OPENAI_MODEL"):
        await trace_train.score_prompt_text("Answer: {input}", [], prompt_file="prompt.md", judge_mode="deterministic")


@pytest.mark.asyncio
async def test_score_prompt_text_returns_zero_when_no_assessments(monkeypatch):
    monkeypatch.setattr(trace_train, "create_openai_client", lambda prompt_file: (object(), {"inference_model": "model"}))

    async def fake_assess_candidates(*args, **kwargs):
        return []

    monkeypatch.setattr(trace_train, "assess_candidates", fake_assess_candidates)

    score = await trace_train.score_prompt_text(
        "Answer: {input}",
        [{"input": "ping", "expected": "pong"}],
        prompt_file="prompt.md",
        judge_mode="deterministic",
    )

    assert score == 0.0


def test_execute_training_case_returns_case_report(tmp_path, monkeypatch):
    prompt_path = tmp_path / "prompt.md"
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"

    prompt_path.write_text("Answer: {input}\n", encoding="utf-8")
    _write_jsonl(train_path, [{"input": "ping", "expected": "pong"}])
    _write_jsonl(val_path, [{"input": "foo", "expected": "bar"}])

    async def fake_run_optimize(**kwargs):
        return json.dumps(
            {
                "ok": True,
                "optimized_prompt": "Optimized answer: {input}\n",
                "candidate_count": 2,
            }
        )

    async def fake_score_prompt_text(prompt_text, dataset, *, prompt_file, judge_mode, judge_prompt_file=None):
        return 0.9 if prompt_text.startswith("Optimized") else 0.4

    monkeypatch.setattr(trace_train, "run_optimize", fake_run_optimize)
    monkeypatch.setattr(trace_train, "score_prompt_text", fake_score_prompt_text)

    report_node = trace_train.execute_training_case(
        json.dumps(
            {
                "prompt_file": str(prompt_path),
                "train_file": str(train_path),
                "val_file": str(val_path),
                "judge_mode": "deterministic",
            },
            sort_keys=True,
        ),
        "apo",
        json.dumps({"iterations": 3, "beam_width": 4, "branch_factor": 4, "n_runners": 4}),
    )
    report = json.loads(report_node.data)

    assert report["prompt_file"] == str(prompt_path)
    assert report["algorithm"] == "apo"
    assert report["baseline_score"] == 0.4
    assert report["optimized_score"] == 0.9
    assert report["improvement"] == 0.5
    assert report["candidate_count"] == 2


def test_execute_training_case_preserves_manual_followup_payload(tmp_path, monkeypatch):
    prompt_path = tmp_path / "prompt.md"
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"

    prompt_path.write_text("Answer: {input}\n", encoding="utf-8")
    _write_jsonl(train_path, [{"input": "ping", "expected": "pong"}])
    _write_jsonl(val_path, [{"input": "foo", "expected": "bar"}])

    async def fake_run_optimize(**kwargs):
        return json.dumps(
            {
                "ok": True,
                "mode": "manual_followup",
                "optimized_prompt": "Answer: {input}\n",
                "followup_instruction": "rerun later",
                "agent_handoff_instruction": "answer model prompt locally",
                "rerun_command": "python run_optimize.py ...",
                "model_prompt": "prompt for model",
                "blocker_reason": "RateLimitError",
                "candidate_count": 0,
            }
        )

    monkeypatch.setattr(trace_train, "run_optimize", fake_run_optimize)

    report_node = trace_train.execute_training_case(
        json.dumps(
            {
                "prompt_file": str(prompt_path),
                "train_file": str(train_path),
                "val_file": str(val_path),
                "judge_mode": "deterministic",
            },
            sort_keys=True,
        ),
        "apo",
        json.dumps({"iterations": 3, "beam_width": 4, "branch_factor": 4, "n_runners": 4}),
    )
    report = json.loads(report_node.data)

    assert report["mode"] == "manual_followup"
    assert report["baseline_score"] is None
    assert report["optimized_score"] is None
    assert report["followup_instruction"] == "rerun later"
    assert report["blocker_reason"] == "RateLimitError"


def test_render_training_feedback_covers_positive_zero_and_negative_cases():
    positive = trace_train.render_training_feedback(
        {"improvement": 0.125, "algorithm": "apo", "iterations": 3, "beam_width": 4}
    )
    neutral = trace_train.render_training_feedback(
        {"improvement": 0.0, "algorithm": "apo", "iterations": 3, "beam_width": 4}
    )
    negative = trace_train.render_training_feedback(
        {"improvement": -0.25, "algorithm": "apo", "iterations": 3, "beam_width": 4}
    )

    assert "improved validation score" in positive
    assert "did not improve over the baseline" in neutral
    assert "regressed validation score" in negative


def test_serialize_trace_parameters_handles_name_fallbacks_and_complex_values():
    class ComplexValue:
        def __str__(self):
            return "complex-value"

    parameters = [
        types.SimpleNamespace(name="explicit_name", data=1),
        types.SimpleNamespace(py_name="fallback_name", data=ComplexValue()),
        types.SimpleNamespace(data=None),
    ]
    policy = types.SimpleNamespace(parameters=lambda: parameters)

    serialized = trace_train.serialize_trace_parameters(policy)

    assert serialized == [
        {"name": "explicit_name", "value": 1},
        {"name": "fallback_name", "value": "complex-value"},
        {"name": "parameter_3", "value": None},
    ]


def test_train_cases_requires_positive_epochs_and_cases():
    with pytest.raises(ValueError, match="At least one training case"):
        trace_train.train_cases([], epochs=1)

    with pytest.raises(ValueError, match="epochs must be at least 1"):
        trace_train.train_cases(
            [{"prompt_file": "prompt.md", "train_file": "train.jsonl", "val_file": "val.jsonl"}],
            epochs=0,
        )


def test_train_cases_without_inference_model_returns_manual_followup(tmp_path, monkeypatch):
    prompt_path = tmp_path / "prompt.md"
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"

    prompt_path.write_text("Answer: {input}\n", encoding="utf-8")
    _write_jsonl(train_path, [{"input": "ping", "expected": "pong"}])
    _write_jsonl(val_path, [{"input": "foo", "expected": "bar"}])

    monkeypatch.setattr(
        trace_train,
        "configure_trace_environment",
        lambda prompt_file: {"provider": "github", "inference_model": None},
    )

    result = trace_train.train_cases(
        [{"prompt_file": str(prompt_path), "train_file": str(train_path), "val_file": str(val_path)}],
        epochs=1,
    )

    assert result["ok"] is True
    assert result["mode"] == "manual_followup"
    assert result["epochs"] == 0
    assert result["history"][0]["mode"] == "manual_followup"


def test_train_cases_runs_multiple_epochs_and_writes_report(tmp_path, monkeypatch):
    prompt_path = tmp_path / "prompt.md"
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"
    report_path = tmp_path / "train-report.json"

    prompt_path.write_text("Answer: {input}\n", encoding="utf-8")
    _write_jsonl(train_path, [{"input": "ping", "expected": "pong"}])
    _write_jsonl(val_path, [{"input": "foo", "expected": "bar"}])

    class FakePolicy:
        def __init__(self):
            self._parameters = [types.SimpleNamespace(name="alpha", data=0.1)]

        def parameters(self):
            return self._parameters

        def choose_algorithm(self, *args):
            return types.SimpleNamespace(data="apo")

        def choose_search_budget(self, *args):
            return types.SimpleNamespace(
                data=json.dumps({"iterations": 3, "beam_width": 4, "branch_factor": 4, "n_runners": 4})
            )

    optimizer_state: dict[str, Any] = {}

    class FakeOptoPrime:
        def __init__(self, params, llm, log):
            optimizer_state["params"] = list(params)
            optimizer_state["llm"] = llm
            optimizer_state["log"] = log
            optimizer_state["zero_calls"] = 0
            optimizer_state["backward_calls"] = []
            optimizer_state["step_calls"] = 0

        def zero_feedback(self):
            optimizer_state["zero_calls"] += 1

        def backward(self, report_node, feedback):
            optimizer_state["backward_calls"].append((report_node.data, feedback))

        def step(self):
            optimizer_state["step_calls"] += 1

    class FakeLLM:
        def __init__(self, model):
            self.model = model

    monkeypatch.setattr(trace_train, "TraceSelfOptimizationPolicy", FakePolicy)
    monkeypatch.setattr(
        trace_train,
        "configure_trace_environment",
        lambda prompt_file: {"provider": "github", "inference_model": "openai/gpt-4.1-mini"},
    )
    monkeypatch.setattr(
        trace_train,
        "execute_training_case",
        lambda *args, **kwargs: types.SimpleNamespace(
            data=json.dumps(
                {
                    "prompt_file": str(prompt_path),
                    "train_file": str(train_path),
                    "val_file": str(val_path),
                    "judge_mode": "deterministic",
                    "algorithm": "apo",
                    "iterations": 3,
                    "beam_width": 4,
                    "branch_factor": 4,
                    "n_runners": 4,
                    "baseline_score": 0.4,
                    "optimized_score": 0.9,
                    "improvement": 0.5,
                    "candidate_count": 2,
                    "optimized_prompt": "Optimized answer: {input}\n",
                },
                sort_keys=True,
            )
        ),
    )
    monkeypatch.setitem(sys.modules, "opto.optimizers", types.SimpleNamespace(OptoPrime=FakeOptoPrime))
    monkeypatch.setitem(sys.modules, "opto.optimizers.optoprime", types.SimpleNamespace(LLM=FakeLLM))

    result = trace_train.train_cases(
        [{"prompt_file": str(prompt_path), "train_file": str(train_path), "val_file": str(val_path)}],
        epochs=2,
        report_file=str(report_path),
    )

    assert result["ok"] is True
    assert result["epochs"] == 2
    assert result["case_count"] == 1
    assert result["report_file"] == str(report_path)
    assert len(result["history"]) == 2
    assert result["history"][0]["epoch"] == 1
    assert result["history"][1]["epoch"] == 2
    assert result["learned_parameters"] == [{"name": "alpha", "value": 0.1}]
    assert optimizer_state["zero_calls"] == 2
    assert optimizer_state["step_calls"] == 2
    assert len(optimizer_state["backward_calls"]) == 2
    assert report_path.exists()


def test_main_uses_loader_and_training_pipeline(monkeypatch, capsys):
    monkeypatch.setattr(trace_train, "load_training_cases", lambda **kwargs: [{"prompt_file": "prompt.md", "train_file": "train.jsonl", "val_file": "val.jsonl"}])
    monkeypatch.setattr(trace_train, "train_cases", lambda cases, epochs, report_file=None: {"ok": True, "epochs": epochs, "case_count": len(cases)})

    exit_code = trace_train.main(["--prompt-file", "prompt.md", "--train-file", "train.jsonl", "--val-file", "val.jsonl", "--epochs", "2"])

    assert exit_code == 0
    assert '"epochs": 2' in capsys.readouterr().out


def test_train_module_entrypoint_executes_main(tmp_path, monkeypatch, capsys):
    import run_optimize as optimize_module

    prompt_path = tmp_path / "prompt.md"
    train_path = tmp_path / "train.jsonl"
    val_path = tmp_path / "val.jsonl"

    prompt_path.write_text("Answer: {input}\n", encoding="utf-8")
    _write_jsonl(train_path, [{"input": "ping", "expected": "pong"}])
    _write_jsonl(val_path, [{"input": "foo", "expected": "bar"}])

    async def fake_run_optimize(**kwargs):
        return json.dumps({"ok": True, "optimized_prompt": "Optimized answer", "candidate_count": 1})

    async def fake_assess_candidates(*args, **kwargs):
        return [{"score": 0.5}]

    class FakeOptoPrime:
        def __init__(self, params, llm, log):
            self.params = list(params)

        def zero_feedback(self):
            return None

        def backward(self, report_node, feedback):
            return None

        def step(self):
            return None

    class FakeLLM:
        def __init__(self, model):
            self.model = model

    monkeypatch.setattr(
        optimize_module,
        "resolve_model_settings",
        lambda prompt_file: {
            "provider": "github",
            "api_key": "token",
            "base_url": "https://models.github.ai/inference",
            "inference_model": "openai/gpt-4.1-mini",
        },
    )
    monkeypatch.setattr(optimize_module, "run_optimize", fake_run_optimize)
    monkeypatch.setattr(optimize_module, "create_openai_client", lambda prompt_file: (object(), {"inference_model": "openai/gpt-4.1-mini"}))
    monkeypatch.setattr(optimize_module, "assess_candidates", fake_assess_candidates)
    monkeypatch.setitem(sys.modules, "opto.optimizers", types.SimpleNamespace(OptoPrime=FakeOptoPrime))
    monkeypatch.setitem(sys.modules, "opto.optimizers.optoprime", types.SimpleNamespace(LLM=FakeLLM))

    script_path = Path(__file__).resolve().parent.parent / "skills" / "trainer-optimize" / "scripts" / "train.py"
    monkeypatch.setattr(
        "sys.argv",
        [str(script_path), "--prompt-file", str(prompt_path), "--train-file", str(train_path), "--val-file", str(val_path), "--epochs", "1"],
    )

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path(str(script_path), run_name="__main__")

    assert exc_info.value.code == 0
    assert '"ok": true' in capsys.readouterr().out.lower()