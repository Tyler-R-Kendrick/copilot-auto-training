from __future__ import annotations

from pathlib import Path
from typing import Any


def derive_dataset_targets(prompt_file: str) -> dict[str, Any]:
    from run_optimize import extract_placeholders

    prompt_path = Path(prompt_file)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    eval_dir = prompt_path.parent / "evals"
    workspace_dir = prompt_path.parent / f"{prompt_path.stem}-workspace"
    return {
        "prompt_file": str(prompt_path),
        "eval_dir": str(eval_dir),
        "manifest_file": str(eval_dir / "evals.json"),
        "files_dir": str(eval_dir / "files"),
        "workspace_dir": str(workspace_dir),
        "benchmark_file": str(workspace_dir / "benchmark.json"),
        "placeholders": sorted(extract_placeholders(prompt_text)),
    }


def build_research_brief(
    prompt_file: str,
    task_description: str,
    scoring_rule: str,
) -> dict[str, Any]:
    targets = derive_dataset_targets(prompt_file)
    placeholders = ", ".join(targets["placeholders"]) if targets["placeholders"] else "input"
    research_queries = [
        f"public dataset {task_description}",
        f"benchmark dataset {task_description} eval cases",
        f"open data {task_description} labels {scoring_rule}",
        f"examples for prompt placeholders {placeholders}",
    ]
    workflow = [
        "Inspect the prompt interface and derive eval targets for evals/evals.json, evals/files/, and the workspace benchmark.",
        "Build research queries that match the task, scoring rule, and prompt schema.",
        "Create a source shortlist from public datasets, benchmarks, or documentation.",
        "Map promising source fields into realistic user prompts, expected outputs, optional input files, and objective assertions.",
        "Hand the source shortlist and mapping notes to the synthesize stage for evals/evals.json generation.",
    ]
    return {
        "skill": "research",
        "prompt_file": prompt_file,
        "task_description": task_description,
        "scoring_rule": scoring_rule,
        "targets": targets,
        "research_queries": research_queries,
        "workflow": workflow,
    }