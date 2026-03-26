"""
Tests for the evaluate_output function (all judge modes) in run_optimize.py.
"""
from __future__ import annotations

import pytest

from run_optimize import evaluate_output


class TestEvaluateOutputDeterministic:
    @pytest.mark.asyncio
    async def test_exact_match_returns_one(self):
        task = {"input": "x", "expected": "hello"}
        score = await evaluate_output(task, "hello", judge_mode="deterministic")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_whitespace_trimmed_before_compare(self):
        task = {"input": "x", "expected": "hello"}
        score = await evaluate_output(task, "  hello  ", judge_mode="deterministic")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_mismatch_returns_zero(self):
        task = {"input": "x", "expected": "hello"}
        score = await evaluate_output(task, "world", judge_mode="deterministic")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_missing_expected_raises(self):
        task = {"input": "x"}
        with pytest.raises(ValueError, match="expected"):
            await evaluate_output(task, "anything", judge_mode="deterministic")

    @pytest.mark.asyncio
    async def test_default_mode_is_deterministic(self):
        task = {"input": "x", "expected": "match"}
        score = await evaluate_output(task, "match")
        assert score == 1.0


class TestEvaluateOutputCustom:
    @pytest.mark.asyncio
    async def test_custom_mode_raises_not_implemented(self):
        task = {"input": "x", "expected": "y"}
        with pytest.raises(NotImplementedError):
            await evaluate_output(task, "y", judge_mode="custom")


class TestEvaluateOutputLlmJudge:
    @pytest.mark.asyncio
    async def test_llm_judge_mode_raises_not_implemented(self):
        task = {"input": "x", "expected": "y"}
        with pytest.raises(NotImplementedError):
            await evaluate_output(task, "y", judge_mode="llm_judge")


class TestEvaluateOutputUnknownMode:
    @pytest.mark.asyncio
    async def test_unknown_mode_raises_value_error(self):
        task = {"input": "x", "expected": "y"}
        with pytest.raises(ValueError, match="Unsupported"):
            await evaluate_output(task, "y", judge_mode="bogus")
