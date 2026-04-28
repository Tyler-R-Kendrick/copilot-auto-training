# Decision: create-workflow SKILL.md — Iteration 1

**Target:** `skills/create-workflow/SKILL.md`
**Workspace:** `skills/create-workflow/.trainer-workspace/SKILL/`
**Date:** 2026-04-28
**Result:** Student candidate applied ✅

## Changes Applied

Six targeted improvements based on 8 llm_judge training/validation scenarios:

1. **Compilation rule front-loaded** — Added bold rule to CLI Quick Reference before any section
2. **Draft-only mode clarified** — §1 now says "skip compilation entirely, state not runnable, list prereqs"
3. **Safe-outputs reminder in §3** — Write-ops check before finishing authoring phase
4. **§5 rule order fixed** — Frontmatter → recompile listed first with inline command
5. **§6 debug order fixed** — `--verbose` promoted to first bullet in compilation failures
6. **Response contract strengthened** — Item 3 requires frontmatter/body distinction + exact compile command

## Validation

- 856 pytest tests passed, 0 failures
- Teacher review: STOP (all 5 gaps closed, no regressions)
- Adversary review: No SKILL.md exploits; 2 eval assertion gaps fixed in evals.json

## Supporting Artifacts

- Research: `iterations/iteration-1/research/research-brief.md`
- Datasets: `iterations/iteration-1/synthesize/datasets/train.jsonl` (6 cases), `val.jsonl` (2 cases)
- Evals: `skills/create-workflow/evals/evals.json` (8 cases, llm_judge)
- Optimizer: `iterations/iteration-1/optimize/manual-followup-report.json` (torch missing; manual path)
- Optimized prompt: `iterations/iteration-1/optimize/optimized-prompt.md`
- Steering: `iterations/iteration-1/steering/teacher/turn-1/STEERING.md`
