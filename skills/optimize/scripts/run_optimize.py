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
import json
import re
import sys
from pathlib import Path
from typing import Any, Literal


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
    return prompt_text


async def evaluate_output(
    task: dict[str, Any],
    output_text: str,
    judge_mode: str = "deterministic",
) -> float:
    """
    Score *output_text* against *task* and return a float in [0.0, 1.0].

    judge_mode options:
      - "deterministic": exact string match against task["expected"]
      - "custom": implement your own scoring logic (raises NotImplementedError)
      - "llm_judge": use an LLM to score (raises NotImplementedError)
    """
    expected = task.get("expected")

    if judge_mode == "deterministic":
        if expected is None:
            raise ValueError("deterministic judge_mode requires an 'expected' field in each task")
        return 1.0 if output_text.strip() == str(expected).strip() else 0.0

    if judge_mode == "custom":
        # Replace with task-specific scoring logic returning float in [0.0, 1.0].
        raise NotImplementedError("Implement custom evaluator for judge_mode='custom'")

    if judge_mode == "llm_judge":
        # Load judge_prompt_file if provided, or fall back to assets/judge-default.md.
        # Replace with an async LLM judge call using the loaded prompt.
        raise NotImplementedError("Implement LLM judge for judge_mode='llm_judge'")

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


async def topk_select(
    variants: list[str],
    dataset: list[dict[str, Any]],
    judge_mode: str = "deterministic",
    k: int = 1,
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

    scored: list[tuple[str, float]] = []
    for variant in variants:
        total = 0.0
        for task in dataset:
            output = await run_candidate(variant, task)
            total += await evaluate_output(task, output, judge_mode=judge_mode)
        mean = total / len(dataset) if dataset else 0.0
        scored.append((variant, mean))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [v for v, _ in scored[:k]]




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
    train_file: str,
    val_file: str,
    iterations: int = 3,
    algorithm: Literal["apo", "verl"] = "apo",
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
      - JSON report

    When APO produces exactly one candidate, ``n_variants`` paraphrases of that
    candidate are generated and the best one is elected leader via top-k scoring
    against the training dataset.
    """
    # Guard: VERL is not the default for markdown prompt optimization
    if algorithm != "apo":
        return json.dumps(
            {
                "ok": False,
                "message": (
                    "Use APO for optimizing a single markdown prompt file. "
                    "VERL should be reserved for advanced RL/model-path optimization."
                ),
            },
            indent=2,
        )

    import agentlightning as agl
    from openai import AsyncOpenAI

    prompt_text = Path(prompt_file).read_text(encoding="utf-8")
    train_dataset = load_jsonl(train_file)
    val_dataset = load_jsonl(val_file)

    if not train_dataset:
        raise ValueError("train_file must contain at least one task row")
    if not val_dataset:
        raise ValueError("val_file must contain at least one task row")

    sample_task = train_dataset[0]
    validate_template_against_task(prompt_text, sample_task)

    algo = agl.APO(
        AsyncOpenAI(),
        beam_rounds=iterations,
        beam_width=beam_width,
        branch_factor=branch_factor,
        gradient_batch_size=min(4, len(train_dataset)),
        val_batch_size=min(16, len(val_dataset)),
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
        trainer.dev(
            agent=rollout_fn,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
        )
        return json.dumps({"ok": True, "mode": "debug", "message": "Dry run complete"}, indent=2)

    trainer.fit(
        agent=rollout_fn,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
    )

    candidates = algo.get_candidates()
    if not candidates:
        raise RuntimeError("Optimization produced no valid prompt candidates.")

    if len(candidates) == 1:
        # Single-candidate fallback: generate n_variants paraphrases of the sole
        # APO candidate, score each against the training dataset, and elect the
        # highest-scoring variant as the leader via top-k selection.
        variants = generate_variants(candidates[0].template, n_variants)
        top = await topk_select(variants, train_dataset, judge_mode=judge_mode, k=1)
        best_prompt = top[0]
    else:
        # Multiple candidates: use the best prompt selected by APO directly.
        best_result = algo.get_best_prompt()
        if best_result is None:
            raise RuntimeError("Optimization produced no valid prompt candidates.")
        best_prompt = best_result.template

    # The winning (leader) prompt replaces the original prompt file in-place.
    prompt_path = Path(prompt_file)
    prompt_path.write_text(best_prompt, encoding="utf-8")

    # If a separate output_file path was requested, also write there as a backup copy.
    if output_file and Path(output_file) != prompt_path:
        Path(output_file).write_text(best_prompt, encoding="utf-8")

    report_path = Path(report_file or f"{prompt_path.stem}.report.json")

    report = {
        "ok": True,
        "algorithm": "apo",
        "prompt_file": prompt_file,
        "output_file": output_file if output_file else str(prompt_path),
        "iterations": iterations,
        "train_size": len(train_dataset),
        "val_size": len(val_dataset),
        "beam_width": beam_width,
        "branch_factor": branch_factor,
        "n_runners": n_runners,
        "judge_mode": judge_mode,
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

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
    parser.add_argument("--train-file", required=True, help="Path to the JSONL training dataset")
    parser.add_argument("--val-file", required=True, help="Path to the JSONL validation dataset")
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
