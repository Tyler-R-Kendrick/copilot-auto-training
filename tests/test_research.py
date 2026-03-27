"""Tests for the research skill runtime in research/scripts/run_research.py."""
from __future__ import annotations

from run_research import build_research_brief, derive_dataset_targets


def test_derive_dataset_targets_uses_prompt_adjacent_layout(tmp_path):
    prompt_path = tmp_path / "prompts" / "intent.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Classify intent: {input}\n", encoding="utf-8")

    result = derive_dataset_targets(str(prompt_path))

    assert result["placeholders"] == ["input"]
    assert result["train_file"].endswith("/prompts/.evals/intent/train.jsonl")
    assert result["val_file"].endswith("/prompts/.evals/intent/val.jsonl")


def test_build_research_brief_includes_public_dataset_queries(tmp_path):
    prompt_path = tmp_path / "prompts" / "intent.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Classify intent: {input}\n", encoding="utf-8")

    brief = build_research_brief(
        prompt_file=str(prompt_path),
        task_description="Support intent classification",
        scoring_rule="exact_match",
    )

    assert brief["skill"] == "research"
    assert any("public dataset" in query.lower() for query in brief["research_queries"])
    assert any("source shortlist" in step.lower() for step in brief["workflow"])
    assert brief["targets"]["train_file"].endswith("train.jsonl")