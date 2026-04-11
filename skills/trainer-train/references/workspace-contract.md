# Workspace contract

Use the selected target's local trainer workspace instead of any repo-root `*-workspace` directory.

## Workspace layout

1. Derive `<prompt-name>` from the selected file by stripping `.prompty` entirely, or otherwise stripping only the final extension.
2. Use `<target-dir>/.trainer-workspace/<prompt-name>/` as the workspace root.
3. Before any training stage runs, ensure the workspace contains:
   - `engineer-prompt/`
   - `inputs/source/`
   - `iterations/`
4. Snapshot the current source file under `inputs/source/<basename>` when that snapshot is missing.
5. Require the engineering review artifact at `engineer-prompt/review.md` before optimization begins.

## Workflow status

Maintain `workflow-status.json` at the workspace root with:

- `target_file`
- `workspace_root`
- `prompt_name`
- `workflow_state`
- `updated_at`
- `required_artifacts`

Allowed workflow states:

- `pending_engineer_prompt`
- `pending_training`
- `training`
- `complete`

Keep `required_artifacts` updated for:

- `engineer_prompt_review`
- `source_snapshot`
- `latest_iteration_dir`
- `train_dataset`
- `val_dataset`
- `eval_manifest`
- `optimize_report`
- `candidate_dir`
- `candidate_manifest`
- `latest_steering_turn`
- `steering_summary_dir`
- `validation_log`
- `decision_summary`

## Iteration layout

When training starts, create the next `iterations/iteration-N/` directory and add:

- `research/`
- `synthesize/`
- `optimize/`
- `election/`
- `candidates/`
- `steering/`
- `validation/`

Write human-readable rollups such as `decision.md`, optional `benchmark.json`, optional `benchmark.md`, and optional `review.html` at the workspace root only when they summarize the active best result.
