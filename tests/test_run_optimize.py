"""
Tests for run_optimize() — the core optimization function in
optimize/scripts/run_optimize.py.

The AGL Trainer and APO are provided by conftest stubs so no real LLM calls happen.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

import run_optimize as ro
from run_optimize import run_optimize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_file(content: str, suffix: str = ".md") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


def _write_jsonl(rows: list[dict]) -> str:
    lines = [json.dumps(r) for r in rows]
    return _write_file("\n".join(lines), suffix=".jsonl")


SIMPLE_TEMPLATE = "You are a helper. Answer: {input}\n"
SIMPLE_TRAIN = [{"input": "ping", "expected": "pong"}] * 3
SIMPLE_VAL = [{"input": "foo", "expected": "bar"}] * 2


# ---------------------------------------------------------------------------
# Algorithm support
# ---------------------------------------------------------------------------

class TestRunOptimizeAlgorithmSupport:
    @pytest.mark.asyncio
    async def test_verl_returns_ok_true(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        report = str(tmp_path / "report.json")
        result = json.loads(await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            algorithm="verl",
            report_file=report,
        ))
        assert result["ok"] is True
        assert result["algorithm"] == "verl"

    @pytest.mark.asyncio
    async def test_verl_writes_output_file(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "out.md")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            algorithm="verl", output_file=out,
        )
        assert Path(out).exists()

    @pytest.mark.asyncio
    async def test_unknown_algorithm_returns_ok_false(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            algorithm="bogus",
        ))
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

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        openai_module = sys.modules["openai"]
        assert openai_module.AsyncOpenAI.last_init_kwargs["api_key"] == "test-github-token"
        assert openai_module.AsyncOpenAI.last_init_kwargs["base_url"] == "https://models.github.ai/inference"
        assert result["model_provider"] == "github"
        assert result["model_endpoint"] == "https://models.github.ai/inference"
        assert result["gradient_model"] == "openai/gpt-4.1-mini"
        assert result["apply_edit_model"] == "openai/gpt-4.1-mini"

    @pytest.mark.asyncio
    async def test_github_models_config_without_api_key_raises_clear_error(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        (repo_root / "requirements.txt").write_text("agentlightning>=0.1.0\n", encoding="utf-8")
        (repo_root / ".env").write_text(
            "\n".join(
                [
                    "GITHUB_MODELS_ENDPOINT=https://models.github.ai/inference",
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

        with pytest.raises(ValueError, match="GITHUB_MODELS_API_KEY|OPENAI_API_KEY"):
            await run_optimize(
                prompt_file=str(prompt_path),
                train_file=train,
                val_file=val,
            )


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# debug_only mode
# ---------------------------------------------------------------------------

class TestRunOptimizeDebugOnly:
    @pytest.mark.asyncio
    async def test_debug_only_returns_debug_json(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            debug_only=True,
        ))
        assert result["ok"] is True
        assert result["mode"] == "debug"

    @pytest.mark.asyncio
    async def test_debug_only_does_not_write_output_file(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "out.md")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            debug_only=True, output_file=out,
        )
        assert not Path(out).exists()


# ---------------------------------------------------------------------------
# Normal (full) run
# ---------------------------------------------------------------------------

class TestRunOptimizeNormalRun:
    @pytest.mark.asyncio
    async def test_trainer_fit_can_call_asyncio_run_without_nested_loop_failure(self, tmp_path, monkeypatch):
        agl = sys.modules["agentlightning"]
        original_fit = agl.Trainer.fit

        def fit_with_internal_asyncio_run(self, *, agent, train_dataset, val_dataset):
            asyncio.run(asyncio.sleep(0))
            return original_fit(
                self,
                agent=agent,
                train_dataset=train_dataset,
                val_dataset=val_dataset,
            )

        monkeypatch.setattr(agl.Trainer, "fit", fit_with_internal_asyncio_run)

        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt,
            train_file=train,
            val_file=val,
        ))

        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_writes_output_file(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "optimized.md")
        report = str(tmp_path / "report.json")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            output_file=out, report_file=report,
        )
        assert Path(out).exists()
        assert Path(out).read_text(encoding="utf-8").strip()

    @pytest.mark.asyncio
    async def test_writes_report_file(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "optimized.md")
        report_path = str(tmp_path / "report.json")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            output_file=out, report_file=report_path,
        )
        assert Path(report_path).exists()
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        assert report["ok"] is True
        assert report["algorithm"] == "apo"

    @pytest.mark.asyncio
    async def test_report_contains_required_fields(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "optimized.md")
        report_path = str(tmp_path / "report.json")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            output_file=out, report_file=report_path,
            iterations=2, beam_width=2, branch_factor=2, n_runners=2,
        )
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        required = {
            "ok", "algorithm", "prompt_file", "output_file",
            "iterations", "train_size", "val_size",
            "beam_width", "branch_factor", "n_runners", "judge_mode",
        }
        assert required <= set(report.keys())

    @pytest.mark.asyncio
    async def test_report_train_and_val_sizes(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)         # 3 rows
        val = _write_jsonl(SIMPLE_VAL)             # 2 rows
        out = str(tmp_path / "optimized.md")
        report_path = str(tmp_path / "report.json")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            output_file=out, report_file=report_path,
        )
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
        assert report["train_size"] == 3
        assert report["val_size"] == 2

    @pytest.mark.asyncio
    async def test_default_output_path_is_prompt_file_itself(self, tmp_path):
        """When no output_file is given the report's output_file is the prompt_file."""
        prompt_path = str(tmp_path / "support.md")
        Path(prompt_path).write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt_path,
            train_file=train,
            val_file=val,
        ))
        assert result["output_file"] == prompt_path

    @pytest.mark.asyncio
    async def test_default_report_path_is_workspace_benchmark(self, tmp_path, monkeypatch):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        monkeypatch.chdir(tmp_path)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        expected_report = prompt_dir / "support-workspace" / "benchmark.json"
        assert Path(result["report_file"]) == expected_report
        assert expected_report.is_file()
        assert result["workspace_dir"] == str(prompt_dir / "support-workspace")

    @pytest.mark.asyncio
    async def test_returns_json_string(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result_raw = await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            output_file=str(tmp_path / "out.md"),
            report_file=str(tmp_path / "report.json"),
        )
        assert isinstance(result_raw, str)
        parsed = json.loads(result_raw)
        assert parsed["ok"] is True


class TestExplicitDatasetResolution:
    @pytest.mark.asyncio
    async def test_missing_explicit_datasets_returns_modern_request(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir(parents=True)
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")

        result = json.loads(await run_optimize(prompt_file=str(prompt_path)))

        assert result["ok"] is False
        assert result["needs_user_input"] is True
        assert result["suggested_train_file"] == str(tmp_path / "datasets" / "train.jsonl")
        assert result["suggested_val_file"] == str(tmp_path / "datasets" / "val.jsonl")
        assert result["workspace_dir"] == str(prompt_dir / "support-workspace")
        assert result["benchmark_file"] == str(prompt_dir / "support-workspace" / "benchmark.json")
        assert not (prompt_dir / ".evals").exists()
        assert not (prompt_dir / "support-workspace").exists()


class TestMissingDatasetRequests:
    @pytest.mark.asyncio
    async def test_missing_datasets_return_generation_request_without_legacy_scaffold(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")

        result = json.loads(await run_optimize(prompt_file=str(prompt_path)))

        assert result["ok"] is False
        assert result["needs_user_input"] is True
        assert len(result["required_info"]) == 3
        assert result["recommended_user_interaction"] == "dialog"
        assert result["input_dialog"]["title"] == "Collect optimization datasets"
        assert [field["key"] for field in result["input_dialog"]["fields"][:3]] == [
            "train_file",
            "val_file",
            "csv_file",
        ]
        assert result["prompt_file"] == str(prompt_path)
        assert result["missing_files"] == [
            str(tmp_path / "datasets" / "train.jsonl"),
            str(tmp_path / "datasets" / "val.jsonl"),
        ]
        assert not (prompt_dir / ".evals").exists()

    @pytest.mark.asyncio
    async def test_missing_datasets_request_includes_modern_targets_and_questions(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "qa.md"
        prompt_path.write_text("Context: {context}\nQuestion: {question}\n", encoding="utf-8")

        result = json.loads(await run_optimize(prompt_file=str(prompt_path)))

        assert result["required_info"] == [
            "A small set of representative examples or a CSV file to turn into train.jsonl and val.jsonl.",
            "Values for every prompt placeholder: context, question.",
            "The expected answer format or scoring rule for each example.",
        ]
        assert "Provide explicit train and validation datasets" in result["message"]
        assert result["suggested_train_file"] == str(tmp_path / "datasets" / "train.jsonl")
        assert result["suggested_val_file"] == str(tmp_path / "datasets" / "val.jsonl")
        assert result["benchmark_file"] == str(prompt_dir / "qa-workspace" / "benchmark.json")
        dialog_fields = {field["key"]: field for field in result["input_dialog"]["fields"]}
        assert dialog_fields["placeholder_values"]["required"] is True
        assert "context, question" in dialog_fields["placeholder_values"]["description"]


class TestElectionDelegation:
    @pytest.mark.asyncio
    async def test_run_optimize_delegates_search_and_leader_election(self, tmp_path, monkeypatch):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        async def fake_election_search(**kwargs):
            assert kwargs["prompt_text"] == SIMPLE_TEMPLATE
            assert kwargs["iterations"] == 3
            return {
                "best_prompt": SIMPLE_TEMPLATE + "\n<!-- election winner -->",
                "persisted_candidates": [
                    {
                        "template": SIMPLE_TEMPLATE,
                        "score": 0.0,
                        "raw_score": 0.0,
                        "penalty": 0.0,
                        "source": "baseline",
                        "is_baseline": True,
                        "is_winner": False,
                        "risks": [],
                        "improvements": [],
                        "steering_hits": [],
                    },
                    {
                        "template": SIMPLE_TEMPLATE + "\n<!-- election winner -->",
                        "score": 1.0,
                        "raw_score": 1.0,
                        "penalty": 0.0,
                        "source": "election_candidate_1",
                        "is_baseline": False,
                        "is_winner": True,
                        "risks": [],
                        "improvements": [],
                        "steering_hits": [],
                    },
                ],
                "steering_applied": False,
            }

        monkeypatch.setattr(ro, "run_election_search", fake_election_search)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        assert result["ok"] is True
        assert any(candidate["source"] == "baseline" for candidate in result["candidates"])
        assert "<!-- election winner -->" in prompt_path.read_text(encoding="utf-8")

    @pytest.mark.asyncio
    async def test_successful_run_writes_benchmark_report_under_workspace(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        )

        benchmark_path = prompt_dir / "support-workspace" / "benchmark.json"
        manifest = json.loads(benchmark_path.read_text(encoding="utf-8"))

        assert manifest["prompt_file"] == str(prompt_path)
        assert manifest["train_file"] == train
        assert manifest["val_file"] == val
        assert manifest["workspace_dir"] == str(prompt_dir / "support-workspace")

    @pytest.mark.asyncio
    async def test_default_report_file_points_to_workspace_benchmark(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        )

        benchmark_path = prompt_dir / "support-workspace" / "benchmark.json"
        manifest = json.loads(benchmark_path.read_text(encoding="utf-8"))

        assert manifest["report_file"] == str(benchmark_path)


# ---------------------------------------------------------------------------
# Leader replaces target prompt (core new behaviour)
# ---------------------------------------------------------------------------

class TestLeaderReplacesTargetPrompt:
    @pytest.mark.asyncio
    async def test_leader_replaces_prompt_file(self, tmp_path):
        """After a successful run the original prompt_file is overwritten with the best prompt."""
        prompt_path = tmp_path / "my_prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        )

        updated = prompt_path.read_text(encoding="utf-8")
        # The stub Trainer appends "<!-- optimized -->" to signal the winner was applied.
        assert "<!-- optimized -->" in updated

    @pytest.mark.asyncio
    async def test_prompt_file_content_differs_from_original_after_run(self, tmp_path):
        """The prompt_file content changes after optimization (it was replaced by the leader)."""
        prompt_path = tmp_path / "my_prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        original_content = prompt_path.read_text(encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        )

        updated = prompt_path.read_text(encoding="utf-8")
        assert updated != original_content, (
            "prompt_file should be updated in-place with the winning prompt"
        )

    @pytest.mark.asyncio
    async def test_report_output_file_points_to_prompt_file_when_no_output_given(self, tmp_path):
        """When no output_file is specified, report['output_file'] == prompt_file."""
        prompt_path = tmp_path / "my_prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        assert result["output_file"] == str(prompt_path)

    @pytest.mark.asyncio
    async def test_explicit_output_file_also_written_with_leader_content(self, tmp_path):
        """When output_file is specified, that path also gets the winning content."""
        prompt_path = tmp_path / "my_prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        out_path = tmp_path / "backup.md"
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            output_file=str(out_path),
        )

        # The backup copy also contains the winning prompt
        assert out_path.exists()
        assert "<!-- optimized -->" in out_path.read_text(encoding="utf-8")

    @pytest.mark.asyncio
    async def test_prompt_file_unchanged_on_debug_only(self, tmp_path):
        """debug_only mode must NOT modify the prompt_file."""
        prompt_path = tmp_path / "my_prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        original_content = prompt_path.read_text(encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            debug_only=True,
        )

        assert prompt_path.read_text(encoding="utf-8") == original_content


# ---------------------------------------------------------------------------
# Selection behavior: baseline candidate + single-candidate fallback
# ---------------------------------------------------------------------------

class TestSelectionBehavior:
    """
    When APO yields exactly one candidate the skill must fall back to generating
    n_variants paraphrases of that candidate and electing the leader via topk,
    always including the original prompt as a baseline candidate.
    """

    @pytest.mark.asyncio
    async def test_single_candidate_pool_includes_baseline(self, tmp_path, monkeypatch):
        captured_pool: list[str] = []

        async def capture_select(variants: list[str], dataset: list[dict], judge_mode: str = "deterministic", k: int = 1) -> list[str]:
            captured_pool.extend(variants)
            return [variants[-1]]

        monkeypatch.setattr(ro, "topk_select", capture_select)

        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=3,
        )

        assert SIMPLE_TEMPLATE in captured_pool
        assert prompt_path.read_text(encoding="utf-8") == SIMPLE_TEMPLATE

    @pytest.mark.asyncio
    async def test_multi_candidate_pool_includes_baseline(self, tmp_path, monkeypatch):
        agl = sys.modules["agentlightning"]
        monkeypatch.setattr(agl.APO, "_num_candidates", 3)

        captured_pool: list[str] = []

        async def capture_select(variants: list[str], dataset: list[dict], judge_mode: str = "deterministic", k: int = 1) -> list[str]:
            captured_pool.extend(variants)
            return [variants[-1]]

        monkeypatch.setattr(ro, "topk_select", capture_select)

        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=3,
        )

        assert SIMPLE_TEMPLATE in captured_pool
        assert any("<!-- optimized -->" in item for item in captured_pool)
        assert prompt_path.read_text(encoding="utf-8") == SIMPLE_TEMPLATE

    @pytest.mark.asyncio
    async def test_single_candidate_leader_written_to_prompt_file(self, tmp_path):
        """prompt_file is replaced with the topk winner (a generated variant)."""
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=3,
        )

        content = prompt_path.read_text(encoding="utf-8")
        # The stub candidate has "<!-- optimized -->" and the best variant must
        # be derived from that candidate (so it also contains the marker).
        assert "<!-- optimized -->" in content

    @pytest.mark.asyncio
    async def test_single_candidate_variant_marker_present(self, tmp_path):
        """The elected leader is one of the generated variants, not the raw candidate."""
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=3,
        )

        content = prompt_path.read_text(encoding="utf-8")
        # Stub generate_variants appends "<!-- variant N -->" markers.
        assert "<!-- variant" in content

    @pytest.mark.asyncio
    async def test_multi_candidate_does_not_generate_variants(self, tmp_path, monkeypatch):
        """When APO returns > 1 candidate, the variant generation path is NOT taken."""
        agl = sys.modules["agentlightning"]
        monkeypatch.setattr(agl.APO, "_num_candidates", 3)

        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=3,
        )

        content = prompt_path.read_text(encoding="utf-8")
        # Multi-candidate path still uses final scored selection and should keep
        # algorithm-generated candidates in the candidate pool.
        assert "<!-- variant" not in content
        assert "<!-- optimized -->" in content

    @pytest.mark.asyncio
    async def test_n_variants_parameter_controls_variant_count(self, tmp_path, monkeypatch):
        """n_variants controls how many variants are generated in the fallback path."""
        generated: list[list[str]] = []

        import run_optimize as ro
        original_generate = ro.generate_variants

        def capturing_generate(prompt_text: str, n: int) -> list[str]:
            result = original_generate(prompt_text, n)
            generated.append(result)
            return result

        monkeypatch.setattr(ro, "generate_variants", capturing_generate)

        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=5,
        )

        assert generated, "generate_variants was not called"
        assert len(generated[0]) == 5

    @pytest.mark.asyncio
    async def test_report_ok_true_on_single_candidate_path(self, tmp_path):
        """The JSON report still reports ok=True even via the variant path."""
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        report_path = tmp_path / "report.json"

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
            report_file=str(report_path),
        )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["ok"] is True


class TestCandidatePersistence:
    @pytest.mark.asyncio
    async def test_report_contains_persisted_candidates(self, tmp_path):
        prompt_path = tmp_path / "prompt.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        report_path = tmp_path / "report.json"

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
            report_file=str(report_path),
        )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert "candidates" in report
        assert any(candidate["is_baseline"] for candidate in report["candidates"])
        assert any(candidate["is_winner"] for candidate in report["candidates"])


class TestRunArtifactsAndSteering:
    @pytest.mark.asyncio
    async def test_debug_only_does_not_create_temp_run_artifacts(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            debug_only=True,
        )

        assert not (prompt_dir / "support-workspace").exists()

    @pytest.mark.asyncio
    async def test_writes_temp_run_artifacts_under_workspace_iterations(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        workspace_dir = prompt_dir / "support-workspace"
        run_dirs = sorted(path for path in workspace_dir.iterdir() if path.is_dir())

        assert workspace_dir.exists()
        assert (workspace_dir / "steering.md").exists()
        assert len(run_dirs) == 1
        assert run_dirs[0].name == "iteration-001"
        assert (run_dirs[0] / "summary.md").exists()
        assert (run_dirs[0] / "report.json").exists()
        assert (run_dirs[0] / "candidates").is_dir()
        assert list((run_dirs[0] / "candidates").glob("*.md"))
        assert result["run_id"].startswith("run-")
        assert result["run_dir"] == str(run_dirs[0])
        assert result["steering_file"] == str(workspace_dir / "steering.md")

    @pytest.mark.asyncio
    async def test_report_persists_artifact_paths_and_candidate_metadata(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        report_path = tmp_path / "report.json"

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            report_file=str(report_path),
            n_variants=2,
        )

        report = json.loads(report_path.read_text(encoding="utf-8"))
        run_report = json.loads(Path(report["run_dir"]).joinpath("report.json").read_text(encoding="utf-8"))

        assert report["run_id"].startswith("run-")
        assert Path(report["run_dir"]).is_dir()
        assert Path(report["steering_file"]).is_file()
        assert run_report == report
        assert all(
            {"raw_score", "score", "penalty", "risks", "improvements", "steering_hits"} <= set(candidate)
            for candidate in report["candidates"]
        )

    @pytest.mark.asyncio
    async def test_candidate_markdown_captures_scores_risks_and_content(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
        ))

        candidate_file = next(Path(result["run_dir"]).joinpath("candidates").glob("*.md"))
        candidate_markdown = candidate_file.read_text(encoding="utf-8")

        assert "# Candidate" in candidate_markdown
        assert "- Adjusted score:" in candidate_markdown
        assert "- Raw score:" in candidate_markdown
        assert "## Risks" in candidate_markdown
        assert "## Content" in candidate_markdown
        assert "```md" in candidate_markdown

    @pytest.mark.asyncio
    async def test_steering_file_bootstraps_default_guidance_and_run_history(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
        ))

        steering = Path(result["steering_file"]).read_text(encoding="utf-8")

        assert "# Optimization Steering" in steering
        assert "## Global Guidance" in steering
        assert "Avoid reward hacking" in steering
        assert "Avoid verbose, irrelevant, or redundant outputs." in steering
        assert f"## Run {result['run_id']}" in steering

    @pytest.mark.asyncio
    async def test_run_summary_captures_winner_failures_and_improvements(self, tmp_path):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
        )

        workspace_dir = prompt_dir / "support-workspace"
        run_dir = next(path for path in workspace_dir.iterdir() if path.is_dir())
        summary = (run_dir / "summary.md").read_text(encoding="utf-8")

        assert "## Winner" in summary
        assert "## Best Results" in summary
        assert "## Failure Analysis" in summary
        assert "avoid reward hacking" in summary.lower()
        assert "avoid verbose, irrelevant, or redundant outputs" in summary.lower()
        assert "## Improvements" in summary

    @pytest.mark.asyncio
    async def test_steering_file_accumulates_runs_and_influences_selection(self, tmp_path, monkeypatch):
        prompt_dir = tmp_path / "prompts"
        prompt_dir.mkdir()
        prompt_path = prompt_dir / "support.md"
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)

        async def always_expected(prompt_text: str, task: dict[str, object]) -> str:
            return str(task["expected"])

        monkeypatch.setattr(ro, "run_candidate", always_expected)

        await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
        )

        workspace_dir = prompt_dir / "support-workspace"
        steering_file = workspace_dir / "steering.md"
        steering_file.write_text(
            steering_file.read_text(encoding="utf-8")
            + "\n- Avoid pattern: <!-- optimized -->\n",
            encoding="utf-8",
        )
        prompt_path.write_text(SIMPLE_TEMPLATE, encoding="utf-8")

        result = json.loads(await run_optimize(
            prompt_file=str(prompt_path),
            train_file=train,
            val_file=val,
            n_variants=2,
        ))

        updated_prompt = prompt_path.read_text(encoding="utf-8")
        steering = steering_file.read_text(encoding="utf-8")

        assert updated_prompt == SIMPLE_TEMPLATE
        assert result["steering_applied"] is True
        assert steering.count("## Run") >= 2


class TestGitignoreCoverage:
    def test_gitignore_ignores_prompt_adjacent_tmp_dirs(self):
        gitignore = Path(".gitignore").read_text(encoding="utf-8")
        assert "**/*-workspace/" in gitignore
