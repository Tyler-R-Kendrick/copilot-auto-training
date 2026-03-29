from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def extract_placeholders(template: str) -> set[str]:
    return set(re.findall(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", template))


def derive_dataset_dir(prompt_file: str) -> Path:
    prompt_path = Path(prompt_file)
    if prompt_path.parent.name == "prompts":
        return prompt_path.parent.parent / "datasets"
    return prompt_path.parent / "datasets"


def derive_dataset_targets(prompt_file: str) -> dict[str, Any]:
    prompt_path = Path(prompt_file)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    eval_dir = prompt_path.parent / "evals"
    dataset_dir = derive_dataset_dir(prompt_file)
    workspace_dir = prompt_path.parent / f"{prompt_path.stem}-workspace"
    return {
        "prompt_file": str(prompt_path),
        "eval_dir": str(eval_dir),
        "manifest_file": str(eval_dir / "evals.json"),
        "files_dir": str(eval_dir / "files"),
        "dataset_dir": str(dataset_dir),
        "train_file": str(dataset_dir / "train.jsonl"),
        "val_file": str(dataset_dir / "val.jsonl"),
        "workspace_dir": str(workspace_dir),
        "benchmark_file": str(workspace_dir / "benchmark.json"),
        "placeholders": sorted(extract_placeholders(prompt_text)),
    }


def render_evals_json(skill_name: str, evals: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "skill_name": skill_name,
            "evals": evals,
        },
        indent=2,
        ensure_ascii=True,
    ) + "\n"