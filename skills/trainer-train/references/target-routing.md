# Target-Type Routing

Read this reference to identify the right specialist training loop for the selected target before running the generic trainer-train loop.

## Routing table

| Target type | Specialist skill | Reference |
|-------------|-----------------|-----------|
| `*.prompt.md`, `*.prompty`, `*.instructions.md`, system prompts | trainer-train-prompt | `references/trainer-train-prompt.md` |
| Python files (`*.py`) optimized with Microsoft Trace | trainer-train-code | `references/trainer-train-code.md` |
| `SKILL.md` files (agentskills.io spec) | trainer-train-skill | `references/trainer-train-skill.md` |
| `*.agent.md`, agent contracts | trainer-train-agent | `references/trainer-train-agent.md` |

## When to bypass delegation

Use the generic trainer-train loop directly only when:
- The target does not match any of the four specialist categories above.
- The caller explicitly bypasses delegation for a known reason.
- The specialist skill is unavailable in the current environment.

## Delegation contract

Each specialist skill owns the target-specific workspace rules, judge-mode defaults, and write-back constraints for its domain. The specialist uses the same workspace layout, stage sequencing, and collaboration rules defined in the trainer-train loop — it adds only the target-specific constraints (e.g., placeholder preservation for prompts, spec compliance for skills, tool routing audit for agents).
