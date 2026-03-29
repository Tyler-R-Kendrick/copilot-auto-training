from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


HIDDEN_SCORING_FIELDS = frozenset({"criteria", "expected", "expected_json", "reference", "scoring"})


class DatasetResolutionError(ValueError):
    def __init__(self, missing_files: list[str]):
        self.missing_files = missing_files
        super().__init__(
            "Explicit train_file and val_file are required. Missing or unreadable dataset files: "
            + ", ".join(missing_files)
        )


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_placeholders(template: str) -> set[str]:
    return set(re.findall(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", template))


def flatten_keys(obj: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if not isinstance(obj, dict):
        return keys
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        keys.add(path)
        keys |= flatten_keys(value, path)
    return keys


def validate_template_against_task(template: str, sample_task: dict[str, Any]) -> None:
    valid_keys = set(sample_task) | flatten_keys(sample_task)
    missing = sorted(name for name in extract_placeholders(template) if name not in valid_keys)
    if missing:
        raise ValueError(
            f"Template placeholders not found in task schema: {missing}. "
            f"Available keys: {sorted(valid_keys)}"
        )


def resolve_dataset_paths(train_file: str | None, val_file: str | None) -> tuple[str, str]:
    missing: list[str] = []
    resolved_paths: dict[str, str] = {}
    for argument_name, path_value in (("train_file", train_file), ("val_file", val_file)):
        if not path_value:
            missing.append(argument_name)
            continue
        if not Path(path_value).is_file():
            missing.append(path_value)
            continue
        resolved_paths[argument_name] = path_value
    if missing:
        raise DatasetResolutionError(missing)
    return resolved_paths["train_file"], resolved_paths["val_file"]


def _prompt_fields(task: dict[str, Any]) -> dict[str, Any]:
    visible: dict[str, Any] = {}
    input_value = task.get("input")
    if isinstance(input_value, dict):
        visible.update(input_value)
    elif input_value is not None:
        visible["input"] = input_value
    for key, value in task.items():
        if key != "input" and key not in HIDDEN_SCORING_FIELDS:
            visible[key] = value
    return visible


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).split()).lower()


def _default_judge_prompt_file() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "judge-default.md"


def _score_exact_match(output_text: str, expected: Any) -> float:
    return 1.0 if output_text.strip() == str(expected).strip() else 0.0


def _require_task_field(task: dict[str, Any], field_name: str, error_message: str) -> Any:
    value = task.get(field_name)
    if value is None:
        raise ValueError(error_message)
    return value


async def _resolve_maybe_awaitable(value: Any) -> Any:
    return await value if hasattr(value, "__await__") else value


def _extract_response_text(response: Any) -> str:
    if isinstance(getattr(response, "output_text", None), str) and response.output_text.strip():
        return response.output_text.strip()
    choices = getattr(response, "choices", None)
    if choices:
        content = getattr(getattr(choices[0], "message", None), "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()
        if isinstance(content, list):
            parts = [item.get("text", "") if isinstance(item, dict) else getattr(item, "text", "") for item in content]
            parts = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
            if parts:
                return "\n".join(parts)
    output_items = getattr(response, "output", None)
    if isinstance(output_items, list):
        parts: list[str] = []
        for item in output_items:
            for content_item in getattr(item, "content", []) or []:
                text_value = getattr(content_item, "text", None)
                if isinstance(text_value, str) and text_value.strip():
                    parts.append(text_value.strip())
        if parts:
            return "\n".join(parts)
    raise ValueError("Model response did not contain any text output.")


async def _complete_text(llm_client: Any, model_name: str, prompt: str) -> str:
    if hasattr(llm_client, "responses") and hasattr(llm_client.responses, "create"):
        return _extract_response_text(await llm_client.responses.create(model=model_name, input=prompt))
    completions = getattr(getattr(llm_client, "chat", None), "completions", None)
    if completions is not None and hasattr(completions, "create"):
        response = await completions.create(model=model_name, messages=[{"role": "user", "content": prompt}])
        return _extract_response_text(response)
    raise ValueError("The configured client does not support text generation.")


def _extract_score(text: str) -> float:
    match = re.search(r"(?<!\d)(0(?:\.\d+)?|1(?:\.0+)?)(?!\d)", text)
    if not match:
        raise ValueError("llm_judge response must contain a score between 0.0 and 1.0")
    score = float(match.group(1))
    if not 0.0 <= score <= 1.0:
        raise ValueError("llm_judge score must be between 0.0 and 1.0")
    return score


async def run_candidate(prompt_text: str, task: dict[str, Any], *, llm_client: Any, model_name: str) -> str:
    return await _complete_text(llm_client, model_name, prompt_text.format(**_prompt_fields(task)))


async def evaluate_output(
    task: dict[str, Any],
    output_text: str,
    *,
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    judge_model: str | None = None,
) -> float:
    if judge_mode == "deterministic":
        expected = _require_task_field(task, "expected", "deterministic judge_mode requires an 'expected' field in each task")
        return _score_exact_match(output_text, expected)
    if judge_mode == "custom":
        if custom_scorer is not None:
            return float(await _resolve_maybe_awaitable(custom_scorer(task, output_text)))
        scoring = task.get("scoring", "custom_python")
        if scoring in {"custom_python", "exact_match"}:
            expected = _require_task_field(task, "expected", "custom exact scoring requires an 'expected' field")
            return _score_exact_match(output_text, expected)
        if scoring == "normalized_match":
            expected = _require_task_field(task, "expected", "normalized_match scoring requires an 'expected' field")
            return 1.0 if _normalize_text(output_text) == _normalize_text(expected) else 0.0
        if scoring == "json_schema":
            expected_json = _require_task_field(task, "expected_json", "json_schema scoring requires an 'expected_json' field")
            try:
                parsed_output = json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise ValueError("json_schema scoring requires JSON output") from exc
            return 1.0 if parsed_output == expected_json else 0.0
        raise ValueError(f"Unsupported custom scoring: {scoring!r}")
    if judge_mode == "llm_judge":
        if llm_client is None:
            from openai import AsyncOpenAI

            llm_client = AsyncOpenAI()
        prompt_template = (Path(judge_prompt_file) if judge_prompt_file else _default_judge_prompt_file()).read_text(encoding="utf-8")
        rendered_prompt = prompt_template.format(
            input=task.get("input", ""),
            expected=task.get("expected", task.get("reference", "")),
            output=output_text,
        )
        judge_score = getattr(llm_client, "judge_score", None)
        if callable(judge_score):
            score = float(await _resolve_maybe_awaitable(judge_score(rendered_prompt)))
            if not 0.0 <= score <= 1.0:
                raise ValueError("llm_judge score must be between 0.0 and 1.0")
            return score
        judge_model = judge_model or os.getenv("OPENAI_MODEL") or os.getenv("GITHUB_MODELS_MODEL")
        if not judge_model:
            raise ValueError("llm_judge requires OPENAI_MODEL or GITHUB_MODELS_MODEL to be configured")
        return _extract_score(await _complete_text(llm_client, judge_model, rendered_prompt))
    raise ValueError(f"Unsupported judge_mode: {judge_mode!r}. Choose from: deterministic, custom, llm_judge")


async def assess_candidates(
    variants: list[str],
    dataset: list[dict[str, Any]],
    *,
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    model_name: str | None = None,
) -> list[dict[str, Any]]:
    assessed: list[dict[str, Any]] = []
    for variant in variants:
        total = 0.0
        for task in dataset:
            output = await run_candidate(variant, task, llm_client=llm_client, model_name=model_name)
            total += await evaluate_output(
                task,
                output,
                judge_mode=judge_mode,
                judge_prompt_file=judge_prompt_file,
                llm_client=llm_client,
                custom_scorer=custom_scorer,
                judge_model=model_name,
            )
        assessed.append({"template": variant, "score": total / len(dataset) if dataset else 0.0})
    return assessed