---
name: judge-outcome
description: Evaluate final outputs, response pairs, scored artifacts, or benchmark-style answer quality without relying on full trajectories. Use this whenever the judging task is mainly about end-state quality, final answer comparison, reference-plus-criteria scoring, or choosing the best output among candidates, even if the user only says compare responses, pick the best answer, or judge the final result.
license: MIT
compatibility: Works in agents that support the Agent Skills standard. The `judge` agent should load this skill through the agent-skills MCP server when outcome quality is the primary comparison target.
metadata:
  author: your-org
  version: "0.1.0"
---

# Outcome Judging

Use this skill when the evidence is mostly about final outputs rather than the full agent trajectory. The main job is to produce a locked, evidence-anchored comparison of end-state quality.

Read `references/outcome-techniques.md` when you need the benchmark rationale for locked rubrics, bias-aware outcome judging, calibration, or skepticism toward unsupported chain-of-thought.

## When to use this skill

- Final-output judging, pairwise response comparison, or benchmark-style answer ranking.
- Cases where `reference`, `criteria`, or explicit outcome artifacts matter more than the full process trace.
- Prompt-candidate comparisons where the decisive evidence is the quality of the final answer, final file, or end-state response.

Do not use this skill as the only judging contract when tool traces, side effects, runtime failures, or intermediate artifacts are central to the verdict. In those cases, switch to a process-aware judging contract instead.

## Required inputs

- The candidate outputs or candidate prompts being compared.
- The baseline output or baseline prompt when available.
- Any task contract, `reference`, `criteria`, or benchmark notes that define what success looks like.
- Outcome-facing artifacts such as final responses, generated files, benchmark summaries, or validation results.

## Outcome judging workflow

1. Lock a task-specific outcome rubric before judging. Keep it to 3 to 7 dimensions and define explicit pass, partial, or fail boundaries.
2. Build an outcome evidence ledger from final outputs, baseline outputs, references, criteria, benchmark summaries, and validation artifacts.
3. Score every candidate against the same rubric. Do not let rhetorical polish substitute for correctness, compliance, completeness, or usefulness.
4. Run an order-robustness check. If the verdict changes when the candidate order changes, report reduced confidence rather than hiding the instability.
5. Treat chain-of-thought or self-explanations as low-trust evidence unless the end-state artifacts corroborate them.
6. Break close calls with stable tie-breakers: stronger rubric compliance, clearer evidence anchoring, lower evaluator risk, better benchmark fit, then clearer writing.
7. Return a concise decision package that preserves the locked rubric, decisive evidence, rejected-candidate failure modes, and calibrated confidence.

## Default outcome dimensions

- Constraint compliance.
- Correctness or groundedness.
- Completeness.
- Safety or policy alignment when relevant.
- Format fidelity or usability when the task requires structured output.

## Output package

- Selected candidate and margin.
- Locked outcome rubric.
- Decisive evidence summary.
- Main weaknesses and concrete failure modes in rejected candidates.
- Confidence or uncertainty note.

## Assets

- `assets/outcome-rubric-template.md` provides a reusable rubric and evidence-ledger template for end-state judging.
