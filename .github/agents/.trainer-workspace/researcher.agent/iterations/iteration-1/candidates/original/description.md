# Original Candidate

This is the original `researcher.agent.md` before optimization.

## Known Issues (from engineer-prompt review)

1. Skill activation step deferred to step 2 (after "Read the target file" in step 1)
2. `run_agent_skill` condition is ambiguous ("only when skill exposes deterministic helper")
3. No explicit no-op path for pre-supplied source materials
4. "DO NOT involve any other agents" is ambiguous about search/read tools
5. Non-interactive gap reporting not specified (defaulting to asking questions)

## Predicted Judge Response

The original scores lower on:
- MCP skill activation compliance (step ordering)
- Non-interactive context handling
- Pre-supplied materials recognition
