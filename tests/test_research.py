"""Tests for the research skill runtime in research/scripts/run_research.py."""
from __future__ import annotations

from run_research import build_research_brief, derive_dataset_targets


def test_derive_dataset_targets_uses_official_eval_layout(tmp_path):
    prompt_path = tmp_path / "prompts" / "intent.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Classify intent: {input}\n", encoding="utf-8")

    result = derive_dataset_targets(str(prompt_path))

    assert result["placeholders"] == ["input"]
    assert result["manifest_file"].endswith("/prompts/evals/evals.json")
    assert result["files_dir"].endswith("/prompts/evals/files")
    assert result["workspace_dir"].endswith("/prompts/.trainer-workspace/intent")
    assert result["benchmark_file"].endswith("/prompts/.trainer-workspace/intent/benchmark.json")


def test_build_research_brief_includes_public_dataset_queries(tmp_path):
    prompt_path = tmp_path / "prompts" / "intent.md"
    prompt_path.parent.mkdir(parents=True)
    prompt_path.write_text("Classify intent: {input}\n", encoding="utf-8")

    brief = build_research_brief(
        prompt_file=str(prompt_path),
        task_description="Support intent classification",
        scoring_rule="exact_match",
    )

    assert brief["agent"] == "researcher"
    assert brief["skill"] == "researcher-research"
    assert any("official" in query.lower() or "primary source" in query.lower() for query in brief["research_queries"])
    assert any("source shortlist" in step.lower() for step in brief["workflow"])
    assert any("without requiring this skill to call any other skill" in step.lower() for step in brief["workflow"])
    assert brief["targets"]["manifest_file"].endswith("evals.json")
    assert any("workspace benchmark" in step.lower() for step in brief["workflow"])
    assert brief["source_preferences"][0].lower().startswith("official primary sources")
    assert any("authority" in item.lower() for item in brief["source_quality_rubric"])
    assert any("licensing" in item.lower() for item in brief["source_quality_rubric"])
