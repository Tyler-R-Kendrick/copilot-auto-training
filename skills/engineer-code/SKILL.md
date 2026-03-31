---
name: engineer-code
description: Improve Python implementations with Microsoft Trace by turning prompts, helper functions, or small agent components into trainable code. Use this whenever the user wants to apply Trace or trace-opt, optimize Python behavior from tests or feedback, make a method trainable with nodes, bundles, or models, or decide how to structure a Trace training loop for code-focused work.
argument-hint: Describe the Python behavior, available feedback signal, candidate trainable boundary, and whether you are choosing between a Trace node, bundle, or model.
license: MIT
compatibility: Requires Python 3.11+. Designed for repositories that can install or already use Microsoft Trace via the `trace-opt` package.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Engineer Code

Use this skill to help users apply Microsoft Trace to optimize Python code implementations instead of treating Trace as a generic prompt-tuning tool.

Read `references/microsoft-trace-trainable-methods.md` before giving detailed guidance. It summarizes the core Trace workflow, code patterns, and caveats with citations to the Trace repository, docs, paper, examples, and generated API docs.
When the task resembles an official Trace example pattern, map to the closest example before inventing a larger custom design.

## When to use this skill

- The user wants to optimize Python behavior with Microsoft Trace or `trace-opt`.
- The user wants to convert a prompt, helper function, or small agent method into a trainable Trace component.
- The user asks how to use `trace.node`, `@trace.bundle`, `@trace.model`, `ExecutionError`, or `OptoPrime`.
- The user wants to train code from unit-test results, benchmark scores, natural-language critiques, compiler errors, or other non-scalar feedback.
- The user wants help deciding what should stay plain Python and what should become a Trace parameter.

Do not use this skill as the primary fix for generic Python runtime performance tuning, missing Trace installation, infrastructure or tooling failures, or tasks with no repeatable feedback signal. In those cases, say Trace is a bad fit or only a secondary lever.

## Required inputs

- The Python behavior or component to improve.
- The candidate trainable surface, or the code boundary under consideration.
- The feedback signal available today: tests, benchmark scores, compiler or runtime errors, or concise natural-language critiques.
- Any repo or runtime constraints, including whether Microsoft Trace is installed and what validation can be rerun deterministically.

## Core workflow

Follow this order:

1. Identify the Python behavior that should improve.
2. Choose the smallest trainable surface that Trace should control.
3. Represent that surface with `trace.node`, `@trace.bundle(trainable=True)`, or `@trace.model`.
4. Define a repeatable feedback signal.
5. Sketch or review the optimization loop with `zero_feedback()`, `backward(...)`, and `step()`.
6. Call out graph-size, dependency, and failure-handling concerns before the user commits to the design.

## Trace design defaults

- Keep orchestration, I/O, and stable business rules in plain Python.
- Make prompts, code snippets, routing decisions, or narrow transformation methods trainable only when feedback can actually improve them.
- Prefer `trace.node(..., trainable=True)` for values such as prompts, instructions, templates, thresholds, or other mutable parameters.
- Prefer `@trace.bundle(trainable=True)` for a function whose implementation or behavior should be optimized as a unit.
- Prefer `@trace.model` when the user has several related trainable members and wants one parameter set for an agent-like object.
- Keep feedback concrete. Tests, benchmark scores, compiler errors, and concise natural-language critiques are better than vague opinions.

## Response contract

When helping the user, structure the answer like this unless they ask for something shorter:

1. `Optimization target`: the Python behavior to improve
2. `Trainable surface`: what to mark trainable and what to leave fixed
3. `Trace pattern`: whether to use nodes, bundles, models, or a combination
4. `Feedback loop`: how the optimization loop should produce and consume feedback
5. `Implementation sketch`: concise Python code or a code-edit plan
6. `Risks`: graph size, error handling, hidden dependencies, or over-broad trainable scope

If Trace is not the main fix, say that explicitly before proposing any Trace pattern or implementation sketch.

## Heuristics for code-focused work

### Use nodes for editable values

Reach for nodes when the user wants to improve values rather than rewrite control flow:

- prompts
- instruction strings
- code-generation exemplars
- thresholds and routing labels
- short reusable templates

### Use trainable bundles for method-level optimization

Reach for trainable bundles when the user wants Trace to optimize the behavior of a Python function or method and the feedback applies to that callable as a unit.

Good fits:

- formatting helpers
- extraction logic
- classification steps
- repair or rewrite functions
- small planner methods inside a larger agent

### Use models for grouped behavior

Reach for models when several trainable nodes and bundled methods belong to one coherent object, such as a coding agent, repair loop, or evaluator pipeline.

Keep the model boundary small enough that the optimizer still receives meaningful, attributable feedback.

## Feedback guidance

- Prefer executable checks first: tests, assertions, score functions, or task-specific validators.
- Add natural-language feedback when executable checks explain *what* failed but not *how* to improve it.
- Preserve failed executions and feed them back through `ExecutionError` when the failure itself is informative.
- Reset feedback each iteration before the next backward pass.

## Code-generation guidance

When generating Trace-based Python:

- keep imports explicit
- show the trainable declarations close to the logic they influence
- make the feedback function easy to run repeatedly
- show the optimization loop in full, including the stop condition
- separate trainable code from surrounding scaffolding so future edits stay understandable

## Limits to call out

- Full-graph methods are powerful, but large graphs can become context-heavy for graph-aware optimizers.
- Hidden dependencies inside a bundled function can break tracing assumptions.
- A trainable surface that is too broad makes feedback noisy and updates harder to interpret.
- Trace helps when the user can iterate on observable feedback; it is weaker when success is undefined or never measured.
