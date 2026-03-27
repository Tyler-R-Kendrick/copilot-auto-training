from __future__ import annotations

from pathlib import Path
from typing import Any


def derive_dataset_targets(prompt_file: str) -> dict[str, Any]:
    from run_optimize import extract_placeholders

    prompt_path = Path(prompt_file)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    eval_dir = prompt_path.parent / ".evals" / prompt_path.stem
    return {
        "prompt_file": str(prompt_path),
        "eval_dir": str(eval_dir),
        "train_file": str(eval_dir / "train.jsonl"),
        "val_file": str(eval_dir / "val.jsonl"),
        "test_file": str(eval_dir / "test.jsonl"),
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
        f"benchmark dataset {task_description} jsonl",
        f"open data {task_description} labels {scoring_rule}",
        f"examples for prompt placeholders {placeholders}",
    ]
    workflow = [
        "Inspect the prompt interface and derive prompt-adjacent train.jsonl and val.jsonl targets.",
        "Build research queries that match the task, scoring rule, and prompt schema.",
        "Create a source shortlist from public datasets, benchmarks, or documentation.",
        "Map promising source fields into the prompt-visible schema and note evaluator-only fields.",
        "Hand the source shortlist and mapping notes to the synthesize stage for JSONL generation.",
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