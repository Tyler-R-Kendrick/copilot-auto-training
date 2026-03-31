# Engineer Prompt

Improve broken prompts and context plans by choosing the smallest prompt-engineering technique that fits. Use this whenever the user asks how to rewrite or debug a prompt, compare prompt-design options, choose between grounding, structured output, examples, chaining, reasoning, or RAG for a prompt, or reduce prompt length by moving schemas, workflow specs, and repeated instructions into better structures.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts. See [assets/README.md](assets/README.md).
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- The user wants to improve a prompt.
- The user asks which prompt engineering technique to use.
- The user wants to compare multiple prompt patterns or prompting families.
- The user needs a concrete markdown prompt example.
- The user wants to debug why a prompt is underperforming.
- The user mentions grounding, examples, output schemas, reasoning style, prompt chaining, RAG, or determinism and needs help choosing among them.
- The user wants to reduce prompt length without losing critical instructions, or wants help placing schemas, workflow specs, or repeated constraints more effectively.

Do not use this skill when the core problem is clearly application logic, retrieval freshness, source quality, tool availability, or missing product requirements rather than prompt design. In those cases, say that prompt changes are secondary.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
