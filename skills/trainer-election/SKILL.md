---
name: trainer-election
description: Elect the strongest prompt or skill candidate from a spec-compliant evaluation workspace. Use when multiple candidate configurations already have eval outputs, grading, or benchmark artifacts and you need a standalone leader selection step without re-running optimization.
license: MIT
compatibility: Requires Python 3.11+. Reads eval workspaces that follow the Agent Skills evaluation layout with eval metadata, grading.json, timing.json, and optional benchmark.json artifacts.
metadata:
  author: your-org
  version: "0.1.0"

---

# Election

Use this skill to elect a winner from existing evaluation artifacts. This skill does not generate candidates, run search, or know anything about optimize internals.

## When to use this skill

- Multiple candidate configurations already exist as `with_skill`, `without_skill`, `old_skill`, or other config directories inside a skill-eval workspace.
- Each candidate has already been run against authored evals and saved `grading.json` and optional `timing.json` artifacts.
- You need a separate election pass that picks the strongest configuration from workspace results instead of generating new candidates.
- Do not use this skill to gather datasets, synthesize evals, or optimize prompts. Those remain separate skills.

## Inputs

- `workspace_dir`: root workspace path or a specific iteration directory
- `iteration`: optional iteration selector when the workspace contains multiple iterations
- `manifest_file`: optional authored `evals/evals.json` path for expected eval coverage

## Election Behavior

1. Read the requested iteration directory or the latest iteration in the workspace.
2. Discover eval directories and configuration directories that follow the Agent Skills evaluation structure.
3. Aggregate pass rate, coverage, timing, and token usage from `grading.json` and `timing.json`, falling back to `benchmark.json` if raw run artifacts are unavailable.
4. Penalize incomplete eval coverage so partially graded candidates do not beat fully validated ones by omission.
5. Elect the leader by adjusted score, using lower error count, time, and token usage as tie-breakers.
6. Persist candidate metadata so callers can explain the winner and locate the winning prompt artifact when one exists.

## Naming rationale

`election` is still the right public name because the skill owns the act of electing a winner from a scored field of candidates. The key change is that the field now comes from evaluation artifacts rather than from internal optimize-side search.