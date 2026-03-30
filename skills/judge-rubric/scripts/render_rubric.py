#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL_FIELDS = ("domain", "task", "evidence_mode", "decision", "dimensions")
REQUIRED_DIMENSION_FIELDS = (
    "name",
    "why_it_matters",
    "pass_boundary",
    "partial_boundary",
    "fail_boundary",
    "allowed_evidence",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a rubric package from a structured JSON contract.")
    parser.add_argument("--input-file", required=True, help="Path to the JSON contract file.")
    parser.add_argument("--output-file", help="Optional path to write the rendered markdown.")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the structured contract without rendering markdown.",
    )
    return parser.parse_args()


def _load_contract(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Input file was not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Input file is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Top-level contract must be a JSON object")
    return payload


def _require_string(payload: dict, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{key}' must be a non-empty string")
    return value.strip()


def _normalize_list(value: object, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"Field '{field_name}' must be an array of non-empty strings")
    return [item.strip() for item in value]


def _normalize_dimensions(payload: dict) -> list[dict[str, str]]:
    dimensions = payload.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("Field 'dimensions' must be a non-empty array")
    if not 3 <= len(dimensions) <= 7:
        raise ValueError("Field 'dimensions' must contain between 3 and 7 rubric dimensions")

    normalized: list[dict[str, str]] = []
    for index, item in enumerate(dimensions, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Dimension {index} must be an object")
        normalized_item: dict[str, str] = {}
        for key in REQUIRED_DIMENSION_FIELDS:
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Dimension {index} field '{key}' must be a non-empty string")
            normalized_item[key] = value.strip()
        normalized.append(normalized_item)
    return normalized


def _normalize_section(payload: dict, field_name: str, expected_keys: tuple[str, ...]) -> dict[str, list[str] | str]:
    section = payload.get(field_name, {})
    if section is None:
        section = {}
    if not isinstance(section, dict):
        raise ValueError(f"Field '{field_name}' must be an object")

    normalized: dict[str, list[str] | str] = {}
    for key in expected_keys:
        value = section.get(key)
        if isinstance(value, str):
            if not value.strip():
                raise ValueError(f"Field '{field_name}.{key}' must not be empty when provided")
            normalized[key] = value.strip()
        else:
            normalized[key] = _normalize_list(value, f"{field_name}.{key}")
    return normalized


def _render_bullet_value(value: list[str] | str) -> str:
    if isinstance(value, str):
        return value
    if not value:
        return ""
    return "; ".join(value)


def render_markdown(contract: dict) -> str:
    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        _require_string(contract, field_name) if field_name != "dimensions" else None

    dimensions = _normalize_dimensions(contract)
    aggregation_rules = _normalize_section(
        contract,
        "aggregation_rules",
        ("weighting_or_priority", "non_negotiable_failures", "tie_breakers"),
    )
    robustness_checks = _normalize_section(
        contract,
        "robustness_checks",
        (
            "order_bias_check",
            "evidence_quality_check",
            "benchmark_overfitting_check",
            "confidence_guidance",
        ),
    )
    blockers = _normalize_section(
        contract,
        "blockers",
        ("missing_inputs", "weak_evidence_areas", "clarifications_needed"),
    )

    lines = [
        "# Rubric Package",
        "",
        "## Judging Target",
        "",
        f"- Domain: {_require_string(contract, 'domain')}",
        f"- Task being judged: {_require_string(contract, 'task')}",
        f"- Evidence mode: {_require_string(contract, 'evidence_mode')}",
        f"- Decision to make: {_require_string(contract, 'decision')}",
        "",
        "## Locked Rubric",
        "",
        "| Dimension | Why it matters | Pass boundary | Partial boundary | Fail boundary | Allowed evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for dimension in dimensions:
        lines.append(
            "| {name} | {why_it_matters} | {pass_boundary} | {partial_boundary} | {fail_boundary} | {allowed_evidence} |".format(**dimension)
        )

    lines.extend(
        [
            "",
            "Add only the dimensions the task genuinely needs. Keep the rubric fixed once scoring begins.",
            "",
            "## Aggregation Rules",
            "",
            f"- Weighting or priority rules: {_render_bullet_value(aggregation_rules['weighting_or_priority'])}",
            f"- Non-negotiable failures: {_render_bullet_value(aggregation_rules['non_negotiable_failures'])}",
            f"- Tie-breakers: {_render_bullet_value(aggregation_rules['tie_breakers'])}",
            "",
            "## Robustness Checks",
            "",
            f"- Order-bias check: {_render_bullet_value(robustness_checks['order_bias_check'])}",
            f"- Evidence-quality check: {_render_bullet_value(robustness_checks['evidence_quality_check'])}",
            f"- Benchmark-overfitting check: {_render_bullet_value(robustness_checks['benchmark_overfitting_check'])}",
            f"- Confidence guidance: {_render_bullet_value(robustness_checks['confidence_guidance'])}",
            "",
            "## Blockers",
            "",
            f"- Missing inputs: {_render_bullet_value(blockers['missing_inputs'])}",
            f"- Weak evidence areas: {_render_bullet_value(blockers['weak_evidence_areas'])}",
            f"- What must be clarified before judging starts: {_render_bullet_value(blockers['clarifications_needed'])}",
            "",
        ]
    )
    return "\n".join(lines)


def validate_contract(contract: dict) -> dict[str, object]:
    for field_name in REQUIRED_TOP_LEVEL_FIELDS:
        if field_name != "dimensions":
            _require_string(contract, field_name)

    dimensions = _normalize_dimensions(contract)
    aggregation_rules = _normalize_section(
        contract,
        "aggregation_rules",
        ("weighting_or_priority", "non_negotiable_failures", "tie_breakers"),
    )
    robustness_checks = _normalize_section(
        contract,
        "robustness_checks",
        (
            "order_bias_check",
            "evidence_quality_check",
            "benchmark_overfitting_check",
            "confidence_guidance",
        ),
    )
    blockers = _normalize_section(
        contract,
        "blockers",
        ("missing_inputs", "weak_evidence_areas", "clarifications_needed"),
    )

    return {
        "valid": True,
        "dimension_count": len(dimensions),
        "evidence_mode": _require_string(contract, "evidence_mode"),
        "has_aggregation_rules": any(bool(value) for value in aggregation_rules.values()),
        "has_robustness_checks": any(bool(value) for value in robustness_checks.values()),
        "has_blockers": any(bool(value) for value in blockers.values()),
    }


def main() -> int:
    args = _parse_args()
    try:
        contract = _load_contract(Path(args.input_file))
        validation_summary = validate_contract(contract)
        markdown = render_markdown(contract)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.validate_only:
        print(json.dumps(validation_summary, indent=2, sort_keys=True))
        return 0

    if args.output_file:
        Path(args.output_file).write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())