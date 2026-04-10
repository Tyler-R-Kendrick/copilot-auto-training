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
- The user wants to run the same eval against two different targets or models to compare performance.

Do not use this skill for general prompt engineering unrelated to evaluations, or for creating and improving agent skill SKILL.md files and their structure.

## Quickstart

```bash
# Install
npm install -g agentv

# Initialize project
agentv init

# Run an eval
agentv eval evals/my-skill.eval.yaml

# Run with a specific target
agentv eval evals/my-skill.eval.yaml --target claude

# Output formats
agentv eval evals/my.yaml -o report.html    # HTML dashboard
agentv eval evals/my.yaml -o results.xml    # JUnit XML for CI
agentv eval evals/my.yaml -o results.jsonl  # JSONL (default)

# Compare two runs
agentv compare .agentv/results/runs/<run-1>/index.jsonl .agentv/results/runs/<run-2>/index.jsonl
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
| `evals[].expected_output` | `tests[].expected_output` (preserved) and informs `tests[].criteria` |
| `evals[].assertions[]` | `tests[].rubrics[]` (string) or `tests[].assert[]` (typed) |

> **Note on `expected_output` mapping:** In `evals.json`, `expected_output` is a single string used as the reference answer. In EVAL.yaml, `tests[].expected_output` preserves this reference answer exactly, while `tests[].criteria` is a *separate* natural-language description of what counts as success. They serve different roles — do not replace one with the other.

String-only assertions in `evals.json` become `rubrics` (string format) or `llm-grader` assertions in EVAL.yaml. Preserve both `evals.json` and `EVAL.yaml` — the JSON is used by the internal evaluation framework; the YAML is used by AgentV.

## EVAL.yaml minimal example

```yaml
name: my-skill
description: Evaluates my-skill behavior

execution:
  target: default

assert:
  - type: llm-grader
    prompt: ./graders/quality.md
    threshold: 0.7

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

For programmatic checks, `code-grader` runs a script that receives the agent's answer (as plain text) on stdin and must exit 0 to pass:

```yaml
assert:
  - type: code-grader
    command: python ./graders/check_output.py
    required: true
```

For subjective quality checks, `llm-grader` assertions reference a markdown file with the judge prompt:

```yaml
assert:
  - type: llm-grader
    prompt: ./graders/correctness.md
    threshold: 0.7    # Per-assertion minimum score (0.0–1.0)
```

**Writing judge prompts** — use these template variables inside the markdown file:

| Variable | Description |
|----------|-------------|
| `{{answer}}` | The agent's actual response |
| `{{expected_output}}` | The expected output from the test case |
| `{{input}}` | The original prompt sent to the agent |
| `{{criteria}}` | The test case `criteria` field |

**Example judge prompt (`graders/correctness.md`):**

```markdown
You are evaluating whether an AI agent response meets the required criteria.

## Task criteria
{{criteria}}

## Agent response
{{answer}}

## Expected output
{{expected_output}}

Score 0.0–1.0, where 1.0 = fully meets all criteria. Reply with JSON only:
{"score": 0.9, "reasoning": "Brief explanation of the score"}
```

**Threshold vs. `--threshold`:** The `threshold` field on an `llm-grader` assertion is per-assertion (minimum score to pass). The `--threshold` CLI flag sets a minimum overall suite pass rate for CI gating. These are independent.

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

## Set up targets

Configure `.agentv/targets.yaml` to point to your agent. Run `agentv init` to create a starter file.

```yaml
# .agentv/targets.yaml
default:
  type: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}   # Use env vars — never hardcode keys

claude:
  type: anthropic
  model: claude-opus-4-5
  api_key: ${ANTHROPIC_API_KEY}
```

Read `references/targets.md` for all target types (OpenAI, Anthropic, local CLI, HTTP endpoints).

### Multi-target comparison

Run the same eval suite against two targets to compare performance:

```bash
# Run against each target
agentv eval evals/my-skill.eval.yaml --target default
agentv eval evals/my-skill.eval.yaml --target claude

# Compare the two runs
agentv compare .agentv/results/runs/*/index.jsonl
```

## CI/CD integration

Set the API key as a repository secret and inject it into the environment:

```yaml
# GitHub Actions
- name: Run evals
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: agentv eval evals/*.yaml
```

```bash
# Run with exit code on failures (for CI gates)
agentv eval evals/*.yaml --exit-on-failure

# JUnit output for GitHub Actions / Jenkins
agentv eval evals/*.yaml -o results.xml

# Threshold gate: fail if pass rate drops below 80%
agentv eval evals/*.yaml --threshold 0.8
```

`agentv eval` exits with a non-zero exit code when `--exit-on-failure` is set and any test fails, or when the pass rate falls below the `--threshold` value. This makes it suitable as a CI gate step.

## Comparing runs

```bash
# After two runs, compare results
agentv compare .agentv/results/runs/run-1/index.jsonl .agentv/results/runs/run-2/index.jsonl

# Compare latest two runs automatically (ordered by run directory timestamp)
agentv compare --last 2
```

**Sample comparison output:**

```
Comparison: run-1 vs run-2
────────────────────────────────────────
Test                  run-1   run-2   Δ
────────────────────────────────────────
detect-off-by-one     pass    pass    =
no-bug-present        fail    pass    ↑
security-vuln         pass    pass    =
────────────────────────────────────────
Pass rate             66.7%   100%    +33.3%
```

Improvements (↑) and regressions (↓) are highlighted. Use this to verify a skill change improves eval quality without introducing regressions.

## Debugging failing evaluations

When a test case fails — especially with `llm-grader` giving unexpectedly low scores — follow these steps:

1. **Inspect the JSONL results** at `.agentv/results/runs/<timestamp>/index.jsonl`. Each test result includes:
   - `pass` — boolean pass/fail for the overall test
   - `score` — numeric score from the LLM grader (0.0–1.0)
   - `reasoning` — the judge's explanation for the score
   - `assertions` — per-assertion breakdown showing which checks passed or failed

2. **Improve the judge prompt** — if the reasoning reveals the judge is misinterpreting the criteria, edit the referenced markdown file (e.g., `./graders/correctness.md`) to add clearer instructions or examples, then re-run.

3. **Adjust the threshold** — if scores are consistently in a borderline range (e.g., 0.65 when threshold is 0.7), decide whether to lower the `threshold` on the assertion or improve the prompt to score higher.

4. **Distinguish per-assertion vs. suite threshold:**
   - `threshold` on an `llm-grader` assertion: minimum score for that single assertion to pass (default: 0.5)
   - `--threshold 0.8` CLI flag: minimum fraction of tests that must pass for the suite to exit 0

5. **Handle non-deterministic scores** — LLM graders can return different scores across runs due to temperature. If a test flips between pass and fail on re-runs, lower the judge model's temperature to `0.0` in `.agentv/targets.yaml`, widen the threshold margin (e.g., use `0.6` instead of `0.7`), or adjust your judge prompt to produce more decisive scores.

```bash
# Re-run a single file to iterate quickly
agentv eval evals/my-skill.eval.yaml -o debug.jsonl
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
