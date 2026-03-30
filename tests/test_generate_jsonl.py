from __future__ import annotations

import csv
import json
from pathlib import Path

from generate_jsonl import derive_dataset_dir, generate_datasets, rows_from_csv, split_rows


def test_derive_dataset_dir_uses_modern_layout(tmp_path):
    prompt_path = tmp_path / "prompts" / "support.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Question: {input}\n", encoding="utf-8")

    dataset_dir = derive_dataset_dir(str(prompt_path))
    assert dataset_dir == tmp_path / "datasets"


def test_rows_from_csv_builds_exact_match_rows(tmp_path):
    csv_path = tmp_path / "examples.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["input", "expected"])
        writer.writeheader()
        writer.writerow({"input": "ping", "expected": "pong"})

    rows = rows_from_csv(csv_path)
    assert rows == [{"input": "ping", "expected": "pong", "scoring": "exact_match"}]


def test_split_rows_uses_train_ratio():
    rows = [{"input": str(index), "expected": str(index)} for index in range(10)]
    train_rows, val_rows = split_rows(rows, train_ratio=0.8)
    assert len(train_rows) == 8
    assert len(val_rows) == 2


def test_generate_datasets_writes_modern_train_and_val(tmp_path):
    prompt_path = tmp_path / "prompts" / "support.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Question: {input}\n", encoding="utf-8")

    rows = [
        {"input": f"request-{index}", "expected": f"answer-{index}", "scoring": "exact_match"}
        for index in range(5)
    ]
    generated = generate_datasets(str(prompt_path), rows, train_ratio=0.6)

    train_path = Path(generated["train_file"])
    val_path = Path(generated["val_file"])
    assert train_path.is_file()
    assert val_path.is_file()

    train_rows = [json.loads(line) for line in train_path.read_text(encoding="utf-8").splitlines()]
    val_rows = [json.loads(line) for line in val_path.read_text(encoding="utf-8").splitlines()]
    assert len(train_rows) == 3
    assert len(val_rows) == 2