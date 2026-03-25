from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Literal

import agentlightning as agl
from openai import AsyncOpenAI
from agent_framework import Skill

SKILL_DIR = Path(__file__).resolve().parent / "skills" / "optimize"

optimize_skill = Skill(
    name="optimize",
    description="Improve a markdown prompt file using Agent Lightning APO.",
    content=(SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"),
)


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def extract_placeholders(template: str) -> set[str]:
    return set(re.findall(r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})", template))


def flatten_keys(obj: Any, prefix: str = "") -> set[str]:
    keys: set[str] = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            keys |= flatten_keys(v, path)
    return keys


def validate_template_against_task(template: str, sample_task: dict[str, Any]) -> None:
    placeholders = extract_placeholders(template)
    task_keys = flatten_keys(sample_task)
    simple_keys = set(sample_task.keys())
    valid_keys = task_keys | simple_keys
    missing = sorted(p for p in placeholders if p not in valid_keys)
    if missing:
        raise ValueError(f"Template placeholders not found in task schema: {missing}")


async def run_candidate(prompt_text: str, task: dict[str, Any]) -> str:
    # Stub: replace with your real agent execution path (e.g., an LLM call using prompt_text).
    # Keep this boundary stable so the optimizer only changes the prompt resource.
    # Example replacement: return await llm_client.complete(prompt_text.format(**task))
    rendered_input = task.get("input", task)
    return str(rendered_input)


async def evaluate_output(
    task: dict[str, Any],
    output_text: str,
    judge_mode: str = "deterministic",
) -> float:
    expected = task.get("expected")
    if judge_mode == "deterministic":
        if expected is None:
            raise ValueError("deterministic judge_mode requires an 'expected' field")
        return 1.0 if output_text.strip() == str(expected).strip() else 0.0

    if judge_mode == "custom":
        # Replace with task-specific scoring logic.
        raise NotImplementedError("Implement custom evaluator")

    if judge_mode == "llm_judge":
        # Load judge_prompt_file if provided, or fall back to the default judge prompt.
        # Replace with an LLM judge call using the loaded prompt.
        raise NotImplementedError("Implement llm_judge evaluator")

    raise ValueError(f"Unsupported judge_mode: {judge_mode}")


@agl.rollout
async def prompt_optimizer_rollout(
    task: dict[str, Any],
    prompt_template: agl.PromptTemplate,
) -> float:
    output_text = await run_candidate(prompt_template.template, task)
    return await evaluate_output(task, output_text)


@optimize_skill.script(name="run_optimize", description="Optimize a markdown prompt file with Agent Lightning")
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
) -> str:
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

    prompt_text = Path(prompt_file).read_text(encoding="utf-8")
    train_dataset = load_jsonl(train_file)
    val_dataset = load_jsonl(val_file)

    if not train_dataset or not val_dataset:
        raise ValueError("train_file and val_file must both contain at least one task")

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
        initial_resources={
            # "main_prompt" is the resource key injected as `prompt_template` in the rollout.
            "main_prompt": agl.PromptTemplate(template=prompt_text, engine="f-string")
        },
        adapter=agl.TraceToMessages(),
    )

    if debug_only:
        trainer.dev(
            agent=prompt_optimizer_rollout,
            train_dataset=train_dataset,
            val_dataset=val_dataset,
        )
        return json.dumps({"ok": True, "mode": "debug", "message": "Dry run complete"}, indent=2)

    trainer.fit(
        agent=prompt_optimizer_rollout,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
    )

    best_result = algo.get_best_prompt()
    if best_result is None:
        raise RuntimeError("Optimization produced no valid prompt candidates.")
    best_prompt = best_result.template

    output_path = Path(output_file or f"{Path(prompt_file).stem}.optimized.md")
    report_path = Path(report_file or f"{Path(prompt_file).stem}.report.json")

    output_path.write_text(best_prompt, encoding="utf-8")

    report = {
        "ok": True,
        "algorithm": "apo",
        "prompt_file": prompt_file,
        "output_file": str(output_path),
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
