---
name: engineer-prompt
description: Apply DSPy to prompt and instruction artifacts by choosing the smallest trainable prompt surface, compiling it with a DSPy optimizer, and exporting a stable Markdown artifact. Use this when the user wants DSPy, prompt-as-code optimization, MIPROv2, instruction-only optimization, or deterministic prompt artifact export.
argument-hint: Describe the prompt artifact, candidate DSPy surface, available feedback signal, and whether you need a full generated artifact or a deterministic wrapper around optimized instructions.
license: MIT
compatibility: Requires Python 3.11+. Designed for markdown-first prompt work and DSPy-based prompt optimization.
metadata:
  author: Tyler Kendrick
  version: "0.3.0"
---

# Engineer Prompt

Use this skill to help users apply DSPy to prompt engineering instead of treating prompt work as one-off rewriting.

Read `references/dspy-skill-artifacts.md` before giving detailed guidance. Use `references/token-efficient-patterns.md` when the task is also fighting token pressure, large inline schemas, or bulky workflow prose.

## When to use this skill

- The user wants to apply DSPy or prompt-as-code optimization.
- The user wants to convert a prompt, instruction block, or prompt-like artifact into a `dspy.Signature` or `dspy.Module`.
- The user wants to choose between instruction-only optimization and demo-heavy optimization.
- The user wants to decide whether DSPy should emit a full prompt artifact or only an optimized instruction body.
- The user wants to define a metric or eval strategy for a prompt artifact such as `SKILL.md`, `AGENTS.md`, or another markdown prompt file.
- The user wants to export an optimized prompt into a stable checked-in Markdown artifact.

Do not use this skill as the primary fix for stale retrieval, missing tools, unclear product requirements, raw runtime tuning, or one-off prompt rewrites with no repeatable feedback signal. In those cases, say DSPy is a bad fit or only a secondary lever.

## Required inputs

- The prompt or prompt-like artifact to improve.
- The candidate trainable surface, or the boundary under consideration.
- The feedback signal available today: evals, datasets, structural checks, rubric-based judgments, or concise critiques.
- Runtime or repository constraints, including what file shape must remain stable after export.

## Core workflow

Follow this order:

1. Identify the prompt behavior that should improve.
2. Choose the smallest DSPy surface that should become trainable.
3. Decide whether to optimize instructions only or allow demos.
4. Define a repeatable metric or eval target.
5. Choose the export strategy for the final checked-in artifact.
6. Call out packaging risks and non-prompt blockers before the user commits to the design.

## DSPy design defaults

- Keep file shape, front matter, and other stable packaging concerns deterministic whenever the repository expects a strict artifact contract.
- Prefer `dspy.Signature` for narrow prompt interfaces with clear input and output fields.
- Prefer a small `dspy.Module` when orchestration, multiple predictors, or helper steps belong together.
- Prefer instruction-only optimization when the goal is a clean reusable artifact; set demo counts to zero unless runtime quality clearly matters more than artifact cleanliness.
- Save the compiled DSPy program separately from the emitted Markdown artifact.
- Prefer downstream evals or artifact-specific checks over vague string matching when a real validation target already exists.

## Response contract

When helping the user, structure the answer like this unless they ask for something shorter:

1. `Optimization target`: the prompt behavior or artifact to improve
2. `DSPy surface`: what should become a signature or module, and what should stay deterministic
3. `Optimization strategy`: whether to optimize instructions only, allow demos, and which optimizer pattern fits
4. `Metric or evals`: how the optimization loop will be judged
5. `Export strategy`: how the optimized result should become a stable checked-in artifact
6. `Risks`: formatting drift, noisy feedback, non-prompt blockers, or over-broad trainable scope

If DSPy is not the main fix, say that explicitly before proposing any DSPy pattern or export plan.

## Heuristics for prompt-focused work

### Use signatures for stable prompt contracts

Reach for `dspy.Signature` when the prompt behavior is mostly one predictor with a clear input/output contract, such as:

- a single prompt template
- a skill instruction body
- a classification or extraction prompt
- a rewrite prompt with a fixed output contract

### Use modules for grouped prompt behavior

Reach for `dspy.Module` when several prompt decisions should improve together, such as:

- a prompt plus a critique step
- a planner plus a renderer
- an artifact writer plus a deterministic exporter
- a prompt pipeline with narrow reusable helper steps

Keep the module boundary small enough that the feedback still points at one coherent prompt behavior.

### Prefer deterministic export for repository artifacts

Default to deterministic wrapping when the repository expects a stable markdown artifact:

- keep YAML front matter fixed
- keep section layout fixed
- optimize only the instruction body or another narrow prompt surface
- render the final file with a template you own

Let DSPy write the full file only when formatting variance is acceptable and the evals strongly enforce the final shape.

## Feedback guidance

- Prefer real eval cases, benchmark checks, or artifact-specific validators first.
- Use structural checks for packaging requirements such as front matter, headings, trigger conditions, output contracts, and forbidden behaviors.
- Add concise natural-language critique only when executable checks explain what failed but not how to improve it.
- Keep the metric aligned with the artifact the user actually plans to commit.

## Artifact guidance

When the user wants a checked-in prompt artifact:

- optimize the narrowest reusable prompt surface
- wrap the optimized surface in a deterministic renderer when repository shape matters
- save the compiled program for reuse or debugging
- keep demos out of the checked-in artifact unless the runtime contract truly needs them
- validate the final artifact against the same downstream checks reviewers will rely on

## Limits to call out

- DSPy is strongest when the user has repeatable feedback; it is weaker when success is undefined or only judged informally once.
- Few-shot-heavy optimized programs may perform better at runtime but often export poorly as one neat Markdown file.
- If the main blocker is stale retrieval, missing tools, or unclear requirements, DSPy will not fix the root cause.
- A trainable surface that is too broad makes the exported artifact harder to reason about and the feedback harder to trust.
