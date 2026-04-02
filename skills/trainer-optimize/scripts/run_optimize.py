"""Single-shot Agent Lightning prompt optimization runtime."""
from __future__ import annotations

import argparse
import asyncio
from contextlib import contextmanager
from datetime import UTC, datetime
import json
import os
import socket
import sys
from typing import Any, Literal
from uuid import uuid4

from opto import trace

from config import (
    DEFAULT_COPILOT_MODEL,
    create_openai_client,
    resolve_model_settings,
)
from optimize_support import (
    DatasetResolutionError,
    extract_placeholders,
    flatten_keys,
    load_jsonl,
    render_prompt_text,
    resolve_dataset_paths,
    smoke_test_prompt,
    uses_implicit_task_context,
    validate_template_against_task,
)
import optimize_support as support


def _pick_free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


@contextmanager
def _configure_agentlightning_server() -> Any:
    original_host = os.getenv("AGL_SERVER_HOST")
    original_port = os.getenv("AGL_SERVER_PORT")

    host = original_host or "127.0.0.1"
    port = int(original_port) if original_port else _pick_free_local_port()

    os.environ["AGL_SERVER_HOST"] = host
    os.environ["AGL_SERVER_PORT"] = str(port)
    try:
        yield {"host": host, "port": port, "dashboard_url": f"http://{host}:{port}"}
    finally:
        if original_host is None:
            os.environ.pop("AGL_SERVER_HOST", None)
        else:
            os.environ["AGL_SERVER_HOST"] = original_host
        if original_port is None:
            os.environ.pop("AGL_SERVER_PORT", None)
        else:
            os.environ["AGL_SERVER_PORT"] = original_port


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
            "input_binding: " + ("implicit_task_context" if uses_implicit_task_context(prompt_text) else "placeholders"),
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
        try:
            output_text = await support.run_candidate(
                prompt_template.template,
                task,
                llm_client=llm_client,
                model_name=model_name,
            )
        except support.PromptTemplateValidationError:
            return 0.0
        return await evaluate_output(
            task,
            output_text,
            judge_mode=judge_mode,
            judge_prompt_file=judge_prompt_file,
            llm_client=llm_client,
            judge_model=model_name,
        )

    return prompt_optimizer_rollout


def _run_debug_smoke_test(
    prompt_text: str,
    train_dataset: list[dict[str, Any]],
    *,
    judge_mode: str,
    llm_client: Any,
    model_name: str,
    judge_prompt_file: str | None,
) -> dict[str, Any]:
    sample = asyncio.run(
        smoke_test_prompt(
            prompt_text,
            train_dataset[0],
            judge_mode=judge_mode,
            llm_client=llm_client,
            model_name=model_name,
            judge_prompt_file=judge_prompt_file,
        )
    )
    return {
        "ok": True,
        "mode": "debug",
        "message": "Smoke test complete",
        "sample_score": sample["score"],
        "input_binding": sample["input_binding"],
    }


def run_optimize_sync(
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
    model_name = model_settings.get("model")
    def manual_followup(reason: str, *, dashboard_url: str | None = None, persist_report: bool = True) -> str:
        result = support.build_manual_followup_result(
            prompt_file=prompt_file,
            prompt_text=prompt_text,
            train_file=train_file,
            val_file=val_file,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            model_settings=model_settings,
            algorithm=algorithm,
            iterations=iterations,
            beam_width=beam_width,
            branch_factor=branch_factor,
            n_runners=n_runners,
            judge_mode=judge_mode,
            judge_prompt_file=judge_prompt_file,
            reason=reason,
            dashboard_url=dashboard_url,
        )
        if not debug_only and persist_report and report_file:
            result["report_file"] = report_file
            Path(report_file).write_text(json.dumps(result, indent=2), encoding="utf-8")
        return json.dumps(result, indent=2)
    if model_name is None:
        return manual_followup("No model was configured.")

    with _configure_agentlightning_server() as server_settings:
        if debug_only:
            try:
                result = _run_debug_smoke_test(
                    prompt_text,
                    train_dataset,
                    judge_mode=judge_mode,
                    llm_client=openai_client,
                    model_name=str(model_name),
                    judge_prompt_file=judge_prompt_file,
                )
            except Exception as exc:
                if not support.is_model_unavailable_error(exc):
                    raise
                return manual_followup(str(exc), dashboard_url=server_settings["dashboard_url"], persist_report=False)
            result["dashboard_url"] = server_settings["dashboard_url"]
            return json.dumps(result, indent=2)

        import agentlightning as agl

        try:
            algo = {"apo": agl.APO, "verl": agl.VERL}[algorithm](
                openai_client,
                beam_rounds=iterations,
                beam_width=beam_width,
                branch_factor=branch_factor,
                gradient_batch_size=min(4, len(train_dataset)),
                val_batch_size=min(16, len(val_dataset)),
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
                model_name=str(model_name),
                judge_prompt_file=judge_prompt_file,
            )
            trainer.fit(agent=rollout_fn, train_dataset=train_dataset, val_dataset=val_dataset)

            optimized_prompt = _extract_best_prompt_template(algo)
        except Exception as exc:
            if not support.is_model_unavailable_error(exc):
                raise
            return manual_followup(str(exc), dashboard_url=server_settings["dashboard_url"])
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
        "dashboard_url": server_settings["dashboard_url"],
        "model": model_settings["model"],
        "iterations": iterations,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "beam_width": beam_width,
        "branch_factor": branch_factor,
        "n_runners": n_runners,
        "judge_mode": judge_mode,
        "input_binding": "implicit_task_context" if uses_implicit_task_context(prompt_text) else "placeholders",
        "candidate_count": _count_candidates(algo),
    }
    if report_file:
        Path(report_file).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return json.dumps(report, indent=2)


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
    return await asyncio.to_thread(
        run_optimize_sync,
        prompt_file,
        train_file,
        val_file,
        iterations,
        algorithm,
        output_file,
        report_file,
        beam_width,
        branch_factor,
        n_runners,
        judge_mode,
        judge_prompt_file,
        debug_only,
        in_place,
    )


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
    result = run_optimize_sync(
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
    print(result)
    return 0 if json.loads(result).get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
