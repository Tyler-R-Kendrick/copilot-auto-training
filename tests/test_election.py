"""Tests for the extracted leader-election runtime in election/scripts/run_election.py."""
from __future__ import annotations

import sys

import pytest

from run_election import build_selection_pool, run_election_search


SIMPLE_TEMPLATE = "You are a helper. Answer: {input}\n"
SIMPLE_TRAIN = [{"input": "ping", "expected": "pong"}] * 3
SIMPLE_VAL = [{"input": "foo", "expected": "bar"}] * 2


class TestBuildSelectionPool:
    def test_single_candidate_pool_includes_variants_and_baseline(self):
        pool, sources = build_selection_pool(
            candidate_templates=[SIMPLE_TEMPLATE + "\n<!-- optimized -->"],
            baseline_prompt=SIMPLE_TEMPLATE,
            algorithm="election",
            n_variants=3,
        )

        assert len(pool) == 4
        assert pool[-1] == SIMPLE_TEMPLATE
        assert sources == ["variant_1", "variant_2", "variant_3", "baseline"]

    def test_multi_candidate_pool_uses_algorithm_candidate_labels(self):
        pool, sources = build_selection_pool(
            candidate_templates=[
                SIMPLE_TEMPLATE + "\n<!-- optimized -->",
                SIMPLE_TEMPLATE + "\n<!-- optimized -->\n<!-- candidate 2 -->",
            ],
            baseline_prompt=SIMPLE_TEMPLATE,
            algorithm="election",
            n_variants=3,
        )

        assert len(pool) == 3
        assert sources == ["election_candidate_1", "election_candidate_2", "baseline"]


class TestRunElectionSearch:
    @pytest.mark.asyncio
    async def test_returns_persisted_candidates_with_winner_and_baseline(self):
        openai_client = sys.modules["openai"].AsyncOpenAI()
        model_settings = {
            "gradient_model": "openai/gpt-4.1-mini",
            "apply_edit_model": "openai/gpt-4.1-mini",
        }

        result = await run_election_search(
            prompt_text=SIMPLE_TEMPLATE,
            train_dataset=SIMPLE_TRAIN,
            val_dataset=SIMPLE_VAL,
            openai_client=openai_client,
            model_settings=model_settings,
            algorithm="apo",
            iterations=3,
            beam_width=4,
            branch_factor=4,
            n_runners=4,
            judge_mode="deterministic",
            n_variants=2,
            steering_text="",
        )

        assert "best_prompt" in result
        assert any(candidate["is_baseline"] for candidate in result["persisted_candidates"])
        assert any(candidate["is_winner"] for candidate in result["persisted_candidates"])
        assert result["steering_applied"] is False