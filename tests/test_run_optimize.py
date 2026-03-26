"""
Tests for run_optimize() — the core optimization function in
optimize/scripts/run_optimize.py.

The AGL Trainer and APO are provided by conftest stubs so no real LLM calls happen.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

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
# Algorithm guard
# ---------------------------------------------------------------------------

class TestRunOptimizeAlgorithmGuard:
    @pytest.mark.asyncio
    async def test_verl_returns_ok_false(self):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            algorithm="verl",
        ))
        assert result["ok"] is False
        assert "APO" in result["message"] or "apo" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_verl_does_not_touch_files(self, tmp_path):
        prompt = _write_file(SIMPLE_TEMPLATE)
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        out = str(tmp_path / "out.md")
        await run_optimize(
            prompt_file=prompt, train_file=train, val_file=val,
            algorithm="verl", output_file=out,
        )
        assert not Path(out).exists()


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
    async def test_default_output_path_derived_from_prompt_filename(self, tmp_path):
        prompt_path = str(tmp_path / "support.md")
        Path(prompt_path).write_text(SIMPLE_TEMPLATE, encoding="utf-8")
        train = _write_jsonl(SIMPLE_TRAIN)
        val = _write_jsonl(SIMPLE_VAL)
        result = json.loads(await run_optimize(
            prompt_file=prompt_path,
            train_file=train,
            val_file=val,
        ))
        assert "support" in result["output_file"]
        assert result["output_file"].endswith(".md")

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
