---
name: agentv
description: Create, run, and manage AgentV evaluations for AI agents and skills using the AgentV CLI and AgentEvals standard EVAL.yaml format. Use this skill whenever the user wants to write evaluation files for AI agents, run evals with agentv CLI, convert existing test cases to EVAL.yaml, set up eval targets, understand the AgentEvals specification, debug failing evaluations, integrate evals into CI/CD pipelines, or compare agent runs with `agentv compare`. Also use this when the user mentions EVAL.yaml, agentevals, agentv, or wants to evaluate skill quality with a declarative format.
license: MIT
compatibility: Requires Node.js 18+ with `agentv` globally installed (`npm install -g agentv`). Supports any agent target — Claude, Codex, Copilot, local CLI scripts, or OpenAI-compatible providers.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# AgentV Skill

Use this skill to author, run, and manage evaluations for AI agents and skills using the [AgentV CLI](https://agentv.dev) and the [AgentEvals](https://github.com/agentevals/agentevals) declarative YAML standard.

Read `references/eval-yaml-schema.md` for the complete EVAL.yaml schema reference before authoring new eval files.
Read `references/targets.md` for target configuration options.

## When to use this skill

- The user wants to write `EVAL.yaml` evaluation files for a skill or agent.
- The user wants to run evals with `agentv eval`.
- The user wants to convert existing test cases (e.g., `evals.json`) to EVAL.yaml format.
- The user wants to understand the AgentEvals specification or schema.
- The user wants to set up or update `.agentv/targets.yaml`.
- The user wants to run `agentv compare` to detect regressions across runs.
- The user wants to integrate AgentV into a CI/CD pipeline.
- The user wants to write LLM judges, rubrics, or code graders for evaluation.

Do not use this skill for general prompt engineering unrelated to evaluations, or for creating and improving agent skill SKILL.md files and their structure.

## Quickstart

```bash
# Install
npm install -g agentv

# Initialize project
agentv init

# Run an eval
agentv eval evals/my-skill.eval.yaml

# Compare runs
agentv compare .agentv/results/runs/<timestamp>/index.jsonl

# Output formats
agentv eval evals/my.yaml -o report.html    # HTML dashboard
agentv eval evals/my.yaml -o results.xml    # JUnit XML for CI
agentv eval evals/my.yaml -o results.jsonl  # JSONL (default)
```

## Core workflow

Follow this order when creating or updating evals:

1. **Understand the skill/agent** — what does it do, what inputs does it accept, what outputs should it produce?
2. **Set up the target** — configure `.agentv/targets.yaml` to point to the agent being evaluated.
3. **Author the EVAL.yaml** — write test cases with inputs, expected outputs, and assertions.
4. **Add evaluators** — choose deterministic assertions (`contains`, `equals`, `regex`, `is-json`) or LLM judges for subjective quality.
5. **Run and inspect** — `agentv eval` produces JSONL output; use `--output report.html` for a visual dashboard.
6. **Iterate** — improve the skill based on failing tests and re-run.

## Converting evals.json to EVAL.yaml

When migrating an existing `evals/evals.json` file, map the fields as follows:

| evals.json field | EVAL.yaml field |
|------------------|-----------------|
| `skill_name` | `name` (top-level) |
| `evals[].id` | `tests[].id` |
| `evals[].prompt` | `tests[].input` |
| `evals[].expected_output` | `tests[].criteria` |
| `evals[].assertions[]` | `tests[].rubrics[]` or `tests[].assert[]` |

String-only assertions in `evals.json` become `rubrics` (string format) or `llm-grader` assertions in EVAL.yaml. Preserve both `evals.json` and `EVAL.yaml` — the JSON is used by the internal evaluation framework; the YAML is used by AgentV.

## EVAL.yaml minimal example

```yaml
name: my-skill
description: Evaluates my-skill behavior

execution:
  target: default

tests:
  - id: basic-task
    criteria: Correctly handles the basic task
    input: Do the thing I asked for
    expected_output: The expected result
    rubrics:
      - The output is complete
      - The output is correctly formatted
```

## Evaluator types

| Type | Use case |
|------|----------|
| `contains` | Output includes a specific string |
| `equals` | Exact match |
| `regex` | Output matches a regular expression |
| `is-json` | Output is valid JSON |
| `llm-grader` | Subjective quality via a markdown judge prompt |
| `code-grader` | Custom logic in Python/TypeScript/shell |
| `rubric` | Structured criteria with optional weights and score ranges |

For subjective quality checks, `llm-grader` assertions reference a markdown file with the judge prompt:

```yaml
assert:
  - type: llm-grader
    prompt: ./graders/correctness.md
    threshold: 0.7
```

## Rubrics

Use rubrics when you need weighted or structured grading criteria:

```yaml
rubrics:
  - id: completeness
    outcome: Response addresses all parts of the request
    weight: 2
    required: true
  - id: quality
    outcome: Response is clear and well-structured
    weight: 1
    score_ranges:
      0: Unreadable or missing
      5: Partially addressed
      10: Complete and clear
```

## Suite-level assertions

Use top-level `assert:` to apply evaluators to all test cases:

```yaml
assert:
  - type: is-json          # All responses must be valid JSON
  - type: llm-grader
    prompt: ./graders/quality.md

tests:
  - id: test-1
    input: ...
    assert:
      - type: contains     # Per-test assertion (merged with suite-level)
        value: "status"
```

## File references

Test inputs and judge prompts can reference files:

```yaml
tests:
  - id: file-input-test
    input:
      - role: user
        content:
          - type: file
            path: ./fixtures/sample.txt
    criteria: Correctly processes the document
```

## CI/CD integration

```bash
# Run with exit code on failures (for CI gates)
agentv eval evals/*.yaml --exit-on-failure

# JUnit output for GitHub Actions / Jenkins
agentv eval evals/*.yaml -o results.xml

# Threshold gate: fail if pass rate drops below 80%
agentv eval evals/*.yaml --threshold 0.8
```

## Comparing runs

```bash
# After two runs, compare results
agentv compare .agentv/results/runs/run-1/index.jsonl .agentv/results/runs/run-2/index.jsonl

# Compare latest two runs automatically
agentv compare --last 2
```

## Project structure

```
project/
├── evals/
│   ├── my-skill.eval.yaml      # AgentV eval definitions
│   └── graders/                # LLM judge markdown prompts
│       └── correctness.md
├── .agentv/
│   ├── targets.yaml            # Agent/model targets
│   └── results/                # Run outputs (JSONL)
└── ...
```

## Skills integration pattern

When evaluating skills in this repository, each skill keeps both formats:

```
skills/my-skill/
└── evals/
    ├── evals.json       # Internal eval framework format
    └── EVAL.yaml        # AgentV-compatible format
```

Both files cover the same test cases. `evals.json` drives the internal skill-creator benchmarking workflow; `EVAL.yaml` enables `agentv eval` CLI execution and CI integration.
