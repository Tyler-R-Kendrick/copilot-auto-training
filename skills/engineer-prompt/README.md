# Engineer Prompt

Apply DSPy to prompt and instruction artifacts by choosing the smallest trainable prompt surface, compiling it with a DSPy optimizer, and exporting a stable Markdown artifact. Use this whenever the user wants DSPy, prompt-as-code optimization, MIPROv2, instruction-only optimization, or deterministic prompt artifact export.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- The user wants to apply DSPy to a prompt, instruction file, or agent skill artifact.
- The user wants to decide what should become a `dspy.Signature` or `dspy.Module`.
- The user wants to choose between instruction-only optimization and demo-heavy optimization.
- The user wants to export optimized prompt content into a stable checked-in Markdown artifact.
- The user wants help designing metrics or evals for DSPy-driven prompt optimization.

Do not use this skill when the core problem is clearly retrieval freshness, tool availability, source quality, missing requirements, or generic runtime performance rather than prompt optimization. In those cases, say DSPy is secondary.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
