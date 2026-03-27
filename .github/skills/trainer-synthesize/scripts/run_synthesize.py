from __future__ import annotations

import json
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


def render_evals_json(skill_name: str, evals: list[dict[str, Any]]) -> str:
    return json.dumps(
        {
            "skill_name": skill_name,
            "evals": evals,
        },
        indent=2,
        ensure_ascii=True,
    ) + "\n"