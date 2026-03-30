"""Utilities for building explicit JSONL datasets for APO runs."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def derive_dataset_dir(prompt_file: str) -> Path:
    prompt_path = Path(prompt_file)
    if prompt_path.parent.name == "prompts":
        return prompt_path.parent.parent / "datasets"
    return prompt_path.parent / "datasets"


def rows_from_csv(
    csv_path: str | Path,
    input_field: str = "input",
    expected_field: str = "expected",
    scoring: str = "exact_match",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(csv_path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "input": row[input_field],
                    "expected": row[expected_field],
                    "scoring": scoring,
                }
            )
    return rows


def split_rows(rows: list[dict[str, Any]], train_ratio: float = 0.8) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be between 0.0 and 1.0")
    split_index = int(len(rows) * train_ratio)
    return rows[:split_index], rows[split_index:]


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> str:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return str(output_path)


def generate_datasets(
    prompt_file: str,
    rows: list[dict[str, Any]],
    train_ratio: float = 0.8,
) -> dict[str, str]:
    dataset_dir = derive_dataset_dir(prompt_file)
    train_rows, val_rows = split_rows(rows, train_ratio=train_ratio)
    train_file = write_jsonl(dataset_dir / "train.jsonl", train_rows)
    val_file = write_jsonl(dataset_dir / "val.jsonl", val_rows)
    return {
        "train_file": train_file,
        "val_file": val_file,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="generate_jsonl.py",
        description="Generate explicit train.jsonl and val.jsonl files under the modern datasets/ layout.",
    )
    parser.add_argument("--prompt-file", required=True, help="Path to the target markdown prompt file")
    parser.add_argument("--csv-file", required=True, help="CSV file with input and expected columns")
    parser.add_argument("--input-field", default="input")
    parser.add_argument("--expected-field", default="expected")
    parser.add_argument("--scoring", default="exact_match")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    rows = rows_from_csv(
        args.csv_file,
        input_field=args.input_field,
        expected_field=args.expected_field,
        scoring=args.scoring,
    )
    generated = generate_datasets(args.prompt_file, rows, train_ratio=args.train_ratio)
    print(json.dumps(generated, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())