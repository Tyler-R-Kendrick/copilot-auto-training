# Optimize Blocker

## Stage

- Skill: `trainer-optimize`
- Invocation path: agent-skills MCP `run_agent_skill`
- Script: `skills/trainer-optimize/scripts/run_optimize.py`

## Result

- Exit code: `1`
- Candidate written: no
- Source prompt updated: no

## stderr

```text
Traceback (most recent call last):
  File "/workspaces/copilot-apo/skills/trainer-optimize/scripts/run_optimize.py", line 15, in <module>
    from opto import trace
ModuleNotFoundError: No module named 'opto'
```

## Diagnosis

- The repository virtual environment does contain `opto`.
- The failure is specific to the interpreter used by the MCP skill runner, not the repo's configured `.venv`.
- Because the optimize stage never reached rollout execution, this is an environment blocker rather than evidence that the prompt or datasets performed poorly.