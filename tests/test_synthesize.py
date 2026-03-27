"""Tests for the synthesize skill runtime in synthesize/scripts/run_synthesize.py."""
from __future__ import annotations

import json

from run_synthesize import derive_dataset_targets, render_jsonl


def test_derive_dataset_targets_uses_prompt_adjacent_layout(tmp_path):
    prompt_path = tmp_path / "prompts" / "support.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Question: {question}\nContext: {context}\n", encoding="utf-8")

    result = derive_dataset_targets(str(prompt_path))

    assert result["placeholders"] == ["context", "question"]
    assert result["train_file"].endswith("/prompts/.evals/support/train.jsonl")
    assert result["val_file"].endswith("/prompts/.evals/support/val.jsonl")


def test_render_jsonl_writes_one_json_object_per_line():
    text = render_jsonl([
        {"input": {"question": "What is the refund policy?"}, "expected": "refund_policy", "scoring": "exact_match"},
        {"input": {"question": "How do I reset my password?"}, "expected": "reset_password", "scoring": "exact_match"},
    ])

    lines = text.splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["expected"] == "refund_policy"