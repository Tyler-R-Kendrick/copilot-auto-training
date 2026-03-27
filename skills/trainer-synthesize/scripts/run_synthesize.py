from __future__ import annotations

import json
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


def render_jsonl(rows: list[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(row, ensure_ascii=True) for row in rows)