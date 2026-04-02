from __future__ import annotations

import json
import os
import re
import shlex
from pathlib import Path
from typing import Any


HIDDEN_SCORING_FIELDS = frozenset({"criteria", "expected", "expected_json", "reference", "scoring"})
PLACEHOLDER_PATTERN = re.compile(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}(?!\})")
ESCAPED_OPEN_BRACE = "\x00OPEN_BRACE\x00"
ESCAPED_CLOSE_BRACE = "\x00CLOSE_BRACE\x00"
IMPLICIT_TASK_CONTEXT_HEADING = "Task Context"
MODEL_UNAVAILABLE_MARKERS = (
    "rate limit",
    "ratelimit",
    "too many requests",
    "service unavailable",
    "model unavailable",
    "temporarily unavailable",
    "connection error",
    "timed out",
    "timeout",
)


class DatasetResolutionError(ValueError):
    def __init__(self, missing_files: list[str]):
        self.missing_files = missing_files
        super().__init__(
            "Explicit train_file and val_file are required. Missing or unreadable dataset files: "
            + ", ".join(missing_files)
        )


class PromptTemplateValidationError(ValueError):
    """Raised when a prompt template references fields missing from a task payload."""


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_placeholders(template: str) -> set[str]:
    return set(PLACEHOLDER_PATTERN.findall(template))


def uses_implicit_task_context(template: str) -> bool:
    return not extract_placeholders(template)


def flatten_keys(obj: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if not isinstance(obj, dict):
        return keys
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        keys.add(path)
        keys |= flatten_keys(value, path)
    return keys


def flatten_values(obj: Any, prefix: str = "") -> dict[str, Any]:
    values: dict[str, Any] = {}
    if not isinstance(obj, dict):
        return values
    for key, value in obj.items():
        path = f"{prefix}.{key}" if prefix else key
        values[path] = value
        values.update(flatten_values(value, path))
    return values


def validate_template_against_task(template: str, sample_task: dict[str, Any]) -> None:
    valid_keys = set(sample_task) | flatten_keys(sample_task)
    missing = sorted(name for name in extract_placeholders(template) if name not in valid_keys)
    if missing:
        raise PromptTemplateValidationError(
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
        visible["input"] = input_value
        visible.update(input_value)
    elif input_value is not None:
        visible["input"] = input_value
    for key, value in task.items():
        if key != "input" and key not in HIDDEN_SCORING_FIELDS:
            visible[key] = value
    return visible


def render_prompt_text(prompt_text: str, task: dict[str, Any]) -> str:
    prompt_fields = flatten_values(_prompt_fields(task))
    missing = sorted(name for name in extract_placeholders(prompt_text) if name not in prompt_fields)
    if missing:
        raise PromptTemplateValidationError(
            f"Prompt placeholders not found in task payload at render time: {missing}. "
            f"Available keys: {sorted(prompt_fields)}"
        )

    escaped_prompt = prompt_text.replace("{{", ESCAPED_OPEN_BRACE).replace("}}", ESCAPED_CLOSE_BRACE)
    rendered = PLACEHOLDER_PATTERN.sub(lambda match: str(prompt_fields[match.group(1)]), escaped_prompt)
    return rendered.replace(ESCAPED_OPEN_BRACE, "{").replace(ESCAPED_CLOSE_BRACE, "}")


def _serialize_task_context(task: dict[str, Any]) -> str:
    visible_fields = _prompt_fields(task)
    if set(visible_fields) == {"input"} and not isinstance(visible_fields["input"], dict):
        return str(visible_fields["input"])
    return json.dumps(visible_fields, indent=2, sort_keys=True, ensure_ascii=True)


def compose_runtime_prompt(prompt_text: str, task: dict[str, Any]) -> str:
    if not uses_implicit_task_context(prompt_text):
        return render_prompt_text(prompt_text, task)
    task_context = _serialize_task_context(task)
    return f"{prompt_text.rstrip()}\n\n{IMPLICIT_TASK_CONTEXT_HEADING}:\n{task_context}\n"


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).split()).lower()


def _default_judge_prompt_file() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "judge-default.md"


def _serialize_example_rows(rows: list[dict[str, Any]], *, limit: int = 2) -> str:
    return json.dumps(rows[:limit], indent=2, sort_keys=True, ensure_ascii=True)


def is_model_unavailable_error(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    return any(marker in name for marker in ("ratelimit", "timeout")) or any(
        marker in message for marker in MODEL_UNAVAILABLE_MARKERS
    )


def build_manual_followup_result(
    *,
    prompt_file: str,
    prompt_text: str,
    train_file: str,
    val_file: str,
    train_dataset: list[dict[str, Any]],
    val_dataset: list[dict[str, Any]],
    model_settings: dict[str, Any],
    algorithm: str,
    iterations: int,
    beam_width: int,
    branch_factor: int,
    n_runners: int,
    judge_mode: str,
    judge_prompt_file: str | None,
    reason: str,
    dashboard_url: str | None = None,
) -> dict[str, Any]:
    command = [
        "python",
        "skills/trainer-optimize/scripts/run_optimize.py",
        "--prompt-file",
        prompt_file,
        "--train-file",
        train_file,
        "--val-file",
        val_file,
        "--iterations",
        str(iterations),
        "--algorithm",
        algorithm,
        "--beam-width",
        str(beam_width),
        "--branch-factor",
        str(branch_factor),
        "--n-runners",
        str(n_runners),
        "--judge-mode",
        judge_mode,
    ]
    if judge_prompt_file:
        command.extend(["--judge-prompt-file", judge_prompt_file])
    input_binding = "implicit_task_context" if uses_implicit_task_context(prompt_text) else "placeholders"
    model_prompt = "\n\n".join(
        [
            "You are reproducing the repository's Agent Lightning prompt-optimization step because the runtime could not reach an external model.",
            "Return only a revised markdown prompt. Preserve existing placeholders unless the provided datasets prove a new placeholder is valid. Do not expose evaluator-only fields such as expected, expected_json, reference, criteria, or scoring in the prompt body.",
            f"Judge mode: {judge_mode}",
            f"Input binding: {input_binding}",
            "Baseline prompt:\n" + prompt_text.strip(),
            "Training examples (first rows):\n" + _serialize_example_rows(train_dataset),
            "Validation examples (first rows):\n" + _serialize_example_rows(val_dataset),
            "Constraints:\n- Keep literal braces/examples literal.\n- If the prompt has no placeholders, assume the runtime appends a Task Context JSON block.\n- Any candidate that introduces unsupported placeholders is invalid.\n- Optimize for the supplied datasets only.",
        ]
    )
    if judge_mode == "llm_judge":
        judge_prompt_path = Path(judge_prompt_file) if judge_prompt_file else _default_judge_prompt_file()
        model_prompt += "\n\nJudge prompt:\n" + judge_prompt_path.read_text(encoding="utf-8").strip()
    rerun_command = " ".join(shlex.quote(part) for part in command)
    return {
        "ok": True,
        "mode": "manual_followup",
        "message": "External model unavailable; completed deterministic preparation and generated an agent-side inference handoff.",
        "blocker_reason": reason,
        "prompt_file": prompt_file,
        "train_file": train_file,
        "val_file": val_file,
        "optimized_prompt": prompt_text,
        "optimized_prompt_changed": False,
        "output_file": None,
        "report_file": None,
        "prompt_file_updated": False,
        "dashboard_url": dashboard_url,
        "model_provider": model_settings.get("provider"),
        "model_endpoint": model_settings.get("base_url"),
        "inference_model": model_settings.get("inference_model"),
        "gradient_model": model_settings.get("gradient_model"),
        "apply_edit_model": model_settings.get("apply_edit_model"),
        "algorithm": algorithm,
        "iterations": iterations,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "beam_width": beam_width,
        "branch_factor": branch_factor,
        "n_runners": n_runners,
        "judge_mode": judge_mode,
        "input_binding": input_binding,
        "candidate_count": 0,
        "rerun_command": rerun_command,
        "agent_handoff_instruction": (
            "Use the current @trainer agent to answer the `model_prompt`, save the returned markdown as `optimized-prompt.md`, "
            "and continue validation without requiring an external inference token."
        ),
        "manual_reproduction_steps": [
            "Reuse the same prompt file and explicit train/val JSONL datasets; dataset discovery already succeeded.",
            "Use the current @trainer agent as the inference step by answering the `model_prompt` directly and saving the reply as `optimized-prompt.md`.",
            "Continue the trainer workflow with the generated candidate prompt and the same datasets, judge mode, and validation checks.",
            "Re-run the optimize command later only if you want a fully automated model-backed pass after rate limits clear.",
        ],
        "followup_instruction": (
            "Use the current @trainer agent to answer `model_prompt`, save the markdown reply as `optimized-prompt.md`, continue validation, "
            f"and use this command only for a later fully automated rerun if needed: {rerun_command}"
        ),
        "model_prompt": model_prompt,
        "sample_runtime_prompt": compose_runtime_prompt(prompt_text, train_dataset[0]) if train_dataset else prompt_text,
    }


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


def _is_unsupported_responses_route_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code == 404:
        return True
    response = getattr(exc, "response", None)
    if getattr(response, "status_code", None) == 404:
        return True
    message = str(exc).lower()
    return "404" in message and "not found" in message


def _metadata_not_supported(exc: TypeError) -> bool:
    message = " ".join(str(part) for part in exc.args).lower()
    return "metadata" in message and "unexpected keyword argument" in message


async def _call_with_optional_metadata(call: Any, **kwargs: Any) -> Any:
    try:
        return await call(**kwargs)
    except TypeError as exc:
        if "metadata" not in kwargs or not _metadata_not_supported(exc):
            raise
        fallback_kwargs = {key: value for key, value in kwargs.items() if key != "metadata"}
        return await call(**fallback_kwargs)


async def _complete_text_with_metadata_fallback(
    llm_client: Any,
    model_name: str,
    prompt: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> str:
    # _complete_text already downgrades client calls that reject metadata, but this
    # wrapper preserves compatibility with tests or stubs that replace _complete_text
    # itself with a simpler signature.
    try:
        return await _complete_text(llm_client, model_name, prompt, metadata=metadata)
    except TypeError as exc:
        if not _metadata_not_supported(exc):
            raise
        return await _complete_text(llm_client, model_name, prompt)


async def _complete_text(
    llm_client: Any,
    model_name: str,
    prompt: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> str:
    completions = getattr(getattr(llm_client, "chat", None), "completions", None)
    if hasattr(llm_client, "responses") and hasattr(llm_client.responses, "create"):
        try:
            response = await _call_with_optional_metadata(
                llm_client.responses.create,
                model=model_name,
                input=prompt,
                metadata=metadata,
            )
        except Exception as exc:
            # GitHub Models exposes an OpenAI-compatible endpoint, but some routes only support chat completions.
            if completions is None or not hasattr(completions, "create") or not _is_unsupported_responses_route_error(exc):
                raise
        else:
            return _extract_response_text(response)
    if completions is not None and hasattr(completions, "create"):
        response = await _call_with_optional_metadata(
            completions.create,
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            metadata=metadata,
        )
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


def _request_metadata(task: dict[str, Any]) -> dict[str, Any]:
    metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
    # Metadata wins over task-level fields when both are present because callers may
    # attach per-request tracing identifiers without mutating the dataset row itself.
    episode_id = metadata.get("episode_id") or task.get("episode_id") or task.get("id") or "episode"
    step_id = metadata.get("step_id") or task.get("step_id") or "candidate"
    training_run_id = metadata.get("training_run_id") or task.get("training_run_id")
    request_metadata = dict(metadata)
    request_metadata.setdefault("episode_id", str(episode_id))
    request_metadata.setdefault("step_id", str(step_id))
    if training_run_id is not None:
        request_metadata.setdefault("training_run_id", str(training_run_id))
    return request_metadata


async def run_candidate(prompt_text: str, task: dict[str, Any], *, llm_client: Any, model_name: str) -> str:
    prompt = compose_runtime_prompt(prompt_text, task)
    return await _complete_text_with_metadata_fallback(
        llm_client,
        model_name,
        prompt,
        metadata=_request_metadata(task),
    )


async def smoke_test_prompt(
    prompt_text: str,
    task: dict[str, Any],
    *,
    judge_mode: str,
    llm_client: Any,
    model_name: str,
    judge_prompt_file: str | None = None,
    custom_scorer: Any | None = None,
) -> dict[str, Any]:
    output_text = await run_candidate(prompt_text, task, llm_client=llm_client, model_name=model_name)
    score = await evaluate_output(
        task,
        output_text,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        custom_scorer=custom_scorer,
        judge_model=model_name,
    )
    return {
        "output_text": output_text,
        "score": score,
        "input_binding": "implicit_task_context" if uses_implicit_task_context(prompt_text) else "placeholders",
    }


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
        judge_metadata = _request_metadata(task)
        judge_metadata["step_id"] = f"{judge_metadata.get('step_id', 'candidate')}:judge"
        judge_text = await _complete_text_with_metadata_fallback(
            llm_client,
            judge_model,
            rendered_prompt,
            metadata=judge_metadata,
        )
        return _extract_score(judge_text)
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
