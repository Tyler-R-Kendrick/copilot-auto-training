---
name: judge-trajectory
description: Evaluate agent trajectories, tool-use traces, intermediate artifacts, runtime failures, and side effects when process quality is part of the verdict. Use this whenever the judging task involves agent runs, tool calls, planning quality, web or code traces, process reliability, or any comparison where the final answer alone is not enough, even if the user only says judge the run, compare traces, or evaluate the agent workflow.
license: MIT
compatibility: Works in agents that support the Agent Skills standard. The `judge` agent should load this skill through the agent-skills MCP server when process evidence matters.
metadata:
  author: your-org
  version: "0.1.0"
---

# Trajectory Judging

Use this skill when the decisive evidence lives in the process: plans, tool calls, intermediate artifacts, failure handling, gathered evidence, or side effects.

Read `references/trajectory-techniques.md` when you need the benchmark rationale for process-aware judging, trajectory rubrics, verifier-backed evidence gathering, and skepticism toward narrated reasoning.

## When to use this skill

- Agent-run evaluation where trajectories, tool traces, or intermediate artifacts matter.
- Web, code, RAG, or tool-use comparisons where process reliability is part of the verdict.
- Candidate comparisons where runtime failures, evidence-gathering quality, or side effects should influence the score.

Do not use this skill alone for clean outcome-only response comparison. In those cases, switch to an outcome-focused judging contract instead.

## Required inputs

- Candidate trajectories, tool traces, transcripts, failure logs, or intermediate artifacts.
- The baseline trajectory when available.
- Any task contract, `reference`, `criteria`, benchmark notes, or end-state artifacts needed to judge whether the process achieved the right goal.
- Outcome artifacts when the verdict needs both process and end-state quality.

## Trajectory judging workflow

1. Lock a process-aware rubric before judging. Keep it to 4 to 7 dimensions and define explicit pass, partial, or fail boundaries.
2. Build a trajectory evidence ledger from plans, tool calls, retrieved evidence, intermediate artifacts, side effects, failure logs, and final outputs.
3. Score every candidate against the same rubric. Make process quality first-class evidence instead of treating it as optional commentary.
4. Separate operational failures from quality failures. Placeholder mismatches, broken tool usage, missing evidence gathering, and unhandled exceptions should appear explicitly in the verdict.
5. Use final outcomes as one dimension, not the whole verdict, when process quality clearly matters.
6. Run a robustness check before finalizing. Watch for order effects, benchmark overfitting, and unjustified trust in chain-of-thought or self-explanations.
7. Return a concise decision package that preserves the process rubric, decisive trace evidence, rejected-candidate failure modes, and calibrated confidence.

## Default trajectory dimensions

- Plan suitability.
- Evidence gathering or retrieval quality.
- Tool correctness and tool sequencing.
- Failure handling and recovery.
- Side effects or state-change quality.
- Final outcome quality.

## Output package

- Selected candidate and margin.
- Locked trajectory rubric.
- Decisive trace evidence summary.
- Main weaknesses and concrete failure modes in rejected candidates.
- Confidence or uncertainty note.

## Assets

- `assets/trajectory-rubric-template.md` provides a reusable rubric and evidence-ledger template for process-aware judging.
