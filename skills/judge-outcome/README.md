# Outcome Judging

Evaluate final outputs, response pairs, scored artifacts, or benchmark-style answer quality without relying on full trajectories. Use this whenever the judging task is mainly about end-state quality, final answer comparison, reference-plus-criteria scoring, or choosing the best output among candidates, even if the user only says compare responses, pick the best answer, or judge the final result.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts.
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- Final-output judging, pairwise response comparison, or benchmark-style answer ranking.
- Cases where `reference`, `criteria`, or explicit outcome artifacts matter more than the full process trace.
- Prompt-candidate comparisons where the decisive evidence is the quality of the final answer, final file, or end-state response.

Do not use this skill as the only judging contract when tool traces, side effects, runtime failures, or intermediate artifacts are central to the verdict. In those cases, switch to a process-aware judging contract instead.

## Inputs

- The candidate outputs or candidate prompts being compared.
- The baseline output or baseline prompt when available.
- Any task contract, `reference`, `criteria`, or benchmark notes that define what success looks like.
- Outcome-facing artifacts such as final responses, generated files, benchmark summaries, or validation results.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
