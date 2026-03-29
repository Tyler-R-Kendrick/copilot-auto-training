from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any


BASELINE_CONFIGS = {"baseline", "without_skill", "old_skill"}
PROMPT_ARTIFACT_GLOBS = (
    "*prompt*.md",
    "*prompt*.txt",
    "*candidate*.md",
    "*candidate*.txt",
    "*.prompt.md",
    "*.prompt.txt",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_config_dir(path: Path) -> bool:
    return (
        (path / "grading.json").is_file()
        or (path / "outputs").is_dir()
        or any(child.is_dir() and child.name.startswith("run-") for child in path.iterdir())
    )


def _is_eval_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if (path / "eval_metadata.json").is_file():
        return True
    return any(child.is_dir() and _is_config_dir(child) for child in path.iterdir())


def _sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.rsplit("-", 1)
    if len(suffix) == 2 and suffix[1].isdigit():
        return int(suffix[1]), path.name
    return 10**9, path.name


def resolve_iteration_dir(workspace_dir: str | Path, iteration: str | int | None = None) -> Path:
    workspace_path = Path(workspace_dir)
    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace directory not found: {workspace_path}")

    if iteration is None:
        if _is_eval_dir(workspace_path) or any(_is_eval_dir(child) for child in workspace_path.iterdir() if child.is_dir()):
            return workspace_path
        iteration_dirs = sorted(
            [child for child in workspace_path.iterdir() if child.is_dir() and child.name.startswith("iteration-")],
            key=_sort_key,
        )
        if iteration_dirs:
            return iteration_dirs[-1]
        raise FileNotFoundError(f"No iteration directories or eval directories found under {workspace_path}")

    if isinstance(iteration, int) or str(iteration).isdigit():
        candidate = workspace_path / f"iteration-{iteration}"
    else:
        raw_iteration = Path(str(iteration))
        candidate = raw_iteration if raw_iteration.is_absolute() else workspace_path / raw_iteration

    if not candidate.exists():
        raise FileNotFoundError(f"Iteration directory not found: {candidate}")
    return candidate


def resolve_manifest_file(iteration_dir: Path, manifest_file: str | None = None) -> Path | None:
    if manifest_file is not None:
        candidate = Path(manifest_file)
        if not candidate.is_file():
            raise FileNotFoundError(f"Eval manifest not found: {candidate}")
        return candidate

    search_roots = [iteration_dir, iteration_dir.parent, iteration_dir.parent.parent]
    for root in search_roots:
        candidate = root / "evals" / "evals.json"
        if candidate.is_file():
            return candidate
    return None


def _iter_eval_dirs(iteration_dir: Path) -> list[Path]:
    search_root = iteration_dir / "runs" if (iteration_dir / "runs").is_dir() else iteration_dir
    if _is_eval_dir(search_root):
        return [search_root]
    return [child for child in sorted(search_root.iterdir(), key=_sort_key) if _is_eval_dir(child)]


def _iter_run_dirs(config_dir: Path) -> list[Path]:
    run_dirs = [child for child in sorted(config_dir.iterdir(), key=_sort_key) if child.is_dir() and child.name.startswith("run-")]
    if run_dirs:
        return run_dirs
    return [config_dir]


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return _load_json(path)


def _coerce_float(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _coerce_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _read_run_record(eval_dir: Path, config_dir: Path, run_dir: Path, eval_index: int) -> dict[str, Any] | None:
    metadata = _read_optional_json(eval_dir / "eval_metadata.json")
    grading = _read_optional_json(run_dir / "grading.json")
    timing = _read_optional_json(run_dir / "timing.json")

    if not grading:
        return None

    summary = grading.get("summary", {})
    timing_block = grading.get("timing", {})
    execution_metrics = grading.get("execution_metrics", {})
    eval_key = str(metadata.get("eval_id", eval_dir.name or eval_index))
    run_number = 1
    if run_dir.name.startswith("run-"):
        run_number = _coerce_int(run_dir.name.split("-", 1)[1]) or 1

    return {
        "config": config_dir.name,
        "eval_key": eval_key,
        "eval_name": str(metadata.get("eval_name", eval_dir.name)),
        "run_number": run_number,
        "pass_rate": _coerce_float(summary.get("pass_rate", 0.0)),
        "passed": _coerce_int(summary.get("passed", 0)),
        "failed": _coerce_int(summary.get("failed", 0)),
        "total": _coerce_int(summary.get("total", 0)),
        "time_seconds": _coerce_float(
            timing_block.get("total_duration_seconds", timing.get("total_duration_seconds", 0.0))
        ),
        "tokens": _coerce_int(timing.get("total_tokens", execution_metrics.get("output_chars", 0))),
        "errors": _coerce_int(execution_metrics.get("errors_encountered", 0)),
        "expectations": grading.get("expectations", []),
        "notes": grading.get("user_notes_summary", {}),
        "run_dir": run_dir,
    }


def _load_runs_from_workspace(iteration_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for eval_index, eval_dir in enumerate(_iter_eval_dirs(iteration_dir)):
        for config_dir in sorted(eval_dir.iterdir(), key=_sort_key):
            if not config_dir.is_dir() or not _is_config_dir(config_dir):
                continue
            for run_dir in _iter_run_dirs(config_dir):
                record = _read_run_record(eval_dir, config_dir, run_dir, eval_index)
                if record is not None:
                    records.append(record)
    return records


def _load_runs_from_benchmark(iteration_dir: Path) -> list[dict[str, Any]]:
    benchmark_file = iteration_dir / "benchmark.json"
    if not benchmark_file.is_file():
        return []

    benchmark = _load_json(benchmark_file)
    records: list[dict[str, Any]] = []
    for run in benchmark.get("runs", []):
        result = run.get("result", {})
        records.append(
            {
                "config": str(run.get("configuration", "unknown")),
                "eval_key": str(run.get("eval_id", run.get("eval_name", "unknown"))),
                "eval_name": str(run.get("eval_name", run.get("eval_id", "unknown"))),
                "run_number": _coerce_int(run.get("run_number", 1)) or 1,
                "pass_rate": _coerce_float(result.get("pass_rate", 0.0)),
                "passed": _coerce_int(result.get("passed", 0)),
                "failed": _coerce_int(result.get("failed", 0)),
                "total": _coerce_int(result.get("total", 0)),
                "time_seconds": _coerce_float(result.get("time_seconds", 0.0)),
                "tokens": _coerce_int(result.get("tokens", 0)),
                "errors": _coerce_int(result.get("errors", 0)),
                "expectations": run.get("expectations", []),
                "notes": run.get("notes", []),
                "run_dir": iteration_dir / str(run.get("configuration", "unknown")),
            }
        )
    return records


def _read_prompt_artifact(run_dirs: list[Path]) -> tuple[str | None, str | None]:
    search_roots: list[Path] = []
    for run_dir in run_dirs:
        outputs_dir = run_dir / "outputs"
        if outputs_dir.is_dir():
            search_roots.append(outputs_dir)
        search_roots.append(run_dir)

    for root in search_roots:
        for pattern in PROMPT_ARTIFACT_GLOBS:
            for candidate in sorted(root.glob(pattern)):
                if not candidate.is_file():
                    continue
                return str(candidate), candidate.read_text(encoding="utf-8")
    return None, None


def _manifest_eval_count(manifest_file: Path | None) -> int | None:
    if manifest_file is None:
        return None
    payload = _load_json(manifest_file)
    evals = payload.get("evals", [])
    return len(evals) if isinstance(evals, list) and evals else None


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _is_baseline(config_name: str) -> bool:
    return config_name in BASELINE_CONFIGS or config_name.endswith("_baseline")


def build_selection_pool(
    workspace_dir: str,
    iteration: str | int | None = None,
    manifest_file: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    iteration_dir = resolve_iteration_dir(workspace_dir, iteration)
    resolved_manifest = resolve_manifest_file(iteration_dir, manifest_file)

    run_records = _load_runs_from_workspace(iteration_dir)
    selection_source = "workspace"
    if not run_records:
        run_records = _load_runs_from_benchmark(iteration_dir)
        selection_source = "benchmark"
    if not run_records:
        raise RuntimeError(
            "No scored candidate runs were found. Expected grading.json/timing.json files "
            "under eval configuration directories or a benchmark.json fallback."
        )

    expected_eval_count = _manifest_eval_count(resolved_manifest)
    if expected_eval_count is None:
        expected_eval_count = len({record["eval_key"] for record in run_records})
    expected_eval_count = max(expected_eval_count, 1)

    by_config: dict[str, list[dict[str, Any]]] = {}
    for record in run_records:
        by_config.setdefault(record["config"], []).append(record)

    selection_pool: list[dict[str, Any]] = []
    for config_name, records in sorted(by_config.items()):
        eval_keys = sorted({record["eval_key"] for record in records})
        prompt_file, prompt_text = _read_prompt_artifact([record["run_dir"] for record in records])
        raw_score = round(_mean([record["pass_rate"] for record in records]), 4)
        coverage_ratio = round(len(eval_keys) / expected_eval_count, 4)
        penalty = round(max(0.0, 1.0 - coverage_ratio), 4)
        adjusted_score = round(max(0.0, raw_score - penalty), 4)
        mean_time = round(_mean([record["time_seconds"] for record in records]), 4)
        mean_tokens = round(_mean([float(record["tokens"]) for record in records]), 4)
        mean_errors = round(_mean([float(record["errors"]) for record in records]), 4)

        selection_pool.append(
            {
                "source": config_name,
                "score": adjusted_score,
                "raw_score": raw_score,
                "penalty": penalty,
                "mean_time_seconds": mean_time,
                "mean_tokens": mean_tokens,
                "mean_errors": mean_errors,
                "run_count": len(records),
                "eval_count": len(eval_keys),
                "coverage_ratio": coverage_ratio,
                "eval_keys": eval_keys,
                "prompt_file": prompt_file,
                "prompt_text": prompt_text,
                "is_baseline": _is_baseline(config_name),
                "is_winner": False,
            }
        )

    selection_pool.sort(
        key=lambda candidate: (
            -candidate["score"],
            -candidate["raw_score"],
            candidate["mean_errors"],
            candidate["mean_time_seconds"],
            candidate["mean_tokens"],
            candidate["source"],
        )
    )

    return selection_pool, {
        "workspace_dir": str(Path(workspace_dir)),
        "iteration_dir": str(iteration_dir),
        "manifest_file": str(resolved_manifest) if resolved_manifest is not None else None,
        "benchmark_file": str(iteration_dir / "benchmark.json"),
        "selection_source": selection_source,
        "expected_eval_count": expected_eval_count,
    }


async def run_election_search(
    workspace_dir: str,
    iteration: str | int | None = None,
    manifest_file: str | None = None,
) -> dict[str, Any]:
    persisted_candidates, context = build_selection_pool(
        workspace_dir=workspace_dir,
        iteration=iteration,
        manifest_file=manifest_file,
    )
    winner = persisted_candidates[0]
    for candidate in persisted_candidates:
        candidate["is_winner"] = candidate["source"] == winner["source"]

    return {
        "winner": winner["source"],
        "best_prompt": winner.get("prompt_text"),
        "best_prompt_file": winner.get("prompt_file"),
        "best_candidate": winner,
        "persisted_candidates": persisted_candidates,
        "steering_applied": False,
        **context,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Elect the strongest configuration from a skill eval workspace.")
    parser.add_argument("workspace_dir", help="Path to the skill evaluation workspace or iteration directory")
    parser.add_argument("--iteration", help="Iteration number, iteration directory name, or explicit path")
    parser.add_argument("--manifest-file", help="Optional path to evals/evals.json")
    parser.add_argument("--output-file", help="Optional path to write the election result JSON")
    args = parser.parse_args(argv)

    result = asyncio.run(
        run_election_search(
            workspace_dir=args.workspace_dir,
            iteration=args.iteration,
            manifest_file=args.manifest_file,
        )
    )
    rendered = json.dumps(result, indent=2, ensure_ascii=True) + "\n"
    if args.output_file:
        Path(args.output_file).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())