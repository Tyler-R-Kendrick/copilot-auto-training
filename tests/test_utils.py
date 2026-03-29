"""
Tests for pure utility functions in trainer-optimize/scripts/run_optimize.py.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from run_optimize import (
    DatasetResolutionError,
    extract_placeholders,
    flatten_keys,
    load_jsonl,
    resolve_dataset_paths,
    validate_template_against_task,
)


class TestExtractPlaceholders:
    def test_single_placeholder(self):
        assert extract_placeholders("Hello {input}") == {"input"}

    def test_multiple_placeholders(self):
        assert extract_placeholders("{question} and {context}") == {"question", "context"}

    def test_no_placeholders(self):
        assert extract_placeholders("No braces here") == set()

    def test_double_braces_are_not_placeholders(self):
        assert extract_placeholders("{{escaped}}") == set()


class TestFlattenKeys:
    def test_flat_dict(self):
        assert flatten_keys({"a": 1, "b": 2}) == {"a", "b"}

    def test_nested_dict(self):
        assert flatten_keys({"input": {"question": "q", "context": "c"}}) == {
            "input",
            "input.question",
            "input.context",
        }

    def test_non_dict_returns_empty(self):
        assert flatten_keys("string") == set()
        assert flatten_keys(42) == set()
        assert flatten_keys(None) == set()


class TestValidateTemplateAgainstTask:
    def test_valid_top_level_key(self):
        validate_template_against_task("Answer: {input}", {"input": "hi", "expected": "hello"})

    def test_missing_placeholder_raises(self):
        with pytest.raises(ValueError, match="missing_key"):
            validate_template_against_task("{missing_key}", {"input": "x", "expected": "y"})

    def test_double_braces_not_validated(self):
        validate_template_against_task("{{escaped}}", {"input": "x"})


class TestResolveDatasetPaths:
    def test_returns_explicit_train_and_val_files(self):
        train = self._write_temp_jsonl('{"input": "hi", "expected": "hello"}')
        val = self._write_temp_jsonl('{"input": "bye", "expected": "goodbye"}')

        assert resolve_dataset_paths(train, val) == (train, val)

    def test_reports_missing_argument_names(self):
        with pytest.raises(DatasetResolutionError) as exc_info:
            resolve_dataset_paths(None, None)

        assert exc_info.value.missing_files == ["train_file", "val_file"]

    @staticmethod
    def _write_temp_jsonl(line: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(line)
        return path


class TestLoadJsonl:
    def _write_temp(self, lines: list[str]) -> str:
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
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

    def test_nested_input_preserved(self):
        row = {"input": {"question": "Q?", "context": "ctx"}, "expected": "A"}
        path = self._write_temp([json.dumps(row)])
        rows = load_jsonl(path)
        assert rows[0]["input"]["question"] == "Q?"
