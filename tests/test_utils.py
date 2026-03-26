"""
Tests for pure utility functions in optimize/scripts/run_optimize.py:
  extract_placeholders, flatten_keys, validate_template_against_task, load_jsonl,
  generate_variants, topk_select
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from run_optimize import (
    extract_placeholders,
    flatten_keys,
    generate_variants,
    load_jsonl,
    topk_select,
    validate_template_against_task,
)

class TestExtractPlaceholders:
    def test_single_placeholder(self):
        assert extract_placeholders("Hello {input}") == {"input"}

    def test_multiple_placeholders(self):
        assert extract_placeholders("{question} — {context}") == {"question", "context"}

    def test_no_placeholders(self):
        assert extract_placeholders("No braces here") == set()

    def test_double_braces_are_not_placeholders(self):
        assert extract_placeholders("{{escaped}}") == set()

    def test_mixed_single_and_double_braces(self):
        assert extract_placeholders("{{literal}} {real}") == {"real"}

    def test_underscore_in_name(self):
        assert extract_placeholders("{my_field}") == {"my_field"}

    def test_alphanumeric_in_name(self):
        assert extract_placeholders("{field1}") == {"field1"}

    def test_digits_only_name_not_matched(self):
        # Python identifiers cannot start with a digit; no placeholder should be extracted
        assert extract_placeholders("{1bad}") == set()

    def test_leading_underscore(self):
        assert extract_placeholders("{_private}") == {"_private"}


class TestFlattenKeys:
    def test_flat_dict(self):
        assert flatten_keys({"a": 1, "b": 2}) == {"a", "b"}

    def test_nested_dict(self):
        result = flatten_keys({"input": {"question": "q", "context": "c"}})
        assert result == {"input", "input.question", "input.context"}

    def test_empty_dict(self):
        assert flatten_keys({}) == set()

    def test_non_dict_returns_empty(self):
        assert flatten_keys("string") == set()
        assert flatten_keys(42) == set()
        assert flatten_keys(None) == set()

    def test_deeply_nested(self):
        result = flatten_keys({"a": {"b": {"c": 1}}})
        assert "a" in result
        assert "a.b" in result
        assert "a.b.c" in result

    def test_prefix_parameter(self):
        result = flatten_keys({"x": 1}, prefix="outer")
        assert "outer.x" in result


class TestValidateTemplateAgainstTask:
    def test_valid_top_level_key(self):
        validate_template_against_task("Answer: {input}", {"input": "hi", "expected": "hello"})

    def test_valid_multiple_keys(self):
        validate_template_against_task(
            "{question} {context}",
            {"question": "What?", "context": "facts", "expected": "42"},
        )

    def test_missing_placeholder_raises(self):
        with pytest.raises(ValueError, match="missing_key"):
            validate_template_against_task("{missing_key}", {"input": "x", "expected": "y"})

    def test_error_message_lists_all_missing(self):
        with pytest.raises(ValueError) as exc_info:
            validate_template_against_task("{a} and {b}", {"c": "v"})
        msg = str(exc_info.value)
        assert "a" in msg
        assert "b" in msg

    def test_double_braces_not_validated(self):
        validate_template_against_task("{{escaped}}", {"input": "x"})

    def test_no_placeholders_always_valid(self):
        validate_template_against_task("No placeholders here.", {"input": "x"})


class TestLoadJsonl:
    def _write_temp(self, lines: list[str]) -> str:
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w") as f:
            f.write("\n".join(lines))
        return path

    def test_single_row(self):
        path = self._write_temp(['{"input": "hi", "expected": "hello"}'])
        rows = load_jsonl(path)
        assert rows == [{"input": "hi", "expected": "hello"}]

    def test_multiple_rows(self):
        path = self._write_temp([
            '{"input": "a", "expected": "1"}',
            '{"input": "b", "expected": "2"}',
        ])
        rows = load_jsonl(path)
        assert len(rows) == 2
        assert rows[0]["input"] == "a"
        assert rows[1]["input"] == "b"

    def test_blank_lines_skipped(self):
        path = self._write_temp([
            '{"input": "a", "expected": "1"}',
            "",
            '{"input": "b", "expected": "2"}',
        ])
        rows = load_jsonl(path)
        assert len(rows) == 2

    def test_returns_list_of_dicts(self):
        path = self._write_temp(['{"input": "x", "expected": "y"}'])
        rows = load_jsonl(path)
        assert isinstance(rows, list)
        assert isinstance(rows[0], dict)

    def test_nested_input_preserved(self):
        row = {"input": {"question": "Q?", "context": "ctx"}, "expected": "A"}
        path = self._write_temp([json.dumps(row)])
        rows = load_jsonl(path)
        assert rows[0]["input"]["question"] == "Q?"


class TestGenerateVariants:
    def test_returns_n_variants(self):
        variants = generate_variants("Hello {input}", n=4)
        assert len(variants) == 4

    def test_returns_one_variant_when_n_is_1(self):
        variants = generate_variants("Hello {input}", n=1)
        assert len(variants) == 1

    def test_each_variant_contains_original_text(self):
        original = "My prompt {input}"
        for v in generate_variants(original, n=3):
            assert original in v

    def test_variants_are_pairwise_distinct(self):
        variants = generate_variants("Hello {input}", n=4)
        assert len(set(variants)) == 4, "All variants must be unique"

    def test_zero_variants_returns_empty_list(self):
        assert generate_variants("Hello {input}", n=0) == []


class TestTopkSelect:
    # Dataset where expected=="pong" so "pong" scores 1.0 and anything else 0.0.
    DATASET = [{"input": "ping", "expected": "pong"}]

    @pytest.mark.asyncio
    async def test_returns_k_items(self):
        variants = ["pong", "hello", "world", "foo"]
        result = await topk_select(variants, self.DATASET, judge_mode="deterministic", k=2)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_k1_returns_single_best(self):
        # "pong" is the exact match → score 1.0; others score 0.0
        variants = ["other", "pong", "another"]
        result = await topk_select(variants, self.DATASET, judge_mode="deterministic", k=1)
        assert len(result) == 1
        assert result[0] == "pong"

    @pytest.mark.asyncio
    async def test_highest_scoring_variant_is_first(self):
        variants = ["no_match", "pong", "also_wrong"]
        result = await topk_select(variants, self.DATASET, judge_mode="deterministic", k=2)
        # The best scorer must appear first
        assert result[0] == "pong"

    @pytest.mark.asyncio
    async def test_all_zero_scores_still_returns_k(self):
        variants = ["a", "b", "c"]
        result = await topk_select(variants, self.DATASET, judge_mode="deterministic", k=2)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_k_larger_than_variants_returns_all(self):
        variants = ["a", "b"]
        result = await topk_select(variants, self.DATASET, judge_mode="deterministic", k=10)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_empty_variants_returns_empty(self):
        result = await topk_select([], self.DATASET, judge_mode="deterministic", k=1)
        assert result == []

    @pytest.mark.asyncio
    async def test_multi_task_dataset_scores_averaged(self):
        # Two tasks: "pong" matches task 1 (score 1.0) but not task 2 (score 0.0) → mean 0.5
        # "bar" matches neither → mean 0.0
        dataset = [
            {"input": "ping", "expected": "pong"},
            {"input": "foo", "expected": "baz"},
        ]
        variants = ["pong", "bar"]
        result = await topk_select(variants, dataset, judge_mode="deterministic", k=1)
        assert result[0] == "pong"
