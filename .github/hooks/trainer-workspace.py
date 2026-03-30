#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


WORKFLOW_STATES = (
    "pending_engineer_prompt",
    "pending_training",
    "training",
    "complete",
)
ITERATION_SUBDIRS = ("research", "synthesize", "optimize", "election", "validation")
ITERATIONS_DIRNAME = "iterations"


def detect_optimize_artifact(repo_root: Path, iteration_abs: Path) -> str | None:
    optimize_dir = iteration_abs / "optimize"
    candidates = (
        optimize_dir / "optimize-report.json",
        optimize_dir / "manual-followup-report.json",
    )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.relative_to(repo_root))
    return None


def prompt_name_for(path: str | Path) -> str:
    base = Path(path).name
    if base.endswith(".prompty"):
        return base[: -len(".prompty")]
    if base.endswith(".md"):
        return base[: -len(".md")]
    return Path(base).stem


def resolve_repo_root(repo_root: str | Path) -> Path:
    return Path(repo_root).resolve()


def resolve_repo_path(repo_root: Path, value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve()


def to_repo_relative(repo_root: Path, path: str | Path | None) -> str | None:
    if path is None:
        return None
    resolved = resolve_repo_path(repo_root, path)
    return str(resolved.relative_to(repo_root))


def workspace_root_for(target_file: str | Path) -> Path:
    target_path = Path(target_file)
    return target_path.parent / ".trainer-workspace" / prompt_name_for(target_path)


def load_status(status_path: Path) -> dict[str, Any]:
    if not status_path.is_file():
        return {}
    return json.loads(status_path.read_text(encoding="utf-8"))


def write_status(status_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def artifact_defaults(workspace_rel: str, source_snapshot_rel: str) -> dict[str, Any]:
    return {
        "engineer_prompt_review": f"{workspace_rel}/engineer-prompt/review.md",
        "source_snapshot": source_snapshot_rel,
        "latest_iteration_dir": None,
        "train_dataset": None,
        "val_dataset": None,
        "eval_manifest": None,
        "optimize_report": None,
        "validation_log": None,
        "decision_summary": f"{workspace_rel}/decision.md",
    }


def artifact_contract() -> dict[str, str]:
    return {
        "engineer_prompt": "Save the engineering review and rewrite notes under engineer-prompt/.",
        "inputs": "Keep stable prompt snapshots and any reused dataset references under inputs/.",
        "iterations": "Write research, synthesis, optimize, election, benchmark, and validation outputs under iterations/iteration-N/.",
        "decision": "Summarize the winning prompt decision and validation outcome in decision.md.",
    }


def initialize_workspace(repo_root: Path, target_file: str | Path, state: str) -> dict[str, Any]:
    if state not in WORKFLOW_STATES:
        raise ValueError(f"Unsupported workflow state: {state}")

    target_abs = resolve_repo_path(repo_root, target_file)
    workspace_abs = workspace_root_for(target_abs)
    workspace_rel = str(workspace_abs.relative_to(repo_root))
    target_rel = str(target_abs.relative_to(repo_root))
    workspace_parent = str(target_abs.parent.relative_to(repo_root)) if target_abs.parent != repo_root else "."

    (workspace_abs / "engineer-prompt").mkdir(parents=True, exist_ok=True)
    (workspace_abs / ITERATIONS_DIRNAME).mkdir(parents=True, exist_ok=True)
    source_dir = workspace_abs / "inputs" / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    source_snapshot_abs = source_dir / target_abs.name
    if not source_snapshot_abs.exists():
        shutil.copy2(target_abs, source_snapshot_abs)

    status_path = workspace_abs / "workflow-status.json"
    existing = load_status(status_path)
    payload = {
        **existing,
        "target_file": target_rel,
        "workspace_root": workspace_rel,
        "workspace_parent": workspace_parent,
        "prompt_name": prompt_name_for(target_abs),
        "workflow_state": state,
        "updated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "required_artifacts": {
            **artifact_defaults(workspace_rel, str(source_snapshot_abs.relative_to(repo_root))),
            **existing.get("required_artifacts", {}),
        },
        "artifact_contract": artifact_contract(),
        "notes": "Run /engineer-prompt first, then @trainer. Keep repo-specific optimization artifacts in .trainer-workspace instead of a generic copied eval layout.",
    }
    payload["required_artifacts"]["source_snapshot"] = str(source_snapshot_abs.relative_to(repo_root))
    return write_status(status_path, payload)


def update_workspace(
    repo_root: Path,
    *,
    workspace_root: str | Path | None,
    target_file: str | Path | None,
    state: str | None,
    engineer_prompt_review: str | None,
    train_dataset: str | None,
    val_dataset: str | None,
    eval_manifest: str | None,
    optimize_report: str | None,
    validation_log: str | None,
    decision_summary: str | None,
    iteration: str | None,
    create_iteration_layout: bool,
) -> dict[str, Any]:
    if workspace_root is None and target_file is None:
        raise ValueError("workspace_root or target_file is required")

    if target_file is not None:
        target_abs = resolve_repo_path(repo_root, target_file)
        workspace_abs = workspace_root_for(target_abs)
    else:
        workspace_abs = resolve_repo_path(repo_root, workspace_root)

    workspace_rel = str(workspace_abs.relative_to(repo_root))
    status_path = workspace_abs / "workflow-status.json"
    payload = load_status(status_path)
    if not payload:
        if target_file is None:
            raise FileNotFoundError(f"No workflow-status.json found under {workspace_abs}")
        payload = initialize_workspace(repo_root, target_file, state or "pending_engineer_prompt")

    if state is not None:
        if state not in WORKFLOW_STATES:
            raise ValueError(f"Unsupported workflow state: {state}")
        payload["workflow_state"] = state

    required = payload.setdefault("required_artifacts", {})
    for key, value in {
        "engineer_prompt_review": engineer_prompt_review,
        "train_dataset": train_dataset,
        "val_dataset": val_dataset,
        "eval_manifest": eval_manifest,
        "optimize_report": optimize_report,
        "validation_log": validation_log,
        "decision_summary": decision_summary,
    }.items():
        if value is not None:
            required[key] = to_repo_relative(repo_root, value)

    if iteration is not None:
        iteration_abs = workspace_abs / ITERATIONS_DIRNAME / iteration
        if create_iteration_layout:
            for name in ITERATION_SUBDIRS:
                (iteration_abs / name).mkdir(parents=True, exist_ok=True)
        required["latest_iteration_dir"] = str(iteration_abs.relative_to(repo_root))
        if optimize_report is None:
            detected_optimize_artifact = detect_optimize_artifact(repo_root, iteration_abs)
            if detected_optimize_artifact is not None:
                required["optimize_report"] = detected_optimize_artifact

    if required.get("latest_iteration_dir") and optimize_report is None and required.get("optimize_report") is None:
        latest_iteration_abs = resolve_repo_path(repo_root, required["latest_iteration_dir"])
        detected_optimize_artifact = detect_optimize_artifact(repo_root, latest_iteration_abs)
        if detected_optimize_artifact is not None:
            required["optimize_report"] = detected_optimize_artifact

    payload["workspace_root"] = workspace_rel
    payload["artifact_contract"] = artifact_contract()
    payload["updated_at"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    return write_status(status_path, payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Initialize or update repo-specific trainer workspace artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a local .trainer-workspace tree for a prompt-like file")
    init_parser.add_argument("--repo-root", required=True)
    init_parser.add_argument("--target-file", required=True)
    init_parser.add_argument("--state", default="pending_engineer_prompt", choices=WORKFLOW_STATES)

    update_parser = subparsers.add_parser("update", help="Update workflow status and artifact paths")
    update_parser.add_argument("--repo-root", required=True)
    update_parser.add_argument("--workspace-root")
    update_parser.add_argument("--target-file")
    update_parser.add_argument("--state", choices=WORKFLOW_STATES)
    update_parser.add_argument("--engineer-prompt-review")
    update_parser.add_argument("--train-dataset")
    update_parser.add_argument("--val-dataset")
    update_parser.add_argument("--eval-manifest")
    update_parser.add_argument("--optimize-report")
    update_parser.add_argument("--validation-log")
    update_parser.add_argument("--decision-summary")
    update_parser.add_argument("--iteration")
    update_parser.add_argument("--create-iteration-layout", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)

    if args.command == "init":
        payload = initialize_workspace(repo_root, args.target_file, args.state)
    else:
        payload = update_workspace(
            repo_root,
            workspace_root=args.workspace_root,
            target_file=args.target_file,
            state=args.state,
            engineer_prompt_review=args.engineer_prompt_review,
            train_dataset=args.train_dataset,
            val_dataset=args.val_dataset,
            eval_manifest=args.eval_manifest,
            optimize_report=args.optimize_report,
            validation_log=args.validation_log,
            decision_summary=args.decision_summary,
            iteration=args.iteration,
            create_iteration_layout=args.create_iteration_layout,
        )

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())