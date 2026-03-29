"""Single-shot Agent Lightning prompt optimization runtime."""
from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
import json
import sys
from typing import Any, Literal
from uuid import uuid4

from opto import trace

from config import (
    DEFAULT_GITHUB_APPLY_EDIT_MODEL,
    DEFAULT_GITHUB_GRADIENT_MODEL,
    create_openai_client,
    resolve_model_settings,
)
from optimize_support import (
    DatasetResolutionError,
    extract_placeholders,
    flatten_keys,
    load_jsonl,
    resolve_dataset_paths,
    validate_template_against_task,
)
import optimize_support as support


def build_trace_case_summary(
    prompt_text: str,
    train_dataset: list[dict[str, Any]],
    val_dataset: list[dict[str, Any]],
    judge_mode: str,
    *,
    prompt_file: str | None = None,
) -> str:
    placeholders = sorted(extract_placeholders(prompt_text))
    return "\n".join(
        [
            f"prompt_file: {prompt_file or '<memory>'}",
            f"train_size: {len(train_dataset)}",
            f"val_size: {len(val_dataset)}",
            f"judge_mode: {judge_mode}",
            "placeholders: " + (", ".join(placeholders) if placeholders else "<none>"),
            "prompt_preview:",
            prompt_text.strip()[:400] or "<empty>",
        ]
    )


def parse_trace_search_budget(raw_budget: Any, *, default_algorithm: str = "apo") -> dict[str, int | str]:
    defaults: dict[str, int | str] = {
        "algorithm": default_algorithm if default_algorithm in {"apo", "verl"} else "apo",
        "iterations": 3,
        "beam_width": 4,
        "branch_factor": 4,
        "n_runners": 4,
    }
    if hasattr(raw_budget, "data"):
        raw_budget = raw_budget.data
    parsed: dict[str, Any] = {}
    if isinstance(raw_budget, dict):
        parsed = raw_budget
    elif isinstance(raw_budget, str):
        try:
            parsed = json.loads(raw_budget)
        except json.JSONDecodeError:
            parsed = {}
    normalized = dict(defaults)
    if parsed.get("algorithm") in {"apo", "verl"}:
        normalized["algorithm"] = parsed["algorithm"]
    for key in ("iterations", "beam_width", "branch_factor", "n_runners"):
        try:
            normalized[key] = max(1, int(parsed.get(key, normalized[key])))
        except (TypeError, ValueError):
            continue
    return normalized


@trace.model
class TraceSelfOptimizationPolicy:
    @trace.bundle(trainable=True)
    def choose_algorithm(self, train_size: int, val_size: int, placeholder_count: int, judge_mode: str) -> str:
        if judge_mode == "llm_judge" or max(train_size, val_size) >= 64 or placeholder_count >= 4:
            return "verl"
        return "apo"

    @trace.bundle(trainable=True)
    def choose_search_budget(self, train_size: int, val_size: int, placeholder_count: int, judge_mode: str) -> str:
        largest_split = max(train_size, val_size)
        return json.dumps(
            {
                "iterations": 4 if judge_mode == "llm_judge" or largest_split >= 64 else 3,
                "beam_width": 6 if largest_split >= 96 else 4,
                "branch_factor": 5 if placeholder_count >= 4 else 4,
                "n_runners": 6 if largest_split >= 96 else 4,
            },
            sort_keys=True,
        )


async def evaluate_output(
    task: dict[str, Any],
    output_text: str,
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    judge_model: str | None = None,
) -> float:
    return await support.evaluate_output(
        task,
        output_text,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        custom_scorer=custom_scorer,
        judge_model=judge_model,
    )


async def assess_candidates(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    model_name: str | None = None,
) -> list[dict[str, Any]]:
    return await support.assess_candidates(
        variants,
        dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        custom_scorer=custom_scorer,
        model_name=model_name,
    )


def _extract_best_prompt_template(algo: Any) -> str:
    best_prompt = algo.get_best_prompt() if hasattr(algo, "get_best_prompt") else None
    if best_prompt is None and hasattr(algo, "get_candidates"):
        candidates = algo.get_candidates()
        if candidates:
            best_prompt = candidates[0]
    template = getattr(best_prompt, "template", None)
    if not isinstance(template, str) or not template.strip():
        raise RuntimeError("Optimization did not produce a usable prompt template.")
    return template


def _count_candidates(algo: Any) -> int | None:
    if hasattr(algo, "get_candidates") and isinstance(algo.get_candidates(), list):
        return len(algo.get_candidates())
    return None


def _write_text_if_requested(file_path: str | None, content: str) -> str | None:
    if not file_path:
        return None
    from pathlib import Path

    path = Path(file_path)
    path.write_text(content, encoding="utf-8")
    return str(path)


def _make_rollout(judge_mode: str, *, llm_client: Any, model_name: str, judge_prompt_file: str | None = None):
    import agentlightning as agl

    @agl.rollout
    async def prompt_optimizer_rollout(task: dict[str, Any], prompt_template: agl.PromptTemplate) -> float:
        output_text = await support.run_candidate(prompt_template.template, task, llm_client=llm_client, model_name=model_name)
        return await evaluate_output(
            task,
            output_text,
            judge_mode=judge_mode,
            judge_prompt_file=judge_prompt_file,
            llm_client=llm_client,
            judge_model=model_name,
        )

    return prompt_optimizer_rollout


async def run_optimize(
    prompt_file: str,
    train_file: str | None = None,
    val_file: str | None = None,
    iterations: int = 3,
    algorithm: str = "apo",
    output_file: str | None = None,
    report_file: str | None = None,
    beam_width: int = 4,
    branch_factor: int = 4,
    n_runners: int = 4,
    judge_mode: Literal["deterministic", "custom", "llm_judge"] = "deterministic",
    judge_prompt_file: str | None = None,
    debug_only: bool = False,
    in_place: bool = False,
) -> str:
    try:
        train_file, val_file = resolve_dataset_paths(train_file, val_file)
    except DatasetResolutionError as exc:
        return json.dumps(
            {
                "ok": False,
                "message": str(exc),
                "prompt_file": prompt_file,
                "missing_files": exc.missing_files,
            },
            indent=2,
        )
    if algorithm not in {"apo", "verl"}:
        return json.dumps({"ok": False, "message": f"Unsupported algorithm: {algorithm!r}"}, indent=2)
    from pathlib import Path
    prompt_text = Path(prompt_file).read_text(encoding="utf-8")
    train_dataset = load_jsonl(train_file)
    val_dataset = load_jsonl(val_file)
    if not train_dataset:
        raise ValueError("train_file must contain at least one task row")
    if not val_dataset:
        raise ValueError("val_file must contain at least one task row")
    validate_template_against_task(prompt_text, train_dataset[0])
    openai_client, model_settings = create_openai_client(prompt_file)
    inference_model = model_settings.get("inference_model")
    if debug_only and inference_model is None:
        return json.dumps({"ok": True, "mode": "debug", "message": "Dry run complete"}, indent=2)
    if not debug_only and inference_model is None:
        raise ValueError("Optimization requires GITHUB_MODELS_MODEL or OPENAI_MODEL to execute prompt rollouts.")

    import agentlightning as agl

    algo = {"apo": agl.APO, "verl": agl.VERL}[algorithm](
        openai_client,
        beam_rounds=iterations,
        beam_width=beam_width,
        branch_factor=branch_factor,
        gradient_batch_size=min(4, len(train_dataset)),
        val_batch_size=min(16, len(val_dataset)),
        gradient_model=model_settings.get("gradient_model") or DEFAULT_GITHUB_GRADIENT_MODEL,
        apply_edit_model=model_settings.get("apply_edit_model") or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
    )
    trainer = agl.Trainer(
        algorithm=algo,
        n_runners=n_runners,
        tracer=agl.OtelTracer(),
        initial_resources={"main_prompt": agl.PromptTemplate(template=prompt_text, engine="f-string")},
        adapter=agl.TraceToMessages(),
    )
    rollout_fn = _make_rollout(
        judge_mode,
        llm_client=openai_client,
        model_name=str(inference_model),
        judge_prompt_file=judge_prompt_file,
    )
    if debug_only:
        await asyncio.to_thread(trainer.dev, agent=rollout_fn, train_dataset=train_dataset, val_dataset=val_dataset)
        return json.dumps({"ok": True, "mode": "debug", "message": "Dry run complete"}, indent=2)
    await asyncio.to_thread(trainer.fit, agent=rollout_fn, train_dataset=train_dataset, val_dataset=val_dataset)

    optimized_prompt = _extract_best_prompt_template(algo)
    prompt_file_updated = False
    if in_place:
        _write_text_if_requested(prompt_file, optimized_prompt)
        prompt_file_updated = True
    written_output_file = _write_text_if_requested(output_file, optimized_prompt)
    report = {
        "ok": True,
        "run_id": "run-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8],
        "algorithm": algorithm,
        "prompt_file": prompt_file,
        "train_file": train_file,
        "val_file": val_file,
        "optimized_prompt": optimized_prompt,
        "output_file": written_output_file,
        "report_file": report_file,
        "prompt_file_updated": prompt_file_updated,
        "model_provider": model_settings["provider"],
        "model_endpoint": model_settings["base_url"],
        "inference_model": model_settings["inference_model"],
        "gradient_model": model_settings["gradient_model"],
        "apply_edit_model": model_settings["apply_edit_model"],
        "iterations": iterations,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "beam_width": beam_width,
        "branch_factor": branch_factor,
        "n_runners": n_runners,
        "judge_mode": judge_mode,
        "candidate_count": _count_candidates(algo),
    }
    if report_file:
        Path(report_file).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return json.dumps(report, indent=2)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Optimize a markdown prompt file using Agent Lightning.")
    parser.add_argument("--prompt-file", required=True, help="Path to the markdown prompt file")
    parser.add_argument("--train-file", default=None, help="Path to the JSONL training dataset")
    parser.add_argument("--val-file", default=None, help="Path to the JSONL validation dataset")
    parser.add_argument("--iterations", type=int, default=3, help="Beam rounds")
    parser.add_argument("--algorithm", default="apo", choices=["apo", "verl"], help="Optimization algorithm")
    parser.add_argument("--output-file", default=None, help="Optional optimized prompt output path")
    parser.add_argument("--report-file", default=None, help="Optional JSON report output path")
    parser.add_argument("--beam-width", type=int, default=4)
    parser.add_argument("--branch-factor", type=int, default=4)
    parser.add_argument("--n-runners", type=int, default=4)
    parser.add_argument("--judge-mode", default="deterministic", choices=["deterministic", "custom", "llm_judge"])
    parser.add_argument("--judge-prompt-file", default=None, help="Optional llm_judge prompt path")
    parser.add_argument("--debug-only", action="store_true", help="Run a smoke test without writing files")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the source prompt with the optimized result")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    result = asyncio.run(
        run_optimize(
            prompt_file=args.prompt_file,
            train_file=args.train_file,
            val_file=args.val_file,
            iterations=args.iterations,
            algorithm=args.algorithm,
            output_file=args.output_file,
            report_file=args.report_file,
            beam_width=args.beam_width,
            branch_factor=args.branch_factor,
            n_runners=args.n_runners,
            judge_mode=args.judge_mode,
            judge_prompt_file=args.judge_prompt_file,
            debug_only=args.debug_only,
            in_place=args.in_place,
        )
    )
    print(result)
    return 0 if json.loads(result).get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())