"""Trace-powered self-training helper for trainer-optimize."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from opto import trace

from run_optimize import (
    TraceSelfOptimizationPolicy,
    assess_candidates,
    build_trace_case_summary,
    create_openai_client,
    extract_placeholders,
    load_jsonl,
    parse_trace_search_budget,
    resolve_model_settings,
    run_optimize,
)


def normalize_training_case(case: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize one Trace training case."""
    required = ("prompt_file", "train_file", "val_file")
    missing = [key for key in required if not case.get(key)]
    if missing:
        raise ValueError(f"Training case is missing required fields: {missing}")

    normalized = {
        "prompt_file": str(case["prompt_file"]),
        "train_file": str(case["train_file"]),
        "val_file": str(case["val_file"]),
        "judge_mode": str(case.get("judge_mode", "deterministic")),
    }
    if case.get("judge_prompt_file"):
        normalized["judge_prompt_file"] = str(case["judge_prompt_file"])
    return normalized


def load_training_cases(
    *,
    cases_file: str | None = None,
    prompt_file: str | None = None,
    train_file: str | None = None,
    val_file: str | None = None,
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
) -> list[dict[str, Any]]:
    """Load Trace training cases from JSONL or a single prompt/dataset trio."""
    if cases_file and any(value is not None for value in (prompt_file, train_file, val_file)):
        raise ValueError("Use either --cases-file or the explicit --prompt-file/--train-file/--val-file trio.")

    if cases_file:
        return [normalize_training_case(row) for row in load_jsonl(cases_file)]

    if prompt_file and train_file and val_file:
        return [
            normalize_training_case(
                {
                    "prompt_file": prompt_file,
                    "train_file": train_file,
                    "val_file": val_file,
                    "judge_mode": judge_mode,
                    "judge_prompt_file": judge_prompt_file,
                }
            )
        ]

    raise ValueError("Provide --cases-file or all of --prompt-file, --train-file, and --val-file.")


def configure_trace_environment(prompt_file: str) -> dict[str, str | None]:
    """Map the repo's model settings into the env vars Trace/LiteLLM expects."""
    model_settings = resolve_model_settings(prompt_file)
    if model_settings.get("api_key"):
        os.environ["OPENAI_API_KEY"] = str(model_settings["api_key"])
    if model_settings.get("base_url"):
        base_url = str(model_settings["base_url"])
        os.environ["OPENAI_BASE_URL"] = base_url
        os.environ["OPENAI_API_BASE"] = base_url
    if model_settings.get("inference_model"):
        os.environ["TRACE_LITELLM_MODEL"] = str(model_settings["inference_model"])
    return model_settings


async def score_prompt_text(
    prompt_text: str,
    dataset: list[dict[str, Any]],
    *,
    prompt_file: str,
    judge_mode: str,
    judge_prompt_file: str | None = None,
) -> float:
    """Score one prompt template across a dataset with the current model settings."""
    llm_client, model_settings = create_openai_client(prompt_file)
    model_name = model_settings.get("inference_model")
    if not model_name:
        raise ValueError("Trace training requires GITHUB_MODELS_MODEL or OPENAI_MODEL to be configured.")

    assessed = await assess_candidates(
        [prompt_text],
        dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        model_name=str(model_name),
    )
    return float(assessed[0]["score"]) if assessed else 0.0


@trace.bundle(allow_external_dependencies=True)
def execute_training_case(case_json: str, algorithm: str, budget_json: str) -> str:
    """Execute one self-training case and return a JSON report."""
    case = normalize_training_case(json.loads(case_json))
    prompt_path = Path(case["prompt_file"])
    prompt_text = prompt_path.read_text(encoding="utf-8")
    val_dataset = load_jsonl(case["val_file"])
    search_budget = parse_trace_search_budget(budget_json, default_algorithm=algorithm)

    optimize_result = json.loads(
        asyncio.run(
            run_optimize(
                prompt_file=case["prompt_file"],
                train_file=case["train_file"],
                val_file=case["val_file"],
                algorithm=str(search_budget["algorithm"]),
                iterations=int(search_budget["iterations"]),
                beam_width=int(search_budget["beam_width"]),
                branch_factor=int(search_budget["branch_factor"]),
                n_runners=int(search_budget["n_runners"]),
                judge_mode=case["judge_mode"],
                judge_prompt_file=case.get("judge_prompt_file"),
            )
        )
    )

    baseline_score = asyncio.run(
        score_prompt_text(
            prompt_text,
            val_dataset,
            prompt_file=case["prompt_file"],
            judge_mode=case["judge_mode"],
            judge_prompt_file=case.get("judge_prompt_file"),
        )
    )
    optimized_score = asyncio.run(
        score_prompt_text(
            str(optimize_result["optimized_prompt"]),
            val_dataset,
            prompt_file=case["prompt_file"],
            judge_mode=case["judge_mode"],
            judge_prompt_file=case.get("judge_prompt_file"),
        )
    )

    report = {
        "prompt_file": case["prompt_file"],
        "train_file": case["train_file"],
        "val_file": case["val_file"],
        "judge_mode": case["judge_mode"],
        "algorithm": search_budget["algorithm"],
        "iterations": int(search_budget["iterations"]),
        "beam_width": int(search_budget["beam_width"]),
        "branch_factor": int(search_budget["branch_factor"]),
        "n_runners": int(search_budget["n_runners"]),
        "baseline_score": baseline_score,
        "optimized_score": optimized_score,
        "improvement": optimized_score - baseline_score,
        "candidate_count": optimize_result.get("candidate_count"),
        "optimized_prompt": optimize_result["optimized_prompt"],
    }
    return json.dumps(report, sort_keys=True)


def render_training_feedback(report: dict[str, Any]) -> str:
    """Convert one case report into Trace feedback."""
    improvement = float(report["improvement"])
    if improvement > 0.0:
        return (
            f"The proposed single-shot settings improved validation score by {improvement:.3f}. "
            f"Preserve the gain while keeping the runtime non-destructive and election-free. "
            f"Algorithm={report['algorithm']}, iterations={report['iterations']}, beam_width={report['beam_width']}."
        )
    if improvement == 0.0:
        return (
            "The proposed settings did not improve over the baseline. "
            "Adjust the algorithm and search budget to find a better optimized prompt without adding extra stages."
        )
    return (
        f"The proposed settings regressed validation score by {abs(improvement):.3f}. "
        f"Avoid similar configurations and search for a stronger single-shot optimization policy."
    )


def serialize_trace_parameters(policy: TraceSelfOptimizationPolicy) -> list[dict[str, Any]]:
    """Expose the current Trace parameters for inspection or persistence."""
    serialized: list[dict[str, Any]] = []
    for index, parameter in enumerate(policy.parameters(), start=1):
        name = getattr(parameter, "name", None) or getattr(parameter, "py_name", None) or f"parameter_{index}"
        value = getattr(parameter, "data", None)
        if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
            value = str(value)
        serialized.append({"name": str(name), "value": value})
    return serialized


def train_cases(
    cases: list[dict[str, Any]],
    *,
    epochs: int = 3,
    report_file: str | None = None,
) -> dict[str, Any]:
    """Run Trace self-training across one or more optimize benchmark cases."""
    if epochs <= 0:
        raise ValueError("epochs must be at least 1")
    if not cases:
        raise ValueError("At least one training case is required")

    normalized_cases = [normalize_training_case(case) for case in cases]
    model_settings = configure_trace_environment(normalized_cases[0]["prompt_file"])
    model_name = model_settings.get("inference_model")
    if not model_name:
        raise ValueError("Trace training requires GITHUB_MODELS_MODEL or OPENAI_MODEL to be configured.")

    from opto.optimizers import OptoPrime
    from opto.optimizers.optoprime import LLM

    policy = TraceSelfOptimizationPolicy()
    optimizer = OptoPrime(policy.parameters(), llm=LLM(model=str(model_name)), log=False)

    history: list[dict[str, Any]] = []
    for epoch in range(1, epochs + 1):
        for case in normalized_cases:
            prompt_text = Path(case["prompt_file"]).read_text(encoding="utf-8")
            train_dataset = load_jsonl(case["train_file"])
            val_dataset = load_jsonl(case["val_file"])
            placeholder_count = len(extract_placeholders(prompt_text))
            case_summary = build_trace_case_summary(
                prompt_text,
                train_dataset,
                val_dataset,
                case["judge_mode"],
                prompt_file=case["prompt_file"],
            )

            algorithm_node = policy.choose_algorithm(
                len(train_dataset),
                len(val_dataset),
                placeholder_count,
                case["judge_mode"],
            )
            budget_node = policy.choose_search_budget(
                len(train_dataset),
                len(val_dataset),
                placeholder_count,
                case["judge_mode"],
            )
            report_node = execute_training_case(
                json.dumps(case, sort_keys=True),
                algorithm_node,
                budget_node,
            )
            report = json.loads(report_node.data)
            report["epoch"] = epoch
            report["case_summary"] = case_summary
            history.append(report)

            optimizer.zero_feedback()
            optimizer.backward(report_node, render_training_feedback(report))
            optimizer.step()

    result = {
        "ok": True,
        "epochs": epochs,
        "case_count": len(normalized_cases),
        "model_provider": model_settings["provider"],
        "inference_model": model_name,
        "history": history,
        "learned_parameters": serialize_trace_parameters(policy),
    }
    if report_file:
        Path(report_file).write_text(json.dumps(result, indent=2), encoding="utf-8")
        result["report_file"] = report_file
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train trainer-optimize settings with Microsoft Trace")
    parser.add_argument("--cases-file", default=None, help="JSONL file of training cases")
    parser.add_argument("--prompt-file", default=None, help="Prompt file for a single training case")
    parser.add_argument("--train-file", default=None, help="Train JSONL for a single training case")
    parser.add_argument("--val-file", default=None, help="Validation JSONL for a single training case")
    parser.add_argument("--judge-mode", default="deterministic", choices=["deterministic", "custom", "llm_judge"])
    parser.add_argument("--judge-prompt-file", default=None, help="Optional judge prompt file for llm_judge cases")
    parser.add_argument("--epochs", type=int, default=3, help="Number of Trace training epochs")
    parser.add_argument("--report-file", default=None, help="Optional JSON report output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    cases = load_training_cases(
        cases_file=args.cases_file,
        prompt_file=args.prompt_file,
        train_file=args.train_file,
        val_file=args.val_file,
        judge_mode=args.judge_mode,
        judge_prompt_file=args.judge_prompt_file,
    )
    result = train_cases(cases, epochs=args.epochs, report_file=args.report_file)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())