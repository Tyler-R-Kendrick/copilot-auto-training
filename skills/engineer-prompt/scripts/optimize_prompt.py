#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import asyncio
import json
from pathlib import Path
import re
from types import SimpleNamespace
import sys
from typing import Any

import yaml


ENGINEER_PROMPT_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ENGINEER_PROMPT_DIR.parents[1]
DEFAULT_PROGRAM_FILE_PATH = ENGINEER_PROMPT_DIR / "assets" / "prompt_program_optimized.json"
PLACEHOLDER_PATTERN = re.compile(r"\$\{[^}]+\}|\{\{[^}]+\}\}")
MARKDOWN_TOKENS = ("#", "- ", "1.", "```")
EMPTY_CONSTRAINT_MARKER = "<none>"
# Disable demonstrations so the compiled artifact stays close to a clean checked-in markdown prompt.
MAX_DEMO_COUNT = 0
DEFAULT_MIN_BODY_LENGTH = 40
DEFAULT_MAX_BODY_LENGTH_MULTIPLIER = 2
TRAIN_SET_SIZE = 3
DEFAULT_GOAL = (
    "Improve clarity, structure, and operational usefulness while preserving placeholders, markdown shape, "
    "and the prompt's general task scope."
)
DEFAULT_OPTIMIZATION_INSTRUCTIONS = (
    "Clarify the prompt's task objective, required inputs, and success criteria.",
    "Improve scannability with a clean markdown structure and a logical instruction order.",
    "Make the expected response format and output constraints explicit.",
    "Preserve every placeholder exactly and retain all required text.",
    "Remove redundant wording without changing the prompt's scope or intent.",
)
DEFAULT_VARIANT_FOCUS_AREAS = (
    ("Emphasize the task objective, user inputs, and success criteria.",),
    ("Emphasize section structure, heading quality, and instruction order.",),
    ("Emphasize output formatting rules, required text, and placeholder safety.",),
    ("Emphasize concision by removing repetition while keeping all constraints.",),
)
CHARS_PER_TOKEN_ESTIMATE = 4


@dataclass(slots=True)
class PromptOptimizationTask:
    prompt_path: Path
    frontmatter: dict[str, Any]
    prompt_body: str
    optimization_goal: str
    optimization_instructions: tuple[str, ...]
    supporting_context: str
    required_text: tuple[str, ...]
    forbidden_text: tuple[str, ...]
    placeholders: tuple[str, ...]
    min_body_length: int
    max_body_length: int


def _load_dspy() -> Any:
    try:
        import dspy  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised through CLI path
        raise RuntimeError(
            "DSPy is required for --optimize. Install repository dependencies using the repository setup instructions "
            "and requirements.txt before running this command."
        ) from exc
    return dspy


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError(
            "Invalid markdown front matter block: frontmatter must start with '---', contain YAML key-value pairs, "
            f"and end with '---' before the body; got {len(parts)} part(s)."
        )
    _, raw_frontmatter, body = parts
    frontmatter = yaml.safe_load(raw_frontmatter) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError(f"Markdown frontmatter must be a dictionary of key-value pairs, got {type(frontmatter).__name__}")
    return frontmatter, body.strip()


def extract_placeholders(text: str) -> tuple[str, ...]:
    seen: list[str] = []
    for match in PLACEHOLDER_PATTERN.findall(text):
        if match not in seen:
            seen.append(match)
    return tuple(seen)


def _read_context_files(paths: list[str]) -> str:
    chunks: list[str] = []
    for raw_path in paths:
        path = Path(raw_path).resolve()
        chunks.append(f"File: {path}\n{path.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(chunk for chunk in chunks if chunk)


def build_prompt_task(
    prompt_file: str,
    *,
    goal: str | None = None,
    optimization_instructions: list[str] | None = None,
    context_files: list[str] | None = None,
    required_text: list[str] | None = None,
    forbidden_text: list[str] | None = None,
    min_body_length: int = DEFAULT_MIN_BODY_LENGTH,
    max_body_length: int | None = None,
) -> PromptOptimizationTask:
    prompt_path = Path(prompt_file).resolve()
    prompt_text = prompt_path.read_text(encoding="utf-8")
    frontmatter, prompt_body = _split_frontmatter(prompt_text)
    placeholders = extract_placeholders(prompt_text)
    resolved_max_body_length = (
        max_body_length
        if max_body_length is not None
        else max(len(prompt_body) * DEFAULT_MAX_BODY_LENGTH_MULTIPLIER, min_body_length)
    )
    return PromptOptimizationTask(
        prompt_path=prompt_path,
        frontmatter=frontmatter,
        prompt_body=prompt_body,
        optimization_goal=(goal or DEFAULT_GOAL).strip(),
        optimization_instructions=tuple(
            item.strip() for item in (optimization_instructions or DEFAULT_OPTIMIZATION_INSTRUCTIONS) if item.strip()
        ),
        supporting_context=_read_context_files(context_files or []),
        required_text=tuple(item.strip() for item in (required_text or []) if item.strip()),
        forbidden_text=tuple(item.strip() for item in (forbidden_text or []) if item.strip()),
        placeholders=placeholders,
        min_body_length=max(1, int(min_body_length)),
        max_body_length=max(1, int(resolved_max_body_length)),
    )


def render_prompt_markdown(prompt_body: str, *, frontmatter: dict[str, Any]) -> str:
    cleaned_body = prompt_body.strip()
    if not frontmatter:
        return f"{cleaned_body}\n"
    rendered_frontmatter = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    return f"---\n{rendered_frontmatter}\n---\n\n{cleaned_body}\n"


def validate_prompt_markdown(
    markdown: str,
    *,
    expected_placeholders: tuple[str, ...] = (),
    required_text: tuple[str, ...] = (),
    forbidden_text: tuple[str, ...] = (),
    min_body_length: int = DEFAULT_MIN_BODY_LENGTH,
    max_body_length: int | None = None,
) -> dict[str, Any]:
    frontmatter, body = _split_frontmatter(markdown)
    markdown_lower = markdown.lower()
    missing_placeholders = [item for item in expected_placeholders if item not in markdown]
    missing_required_text = [item for item in required_text if item not in markdown]
    forbidden_text_present = [item for item in forbidden_text if item.lower() in markdown_lower]
    body_length = len(body.strip())
    too_short = body_length < min_body_length
    too_long = max_body_length is not None and body_length > max_body_length
    looks_like_markdown = bool(body.strip()) and any(token in body for token in MARKDOWN_TOKENS)
    return {
        "valid": not missing_placeholders and not missing_required_text and not forbidden_text_present and not too_short and not too_long and looks_like_markdown,
        "has_frontmatter": bool(frontmatter),
        "body_length": body_length,
        "missing_placeholders": missing_placeholders,
        "missing_required_text": missing_required_text,
        "forbidden_text_present": forbidden_text_present,
        "too_short": too_short,
        "too_long": too_long,
        "looks_like_markdown": looks_like_markdown,
    }


def prompt_metric(example: Any, pred: Any, _trace: Any = None) -> float:
    frontmatter = getattr(example, "frontmatter", None) or example.get("frontmatter", {})
    markdown = render_prompt_markdown(getattr(pred, "optimized_prompt"), frontmatter=frontmatter)
    summary = validate_prompt_markdown(
        markdown,
        expected_placeholders=tuple(getattr(example, "placeholders", ()) or example.get("placeholders", ())),
        required_text=tuple(getattr(example, "required_text", ()) or example.get("required_text", ())),
        forbidden_text=tuple(getattr(example, "forbidden_text", ()) or example.get("forbidden_text", ())),
        min_body_length=int(getattr(example, "min_body_length", DEFAULT_MIN_BODY_LENGTH) or example.get("min_body_length", DEFAULT_MIN_BODY_LENGTH)),
        max_body_length=getattr(example, "max_body_length", None) or example.get("max_body_length", None),
    )
    checks = [
        not summary["missing_placeholders"],
        not summary["missing_required_text"],
        not summary["forbidden_text_present"],
        not summary["too_short"],
        not summary["too_long"],
        summary["looks_like_markdown"],
    ]
    return sum(1.0 for check in checks if check) / len(checks)


def _task_variants(task: PromptOptimizationTask) -> list[dict[str, str]]:
    variants: list[dict[str, str]] = []
    for focus_area in ((), *DEFAULT_VARIANT_FOCUS_AREAS):
        instructions = "\n".join([*task.optimization_instructions, *focus_area])
        variants.append(
            {
                "optimization_goal": task.optimization_goal,
                "optimization_instructions": instructions,
                "supporting_context": task.supporting_context,
            }
        )
    return variants


def build_example_sets(task: PromptOptimizationTask, dspy: Any) -> tuple[list[Any], list[Any]]:
    examples = []
    for variant in _task_variants(task):
        examples.append(
            dspy.Example(
                frontmatter=task.frontmatter,
                optimization_goal=variant["optimization_goal"],
                optimization_instructions=variant["optimization_instructions"],
                supporting_context=variant["supporting_context"],
                required_text=task.required_text,
                forbidden_text=task.forbidden_text,
                placeholders=task.placeholders,
                min_body_length=task.min_body_length,
                max_body_length=task.max_body_length,
                draft_prompt=task.prompt_body,
            ).with_inputs(
                "optimization_goal",
                "optimization_instructions",
                "supporting_context",
                "required_text",
                "forbidden_text",
                "placeholders",
                "draft_prompt",
            )
        )
    return examples[:TRAIN_SET_SIZE], examples[TRAIN_SET_SIZE:]


def _estimate_tokens_from_text(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN_ESTIMATE) if text else 0


def _estimate_prompt_tokens(messages: list[dict[str, Any]]) -> int:
    total = 0
    for message in messages:
        content = message.get("content")
        if isinstance(content, str) and content:
            total += _estimate_tokens_from_text(content)
    return total


def _ensure_repo_root_on_path() -> None:
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _create_copilot_client(prompt_file: str, *, model: str | None, temperature: float) -> tuple[Any, dict[str, Any], Any]:
    _ensure_repo_root_on_path()
    from copilot_runtime import InferenceRequest, create_runtime_client

    client, resolved_settings = create_runtime_client(prompt_file, model=model, temperature=temperature)
    return client, resolved_settings, InferenceRequest


def _run_async(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    raise RuntimeError(
        "Copilot-backed prompt optimization cannot run inside an active event loop. "
        "DSPy calls this optimizer synchronously, so run this script outside of an async context or invoke it in a "
        "separate process, for example: python skills/engineer-prompt/scripts/optimize_prompt.py --optimize ..."
    )


def _build_copilot_dspy_lm(dspy: Any, *, client: Any, model: str, temperature: float, inference_request_cls: Any) -> Any:
    class CopilotDSPyLM(dspy.BaseLM):
        def __init__(self) -> None:
            super().__init__(model=model, model_type="chat", temperature=temperature, cache=False)
            self._client = client

        def forward(
            self,
            prompt: str | None = None,
            messages: list[dict[str, Any]] | None = None,
            **kwargs: Any,
        ) -> Any:
            return _run_async(self.aforward(prompt=prompt, messages=messages, **kwargs))

        async def aforward(
            self,
            prompt: str | None = None,
            messages: list[dict[str, Any]] | None = None,
            **kwargs: Any,
        ) -> Any:
            request_messages = messages or [{"role": "user", "content": prompt or ""}]
            try:
                response = await self._client.provider.generate(
                    inference_request_cls(
                        messages=request_messages,
                        model=self.model,
                        metadata={"interaction": "engineer-prompt.optimize_prompt", **(kwargs.get("metadata") or {})},
                    )
                )
            except Exception as exc:
                raise RuntimeError(
                    "Copilot runtime failed while optimizing the prompt. Verify that this command is running in a "
                    "signed-in GitHub Copilot session and that the selected Copilot model is available in this "
                    "repository."
                ) from exc
            usage = dict(response.usage or {})
            prompt_tokens = _estimate_prompt_tokens(request_messages)
            usage.setdefault("prompt_tokens", prompt_tokens)
            usage.setdefault("completion_tokens", _estimate_tokens_from_text(response.text))
            usage.setdefault("total_tokens", usage["prompt_tokens"] + usage["completion_tokens"])
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=response.text))],
                usage=usage,
                model=str(response.model or self.model),
                finish_reason=response.finish_reason,
                raw=response.raw,
            )

    return CopilotDSPyLM()


def _configure_dspy_language_model(dspy: Any, *, prompt_file: str, model: str | None, temperature: float) -> Any:
    client, model_settings, inference_request_cls = _create_copilot_client(prompt_file, model=model, temperature=temperature)
    resolved_model = str(model_settings.get("model") or "default")
    client.default_model = resolved_model
    client.provider.config.model = resolved_model
    lm = _build_copilot_dspy_lm(
        dspy,
        client=client,
        model=resolved_model,
        temperature=temperature,
        inference_request_cls=inference_request_cls,
    )
    dspy.configure(lm=lm)
    return lm


def compile_prompt(
    task: PromptOptimizationTask,
    *,
    program_file: Path | None = None,
    model: str | None = None,
    temperature: float = 0.2,
) -> tuple[str, Any]:
    dspy = _load_dspy()
    _configure_dspy_language_model(dspy, prompt_file=str(task.prompt_path), model=model, temperature=temperature)

    class PromptOptimizerSignature(dspy.Signature):
        """Rewrite a markdown prompt to improve quality while preserving placeholders and task scope."""

        optimization_goal = dspy.InputField(desc="Primary rewrite objective that defines what outcome the prompt should improve.")
        optimization_instructions = dspy.InputField(
            desc="Ordered rewrite instructions covering clarity, structure, output contract, placeholder preservation, and concision."
        )
        supporting_context = dspy.InputField(desc="Reference material, style guidance, or product context that should inform the rewrite.")
        required_text = dspy.InputField(desc="Text that must remain in the rewritten prompt when provided.")
        forbidden_text = dspy.InputField(desc="Text that must not appear in the rewritten prompt when provided.")
        placeholders = dspy.InputField(desc="Template placeholders that must be copied exactly into the rewritten prompt.")
        draft_prompt = dspy.InputField(desc="The current markdown prompt body that needs to be improved.")
        optimized_prompt = dspy.OutputField(desc="A rewritten markdown prompt body that satisfies the goal and rewrite instructions.")

    class PromptOptimizerProgram(dspy.Module):
        def __init__(self) -> None:
            super().__init__()
            self.rewrite = dspy.Predict(PromptOptimizerSignature)

        def forward(
            self,
            optimization_goal: str,
            optimization_instructions: str,
            supporting_context: str,
            required_text: tuple[str, ...],
            forbidden_text: tuple[str, ...],
            placeholders: tuple[str, ...],
            draft_prompt: str,
        ) -> Any:
            return self.rewrite(
                optimization_goal=optimization_goal,
                optimization_instructions=optimization_instructions,
                supporting_context=supporting_context,
                required_text="\n".join(required_text) if required_text else EMPTY_CONSTRAINT_MARKER,
                forbidden_text="\n".join(forbidden_text) if forbidden_text else EMPTY_CONSTRAINT_MARKER,
                placeholders="\n".join(placeholders) if placeholders else EMPTY_CONSTRAINT_MARKER,
                draft_prompt=draft_prompt,
            )

    trainset, valset = build_example_sets(task, dspy)
    program = PromptOptimizerProgram()
    optimizer = dspy.MIPROv2(
        metric=prompt_metric,
        auto="light",
        max_bootstrapped_demos=MAX_DEMO_COUNT,
        max_labeled_demos=MAX_DEMO_COUNT,
    )
    compiled = optimizer.compile(
        student=program,
        trainset=trainset,
        valset=valset,
        requires_permission_to_run=False,
    )
    prediction = compiled(
        optimization_goal=task.optimization_goal,
        optimization_instructions="\n".join(task.optimization_instructions),
        supporting_context=task.supporting_context,
        required_text=task.required_text,
        forbidden_text=task.forbidden_text,
        placeholders=task.placeholders,
        draft_prompt=task.prompt_body,
    )
    if program_file is not None and hasattr(compiled, "save"):
        compiled.save(str(program_file), save_program=True)
    return str(prediction.optimized_prompt).strip(), compiled


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate or optimize a markdown prompt file using the Copilot runtime.")
    parser.add_argument("--prompt-file", required=True, help="Required path to the markdown prompt file to validate or optimize.")
    parser.add_argument("--output-file", help="Optional path for the rendered markdown artifact.")
    parser.add_argument("--program-file", default=str(DEFAULT_PROGRAM_FILE_PATH), help="Path to save the compiled DSPy program when --optimize is used.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the source prompt file.")
    parser.add_argument("--optimize", action="store_true", help="Run the DSPy optimizer before rendering the markdown artifact.")
    parser.add_argument("--validate-only", action="store_true", help="Validate the rendered prompt contract and print a JSON summary.")
    parser.add_argument("--goal", default=DEFAULT_GOAL, help="Optimization goal for the prompt rewrite.")
    parser.add_argument(
        "--optimization-instruction",
        action="append",
        default=[],
        help="Concrete rewrite instruction to apply during optimization. Repeatable.",
    )
    parser.add_argument("--context-file", action="append", default=[], help="Additional file to pass as supporting context. Repeatable.")
    parser.add_argument("--required-text", action="append", default=[], help="Text that must appear in the optimized prompt. Repeatable.")
    parser.add_argument("--forbidden-text", action="append", default=[], help="Text that must not appear in the optimized prompt. Repeatable.")
    parser.add_argument("--min-body-length", type=int, default=DEFAULT_MIN_BODY_LENGTH, help="Minimum non-frontmatter body length for validation.")
    parser.add_argument("--max-body-length", type=int, help="Maximum non-frontmatter body length for validation.")
    parser.add_argument("--model", help="Optional Copilot model override. Defaults to the repository Copilot runtime configuration.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature passed to the Copilot-backed DSPy client.")
    return parser.parse_args()


def _write_output(markdown: str, *, output_file: str | None, in_place: bool, prompt_path: Path) -> str | None:
    target_path: Path | None = None
    if in_place:
        target_path = prompt_path
    elif output_file:
        target_path = Path(output_file)
    if target_path is None:
        return None
    target_path.write_text(markdown, encoding="utf-8")
    return str(target_path)


def main() -> int:
    args = _parse_args()
    try:
        task = build_prompt_task(
            args.prompt_file,
            goal=args.goal,
            optimization_instructions=args.optimization_instruction,
            context_files=args.context_file,
            required_text=args.required_text,
            forbidden_text=args.forbidden_text,
            min_body_length=args.min_body_length,
            max_body_length=args.max_body_length,
        )
        optimized_body = task.prompt_body
        if args.optimize:
            optimized_body, _ = compile_prompt(
                task,
                program_file=Path(args.program_file) if args.program_file else None,
                model=args.model,
                temperature=args.temperature,
            )
        markdown = render_prompt_markdown(optimized_body, frontmatter=task.frontmatter)
        if args.validate_only:
            summary = validate_prompt_markdown(
                markdown,
                expected_placeholders=task.placeholders,
                required_text=task.required_text,
                forbidden_text=task.forbidden_text,
                min_body_length=task.min_body_length,
                max_body_length=task.max_body_length,
            )
            summary["prompt_file"] = str(task.prompt_path)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0 if summary["valid"] else 1
        written = _write_output(markdown, output_file=args.output_file, in_place=args.in_place, prompt_path=task.prompt_path)
    except FileNotFoundError as exc:  # pragma: no cover - exercised via CLI path
        missing_path = exc.filename or str(exc)
        print(f"File not found: {missing_path}", file=sys.stderr)
        return 1
    except ImportError as exc:  # pragma: no cover - exercised via CLI path
        print(f"Missing dependency for prompt optimization: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - exercised via CLI path
        print(f"Prompt optimization failed: {exc}", file=sys.stderr)
        return 1

    if written:
        print(written)
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
