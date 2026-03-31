# Trajectory Judging

Evaluate agent trajectories, tool-use traces, intermediate artifacts, runtime failures, and side effects when process quality is part of the verdict. Use this whenever the judging task involves agent runs, tool calls, planning quality, web or code traces, process reliability, or any comparison where the final answer alone is not enough, even if the user only says judge the run, compare traces, or evaluate the agent workflow.

## Canonical files

- [SKILL.md](SKILL.md): canonical skill contract and invocation guidance.
- [evals/evals.json](evals/evals.json): official authored evaluation manifest for the skill.
- [references/](references/): background material, source notes, and supporting guidance.
- [assets/](assets/): templates, examples, or supporting artifacts.
- [scripts/](scripts/): runtime helpers or implementation details. See [scripts/README.md](scripts/README.md).

## When to use

- Agent-run evaluation where trajectories, tool traces, or intermediate artifacts matter.
- Web, code, RAG, or tool-use comparisons where process reliability is part of the verdict.
- Candidate comparisons where runtime failures, evidence-gathering quality, or side effects should influence the score.

Do not use this skill alone for clean outcome-only response comparison. In those cases, switch to an outcome-focused judging contract instead.

## Inputs

- Candidate trajectories, tool traces, transcripts, failure logs, or intermediate artifacts.
- The baseline trajectory when available.
- Any task contract, `reference`, `criteria`, benchmark notes, or end-state artifacts needed to judge whether the process achieved the right goal.
- Outcome artifacts when the verdict needs both process and end-state quality.

## Repository context

- Return to the [root README](../../README.md) for repository-level installation, workflow setup, and plugin usage.
- Treat [SKILL.md](SKILL.md) as the authoritative contract when the README summary and the skill prompt diverge.
