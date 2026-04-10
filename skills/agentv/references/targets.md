# AgentV Targets Configuration Reference

Targets define which AI agent or LLM provider AgentV will send test inputs to during evaluation.
Configuration lives in `.agentv/targets.yaml` at the project root.

---

## File location

```
project/
└── .agentv/
    └── targets.yaml
```

Initialize with: `agentv init` (creates a starter `targets.yaml`).

---

## Target types

### OpenAI-compatible (default)

```yaml
default:
  type: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}   # Use env var references for secrets
  base_url: https://api.openai.com/v1  # Optional: override for Azure or proxies
  temperature: 0.0              # Optional: deterministic output for evals
  max_tokens: 2048              # Optional
```

### Anthropic Claude

```yaml
claude:
  type: anthropic
  model: claude-opus-4-5
  api_key: ${ANTHROPIC_API_KEY}
  temperature: 0.0
```

### Azure OpenAI

```yaml
azure-gpt4:
  type: openai
  model: gpt-4o
  api_key: ${AZURE_OPENAI_KEY}
  base_url: https://my-resource.openai.azure.com/openai/deployments/my-deployment
```

### Local CLI agent

Use for any agent that reads from stdin and writes to stdout:

```yaml
local-agent:
  type: cli
  command: python
  args: [./agent.py, --mode, eval]
  env:
    AGENT_CONFIG: ./config.json
  timeout_seconds: 120
```

### GitHub Copilot agent

```yaml
copilot:
  type: copilot
  model: gpt-4o
  token: ${GITHUB_TOKEN}
```

### Custom HTTP endpoint

```yaml
my-api:
  type: http
  url: https://my-api.example.com/chat
  headers:
    Authorization: Bearer ${MY_API_KEY}
    Content-Type: application/json
  method: POST
  body_template: |
    {"message": "{{input}}", "model": "my-model"}
```

---

## Using targets in EVAL.yaml

Reference targets by name in the `execution.target` field:

```yaml
execution:
  target: claude       # Uses the 'claude' target from targets.yaml

tests:
  - id: test-1
    input: Hello!
```

Or override per-test (advanced):

```yaml
tests:
  - id: comparison
    input: Write FizzBuzz
    execution:
      target: azure-gpt4
```

---

## Multiple targets (benchmarking)

Run the same evals against multiple targets to compare performance:

```bash
agentv eval evals/my.yaml --target default
agentv eval evals/my.yaml --target claude
agentv compare .agentv/results/runs/*/index.jsonl
```

---

## Environment variables

Always use `${VAR_NAME}` syntax for secrets — never hardcode API keys in `targets.yaml`.
Set variables in `.env` (gitignored) or in your CI/CD environment.

```yaml
default:
  type: openai
  api_key: ${OPENAI_API_KEY}
  model: ${EVAL_MODEL:-gpt-4o}   # With fallback default
```

---

## AgentV initialization

```bash
# Creates .agentv/targets.yaml with a starter config
agentv init

# Validate that targets are reachable
agentv targets list
agentv targets test default
```
