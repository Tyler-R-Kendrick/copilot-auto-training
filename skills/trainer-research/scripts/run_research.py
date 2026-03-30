from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def extract_placeholders(template: str) -> set[str]:
    return set(re.findall(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", template))


def trainer_workspace_dir(prompt_path: Path) -> Path:
    prompt_name = prompt_path.name
    if prompt_name.endswith(".prompty"):
        prompt_name = prompt_name[: -len(".prompty")]
    elif prompt_name.endswith(".md"):
        prompt_name = prompt_name[: -len(".md")]
    else:
        prompt_name = prompt_path.stem
    return prompt_path.parent / ".trainer-workspace" / prompt_name


def derive_dataset_targets(prompt_file: str) -> dict[str, Any]:
    prompt_path = Path(prompt_file)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    eval_dir = prompt_path.parent / "evals"
    workspace_dir = trainer_workspace_dir(prompt_path)
    return {
        "prompt_file": str(prompt_path),
        "eval_dir": str(eval_dir),
        "manifest_file": str(eval_dir / "evals.json"),
        "files_dir": str(eval_dir / "files"),
        "workspace_dir": str(workspace_dir),
        "benchmark_file": str(workspace_dir / "benchmark.json"),
        "placeholders": sorted(extract_placeholders(prompt_text)),
    }


def build_research_brief(
    prompt_file: str,
    task_description: str,
    scoring_rule: str,
) -> dict[str, Any]:
    targets = derive_dataset_targets(prompt_file)
    placeholders = ", ".join(targets["placeholders"]) if targets["placeholders"] else "input"
    research_questions = [
        f"Which official datasets, benchmarks, or source documents best match {task_description}?",
        f"What labels, schemas, or evaluation rules does the source owner define for {scoring_rule}?",
        "Which licensing, provenance, or leakage constraints could block eval reuse?",
        f"How can the available source fields map onto the prompt placeholders: {placeholders}?",
    ]
    source_approval_bar = [
        "Accountable maintainer, publisher, or standards body.",
        "Traceable data origin, schema, and label definitions.",
        "Owner-provided evaluation rules, annotation guide, or benchmark protocol when available.",
        "Explicit licensing or reuse terms.",
        "Stable version, publication date, or release identifier.",
        "Acceptable contamination, leakage, privacy, and bias risk for authored eval use.",
    ]
    research_queries = [
        f"official benchmark dataset {task_description}",
        f"primary source dataset {task_description} annotation guidelines",
        f"official documentation {task_description} labels {scoring_rule}",
        f"original paper dataset card {task_description}",
        f"examples for prompt placeholders {placeholders}",
    ]
    workflow = [
        "Inspect the prompt interface and derive eval targets for evals/evals.json, evals/files/, and the workspace benchmark.",
        "Build a research plan that names the task boundary, research questions, approval bar, and any missing constraints before searching.",
        "Build primary-source-first research queries that match the task, scoring rule, and prompt schema.",
        "Collect candidate sources from official maintainers, benchmark owners, dataset cards, annotation guides, standards bodies, and original papers before considering secondary summaries.",
        "Score each candidate for authority, provenance, task fit, annotation quality, recency, licensing, and leakage risk, then reject weak or derivative sources.",
        "Assemble a ranked source shortlist with evidence notes and explicit rejection reasons.",
        "Map approved source fields into realistic user prompts, expected outputs, optional input files, and objective assertions.",
        "If no candidate clears the approval bar, stop and report the missing evidence instead of forcing a recommendation.",
        "Deliver a standalone research brief that another workflow can use without requiring this skill to call any other skill.",
    ]
    return {
        "skill": "research",
        "prompt_file": prompt_file,
        "task_description": task_description,
        "scoring_rule": scoring_rule,
        "targets": targets,
        "research_plan": {
            "target_layout": {
                "manifest_file": targets["manifest_file"],
                "files_dir": targets["files_dir"],
                "workspace_dir": targets["workspace_dir"],
                "benchmark_file": targets["benchmark_file"],
            },
            "observed_interface": {
                "placeholders": targets["placeholders"],
                "prompt_file": targets["prompt_file"],
            },
            "research_questions": research_questions,
            "approval_bar": source_approval_bar,
            "missing_inputs": [],
        },
        "research_queries": research_queries,
        "workflow": workflow,
        "source_approval_bar": source_approval_bar,
        "source_preferences": [
            "Official primary sources from benchmark owners, dataset maintainers, standards bodies, and original papers.",
            "High-credibility secondary sources only when they help locate or verify the primary source.",
            "Reject tertiary summaries, mirrors, and unverifiable aggregators when a primary source exists.",
        ],
        "source_quality_rubric": [
            "Authority: the source has an accountable owner, maintainer, or publisher.",
            "Provenance: the data origin, collection method, and labeling process are documented.",
            "Task fit: the source aligns with the prompt task, scoring rule, and expected outputs.",
            "Annotation quality: label definitions, instructions, and ambiguity handling are clear.",
            "Stability: version, publication date, and update history are available.",
            "Licensing: reuse terms are explicit and compatible with authored eval assets.",
            "Reliability risks: contamination, sampling bias, or derivative copying risks are identified.",
        ],
        "handoff_notes": [
            "Use approved sources, not rejected leads, when converting research into eval rows.",
            "Carry unresolved licensing, provenance, or leakage concerns into synthesis instead of hiding them.",
            "Stop at mapping notes unless the user explicitly asks to author eval rows.",
        ],
        "deliverable": "Standalone research brief with ranked sources, rejected candidates, and eval-authoring mapping notes.",
    }