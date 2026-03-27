"""
Tests for the evaluate_output function (all judge modes) in run_optimize.py.
"""
from __future__ import annotations

from pathlib import Path

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
    async def test_custom_mode_supports_normalized_match(self):
        task = {"input": "x", "expected": "Hello   World", "scoring": "normalized_match"}
        score = await evaluate_output(task, "  hello world  ", judge_mode="custom")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_custom_mode_supports_json_schema(self):
        task = {"input": "x", "expected_json": {"priority": "high"}, "scoring": "json_schema"}
        score = await evaluate_output(task, '{"priority": "high"}', judge_mode="custom")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_custom_mode_rejects_unknown_scoring(self):
        task = {"input": "x", "expected": "y", "scoring": "bogus"}
        with pytest.raises(ValueError, match="Unsupported custom scoring"):
            await evaluate_output(task, "y", judge_mode="custom")


class TestEvaluateOutputLlmJudge:
    @pytest.mark.asyncio
    async def test_llm_judge_mode_uses_client_score(self, tmp_path):
        judge_prompt = tmp_path / "judge.md"
        judge_prompt.write_text("Score this output.\n{input}\n{output}\n", encoding="utf-8")

        class FakeJudgeClient:
            async def judge_score(self, rendered_prompt: str) -> float:
                assert "Score this output" in rendered_prompt
                return 0.75

        task = {"input": "x", "reference": "y", "criteria": ["correctness"]}
        score = await evaluate_output(
            task,
            "candidate output",
            judge_mode="llm_judge",
            judge_prompt_file=str(judge_prompt),
            llm_client=FakeJudgeClient(),
        )
        assert score == 0.75

    @pytest.mark.asyncio
    async def test_llm_judge_mode_rejects_invalid_score(self, tmp_path):
        judge_prompt = tmp_path / "judge.md"
        judge_prompt.write_text("Score this output.\n{input}\n{output}\n", encoding="utf-8")

        class BadJudgeClient:
            async def judge_score(self, rendered_prompt: str) -> float:
                return 2.0

        task = {"input": "x", "reference": "y", "criteria": ["correctness"]}
        with pytest.raises(ValueError, match="between 0.0 and 1.0"):
            await evaluate_output(
                task,
                "candidate output",
                judge_mode="llm_judge",
                judge_prompt_file=str(judge_prompt),
                llm_client=BadJudgeClient(),
            )


class TestEvaluateOutputUnknownMode:
    @pytest.mark.asyncio
    async def test_unknown_mode_raises_value_error(self):
        task = {"input": "x", "expected": "y"}
        with pytest.raises(ValueError, match="Unsupported"):
            await evaluate_output(task, "y", judge_mode="bogus")
