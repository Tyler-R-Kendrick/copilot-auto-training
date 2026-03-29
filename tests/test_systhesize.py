"""Tests for the synthesize skill runtime in synthesize/scripts/run_synthesize.py."""
from __future__ import annotations

import json

from run_synthesize import derive_dataset_targets, render_evals_json


def test_derive_dataset_targets_uses_official_eval_layout(tmp_path):
    prompt_path = tmp_path / "prompts" / "support.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Question: {question}\nContext: {context}\n", encoding="utf-8")

    result = derive_dataset_targets(str(prompt_path))

    assert result["placeholders"] == ["context", "question"]
    assert result["manifest_file"].endswith("/prompts/evals/evals.json")
    assert result["files_dir"].endswith("/prompts/evals/files")
    assert result["dataset_dir"].endswith("/datasets")
    assert result["train_file"].endswith("/datasets/train.jsonl")
    assert result["val_file"].endswith("/datasets/val.jsonl")
    assert result["workspace_dir"].endswith("/prompts/.trainer-workspace/support")


def test_derive_dataset_targets_uses_local_datasets_for_skill_files(tmp_path):
    skill_path = tmp_path / "skills" / "demo-skill" / "SKILL.md"
    skill_path.parent.mkdir(parents=True)
    skill_path.write_text("Question: {question}\n", encoding="utf-8")

    result = derive_dataset_targets(str(skill_path))

    assert result["dataset_dir"].endswith("/skills/demo-skill/datasets")
    assert result["train_file"].endswith("/skills/demo-skill/datasets/train.jsonl")
    assert result["val_file"].endswith("/skills/demo-skill/datasets/val.jsonl")


def test_render_evals_json_writes_official_manifest_shape():
    text = render_evals_json(
        "support-skill",
        [
            {
                "id": 1,
                "prompt": "What is the refund policy?",
                "expected_output": "A support answer that explains the refund policy clearly.",
                "files": ["evals/files/policy.md"],
                "assertions": ["The answer mentions the refund window."],
            },
            {
                "id": 2,
                "prompt": "How do I reset my password?",
                "expected_output": "A support answer that explains the password reset steps.",
            },
        ],
    )

    payload = json.loads(text)
    assert payload["skill_name"] == "support-skill"
    assert len(payload["evals"]) == 2
    assert payload["evals"][0]["files"] == ["evals/files/policy.md"]
    assert payload["evals"][1]["expected_output"].startswith("A support answer")