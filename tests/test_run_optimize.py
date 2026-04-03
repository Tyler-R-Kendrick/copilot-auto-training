"""
Tests for run_optimize() — the single-shot optimization entry point in
trainer-optimize/scripts/run_optimize.py.

External integrations are provided through test doubles in conftest, but the
optimize business logic is validated against the public runtime contract.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

import run_optimize as optimize_module
from run_optimize import _make_rollout, run_optimize, run_optimize_sync
from training.lightning_integration import ProviderBackedOpenAIClient


def _write_file(content: str, suffix: str = ".md") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def _write_jsonl(rows: list[dict]) -> str:
    return _write_file("\n".join(json.dumps(row) for row in rows), suffix=".jsonl")


SIMPLE_TEMPLATE = "You are a helper. Answer: {input}\n"
SIMPLE_TRAIN = [{"input": "ping", "expected": "pong"}] * 3
SIMPLE_VAL = [{"input": "foo", "expected": "bar"}] * 2


class TestRunOptimizeModuleShape:
    def test_runtime_stays_compact_and_single_shot(self):
        source = Path(optimize_module.__file__).read_text(encoding="utf-8")

        assert len(source.splitlines()) < 500
        assert "def generate_variants(" not in source
        assert "def score_variants(" not in source
        assert "def topk_select(" not in source
        assert "run_election_search(" not in source
        assert "steering" not in source

    def test_main_uses_sync_entry_point_for_live_runs(self):
        source = Path(optimize_module.__file__).read_text(encoding="utf-8")

        assert "result = run_optimize_sync(" in source

    def test_support_module_has_no_dataset_synthesis_helpers(self):
        support_source = Path(optimize_module.__file__).with_name("optimize_support.py").read_text(encoding="utf-8")

        assert "def build_missing_dataset_request(" not in support_source
        assert "def derive_dataset_paths(" not in support_source
        assert "def derive_workspace_paths(" not in support_source
        assert "needs_user_input" not in support_source

    def test_env_and_secret_management_moves_to_config_module(self):
        scripts_dir = Path(optimize_module.__file__).parent
        support_source = (scripts_dir / "optimize_support.py").read_text(encoding="utf-8")
        config_source = (scripts_dir / "config.py").read_text(encoding="utf-8")

        assert "def find_repo_root(" not in support_source
        assert "def load_dotenv_file(" not in support_source
        assert "def resolve_model_settings(" not in support_source
        assert "def create_openai_client(" not in support_source

        assert "def find_repo_root(" in config_source
        assert "def load_dotenv_file(" in config_source
        assert "def resolve_model_settings(" in config_source
        assert "def create_openai_client(" in config_source

    def test_env_sample_documents_expected_copilot_model_setting(self):
        env_sample = Path(optimize_module.__file__).parent.parent.parent.parent / ".env.sample"
        text = env_sample.read_text(encoding="utf-8")

        assert "COPILOT_MODEL" in text


class TestRunOptimizeAlgorithmSupport:
    @pytest.mark.asyncio
    async def test_verl_returns_ok_true(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        report = str(tmp_path / "report.json")

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                algorithm="verl",
                report_file=report,
            )
        )

        assert result["ok"] is True
        assert result["algorithm"] == "verl"
        assert result["optimized_prompt"].strip()

    @pytest.mark.asyncio
    async def test_unknown_algorithm_returns_ok_false(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                algorithm="bogus",
            )
        )

        assert result["ok"] is False
        assert "Unsupported algorithm" in result["message"]

    @pytest.mark.asyncio
    async def test_apo_receives_provider_backed_openai_client(self, monkeypatch):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        agl = sys.modules["agentlightning"]
        captured: dict[str, object] = {}
        original_apo = agl.APO

        class CapturingAPO(original_apo):
            def __init__(self, client, **kwargs):
                captured["client"] = client
                super().__init__(client, **kwargs)

        monkeypatch.setattr(agl, "APO", CapturingAPO)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                algorithm="apo",
            )
        )

        assert result["ok"] is True
        assert isinstance(captured["client"], ProviderBackedOpenAIClient)


class TestCopilotConfiguration:
    @pytest.mark.asyncio
    async def test_loads_copilot_settings_from_root_env(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
        (repo_root / ".env").write_text(
            "\n".join(
                [
                    "COPILOT_MODEL=default",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        prompt_path = repo_root / "prompts" / "support.md"
        prompt_path.parent.mkdir(parents=True)
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )
        )

        assert result["model"] == "default"


class TestRunOptimizeInputValidation:
    @pytest.mark.asyncio
    async def test_empty_train_raises(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl([])
        val = _write_jsonl(SIMPLE_VAL)

        with pytest.raises(ValueError, match="train_file"):
            await run_optimize(prompt_file=prompt, train_file=train, val_file=val)

    @pytest.mark.asyncio
    async def test_empty_val_raises(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl([])

        with pytest.raises(ValueError, match="val_file"):
            await run_optimize(prompt_file=prompt, train_file=train, val_file=val)

    @pytest.mark.asyncio
    async def test_invalid_placeholder_raises(self):
        prompt = _write_file("Answer {missing_field}\n")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        with pytest.raises(ValueError, match="missing_field"):
            await run_optimize(prompt_file=prompt, train_file=train, val_file=val)


class TestRunOptimizeDebugOnly:
    @staticmethod
    def _stub_complete_text(monkeypatch, response_text: str = "pong") -> None:
        async def fake_complete_text(llm_client, model_name, prompt_text, *, metadata=None):
            return response_text

        monkeypatch.setattr(optimize_module.support, "_complete_text", fake_complete_text)

    @pytest.mark.asyncio
    async def test_debug_only_returns_debug_json(self, monkeypatch):
        self._stub_complete_text(monkeypatch)
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                debug_only=True,
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "debug"
        assert result["input_binding"] == "placeholders"
        assert "sample_score" in result
        assert result["dashboard_url"].startswith("http://")

    @pytest.mark.asyncio
    async def test_debug_only_skips_algorithm_instantiation_and_trainer_dev(self, monkeypatch):
        self._stub_complete_text(monkeypatch)
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        agl = sys.modules["agentlightning"]

        def fail_algorithm(*args, **kwargs):
            raise AssertionError("debug-only should not instantiate optimization algorithms")

        def fail_dev(self, *, agent, train_dataset, val_dataset):
            raise AssertionError("debug-only should not call Trainer.dev")

        monkeypatch.setattr(agl, "APO", fail_algorithm)
        monkeypatch.setattr(agl.Trainer, "dev", fail_dev)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                debug_only=True,
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "debug"

    @pytest.mark.asyncio
    async def test_debug_only_verl_does_not_require_hydra_bound_algorithm_import(self, monkeypatch):
        self._stub_complete_text(monkeypatch)
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        agl = sys.modules["agentlightning"]

        def hydra_failure(*args, **kwargs):
            raise ModuleNotFoundError("No module named 'hydra'")

        monkeypatch.setattr(agl, "VERL", hydra_failure)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                algorithm="verl",
                debug_only=True,
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "debug"

    @pytest.mark.asyncio
    async def test_debug_only_injects_implicit_task_context_for_prompts_without_placeholders(self, monkeypatch):
        prompt = _write_file("You are a careful reviewer.\n")
        train = _write_jsonl([{"input": "review this change", "expected": "pong"}])
        val = _write_jsonl(SIMPLE_VAL)

        captured: dict[str, str] = {}

        async def capture_prompt(llm_client, model_name, prompt_text):
            captured["prompt"] = prompt_text
            return "pong"

        monkeypatch.setattr(optimize_module.support, "_complete_text", capture_prompt)

        result = json.loads(
            await run_optimize(
                prompt_file=prompt,
                train_file=train,
                val_file=val,
                debug_only=True,
            )
        )

        assert result["ok"] is True
        assert result["input_binding"] == "implicit_task_context"
        assert "Task Context:" in captured["prompt"]
        assert "review this change" in captured["prompt"]

    @pytest.mark.asyncio
    async def test_debug_only_does_not_write_files(self, tmp_path, monkeypatch):
        self._stub_complete_text(monkeypatch)
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        out = tmp_path / "out.md"
        report = tmp_path / "report.json"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            debug_only=True,
            output_file=str(out),
            report_file=str(report),
            in_place=True,
        )

        assert prompt_path.read_text(encoding="utf-8") == SIMPLE_TEMPLATE
        assert not out.exists()
        assert not report.exists()


class TestOptimizeSupportMetadataCompatibility:
    @pytest.mark.asyncio
    async def test_call_with_optional_metadata_omits_metadata_for_signature_without_metadata(self):
        captured = {}

        async def no_metadata_call(*, model, input):
            captured["kwargs"] = {"model": model, "input": input}
            return "ok"

        result = await optimize_module.support._call_with_optional_metadata(
            no_metadata_call,
            model="default",
            input="ping",
            metadata={"episode_id": "ep-1"},
        )

        assert result == "ok"
        assert captured["kwargs"] == {"model": "default", "input": "ping"}

    @pytest.mark.asyncio
    async def test_complete_text_with_metadata_fallback_skips_metadata_for_simple_stub(self, monkeypatch):
        captured = {}

        async def fake_complete_text(llm_client, model_name, prompt_text):
            captured["args"] = (llm_client, model_name, prompt_text)
            return "ok"

        monkeypatch.setattr(optimize_module.support, "_complete_text", fake_complete_text)

        result = await optimize_module.support._complete_text_with_metadata_fallback(
            llm_client=object(),
            model_name="default",
            prompt="prompt body",
            metadata={"episode_id": "ep-2"},
        )

        assert result == "ok"
        assert captured["args"][1:] == ("default", "prompt body")


class TestRunOptimizeManualFallback:
    @pytest.mark.asyncio
    async def test_missing_model_returns_manual_followup_payload(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            optimize_module,
            "create_openai_client",
            lambda pf: (
                sys.modules["openai"].AsyncOpenAI(),
                {
                    "model": None,
                    "repo_root": str(tmp_path),
                },
            ),
        )

        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "manual_followup"
        assert result["optimized_prompt"] == SIMPLE_TEMPLATE
        assert result["optimized_prompt_changed"] is False
        assert result["agent_handoff_instruction"].startswith("Use the current @trainer agent")
        assert result["rerun_command"].startswith("python ")
        assert "save the markdown reply as `optimized-prompt.md`" in result["followup_instruction"]
        assert "Baseline prompt:" in result["model_prompt"]
        assert "Training examples" in result["model_prompt"]
        assert result["sample_runtime_prompt"].strip().startswith("You are a helper. Answer: ping")

    @pytest.mark.asyncio
    async def test_rate_limit_returns_manual_followup_and_writes_report(self, tmp_path, monkeypatch):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        report_path = tmp_path / "report.json"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        agl = sys.modules["agentlightning"]

        def raise_rate_limit(self, *, agent, train_dataset, val_dataset):
            raise RuntimeError("RateLimitError: Too many requests")

        monkeypatch.setattr(agl.Trainer, "fit", raise_rate_limit)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
                report_file=str(report_path),
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "manual_followup"
        assert "RateLimitError" in result["blocker_reason"]
        assert result["report_file"] == str(report_path)
        assert report_path.exists()
        assert json.loads(report_path.read_text(encoding="utf-8"))["mode"] == "manual_followup"

    @pytest.mark.asyncio
    async def test_auth_session_error_returns_manual_followup_and_writes_report(self, tmp_path, monkeypatch):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        report_path = tmp_path / "report.json"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        agl = sys.modules["agentlightning"]

        def raise_auth_session_error(self, *, agent, train_dataset, val_dataset):
            raise RuntimeError(
                "CopilotInferenceError: Session error: Execution failed: "
                "Error: Session was not created with authentication info or custom provider"
            )

        monkeypatch.setattr(agl.Trainer, "fit", raise_auth_session_error)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
                report_file=str(report_path),
            )
        )

        assert result["ok"] is True
        assert result["mode"] == "manual_followup"
        assert "authentication info" in result["blocker_reason"]
        assert result["report_file"] == str(report_path)
        assert report_path.exists()
        assert json.loads(report_path.read_text(encoding="utf-8"))["mode"] == "manual_followup"


class TestRolloutCandidateValidation:
    @pytest.mark.asyncio
    async def test_invalid_candidate_placeholder_returns_zero_instead_of_failing(self, monkeypatch):
        async def explode_if_called(*args, **kwargs):
            raise AssertionError("evaluate_output should not run for invalid prompt candidates")

        monkeypatch.setattr(optimize_module, "evaluate_output", explode_if_called)

        rollout = _make_rollout(
            "deterministic",
            llm_client=object(),
            model_name="openai/gpt-4.1-mini",
        )

        score = await rollout(
            {"input": "ping", "expected": "pong"},
            sys.modules["agentlightning"].PromptTemplate("Answer: {missing_field}"),
        )

        assert score == 0.0


class TestRunOptimizeNormalRun:
    def test_sync_entry_point_returns_json_string(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        raw = run_optimize_sync(prompt_file=prompt, train_file=train, val_file=val)
        parsed = json.loads(raw)

        assert isinstance(raw, str)
        assert parsed["ok"] is True

    @pytest.mark.asyncio
    async def test_run_uses_isolated_agentlightning_port_when_env_not_set(self, tmp_path, monkeypatch):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        monkeypatch.delenv("AGL_SERVER_HOST", raising=False)
        monkeypatch.delenv("AGL_SERVER_PORT", raising=False)

        agl = sys.modules["agentlightning"]
        original_fit = agl.Trainer.fit
        observed: dict[str, str | None] = {}

        def fit_with_env_capture(self, *, agent, train_dataset, val_dataset):
            observed["host"] = os.getenv("AGL_SERVER_HOST")
            observed["port"] = os.getenv("AGL_SERVER_PORT")
            return original_fit(self, agent=agent, train_dataset=train_dataset, val_dataset=val_dataset)

        monkeypatch.setattr(agl.Trainer, "fit", fit_with_env_capture)

        result = json.loads(await run_optimize(prompt_file=str(prompt_path), train_file=train, val_file=val))

        assert result["ok"] is True
        assert observed["host"] == "127.0.0.1"
        assert observed["port"] is not None
        assert observed["port"].isdigit()
        assert result["dashboard_url"] == f"http://127.0.0.1:{observed['port']}"
        assert os.getenv("AGL_SERVER_HOST") is None
        assert os.getenv("AGL_SERVER_PORT") is None

    @pytest.mark.asyncio
    async def test_run_preserves_explicit_agentlightning_endpoint(self, tmp_path, monkeypatch):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        monkeypatch.setenv("AGL_SERVER_HOST", "localhost")
        monkeypatch.setenv("AGL_SERVER_PORT", "48123")

        agl = sys.modules["agentlightning"]
        original_fit = agl.Trainer.fit
        observed: dict[str, str | None] = {}

        def fit_with_env_capture(self, *, agent, train_dataset, val_dataset):
            observed["host"] = os.getenv("AGL_SERVER_HOST")
            observed["port"] = os.getenv("AGL_SERVER_PORT")
            return original_fit(self, agent=agent, train_dataset=train_dataset, val_dataset=val_dataset)

        monkeypatch.setattr(agl.Trainer, "fit", fit_with_env_capture)

        result = json.loads(await run_optimize(prompt_file=str(prompt_path), train_file=train, val_file=val))

        assert result["ok"] is True
        assert observed == {"host": "localhost", "port": "48123"}
        assert result["dashboard_url"] == "http://localhost:48123"

    @pytest.mark.asyncio
    async def test_trainer_fit_can_call_asyncio_run_without_nested_loop_failure(self, tmp_path, monkeypatch):
        agl = sys.modules["agentlightning"]
        original_fit = agl.Trainer.fit

        def fit_with_internal_asyncio_run(self, *, agent, train_dataset, val_dataset):
            asyncio.run(asyncio.sleep(0))
            return original_fit(self, agent=agent, train_dataset=train_dataset, val_dataset=val_dataset)

        monkeypatch.setattr(agl.Trainer, "fit", fit_with_internal_asyncio_run)

        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(prompt_file=prompt, train_file=train, val_file=val))

        assert result["ok"] is True
        assert result["optimized_prompt"].strip()

    @pytest.mark.asyncio
    async def test_returns_json_string(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        raw = await run_optimize(prompt_file=prompt, train_file=train, val_file=val)
        parsed = json.loads(raw)

        assert isinstance(raw, str)
        assert parsed["ok"] is True

    @pytest.mark.asyncio
    async def test_default_run_returns_optimized_prompt_without_writing_files(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )
        )

        assert result["optimized_prompt"].strip()
        assert result["optimized_prompt"] != SIMPLE_TEMPLATE
        assert result["output_file"] is None
        assert result["report_file"] is None
        assert result["prompt_file_updated"] is False
        assert prompt_path.read_text(encoding="utf-8") == SIMPLE_TEMPLATE
        assert not (tmp_path / "prompt-workspace").exists()
        assert not (tmp_path / ".trainer-workspace" / "prompt").exists()

    @pytest.mark.asyncio
    async def test_explicit_output_file_writes_only_output_file(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        output_path = tmp_path / "optimized.md"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
                output_file=str(output_path),
            )
        )

        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8") == result["optimized_prompt"]
        assert prompt_path.read_text(encoding="utf-8") == SIMPLE_TEMPLATE
        assert result["output_file"] == str(output_path)
        assert result["prompt_file_updated"] is False

    @pytest.mark.asyncio
    async def test_in_place_updates_prompt_file(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
                in_place=True,
            )
        )

        assert prompt_path.read_text(encoding="utf-8") == result["optimized_prompt"]
        assert result["prompt_file_updated"] is True

    @pytest.mark.asyncio
    async def test_report_file_is_written_only_when_requested(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        report_path = tmp_path / "report.json"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
                report_file=str(report_path),
            )
        )

        assert report_path.exists()
        written = json.loads(report_path.read_text(encoding="utf-8"))
        assert written == result
        assert written["report_file"] == str(report_path)

    @pytest.mark.asyncio
    async def test_result_contains_required_fields(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )
        )

        required = {
            "ok",
            "run_id",
            "algorithm",
            "prompt_file",
            "train_file",
            "val_file",
            "optimized_prompt",
            "output_file",
            "report_file",
            "prompt_file_updated",
            "model",
            "iterations",
            "train_size",
            "val_size",
            "beam_width",
            "branch_factor",
            "n_runners",
            "judge_mode",
            "input_binding",
            "candidate_count",
        }
        assert required <= set(result)


class TestExplicitDatasetResolution:
    @pytest.mark.asyncio
    async def test_missing_explicit_datasets_return_explicit_input_error(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir(parents=True)
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")

        result = json.loads(await run_optimize(prompt_file=str(prompt_path)))

        assert result["ok"] is False
        assert "Explicit train_file and val_file are required" in result["message"]
        assert result["missing_files"] == ["train_file", "val_file"]
        assert "needs_user_input" not in result
        assert "input_dialog" not in result

    @pytest.mark.asyncio
    async def test_missing_dataset_paths_report_missing_arguments_and_files(self, tmp_path):
        prompt_path = tmp_path / "qa.md"
        prompt_path.write_text("Context: {context}\nQuestion: {question}\n", encoding="utf-8")

        result = json.loads(
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=str(tmp_path / "missing-train.jsonl"),
                val_file=str(tmp_path / "missing-val.jsonl"),
            )
        )

        assert result["ok"] is False
        assert str(tmp_path / "missing-train.jsonl") in result["message"]
        assert str(tmp_path / "missing-val.jsonl") in result["message"]
        assert result["missing_files"] == [
            str(tmp_path / "missing-train.jsonl"),
            str(tmp_path / "missing-val.jsonl"),
        ]
