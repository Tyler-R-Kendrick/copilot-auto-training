"""
Tests for pure utility functions in trainer-optimize/scripts/run_optimize.py.
"""
from __future__ import annotations

import json
import os
import tempfile
import types

import pytest

import optimize_support
from run_optimize import (
    DatasetResolutionError,
    extract_placeholders,
    flatten_keys,
    load_jsonl,
    render_prompt_text,
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

    def test_json_literals_are_ignored_but_real_placeholders_are_detected(self):
        template = 'Example row: {"input": "user request", "expected": "ideal answer"}\nRequest: {input}'
        assert extract_placeholders(template) == {"input"}

    def test_nested_placeholders_are_detected(self):
        assert extract_placeholders("Question: {input.question}") == {"input.question"}


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

    def test_nested_placeholder_is_validated_against_nested_task(self):
        validate_template_against_task("Question: {input.question}", {"input": {"question": "hi"}})


class TestRenderPromptText:
    def test_renders_real_placeholder_and_preserves_json_literals(self):
        template = 'Example row: {"input": "user request", "expected": "ideal answer"}\nRequest: {input}'
        rendered = render_prompt_text(template, {"input": "Ship status", "expected": "ignored"})

        assert '{"input": "user request", "expected": "ideal answer"}' in rendered
        assert "Request: Ship status" in rendered

    def test_renders_nested_placeholder_from_input_object(self):
        rendered = render_prompt_text("Question: {input.question}\nContext: {input.context}", {
            "input": {"question": "What changed?", "context": "Release notes"},
            "expected": "ignored",
        })

        assert rendered == "Question: What changed?\nContext: Release notes"

    def test_double_brace_escapes_render_as_literal_braces(self):
        rendered = render_prompt_text("Literal: {{example}}\nInput: {input}", {"input": "value"})

        assert rendered == "Literal: {example}\nInput: value"


class TestRunCandidateCompatibility:
    @pytest.mark.asyncio
    async def test_falls_back_to_chat_completions_when_responses_route_returns_404(self):
        class RouteMissingError(Exception):
            status_code = 404

        class Responses:
            async def create(self, *, model: str, input: str):
                raise RouteMissingError("404 page not found")

        class Completions:
            async def create(self, *, model: str, messages: list[dict[str, str]]):
                return types.SimpleNamespace(
                    choices=[types.SimpleNamespace(message=types.SimpleNamespace(content="chat fallback output"))]
                )

        client = types.SimpleNamespace(
            responses=Responses(),
            chat=types.SimpleNamespace(completions=Completions()),
        )

        rendered = await optimize_support.run_candidate(
            "Request: {input}",
            {"input": "ping", "expected": "pong"},
            llm_client=client,
            model_name="openai/gpt-4.1-mini",
        )

        assert rendered == "chat fallback output"

    @pytest.mark.asyncio
    async def test_preserves_non_404_responses_errors(self):
        class AuthError(Exception):
            status_code = 401

        class Responses:
            async def create(self, *, model: str, input: str):
                raise AuthError("401 unauthorized")

        class Completions:
            async def create(self, *, model: str, messages: list[dict[str, str]]):
                raise AssertionError("chat completions should not run for non-404 errors")

        client = types.SimpleNamespace(
            responses=Responses(),
            chat=types.SimpleNamespace(completions=Completions()),
        )

        with pytest.raises(AuthError, match="401 unauthorized"):
            await optimize_support.run_candidate(
                "Request: {input}",
                {"input": "ping", "expected": "pong"},
                llm_client=client,
                model_name="openai/gpt-4.1-mini",
            )


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
