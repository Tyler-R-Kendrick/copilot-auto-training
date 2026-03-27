"""
run_optimize.py — Standalone script for optimizing a markdown prompt file
using Agent Lightning APO (Automatic Prompt Optimization).

Usage (via CLI):
    python scripts/run_optimize.py --help

Usage (imported in tests):
    from run_optimize import run_optimize, load_jsonl, extract_placeholders, ...
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
from datetime import UTC, datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4


HIDDEN_SCORING_FIELDS = {
    "criteria",
    "expected",
    "expected_json",
    "reference",
    "scoring",
}

DEFAULT_GITHUB_MODELS_ENDPOINT = "https://models.github.ai/inference"
DEFAULT_GITHUB_GRADIENT_MODEL = "openai/gpt-4.1-mini"
DEFAULT_GITHUB_APPLY_EDIT_MODEL = "openai/gpt-4.1-mini"


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def load_jsonl(path: str) -> list[dict[str, Any]]:
    """Load a JSONL file and return a list of parsed dicts (blank lines skipped)."""
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_repo_root(start_path: str) -> Path:
    """Find the nearest repository-like root for the given prompt path."""
    path = Path(start_path).resolve()
    candidates = [path.parent, *path.parents]

    for candidate in candidates:
        if (candidate / ".env").exists():
            return candidate
    for candidate in candidates:
        if any((candidate / marker).exists() for marker in ("requirements.txt", ".git", "README.md")):
            return candidate
    return path.parent


def load_dotenv_file(dotenv_path: Path) -> dict[str, str]:
    """Parse a simple .env file into a dictionary."""
    if not dotenv_path.exists():
        return {}

    parsed: dict[str, str] = {}
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed


def resolve_model_settings(prompt_file: str) -> dict[str, str | None]:
    """Resolve GitHub Models or OpenAI-compatible client settings from repo root .env and process env."""
    repo_root = find_repo_root(prompt_file)
    dotenv_values = load_dotenv_file(repo_root / ".env")

    github_names = (
        "GITHUB_MODELS_API_KEY",
        "GITHUB_MODELS_ENDPOINT",
        "GITHUB_MODELS_MODEL",
        "GITHUB_MODELS_GRADIENT_MODEL",
        "GITHUB_MODELS_APPLY_EDIT_MODEL",
    )

    dotenv_github_selected = any(dotenv_values.get(name) not in (None, "") for name in github_names)
    process_github_selected = any(os.getenv(name) not in (None, "") for name in github_names)

    def get_value(
        name: str,
        default: str | None = None,
        *,
        prefer_dotenv: bool = False,
        dotenv_only: bool = False,
    ) -> str | None:
        dotenv_value = dotenv_values.get(name)
        process_value = os.getenv(name)

        if dotenv_only:
            if dotenv_value not in (None, ""):
                return dotenv_value
            return default

        if prefer_dotenv and dotenv_value not in (None, ""):
            return dotenv_value
        if process_value not in (None, ""):
            return process_value
        if dotenv_value not in (None, ""):
            return dotenv_value
        return default

    github_selected = dotenv_github_selected or process_github_selected

    if github_selected:
        use_dotenv_only = dotenv_github_selected
        api_key = get_value("GITHUB_MODELS_API_KEY", dotenv_only=use_dotenv_only) or get_value(
            "OPENAI_API_KEY", dotenv_only=use_dotenv_only
        )
        if not api_key:
            raise ValueError(
                "GitHub Models configuration requires GITHUB_MODELS_API_KEY or OPENAI_API_KEY."
            )

        gradient_model = get_value(
            "GITHUB_MODELS_GRADIENT_MODEL",
            get_value(
                "GITHUB_MODELS_MODEL",
                DEFAULT_GITHUB_GRADIENT_MODEL,
                dotenv_only=use_dotenv_only,
            ),
            dotenv_only=use_dotenv_only,
        )
        apply_edit_model = get_value(
            "GITHUB_MODELS_APPLY_EDIT_MODEL",
            gradient_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
            dotenv_only=use_dotenv_only,
        )
        return {
            "provider": "github",
            "api_key": api_key,
            "base_url": get_value(
                "GITHUB_MODELS_ENDPOINT",
                DEFAULT_GITHUB_MODELS_ENDPOINT,
                dotenv_only=use_dotenv_only,
            ),
            "gradient_model": gradient_model or DEFAULT_GITHUB_GRADIENT_MODEL,
            "apply_edit_model": apply_edit_model or DEFAULT_GITHUB_APPLY_EDIT_MODEL,
            "repo_root": str(repo_root),
        }

    return {
        "provider": "openai",
        "api_key": get_value("OPENAI_API_KEY"),
        "base_url": get_value("OPENAI_BASE_URL"),
        "gradient_model": DEFAULT_GITHUB_GRADIENT_MODEL,
        "apply_edit_model": DEFAULT_GITHUB_APPLY_EDIT_MODEL,
        "repo_root": str(repo_root),
    }


def create_openai_client(prompt_file: str) -> tuple[Any, dict[str, str | None]]:
    """Create the AsyncOpenAI client using repo-root .env settings when available."""
    from openai import AsyncOpenAI

    model_settings = resolve_model_settings(prompt_file)
    client_kwargs: dict[str, str] = {}
    if model_settings.get("api_key"):
        client_kwargs["api_key"] = str(model_settings["api_key"])
    if model_settings.get("base_url"):
        client_kwargs["base_url"] = str(model_settings["base_url"])
    return AsyncOpenAI(**client_kwargs), model_settings


def extract_placeholders(template: str) -> set[str]:
    """
    Return the set of f-string placeholder names in *template*.

    The regex matches single-brace placeholders like {identifier} while
    excluding double-brace escapes like {{literal}}:
      (?<!\\{)  — negative lookbehind: preceding char is NOT {
      \\{        — literal opening brace
      (...)     — capture group: the identifier name
      [a-zA-Z_][a-zA-Z0-9_]*  — valid Python identifier (must not start with digit)
      \\}        — literal closing brace
      (?!\\})   — negative lookahead: following char is NOT }
    """
    return set(re.findall(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", template))


def flatten_keys(obj: Any, prefix: str = "") -> set[str]:
    """
    Return all dotted key paths for a (potentially nested) dict.

    Non-dict values return an empty set.
    """
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            keys |= flatten_keys(v, path)
    return keys


def validate_template_against_task(template: str, sample_task: dict[str, Any]) -> None:
    """
    Raise ValueError if any placeholder in *template* cannot be satisfied
    from the top-level or nested keys of *sample_task*.
    """
    placeholders = extract_placeholders(template)
    task_keys = flatten_keys(sample_task)
    simple_keys = set(sample_task.keys())
    valid_keys = task_keys | simple_keys
    missing = sorted(p for p in placeholders if p not in valid_keys)
    if missing:
        raise ValueError(
            f"Template placeholders not found in task schema: {missing}. "
            f"Available keys: {sorted(valid_keys)}"
        )


def derive_evals_paths(prompt_file: str) -> tuple[str, str, str]:
    """Return default prompt-adjacent train/val/test dataset paths."""
    prompt_path = Path(prompt_file)
    eval_dir = prompt_path.parent / ".evals" / prompt_path.stem
    return tuple(str(eval_dir / name) for name in ("train.jsonl", "val.jsonl", "test.jsonl"))


def derive_artifact_paths(prompt_file: str) -> tuple[Path, Path, Path]:
    """Return the eval dir, temp artifact dir, and steering file for a prompt."""
    prompt_path = Path(prompt_file)
    eval_dir = prompt_path.parent / ".evals" / prompt_path.stem
    tmp_dir = eval_dir / ".tmp"
    return eval_dir, tmp_dir, tmp_dir / "steering.md"


def _default_evals_readme(prompt_file: str) -> str:
    prompt_path = Path(prompt_file)
    return "\n".join(
        [
            f"# Eval Assets For {prompt_path.stem}",
            "",
            "This folder stores prompt-adjacent optimization datasets and run artifacts.",
            "",
            "Expected dataset files:",
            "- train.jsonl",
            "- val.jsonl",
            "- test.jsonl (optional)",
            "",
            "Temporary run artifacts are written under .tmp/ and are gitignored.",
            "",
        ]
    )


def _minimal_required_info(placeholders: list[str]) -> list[str]:
    placeholder_text = ", ".join(placeholders) if placeholders else "the prompt input"
    return [
        "A small set of representative examples or a CSV file to turn into train.jsonl and val.jsonl.",
        f"Values for every prompt placeholder: {placeholder_text}.",
        "The expected answer format or scoring rule for each example.",
    ]


def build_missing_dataset_request(prompt_file: str) -> dict[str, Any]:
    prompt_path = Path(prompt_file)
    eval_dir, _, _ = derive_artifact_paths(prompt_file)
    default_train, default_val, _ = derive_evals_paths(prompt_file)
    prompt_text = prompt_path.read_text(encoding="utf-8")
    placeholders = sorted(extract_placeholders(prompt_text))

    request = {
        "prompt_file": str(prompt_path),
        "missing_files": [default_train, default_val],
        "placeholders": placeholders,
        "required_info": _minimal_required_info(placeholders),
        "suggested_next_step": (
            "Use scripts/generate_jsonl.py after collecting the minimum required information."
        ),
    }
    request_path = eval_dir / "dataset-request.json"
    request_path.write_text(json.dumps(request, indent=2), encoding="utf-8")
    return request


def ensure_evals_scaffold(
    prompt_file: str,
    train_file: str | None = None,
    val_file: str | None = None,
    report_file: str | None = None,
) -> dict[str, str]:
    """Create a visible prompt-adjacent .evals scaffold and persist dataset hints."""
    eval_dir, _, _ = derive_artifact_paths(prompt_file)
    eval_dir.mkdir(parents=True, exist_ok=True)

    readme_path = eval_dir / "README.md"
    if not readme_path.exists():
        readme_path.write_text(_default_evals_readme(prompt_file), encoding="utf-8")

    manifest_path = eval_dir / "datasets.json"
    manifest = {
        "prompt_file": str(Path(prompt_file)),
        "train_file": train_file,
        "val_file": val_file,
        "default_train_file": str(eval_dir / "train.jsonl"),
        "default_val_file": str(eval_dir / "val.jsonl"),
        "default_test_file": str(eval_dir / "test.jsonl"),
        "default_report_file": str(eval_dir / "report.json"),
        "report_file": report_file or str(eval_dir / "report.json"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def resolve_dataset_paths(
    prompt_file: str,
    train_file: str | None,
    val_file: str | None,
) -> tuple[str, str]:
    """Resolve explicit dataset paths or prompt-adjacent `.evals` defaults."""
    default_train, default_val, _ = derive_evals_paths(prompt_file)
    resolved_train = train_file or default_train
    resolved_val = val_file or default_val

    missing_paths = [
        path for path in (resolved_train, resolved_val)
        if not Path(path).is_file()
    ]
    if missing_paths:
        raise ValueError(
            "Could not resolve required dataset files: "
            + ", ".join(missing_paths)
        )

    return resolved_train, resolved_val


def _prompt_fields(task: dict[str, Any]) -> dict[str, Any]:
    """Return only task fields that should be visible to prompt rendering."""
    visible: dict[str, Any] = {}

    input_value = task.get("input")
    if isinstance(input_value, dict):
        visible.update(input_value)
    elif input_value is not None:
        visible["input"] = input_value

    for key, value in task.items():
        if key != "input" and key not in HIDDEN_SCORING_FIELDS:
            visible[key] = value

    return visible


def _normalize_text(value: Any) -> str:
    return " ".join(str(value).split()).lower()


def _default_judge_prompt_file() -> str:
    return str(Path(__file__).resolve().parent.parent / "assets" / "judge-default.md")


def _default_steering_body() -> str:
    return "\n".join(
        [
            "# Optimization Steering",
            "",
            "Carry forward lessons from prior optimization runs.",
            "Use this file to avoid repeating failures, reward hacking, and verbose, irrelevant, or redundant outputs.",
            "",
            "## Global Guidance",
            "- Prefer direct, task-aligned responses.",
            "- Avoid reward hacking or evaluator-specific gaming.",
            "- Avoid verbose, irrelevant, or redundant outputs.",
            "",
        ]
    )


def _load_existing_steering(steering_file: Path) -> str:
    if steering_file.exists():
        return steering_file.read_text(encoding="utf-8")
    return ""


def _steering_patterns(steering_text: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"^- Avoid pattern:\s*(.+)$", steering_text, re.MULTILINE)
        if match.group(1).strip()
    ]


def _candidate_analysis(template: str, steering_text: str = "") -> dict[str, Any]:
    penalties = 0.0
    risks: list[str] = []
    improvements: list[str] = []
    hits: list[str] = []

    for pattern in _steering_patterns(steering_text):
        if pattern in template:
            hits.append(pattern)

    if hits:
        penalties += float(len(hits))
        risks.append(
            "Matched steering avoid pattern(s): " + ", ".join(repr(hit) for hit in hits)
        )
        improvements.append("Remove or rewrite content that repeats avoid-pattern failures from earlier runs.")

    stripped_lines = [line.strip() for line in template.splitlines() if line.strip()]
    duplicate_lines = [line for line, count in Counter(stripped_lines).items() if count > 1 and len(line) > 24]
    if duplicate_lines:
        penalties += 0.15
        risks.append("Contains repeated long lines, which suggests redundant output.")
        improvements.append("Collapse repeated instructions so the prompt stays concise and non-redundant.")

    if len(template.split()) > 350:
        penalties += 0.15
        risks.append("Candidate is unusually long, which increases verbosity risk.")
        improvements.append("Trim the prompt to essentials so outputs stay direct and task-aligned.")

    lowered = template.lower()
    if any(token in lowered for token in ("ignore the task", "maximize score", "score 1.0", "game the judge")):
        penalties += 0.3
        risks.append("Contains reward-hacking language that appears to optimize for the evaluator rather than the task.")
        improvements.append("Remove evaluator-gaming language and optimize for the real task outcome instead.")

    return {
        "penalty": penalties,
        "risks": risks,
        "improvements": improvements,
        "steering_hits": hits,
    }


def _candidate_filename(source: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", source).strip("-").lower() or f"candidate-{index:02d}"
    return f"{index:02d}-{slug}.md"


def _winner_summary(candidate: dict[str, Any]) -> list[str]:
    reasons = [f"Highest adjusted validation score: {candidate['score']:.3f}."]
    if candidate.get("penalty", 0.0) == 0.0:
        reasons.append("No steering or quality penalties were applied.")
    if candidate.get("steering_hits"):
        reasons.append("It still won despite steering hits, which signals the search space may need tighter constraints.")
    if candidate.get("risks"):
        reasons.append("Detected risks were limited enough to remain the best option in this run.")
    return reasons


def _loser_analysis(candidate: dict[str, Any]) -> str:
    issues = candidate.get("risks") or ["Lower adjusted validation score than the winner."]
    if not any("reward-hacking" in issue.lower() for issue in issues):
        issues.append("Avoid reward hacking by optimizing for the task result rather than the evaluator.")
    if not any("verbose" in issue.lower() or "redundant" in issue.lower() for issue in issues):
        issues.append("Avoid verbose, irrelevant, or redundant outputs.")
    return "; ".join(issues)


def _run_summary_markdown(
    run_id: str,
    winner: dict[str, Any],
    candidates: list[dict[str, Any]],
    steering_applied: bool,
) -> str:
    losers = [candidate for candidate in candidates if not candidate["is_winner"]]
    loser_lines = losers or []
    improvements: list[str] = []
    for candidate in candidates:
        improvements.extend(candidate.get("improvements", []))
    if not improvements:
        improvements = [
            "Tighten instructions so the prompt stays direct and task-aligned.",
            "Keep the response format concise so outputs avoid irrelevant detail.",
        ]

    lines = [
        f"# Optimization Run {run_id}",
        "",
        "## Winner",
        f"- Source: {winner['source']}",
        f"- Adjusted score: {winner['score']:.3f}",
        f"- Raw score: {winner['raw_score']:.3f}",
        "- Why it won:",
    ]
    lines.extend(f"  - {reason}" for reason in _winner_summary(winner))
    lines.extend(
        [
            "",
            "## Best Results",
            f"- Winner: {winner['source']} with adjusted score {winner['score']:.3f}.",
            f"- Steering applied during selection: {'yes' if steering_applied else 'no'}.",
            "- Selection prioritized real task performance over reward-hacking or verbosity risks.",
            "",
            "## Failure Analysis",
        ]
    )
    if loser_lines:
        lines.extend(
            f"- {candidate['source']}: {_loser_analysis(candidate)}"
            for candidate in loser_lines
        )
    else:
        lines.append("- No losing candidates were available for comparison in this run.")
    lines.extend(
        [
            "- Avoid reward hacking by optimizing for task success, not evaluator leakage or rubric mimicry.",
            "- Avoid verbose, irrelevant, or redundant outputs.",
            "",
            "## Improvements",
        ]
    )
    lines.extend(f"- {item}" for item in dict.fromkeys(improvements))
    return "\n".join(lines) + "\n"


def _steering_run_entry(run_id: str, winner: dict[str, Any], candidates: list[dict[str, Any]]) -> str:
    loser_notes = [
        f"- {candidate['source']}: {_loser_analysis(candidate)}"
        for candidate in candidates
        if not candidate["is_winner"]
    ]
    if not loser_notes:
        loser_notes = ["- No losing candidates were available for comparison."]

    improvement_notes = []
    for candidate in candidates:
        improvement_notes.extend(candidate.get("improvements", []))
    if not improvement_notes:
        improvement_notes = [
            "Keep candidate prompts concise and directly tied to the task.",
        ]

    lines = [
        f"## Run {run_id}",
        f"- Winner: {winner['source']} ({winner['score']:.3f})",
        f"- Why it won: {' '.join(_winner_summary(winner))}",
        "- Failure patterns to avoid:",
    ]
    lines.extend(f"  {note}" for note in loser_notes)
    lines.append("- Improvements to pursue:")
    lines.extend(f"  - {item}" for item in dict.fromkeys(improvement_notes))
    return "\n".join(lines) + "\n"


def _persist_run_artifacts(
    prompt_file: str,
    report: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> tuple[str, str]:
    _, tmp_dir, steering_file = derive_artifact_paths(prompt_file)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    existing_steering = _load_existing_steering(steering_file)
    if not existing_steering:
        steering_file.write_text(_default_steering_body(), encoding="utf-8")
        existing_steering = _default_steering_body()

    run_id = report["run_id"]
    run_dir = tmp_dir / run_id
    candidates_dir = run_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    winner = next(candidate for candidate in candidates if candidate["is_winner"])
    summary_text = _run_summary_markdown(
        run_id=run_id,
        winner=winner,
        candidates=candidates,
        steering_applied=report["steering_applied"],
    )
    (run_dir / "summary.md").write_text(summary_text, encoding="utf-8")
    (run_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    for index, candidate in enumerate(candidates, start=1):
        lines = [
            f"# Candidate {index}",
            "",
            f"- Source: {candidate['source']}",
            f"- Adjusted score: {candidate['score']:.3f}",
            f"- Raw score: {candidate['raw_score']:.3f}",
            f"- Baseline: {'yes' if candidate['is_baseline'] else 'no'}",
            f"- Winner: {'yes' if candidate['is_winner'] else 'no'}",
            "",
            "## Risks",
        ]
        risks = candidate.get("risks") or ["No structural warning signals detected."]
        lines.extend(f"- {risk}" for risk in risks)
        lines.extend([
            "",
            "## Content",
            "```md",
            candidate["template"],
            "```",
            "",
        ])
        (candidates_dir / _candidate_filename(candidate["source"], index)).write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

    steering_entry = _steering_run_entry(run_id, winner, candidates)
    updated_steering = existing_steering.rstrip() + "\n\n" + steering_entry
    steering_file.write_text(updated_steering, encoding="utf-8")

    return str(run_dir), str(steering_file)


async def assess_candidates(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    steering_text: str = "",
) -> list[dict[str, Any]]:
    """Return ordered candidate assessments with adjusted scores and risk metadata."""
    assessed: list[dict[str, Any]] = []
    for variant in variants:
        total = 0.0
        for task in dataset:
            output = await run_candidate(variant, task)
            total += await evaluate_output(
                task,
                output,
                judge_mode=judge_mode,
                judge_prompt_file=judge_prompt_file,
                llm_client=llm_client,
                custom_scorer=custom_scorer,
            )
        raw_score = total / len(dataset) if dataset else 0.0
        analysis = _candidate_analysis(variant, steering_text=steering_text)
        assessed.append(
            {
                "template": variant,
                "raw_score": raw_score,
                "score": max(0.0, raw_score - analysis["penalty"]),
                "penalty": analysis["penalty"],
                "risks": analysis["risks"],
                "improvements": analysis["improvements"],
                "steering_hits": analysis["steering_hits"],
            }
        )
    return assessed


# ---------------------------------------------------------------------------
# Evaluator
# ---------------------------------------------------------------------------

async def run_candidate(prompt_text: str, task: dict[str, Any]) -> str:
    """
    Execute the prompt against a task and return the model output as a string.

    Current implementation is an intentional stub for testing — it returns the
    prompt text directly, acting as an echo model so ``topk_select`` and APO can
    run without a live LLM and produce deterministic, variant-dependent scores.
    Replace with a real async LLM call in production, e.g.:
        rendered = prompt_text.format(**task)
        response = await llm_client.complete(rendered)
        return response
    """
    try:
        return prompt_text.format(**_prompt_fields(task))
    except KeyError:
        return prompt_text


async def evaluate_output(
    task: dict[str, Any],
    output_text: str,
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
) -> float:
    """
    Score *output_text* against *task* and return a float in [0.0, 1.0].

    judge_mode options:
      - "deterministic": exact string match against task["expected"]
    - "custom": task-specific scoring based on task["scoring"] or a scorer hook
    - "llm_judge": use an LLM judge prompt and judge client to score
    """
    expected = task.get("expected")

    if judge_mode == "deterministic":
        if expected is None:
            raise ValueError("deterministic judge_mode requires an 'expected' field in each task")
        return 1.0 if output_text.strip() == str(expected).strip() else 0.0

    if judge_mode == "custom":
        if custom_scorer is not None:
            score = custom_scorer(task, output_text)
            if hasattr(score, "__await__"):
                score = await score
            return float(score)

        scoring = task.get("scoring", "custom_python")
        if scoring in {"custom_python", "exact_match"}:
            if expected is None:
                raise ValueError("custom exact scoring requires an 'expected' field")
            return 1.0 if output_text.strip() == str(expected).strip() else 0.0
        if scoring == "normalized_match":
            if expected is None:
                raise ValueError("normalized_match scoring requires an 'expected' field")
            return 1.0 if _normalize_text(output_text) == _normalize_text(expected) else 0.0
        if scoring == "json_schema":
            expected_json = task.get("expected_json")
            if expected_json is None:
                raise ValueError("json_schema scoring requires an 'expected_json' field")
            try:
                parsed_output = json.loads(output_text)
            except json.JSONDecodeError as exc:
                raise ValueError("json_schema scoring requires JSON output") from exc
            return 1.0 if parsed_output == expected_json else 0.0
        raise ValueError(f"Unsupported custom scoring: {scoring!r}")

    if judge_mode == "llm_judge":
        if llm_client is None:
            from openai import AsyncOpenAI

            llm_client = AsyncOpenAI()

        prompt_path = Path(judge_prompt_file or _default_judge_prompt_file())
        prompt_template = prompt_path.read_text(encoding="utf-8")
        rendered_prompt = prompt_template.format(
            input=task.get("input", ""),
            expected=task.get("expected", task.get("reference", "")),
            output=output_text,
        )

        if not hasattr(llm_client, "judge_score"):
            raise ValueError("llm_judge requires a client with a judge_score method")

        score = llm_client.judge_score(rendered_prompt)
        if hasattr(score, "__await__"):
            score = await score
        score = float(score)
        if not 0.0 <= score <= 1.0:
            raise ValueError("llm_judge score must be between 0.0 and 1.0")
        return score

    raise ValueError(f"Unsupported judge_mode: {judge_mode!r}. Choose from: deterministic, custom, llm_judge")


# ---------------------------------------------------------------------------
# Variant generation + top-k leader election (single-candidate fallback)
# ---------------------------------------------------------------------------

def generate_variants(prompt_text: str, n: int) -> list[str]:
    """
    Generate *n* variant paraphrases of *prompt_text*.

    Current implementation is an intentional stub for testing — it appends a
    unique numeric marker to each copy so the elected leader is identifiable in
    tests and the caller can verify this path was taken.

    TODO (production): replace with an async LLM paraphrase call, e.g.:
        return [await llm_client.paraphrase(prompt_text) for _ in range(n)]
    """
    return [f"{prompt_text}\n<!-- variant {i + 1} -->" for i in range(n)]


async def score_variants(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    steering_text: str = "",
) -> list[tuple[str, float]]:
    """Return mean scores for variants in original order."""
    assessed = await assess_candidates(
        variants,
        dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        custom_scorer=custom_scorer,
        steering_text=steering_text,
    )
    return [(item["template"], item["score"]) for item in assessed]


async def topk_select(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    k: int = 1,
    judge_prompt_file: str | None = None,
    llm_client: Any | None = None,
    custom_scorer: Any | None = None,
    steering_text: str = "",
) -> list[str]:
    """
    Score every variant against *dataset* and return the top-*k* by mean score.

    Each variant is executed via ``run_candidate`` and scored via
    ``evaluate_output``.  Variants are ranked by their mean score over all tasks;
    ties are broken by original order (stable sort).  If *k* exceeds the number
    of variants, all variants are returned.
    """
    if not variants:
        return []

    assessed = await assess_candidates(
        variants,
        dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        llm_client=llm_client,
        custom_scorer=custom_scorer,
        steering_text=steering_text,
    )

    assessed.sort(key=lambda item: item["score"], reverse=True)
    return [item["template"] for item in assessed[:k]]




def _make_rollout(judge_mode: str):
    """Return an @agl.rollout-decorated function bound to the given judge_mode."""
    import agentlightning as agl

    @agl.rollout
    async def prompt_optimizer_rollout(
        task: dict[str, Any],
        prompt_template: agl.PromptTemplate,
    ) -> float:
        output_text = await run_candidate(prompt_template.template, task)
        return await evaluate_output(task, output_text, judge_mode=judge_mode)

    return prompt_optimizer_rollout


# ---------------------------------------------------------------------------
# Core run_optimize function (importable + used by CLI)
# ---------------------------------------------------------------------------

async def run_optimize(
    prompt_file: str,
    train_file: str | None = None,
    val_file: str | None = None,
    iterations: int = 3,
    algorithm: str = "apo",
    output_file: str | None = None,
    report_file: str | None = None,
    beam_width: int = 4,
    branch_factor: int = 4,
    n_runners: int = 4,
    judge_mode: Literal["deterministic", "custom", "llm_judge"] = "deterministic",
    judge_prompt_file: str | None = None,
    debug_only: bool = False,
    n_variants: int = 4,
) -> str:
    """
    Optimize a markdown prompt file with Agent Lightning APO.

    Returns a JSON string describing the outcome.
    Writes two files on success (unless debug_only=True):
      - optimized markdown prompt (the original prompt_file is replaced in-place)
      - JSON report with persisted candidate information

    When an algorithm produces exactly one candidate, ``n_variants`` paraphrases
    of that candidate are generated and the best one is elected via top-k
    scoring against the validation dataset, with the original prompt included as
    a baseline candidate.
    """
    ensure_evals_scaffold(prompt_file, train_file=train_file, val_file=val_file, report_file=report_file)
    try:
        train_file, val_file = resolve_dataset_paths(prompt_file, train_file, val_file)
    except ValueError:
        eval_dir, _, _ = derive_artifact_paths(prompt_file)
        dataset_request = build_missing_dataset_request(prompt_file)
        return json.dumps(
            {
                "ok": False,
                "needs_user_input": True,
                "message": "Generate prompt-adjacent datasets by collecting the minimum required information from the user.",
                "prompt_file": prompt_file,
                "evals_dir": str(eval_dir),
                "dataset_request_file": str(eval_dir / "dataset-request.json"),
                "required_info": dataset_request["required_info"],
                "missing_files": dataset_request["missing_files"],
            },
            indent=2,
        )
    ensure_evals_scaffold(prompt_file, train_file=train_file, val_file=val_file, report_file=report_file)

    import agentlightning as agl

    openai_client, model_settings = create_openai_client(prompt_file)

    algorithm_registry = {
        "apo": agl.APO,
        "verl": agl.VERL,
    }
    if algorithm not in algorithm_registry:
        return json.dumps(
            {
                "ok": False,
                "message": f"Unsupported algorithm: {algorithm!r}",
            },
            indent=2,
        )

    prompt_text = Path(prompt_file).read_text(encoding="utf-8")
    train_dataset = load_jsonl(train_file)
    val_dataset = load_jsonl(val_file)

    if not train_dataset:
        raise ValueError("train_file must contain at least one task row")
    if not val_dataset:
        raise ValueError("val_file must contain at least one task row")

    sample_task = train_dataset[0]
    validate_template_against_task(prompt_text, sample_task)

    algo = algorithm_registry[algorithm](
        openai_client,
        beam_rounds=iterations,
        beam_width=beam_width,
        branch_factor=branch_factor,
        gradient_batch_size=min(4, len(train_dataset)),
        val_batch_size=min(16, len(val_dataset)),
        gradient_model=model_settings["gradient_model"],
        apply_edit_model=model_settings["apply_edit_model"],
    )

    trainer = agl.Trainer(
        algorithm=algo,
        n_runners=n_runners,
        tracer=agl.OtelTracer(),
        # "main_prompt" is the resource key injected as `prompt_template` in the rollout.
        initial_resources={
            "main_prompt": agl.PromptTemplate(template=prompt_text, engine="f-string")
        },
        adapter=agl.TraceToMessages(),
    )

    rollout_fn = _make_rollout(judge_mode)

    if debug_only:
        await asyncio.to_thread(
            trainer.dev,
            agent=rollout_fn,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
        )
        return json.dumps({"ok": True, "mode": "debug", "message": "Dry run complete"}, indent=2)

    await asyncio.to_thread(
        trainer.fit,
        agent=rollout_fn,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
    )

    candidates = algo.get_candidates()
    if not candidates:
        raise RuntimeError("Optimization produced no valid prompt candidates.")

    if len(candidates) == 1:
        selection_pool = generate_variants(candidates[0].template, n_variants) + [prompt_text]
        selection_sources = [f"variant_{index + 1}" for index in range(len(selection_pool) - 1)] + ["baseline"]
    else:
        selection_pool = [candidate.template for candidate in candidates] + [prompt_text]
        selection_sources = [
            f"{algorithm}_candidate_{index + 1}" for index in range(len(selection_pool) - 1)
        ] + ["baseline"]

    _, tmp_dir, steering_file = derive_artifact_paths(prompt_file)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    steering_text = _load_existing_steering(steering_file)
    steering_applied = bool(steering_text.strip())

    topk_kwargs: dict[str, Any] = {
        "judge_mode": judge_mode,
        "k": 1,
    }
    if judge_prompt_file is not None:
        topk_kwargs["judge_prompt_file"] = judge_prompt_file
    if steering_applied:
        topk_kwargs["steering_text"] = steering_text

    top = await topk_select(
        selection_pool,
        val_dataset,
        **topk_kwargs,
    )
    if not top:
        raise RuntimeError("Optimization produced no selectable prompt candidates.")
    best_prompt = top[0]

    candidate_assessments = await assess_candidates(
        selection_pool,
        val_dataset,
        judge_mode=judge_mode,
        judge_prompt_file=judge_prompt_file,
        steering_text=steering_text,
    )
    persisted_candidates = [
        {
            "template": candidate["template"],
            "score": candidate["score"],
            "raw_score": candidate["raw_score"],
            "penalty": candidate["penalty"],
            "source": source,
            "is_baseline": source == "baseline",
            "is_winner": candidate["template"] == best_prompt,
            "risks": candidate["risks"],
            "improvements": candidate["improvements"],
            "steering_hits": candidate["steering_hits"],
        }
        for candidate, source in zip(candidate_assessments, selection_sources, strict=True)
    ]

    # The winning (leader) prompt replaces the original prompt file in-place.
    prompt_path = Path(prompt_file)
    prompt_path.write_text(best_prompt, encoding="utf-8")

    # If a separate output_file path was requested, also write there as a backup copy.
    if output_file and Path(output_file) != prompt_path:
        Path(output_file).write_text(best_prompt, encoding="utf-8")

    eval_dir, _, _ = derive_artifact_paths(prompt_file)
    report_path = Path(report_file) if report_file else eval_dir / "report.json"
    run_id = "run-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]

    report = {
        "ok": True,
        "run_id": run_id,
        "algorithm": algorithm,
        "prompt_file": prompt_file,
        "train_file": train_file,
        "val_file": val_file,
        "output_file": output_file if output_file else str(prompt_path),
        "report_file": str(report_path),
        "model_provider": model_settings["provider"],
        "model_endpoint": model_settings["base_url"],
        "gradient_model": model_settings["gradient_model"],
        "apply_edit_model": model_settings["apply_edit_model"],
        "iterations": iterations,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "beam_width": beam_width,
        "branch_factor": branch_factor,
        "n_runners": n_runners,
        "judge_mode": judge_mode,
        "steering_applied": steering_applied,
        "candidates": persisted_candidates,
    }
    run_dir, steering_path = _persist_run_artifacts(prompt_file, report, persisted_candidates)
    report["run_dir"] = run_dir
    report["steering_file"] = steering_path
    ensure_evals_scaffold(prompt_file, train_file=train_file, val_file=val_file, report_file=str(report_path))
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    Path(run_dir, "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    return json.dumps(report, indent=2)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_optimize.py",
        description="Optimize a markdown prompt file using Agent Lightning APO.",
    )
    parser.add_argument("--prompt-file", required=True, help="Path to the markdown prompt file")
    parser.add_argument("--train-file", default=None, help="Path to the JSONL training dataset")
    parser.add_argument("--val-file", default=None, help="Path to the JSONL validation dataset")
    parser.add_argument("--iterations", type=int, default=3, help="APO beam rounds (default: 3)")
    parser.add_argument("--algorithm", default="apo", choices=["apo", "verl"],
                        help="Optimization algorithm (default: apo)")
    parser.add_argument("--output-file", default=None,
                        help="Optional backup path; the winner is always written back to --prompt-file")
    parser.add_argument("--report-file", default=None, help="Output JSON report path")
    parser.add_argument("--beam-width", type=int, default=4)
    parser.add_argument("--branch-factor", type=int, default=4)
    parser.add_argument("--n-runners", type=int, default=4)
    parser.add_argument("--judge-mode", default="deterministic",
                        choices=["deterministic", "custom", "llm_judge"])
    parser.add_argument("--judge-prompt-file", default=None,
                        help="Path to judge prompt file (only for llm_judge mode)")
    parser.add_argument("--debug-only", action="store_true",
                        help="Run a smoke-test pass only; do not write output files")
    parser.add_argument("--n-variants", type=int, default=4,
                        help=(
                            "Number of variants to generate when APO returns only "
                            "one candidate (default: 4)"
                        ))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = asyncio.run(run_optimize(
        prompt_file=args.prompt_file,
        train_file=args.train_file,
        val_file=args.val_file,
        iterations=args.iterations,
        algorithm=args.algorithm,
        output_file=args.output_file,
        report_file=args.report_file,
        beam_width=args.beam_width,
        branch_factor=args.branch_factor,
        n_runners=args.n_runners,
        judge_mode=args.judge_mode,
        judge_prompt_file=args.judge_prompt_file,
        debug_only=args.debug_only,
        n_variants=args.n_variants,
    ))
    print(result)
    parsed = json.loads(result)
    return 0 if parsed.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
