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
from run_optimize import run_optimize


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
        assert "GITHUB_MODELS_API_KEY" not in support_source

        assert "def find_repo_root(" in config_source
        assert "def load_dotenv_file(" in config_source
        assert "def resolve_model_settings(" in config_source
        assert "def create_openai_client(" in config_source

    def test_env_sample_documents_expected_model_secrets(self):
        env_sample = Path(optimize_module.__file__).parent.parent.parent.parent / ".env.sample"
        text = env_sample.read_text(encoding="utf-8")

        assert "GITHUB_MODELS_API_KEY=" in text
        assert "GITHUB_MODELS_ENDPOINT=" in text
        assert "GITHUB_MODELS_MODEL=" in text
        assert "OPENAI_API_KEY=" in text


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


class TestGithubModelsConfiguration:
    @pytest.mark.asyncio
    async def test_loads_github_models_settings_from_root_env(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
        (repo_root / ".env").write_text(
            "\n".join(
                [
                    "GITHUB_MODELS_API_KEY=test-github-token",
                    "GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference",
                    "GITHUB_MODELS_MODEL=openai/gpt-4.1-mini",
                    "GITHUB_MODELS_GRADIENT_MODEL=openai/gpt-4.1-mini",
                    "GITHUB_MODELS_APPLY_EDIT_MODEL=openai/gpt-4.1-mini",
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

        openai_module = sys.modules["openai"]
        assert openai_module.AsyncOpenAI.last_init_kwargs["api_key"] == "test-github-token"
        assert openai_module.AsyncOpenAI.last_init_kwargs["base_url"] == "https://models.github.ai/inference"
        assert result["model_provider"] == "github"
        assert result["model_endpoint"] == "https://models.github.ai/inference"
        assert result["inference_model"] == "openai/gpt-4.1-mini"

    @pytest.mark.asyncio
    async def test_github_models_config_without_api_key_raises_clear_error(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
        (repo_root / ".env").write_text(
            "\n".join(
                [
                    "GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference",
                    "GITHUB_MODELS_MODEL=openai/gpt-4.1-mini",
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

        with pytest.raises(ValueError, match="GITHUB_MODELS_API_KEY|OPENAI_API_KEY"):
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )


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
    @pytest.mark.asyncio
    async def test_debug_only_returns_debug_json(self):
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

    @pytest.mark.asyncio
    async def test_debug_only_does_not_write_files(self, tmp_path):
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


class TestRunOptimizeNormalRun:
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
            "model_provider",
            "model_endpoint",
            "inference_model",
            "gradient_model",
            "apply_edit_model",
            "iterations",
            "train_size",
            "val_size",
            "beam_width",
            "branch_factor",
            "n_runners",
            "judge_mode",
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
