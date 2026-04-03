#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_PATH = SKILL_DIR / "SKILL.md"
EVAL_PATH = SKILL_DIR / "evals" / "evals.json"
SOURCE_ANALYSIS_PATH = SKILL_DIR / "references" / "source-analysis.md"
TOKEN_PATTERNS_PATH = SKILL_DIR / "references" / "token-efficient-patterns.md"
PROGRAM_OUTPUT_PATH = SKILL_DIR / "assets" / "skill_program_optimized.json"
# Disable demos so optimization stays instruction-only and the exported markdown artifact remains readable.
MAX_DEMO_COUNT = 0
MIN_BODY_LENGTH = 400
TRAIN_SET_SIZE = 3
REQUIRED_SECTIONS = (
    "# Engineer Prompt",
    "## When to use this skill",
    "## Core workflow",
    "## Output contract",
    "## Diagnose first",
    "## Default selection heuristic",
    "## Token-budget guidance",
    "## Final rule",
)
GENERAL_GUARDRAILS = (
    "Prompt engineering is not just naming a technique.",
    "The user wants to improve a prompt.",
    "references/token-efficient-patterns.md",
    "prompt changes are secondary",
)
BANNED_PROMPT_TERMS = ("dspy", "miprov2", "instruction-only optimization")


@dataclass(slots=True)
class SkillContract:
    frontmatter: dict[str, Any]
    skill_name: str
    skill_description: str
    operating_constraints: str
    inputs_available: str
    desired_outputs: str
    draft_notes: str
    seed_instruction_body: str


def _load_dspy() -> Any:
    try:
        import dspy  # type: ignore
    except ImportError as exc:  # pragma: no cover - covered by CLI error path
        raise RuntimeError("DSPy is required for --optimize. Install it first, for example with: pip install dspy") from exc
    return dspy


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise ValueError("Expected SKILL.md to start with YAML front matter")
    _, raw_frontmatter, body = text.split("---\n", 2)
    frontmatter = yaml.safe_load(raw_frontmatter) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("SKILL.md front matter must be a YAML mapping")
    return frontmatter, body.strip()


def build_default_contract(skill_dir: Path = SKILL_DIR) -> SkillContract:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(skill_text)
    eval_payload = json.loads((skill_dir / "evals" / "evals.json").read_text(encoding="utf-8"))
    eval_prompts = [case["prompt"] for case in eval_payload.get("evals", [])[:5]]
    source_analysis = (skill_dir / "references" / "source-analysis.md").read_text(encoding="utf-8")
    token_patterns = (skill_dir / "references" / "token-efficient-patterns.md").read_text(encoding="utf-8")
    operating_constraints = "\n".join(
        [
            "Keep the skill focused on general prompt engineering rather than DSPy-specific guidance.",
            "Preserve the markdown-first contract and existing section structure.",
            "Tell the user when prompt changes are secondary to retrieval, tooling, or requirements.",
            "Keep token-budget guidance and retrieval caveats explicit.",
        ]
    )
    inputs_available = "\n".join(
        [
            f"Current SKILL body length: {len(body)} characters.",
            f"Source analysis reference excerpt: {source_analysis[:500].strip()}",
            f"Token patterns reference excerpt: {token_patterns[:500].strip()}",
            "Representative eval prompts:",
            *[f"- {prompt}" for prompt in eval_prompts],
        ]
    )
    desired_outputs = "\n".join(
        [
            "Return markdown that can become a checked-in SKILL.md artifact.",
            "Keep or strengthen the sections for when to use, core workflow, output contract, heuristic selection, token budget guidance, and final rule.",
            "Keep the guidance general to prompt engineering rather than tool-specific.",
            "Mention references/token-efficient-patterns.md when token pressure matters.",
        ]
    )
    draft_notes = "\n\n".join(
        [
            body,
            "Preserve the original purpose: diagnose prompt failures, choose the smallest technique that fits, and give concrete markdown rewrites when useful.",
            "Keep examples spanning structured output, grounding, prompt chaining, reasoning techniques, and token-budget guidance.",
            "Do not turn the skill itself into DSPy guidance; use DSPy only inside the helper that exports the artifact.",
        ]
    )
    return SkillContract(
        frontmatter=frontmatter,
        skill_name=str(frontmatter.get("name") or "engineer-prompt"),
        skill_description=str(frontmatter.get("description") or "").strip(),
        operating_constraints=operating_constraints,
        inputs_available=inputs_available,
        desired_outputs=desired_outputs,
        draft_notes=draft_notes,
        seed_instruction_body=body,
    )


def render_skill_markdown(instruction_body: str, *, frontmatter: dict[str, Any]) -> str:
    rendered_frontmatter = yaml.safe_dump(frontmatter, sort_keys=False).strip()
    return f"---\n{rendered_frontmatter}\n---\n\n{instruction_body.strip()}\n"


def validate_skill_markdown(markdown: str) -> dict[str, Any]:
    frontmatter, body = _split_frontmatter(markdown)
    text_lower = markdown.lower()
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in body]
    missing_guardrails = [rule for rule in GENERAL_GUARDRAILS if rule not in markdown]
    banned_terms_present = [term for term in BANNED_PROMPT_TERMS if term in text_lower]
    summary = {
        "valid": not missing_sections and not missing_guardrails and not banned_terms_present,
        "name": frontmatter.get("name"),
        "has_frontmatter": True,
        "missing_sections": missing_sections,
        "missing_guardrails": missing_guardrails,
        "banned_terms_present": banned_terms_present,
        "body_length": len(body),
    }
    return summary


def skill_metric(example: Any, pred: Any, _trace: Any = None) -> float:
    frontmatter = getattr(example, "frontmatter", None) or example.get("frontmatter", {})
    markdown = render_skill_markdown(getattr(pred, "instruction_body"), frontmatter=frontmatter)
    summary = validate_skill_markdown(markdown)
    checks = [
        summary["has_frontmatter"],
        not summary["missing_sections"],
        not summary["missing_guardrails"],
        not summary["banned_terms_present"],
        summary["body_length"] >= MIN_BODY_LENGTH,
    ]
    return sum(1.0 for check in checks if check) / len(checks)


def _contract_variants(contract: SkillContract) -> list[str]:
    return [
        contract.draft_notes,
        contract.draft_notes + "\n\nEmphasize token-efficiency guidance without dropping the broader technique taxonomy.",
        contract.draft_notes + "\n\nEmphasize that retrieval freshness, missing tools, and unclear requirements are blockers outside prompt design.",
        contract.draft_notes + "\n\nEmphasize that the output contract should stay concise and consistently structured for downstream agent use.",
    ]


def build_example_sets(contract: SkillContract, dspy: Any) -> tuple[list[Any], list[Any]]:
    examples = []
    for draft_notes in _contract_variants(contract):
        examples.append(
            dspy.Example(
                frontmatter=contract.frontmatter,
                skill_name=contract.skill_name,
                skill_description=contract.skill_description,
                operating_constraints=contract.operating_constraints,
                inputs_available=contract.inputs_available,
                desired_outputs=contract.desired_outputs,
                draft_notes=draft_notes,
            ).with_inputs(
                "skill_name",
                "skill_description",
                "operating_constraints",
                "inputs_available",
                "desired_outputs",
                "draft_notes",
            )
        )
    return examples[:TRAIN_SET_SIZE], examples[TRAIN_SET_SIZE:]


def _configure_dspy_lm(dspy: Any, *, model: str | None, api_key: str | None, api_base: str | None, temperature: float) -> Any:
    resolved_model = model or os.getenv("DSPY_MODEL") or os.getenv("OPENAI_MODEL")
    if not resolved_model:
        raise RuntimeError(
            "Model not configured. Set --model or DSPY_MODEL/OPENAI_MODEL "
            "(for example: openai/gpt-4o-mini) before running --optimize."
        )
    kwargs: dict[str, Any] = {"temperature": temperature}
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    resolved_api_base = api_base or os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL")
    if resolved_api_key:
        kwargs["api_key"] = resolved_api_key
    if resolved_api_base:
        kwargs["api_base"] = resolved_api_base
    lm = dspy.LM(model=resolved_model, **kwargs)
    dspy.configure(lm=lm)
    return lm


def compile_instruction_body(
    contract: SkillContract,
    *,
    program_file: Path | None = None,
    model: str | None = None,
    api_key: str | None = None,
    api_base: str | None = None,
    temperature: float = 0.2,
) -> tuple[str, Any]:
    dspy = _load_dspy()
    _configure_dspy_lm(dspy, model=model, api_key=api_key, api_base=api_base, temperature=temperature)

    class SkillWriter(dspy.Signature):
        """Write a general prompt-engineering skill body for a checked-in markdown artifact."""

        skill_name = dspy.InputField(desc="Skill name for the markdown artifact.")
        skill_description = dspy.InputField(desc="Short description used in front matter.")
        operating_constraints = dspy.InputField(desc="Non-negotiable guardrails and scope boundaries.")
        inputs_available = dspy.InputField(desc="Repository references, evals, and source notes available to the writer.")
        desired_outputs = dspy.InputField(desc="Required sections and artifact expectations for the markdown output.")
        draft_notes = dspy.InputField(desc="Existing skill content and rewrite notes to refine.")
        instruction_body = dspy.OutputField(desc="Markdown body for SKILL.md excluding YAML front matter.")

    class SkillWriterProgram(dspy.Module):
        def __init__(self) -> None:
            super().__init__()
            self.writer = dspy.Predict(SkillWriter)

        def forward(
            self,
            skill_name: str,
            skill_description: str,
            operating_constraints: str,
            inputs_available: str,
            desired_outputs: str,
            draft_notes: str,
        ) -> Any:
            return self.writer(
                skill_name=skill_name,
                skill_description=skill_description,
                operating_constraints=operating_constraints,
                inputs_available=inputs_available,
                desired_outputs=desired_outputs,
                draft_notes=draft_notes,
            )

    trainset, valset = build_example_sets(contract, dspy)
    program = SkillWriterProgram()
    optimizer = dspy.MIPROv2(
        metric=skill_metric,
        auto="light",
        max_bootstrapped_demos=MAX_DEMO_COUNT,
        max_labeled_demos=MAX_DEMO_COUNT,
    )
    compiled = optimizer.compile(
        student=program,
        trainset=trainset,
        valset=valset,
        requires_permission_to_run=False,
    )
    prediction = compiled(
        skill_name=contract.skill_name,
        skill_description=contract.skill_description,
        operating_constraints=contract.operating_constraints,
        inputs_available=contract.inputs_available,
        desired_outputs=contract.desired_outputs,
        draft_notes=contract.draft_notes,
    )
    if program_file is not None and hasattr(compiled, "save"):
        compiled.save(str(program_file), save_program=True)
    return str(prediction.instruction_body).strip(), compiled


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render or optimize the engineer-prompt SKILL.md artifact.")
    parser.add_argument("--skill-dir", default=str(SKILL_DIR), help="Path to the engineer-prompt skill directory.")
    parser.add_argument("--output-file", help="Optional path for the rendered markdown artifact.")
    parser.add_argument("--program-file", default=str(PROGRAM_OUTPUT_PATH), help="Path to save the compiled DSPy program when --optimize is used.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the skill's canonical SKILL.md file.")
    parser.add_argument("--optimize", action="store_true", help="Run the DSPy optimizer before rendering the markdown artifact.")
    parser.add_argument("--validate-only", action="store_true", help="Validate the rendered markdown contract and print a JSON summary.")
    parser.add_argument("--model", help="DSPy model identifier, or set DSPY_MODEL/OPENAI_MODEL.")
    parser.add_argument("--api-key", help="API key override for the DSPy LM client.")
    parser.add_argument("--api-base", help="Base URL override for the DSPy LM client.")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature passed to the DSPy LM client.")
    return parser.parse_args()


def _write_output(markdown: str, *, output_file: str | None, in_place: bool, skill_dir: Path) -> str | None:
    target_path: Path | None = None
    if in_place:
        target_path = skill_dir / "SKILL.md"
    elif output_file:
        target_path = Path(output_file)
    if target_path is None:
        return None
    target_path.write_text(markdown, encoding="utf-8")
    return str(target_path)


def main() -> int:
    args = _parse_args()
    skill_dir = Path(args.skill_dir).resolve()
    try:
        contract = build_default_contract(skill_dir)
        instruction_body = contract.seed_instruction_body
        if args.optimize:
            instruction_body, _ = compile_instruction_body(
                contract,
                program_file=Path(args.program_file) if args.program_file else None,
                model=args.model,
                api_key=args.api_key,
                api_base=args.api_base,
                temperature=args.temperature,
            )
        markdown = render_skill_markdown(instruction_body, frontmatter=contract.frontmatter)
        if args.validate_only:
            summary = validate_skill_markdown(markdown)
            print(json.dumps(summary, indent=2, sort_keys=True))
            return 0 if summary["valid"] else 1
        written = _write_output(markdown, output_file=args.output_file, in_place=args.in_place, skill_dir=skill_dir)
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        print(str(exc), file=sys.stderr)
        return 1

    if written:
        print(written)
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
