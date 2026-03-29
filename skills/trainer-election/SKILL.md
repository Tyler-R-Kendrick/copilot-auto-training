---
name: trainer-election
description: Elect the strongest prompt or skill candidate from an existing evaluation workspace. Use this skill whenever a workflow already has multiple scored configurations and needs a separate leader-selection pass over grading, timing, or benchmark artifacts, especially when comparing optimize outputs without pushing that selection logic back into trainer-optimize.
license: MIT
compatibility: Requires Python 3.11+. Reads eval workspaces that follow the Agent Skills evaluation layout with eval metadata, grading.json, timing.json, and optional benchmark.json artifacts.
metadata:
  author: your-org
  version: "0.1.0"

---

# Election

Use this skill to elect a winner from existing evaluation artifacts. Treat it as the standalone selection step after candidates have already been run and graded. It does not generate candidates, perform research, synthesize evals, or re-run optimization.

## When to use this skill

- A workflow already produced multiple candidate configurations and now needs a winner chosen from scored artifacts.
- Multiple candidate configurations already exist as `with_skill`, `without_skill`, `old_skill`, or other config directories inside a skill-eval workspace.
- Each candidate has already been run against authored evals and saved `grading.json` and optional `timing.json` artifacts.
- You need a separate election pass that picks the strongest configuration from workspace results instead of generating new candidates.
- The workflow explicitly needs comparison across multiple optimize outputs, prompt rewrites, or skill revisions without folding that comparison into `trainer-optimize`.

Do not use this skill to gather datasets, synthesize evals, optimize prompts, or run missing evaluations from scratch. Those remain separate skills.

## Inputs

- `workspace_dir`: root workspace path, a specific iteration directory, or a direct eval directory
- `iteration`: optional iteration selector when the workspace contains multiple iterations
- `manifest_file`: optional authored `evals/evals.json` path for expected eval coverage

If `manifest_file` is omitted, the runtime searches `evals/evals.json` next to the iteration directory, then one level higher.

## Accepted workspace layouts

The runtime accepts these shapes:

- a workspace root that contains `iterations/iteration-N/` directories
- a direct `iterations/iteration-N/` directory
- a legacy workspace root that contains `iteration-N/` directories
- a legacy direct iteration directory
- a direct eval directory when only one eval folder is available
- iteration directories that keep evals at the top level or under `runs/`

Config directories may contain `grading.json` and `timing.json` directly or nested `run-N/` subdirectories. Baselines are recognized for `baseline`, `without_skill`, `old_skill`, and names ending in `_baseline`.

## Election Behavior

1. Read the requested iteration directory or the latest iteration in the workspace.
2. Discover eval directories and configuration directories that follow the Agent Skills evaluation structure.
3. Resolve expected eval coverage from the explicit manifest when provided, otherwise from the nearest `evals/evals.json`, otherwise from the discovered eval keys.
4. Load scored runs from raw `grading.json` and `timing.json` artifacts.
5. Fall back to `benchmark.json` only when raw run artifacts are unavailable.
6. Aggregate mean pass rate, coverage ratio, penalty, mean time, mean token count, and mean error count per configuration.
7. Penalize incomplete eval coverage so partially graded candidates do not beat fully validated ones by omission.
8. Elect the leader by adjusted score, using raw score, lower error count, lower time, lower token usage, and stable name ordering as tie-breakers.
9. Persist candidate metadata so callers can explain the winner and locate the winning prompt artifact when one exists.

## Output contract

The runtime returns JSON with these top-level fields:

- `winner`: winning configuration name
- `best_prompt`: prompt text when a prompt artifact is discoverable
- `best_prompt_file`: path to the winning prompt artifact when present
- `best_candidate`: the winning candidate record
- `persisted_candidates`: all candidate summaries with `is_winner`, coverage, score, and cost metadata
- `selection_source`: `workspace` when raw run artifacts were used, otherwise `benchmark`
- `iteration_dir`, `manifest_file`, and `expected_eval_count` for caller traceability

Prompt artifacts are discovered from `outputs/` or the run directory using prompt-like filenames such as `prompt.md`, `candidate.md`, or `*.prompt.md`.

## Guardrails

- Prefer full eval coverage over partial wins.
- Treat missing `grading.json` as unscored instead of inventing results.
- Do not assume optimize internals or regenerate candidates from election.
- Keep baseline configurations in the pool so comparisons remain explainable.
- Stop with a clear error if no scored candidate runs can be found.

## Running the runtime

```bash
python skills/trainer-election/scripts/run_election.py <workspace_dir> \
  [--iteration <iteration-number-or-path>] \
  [--manifest-file <path-to-evals.json>] \
  [--output-file <path-to-result.json>]
```

Use [skills/trainer-election/references/leader-election.md](./references/leader-election.md) for the short rationale behind the scoring model.

## Naming rationale

`election` is still the right public name because the skill owns the act of electing a winner from a scored field of candidates. The key change is that the field now comes from evaluation artifacts rather than from internal optimize-side search.