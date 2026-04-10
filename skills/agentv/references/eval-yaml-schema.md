# EVAL.yaml Schema Reference

Complete reference for the AgentEvals EVAL.yaml format, as implemented by the AgentV CLI.

Source: [AgentEvals specification](https://github.com/agentevals/agentevals) | [AgentV docs](https://agentv.dev/docs/)

---

## Top-level structure

```yaml
name: my-eval               # Required: unique identifier for this eval suite
version: "1.0"              # Optional: version string
description: ...            # Optional: human-readable description
metadata:                   # Optional: arbitrary metadata
  author: username
  tags: [quality, regression]
  license: MIT

execution:                  # Optional: default execution settings
  target: default           # Which target from targets.yaml to use
  timeout_seconds: 60       # Per-test timeout (default: 30)

assert:                     # Optional: suite-level assertions applied to all tests
  - type: contains
    value: "expected"

tests:                      # Required: array of test cases
  - id: my-test
    ...
```

---

## Test case fields

Each entry in `tests:` supports:

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique string identifier for this test |
| `criteria` | Recommended | Natural language description of what counts as success |
| `input` | Yes | The prompt or messages sent to the agent (string or message array) |
| `expected_output` | No | Expected agent response (used by some evaluators) |
| `assert` | No | Per-test assertions (merged with suite-level `assert`) |
| `rubrics` | No | Structured grading rubrics |
| `description` | No | Additional context for this test |
| `metadata` | No | Custom tags, IDs, or labels |

### Simple string input

```yaml
tests:
  - id: addition
    criteria: Correctly calculates 15 + 27 = 42
    input: What is 15 + 27?
    expected_output: "42"
```

### Message array input (multi-turn)

```yaml
tests:
  - id: multi-turn
    criteria: Maintains context across turns
    input:
      - role: user
        content: My name is Alice.
      - role: assistant
        content: Nice to meet you, Alice!
      - role: user
        content: What is my name?
```

### File input

```yaml
tests:
  - id: document-summary
    criteria: Summarizes the document accurately
    input:
      - role: user
        content:
          - type: text
            text: "Please summarize this document:"
          - type: file
            path: ./fixtures/document.txt
```

---

## Assertion types

### Deterministic assertions

Fast, code-based checks that do not call an LLM:

```yaml
assert:
  - type: contains          # Output contains substring
    value: "expected text"
    case_sensitive: false   # Optional, default: true

  - type: equals            # Exact match
    value: "exact response"

  - type: regex             # Regular expression match
    pattern: "\\d{4}-\\d{2}-\\d{2}"  # Matches a date

  - type: is-json           # Output is valid JSON
    required: true          # Fail test if this assertion fails
    schema: ./schema.json   # Optional: validate against JSON Schema

  - type: json-contains     # JSON output has a specific field/value
    path: "$.status"
    value: "success"
```

### LLM-based graders

Use an LLM to judge subjective quality. Reference a markdown file with the judge prompt:

```yaml
assert:
  - type: llm-grader
    prompt: ./graders/correctness.md    # Path to markdown judge prompt
    threshold: 0.7                       # Score threshold (0.0–1.0), default: 0.5
    model: gpt-4o                        # Optional: override the default judge model

  - type: llm-judge                      # Alias for llm-grader
    prompt: ./graders/quality.md
```

**Example judge prompt (`graders/correctness.md`):**

```markdown
You are evaluating whether an AI agent correctly answered a question.

## Criteria
- The answer is factually correct
- The answer directly addresses the question
- The answer is appropriately concise

## Response to evaluate
{{answer}}

## Expected output
{{expected_output}}

Score from 0.0 to 1.0, where 1.0 means perfect. Respond with JSON: {"score": 0.9, "reasoning": "..."}
```

### Code graders

Run a script to evaluate output programmatically:

```yaml
assert:
  - type: code-grader
    command: python ./graders/check_syntax.py
    # Script receives the agent's answer (plain text) via stdin; exit 0 = pass, nonzero = fail

  - type: code-grader
    command: bun ./graders/validate.ts
    required: true
```

---

## Rubrics

Rubrics enable structured, weighted grading with optional score ranges. Good for complex quality criteria.

```yaml
tests:
  - id: essay-quality
    input: Write a paragraph about climate change
    rubrics:
      # Simple string rubric
      - The response mentions at least two specific impacts of climate change

      # Structured rubric
      - id: factuality
        outcome: All facts stated are accurate
        weight: 2            # Higher weight = more impact on final score
        required: true       # Fail test if this rubric is not met
        score_ranges:
          0: Contains factual errors
          5: Minor inaccuracies
          10: Fully accurate

      - id: clarity
        outcome: The response is clear and well-organized
        weight: 1
        score_ranges:
          0: Confusing or unorganized
          5: Somewhat clear
          10: Clear and well-structured
```

---

## Execution configuration

```yaml
execution:
  target: default              # Target from .agentv/targets.yaml (default: "default")
  timeout_seconds: 60          # Per-test timeout
  max_retries: 2               # Retry failed tests up to N times
  concurrency: 4               # Parallel test execution (default: 1)
  before_all: ./setup.sh       # Script to run before all tests
  after_all: ./teardown.sh     # Script to run after all tests
```

---

## Output formats

| Flag | Format | Use case |
|------|--------|----------|
| (none) | JSONL | Default, machine-readable |
| `-o report.html` | HTML | Visual dashboard with pass/fail breakdown |
| `-o results.xml` | JUnit XML | CI/CD integration (GitHub Actions, Jenkins) |
| `-o results.jsonl` | JSONL | Explicit JSONL output |

---

## Full example

```yaml
name: code-review-skill
version: "1.0"
description: Evaluates code review skill quality across bug types

execution:
  target: default
  timeout_seconds: 90

assert:
  - type: is-json
    required: false

tests:
  - id: off-by-one-detection
    criteria: Detects off-by-one error in loop condition
    input:
      - role: user
        content: "Review this code for bugs:\n```python\nfor i in range(0, len(items)):\n    print(items[i+1])\n```"
    rubrics:
      - The response identifies the off-by-one error
      - The response explains why `items[i+1]` is problematic
      - id: fix-provided
        outcome: A correct fix is provided
        required: true

  - id: no-bug-present
    criteria: Does not invent bugs in correct code
    input:
      - role: user
        content: "Review this code:\n```python\nresult = sum(x for x in items if x > 0)\n```"
    rubrics:
      - The response does not claim there are bugs
      - The response acknowledges the code is correct

  - id: security-vulnerability
    criteria: Identifies SQL injection risk
    input: "Review this for security issues: `query = f'SELECT * FROM users WHERE name = {user_input}'`"
    assert:
      - type: contains
        value: "injection"
        case_sensitive: false
    rubrics:
      - The response identifies SQL injection risk
      - id: mitigation
        outcome: A mitigation or fix is suggested
        required: true
        weight: 2
```
