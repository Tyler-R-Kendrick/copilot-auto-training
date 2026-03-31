# Microsoft Trace for trainable Python methods

This reference summarizes the most useful ways to apply Microsoft Trace when the goal is to optimize Python implementations rather than talk about the library abstractly.

## Source map

- Trace repository: <https://github.com/microsoft/Trace>
- Intro docs: <https://microsoft.github.io/Trace/intro.html>
- Paper: <https://arxiv.org/html/2406.16218v2>
- Examples: <https://github.com/microsoft/Trace/tree/main/examples>
- Generated API docs index: <https://github.com/microsoft/Trace/tree/main/generated_docs/opto>

## 1. Start from ordinary Python, then mark only the trainable surface

Trace is designed so users write Python code directly, then designate trainable parts with `node`, `@bundle`, and `@trace.model` instead of rewriting the whole workflow in a special graph language. The repository README and intro docs both frame Trace as an AutoDiff-like system that captures execution traces for ordinary Python workflows, while the paper generalizes that idea to broader AI systems that learn from rich feedback rather than only numeric gradients. [Trace repository](https://github.com/microsoft/Trace) [Intro docs](https://microsoft.github.io/Trace/intro.html) [Paper](https://arxiv.org/html/2406.16218v2)

Best practice for code optimization:

- keep stable orchestration, I/O, and evaluator plumbing as plain Python
- make only prompts, code fragments, routing rules, or narrowly scoped methods trainable
- choose the smallest surface where better feedback could realistically change behavior

That design keeps the execution graph legible and improves credit assignment. [Intro docs](https://microsoft.github.io/Trace/intro.html) [Paper](https://arxiv.org/html/2406.16218v2)

## 2. Use the right Trace primitive for the job

### `trace.node(..., trainable=True)` for editable values

The README quickstart and generated docs describe nodes as trainable values in the computation graph. This is the right default for prompts, instructions, templates, thresholds, labels, or other mutable values that should change without turning an entire method into trainable code. [Trace repository](https://github.com/microsoft/Trace) [Generated API docs index](https://github.com/microsoft/Trace/tree/main/generated_docs/opto)

### `@trace.bundle(trainable=True)` for method-level optimization

The README quickstart and generated `bundle` documentation show that bundled functions behave like regular Python callables while still participating in Trace's graph. For code-focused optimization, this is the most useful primitive when the user wants a helper function, planner step, transformation routine, or repair function to become trainable as a unit. The generated docs also call out that trainable bundles can catch execution errors and track external dependencies, which matters when optimizing real code rather than toy examples. [Trace repository](https://github.com/microsoft/Trace) [Generated API docs index](https://github.com/microsoft/Trace/tree/main/generated_docs/opto)

### `@trace.model` for grouped agent behavior

The intro docs and greeting example use `@trace.model` to group several trainable nodes and bundled methods behind one Python object. Use a model when the user has a cohesive code path, such as a coding assistant, repair agent, or evaluator loop, with multiple trainable members that should be optimized together. [Intro docs](https://microsoft.github.io/Trace/intro.html) [Examples](https://github.com/microsoft/Trace/tree/main/examples)

## 3. Design feedback first, because Trace is strongest with rich, repeatable signals

The Trace README and paper both emphasize that feedback can be numerical rewards, natural-language critiques, compiler errors, or other general signals. That makes Trace a strong fit for Python implementation work where success can come from test failures, benchmark output, lint/compiler diagnostics, or short human critiques. [Trace repository](https://github.com/microsoft/Trace) [Paper](https://arxiv.org/html/2406.16218v2)

For code optimization, good feedback usually looks like this:

- unit-test pass/fail plus failing assertion context
- benchmark or task score
- compiler, parser, or runtime error text
- concise language feedback that explains what to improve next

Weak feedback usually looks like this:

- vague statements like "make it better"
- one-off manual judgments with no replayable loop
- giant, noisy logs with no distilled failure signal

The best Trace workflows combine executable checks with a short explanation of the failure mode. [Paper](https://arxiv.org/html/2406.16218v2) [Examples](https://github.com/microsoft/Trace/tree/main/examples)

## 4. Keep the optimization loop explicit and repeatable

The README quickstart, intro docs, and greeting example all use the same pattern:

1. run the code
2. compute feedback from the result
3. call `optimizer.zero_feedback()`
4. call `optimizer.backward(node, feedback)`
5. call `optimizer.step()`

The generated optimizer docs explain that `zero_feedback()` resets feedback on managed parameters, `backward(...)` propagates feedback through the graph, and `step()` proposes and applies updates to trainable parameters. That is the core loop to preserve whenever you adapt Trace to optimize Python code. [Trace repository](https://github.com/microsoft/Trace) [Intro docs](https://microsoft.github.io/Trace/intro.html) [Generated API docs index](https://github.com/microsoft/Trace/tree/main/generated_docs/opto)

## 5. Preserve failing executions instead of throwing them away

The greeting example catches `ExecutionError`, pulls out `exception_node`, and still feeds that node back into the optimizer. The generated error docs explain that `ExecutionError` packages tracing-time failures as nodes with structured context. For code optimization, this is important because parse failures, runtime exceptions, and tool-use mistakes are often the most valuable training signal. [Examples](https://github.com/microsoft/Trace/tree/main/examples) [Generated API docs index](https://github.com/microsoft/Trace/tree/main/generated_docs/opto)

Practical rule:

- if the failure teaches the optimizer something, capture it as feedback
- if the failure only indicates bad tracing boundaries or hidden dependencies, fix the structure before continuing

## 6. Prefer narrow, testable trainable methods over whole-program mutation

The paper's framing and the examples both point toward end-to-end optimization, but the most usable engineering pattern is still to keep trainable methods small and semantically coherent. The README examples optimize a focused sorting function and a compact greeting agent instead of turning an entire repository into one trainable object. The examples index also highlights task-shaped workflows such as prompt optimization, game agents, and robotics control rather than unrestricted global mutation. [Trace repository](https://github.com/microsoft/Trace) [Examples](https://github.com/microsoft/Trace/tree/main/examples) [Paper](https://arxiv.org/html/2406.16218v2)

For Python implementations, that usually means:

- one trainable function per distinct responsibility
- one feedback function per objective
- one model boundary per cohesive agent or subsystem

## 7. Choose the optimizer with graph size and update style in mind

The README notes that Trace supports multiple optimizers and describes OptoPrime as the graph-aware default. It also warns that full-graph approaches can run into context pressure on large graphs, while simpler optimizers trade off graph awareness for speed. For code optimization, OptoPrime is the default when the interaction between several trainable components matters, but smaller or more local problems may justify a lighter optimizer. [Trace repository](https://github.com/microsoft/Trace) [Generated API docs index](https://github.com/microsoft/Trace/tree/main/generated_docs/opto)

## 8. Use examples as design templates, not just demos

The supplied examples directory is useful as a pattern library:

- `greeting.py` shows a small `@trace.model` agent with trainable nodes, bundled methods, feedback, and `ExecutionError` handling
- `battleship.py` shows a richer environment where behavior improves from environment feedback
- the README example table points to prompt optimization and robotics cases, which is helpful when deciding whether a code-improvement task is local, agentic, or environment-driven

When helping a user optimize Python implementations, match their task to the closest example pattern first and only then draft custom structure. [Examples](https://github.com/microsoft/Trace/tree/main/examples) [Trace repository](https://github.com/microsoft/Trace)
