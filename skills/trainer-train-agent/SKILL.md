---
name: trainer-train-agent
description: Own the end-to-end trainer loop for agent contract targets (*.agent.md files, custom agent definitions, and agent instruction documents). Use this whenever the caller needs to research, synthesize datasets, optimize, validate, and write back a trained candidate for an agent-type target. Prefer this specialized loop whenever the selected target defines tool routing, MCP skill configuration, agent personas, or handoff behavior rather than raw prompts, code, or skill definitions.
argument-hint: Describe the agent contract file, the repository root, the validation command, the available stage capabilities, the agent's tool and MCP configuration, and any existing workspace artifacts or known failure modes (wrong tool routing, over-broad persona, poor handoff behavior).
license: MIT
compatibility: Python 3.11+. Designed for repositories with GitHub Copilot custom agents or compatible agent frameworks. Works in any repository that keeps trainer artifacts in `.trainer-workspace/` next to the selected target.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Trainer Train - Agent

Use this skill as the orchestration contract for one trainer run against an **agent contract target**: a `*.agent.md` file, custom agent definition, or agent instruction document that configures tool routing, MCP skill invocation, agent personas, or handoff behavior.

Read `references/agent-loop-contract.md` for the full routing table, agent-contract constraints, tool-routing rules, and validation requirements before any stage execution.

## When to use this skill

- The selected target is an agent contract file (`*.agent.md`) or agent instruction document.
- The caller needs to initialize or resume a trainer workspace for an agent target.
- Known failure modes include wrong tool routing, over-broad persona, poor MCP skill invocation, or unbounded handoffs.
- Missing datasets or eval manifests need to be synthesized before optimization.
- A winning candidate needs to be validated and written back to the source agent contract.

Do not use this skill for pure prompt files, Python code targets, or skill files. Read the parent trainer skill's `references/target-routing.md` to identify the appropriate specialist for those target types.

## Required inputs

- One selected agent contract file or agent instruction document.
- Repository root or enough path context to derive the local trainer workspace.
- The validation command for the repository (e.g., `python -m pytest -q`).
- The concrete stage capability map: researcher, synthesizer, optimizer, elector.
- The agent's tool list, MCP skill configuration, and known handoff targets.
- Any existing workspace artifacts or documented failure modes.

## Agent-specific loop rules

### Agent contract concerns

Treat tool routing, persona definition, and handoff behavior as three separate optimization concerns:

- **Tool routing:** The agent should invoke the right tool or MCP skill for each user request. Optimize routing instructions when the agent consistently uses the wrong tool or bypasses available MCP skills.
- **Persona and scope:** The agent's persona should be bounded and consistent. Avoid over-broad system instructions that make the agent attempt tasks outside its intended scope.
- **Handoff behavior:** Agent handoffs should be explicit, bounded, and documented. Optimize handoff instructions when agents hand off incorrectly or in unbounded loops.

### Judge mode

Agent contract targets use **llm_judge** mode by default because agent behavior quality is open-ended. Use `deterministic` mode only for rule-checkable properties (e.g., required YAML fields present, tool list non-empty). Treat an explicit row-level `scoring` declaration as authoritative.

### MCP skill routing audit

Before optimization, identify all MCP skills available to the agent. Confirm the routing instructions for each skill match the skill's `description` field. Mismatches between agent routing instructions and skill descriptions are a primary source of agent failure and should be treated as steering context for the optimizer.

### Prompt bloat control

Agent contracts tend to accumulate broad instructions over time. During optimization:
- Remove instructions that duplicate what the available tools already enforce.
- Prefer explicit routing rules over exhaustive lists of what the agent should or should not do.
- Keep the contract body concise enough that an agent can reason about it during a single context window.

### Handoff bounding

Ensure all agent handoffs are bounded to named, real workspace agents. Flag any handoff instructions that are open-ended or that could cause the agent to recursively invoke itself.

## Core workflow

Follow this order. Consult `references/agent-loop-contract.md` when artifact paths, routing rules, or handoff constraints are uncertain.

1. **Resolve target and workspace.** Derive `<agent-name>` from the selected file by stripping only `.md` (e.g., `researcher.agent.md` → `researcher.agent`). Use `<target-dir>/.trainer-workspace/<agent-name>/` as workspace root. If state indicates a resumed run, audit tracked artifact pointers and skip only stages that already produced valid outputs.
2. **Require the workspace review checkpoint.** Confirm the engineering review artifact exists before optimization starts. Report a blocker if it is absent.
3. **Initialize or refresh workspace.** Create or update `workflow-status.json`, source snapshot, the review subdirectory, `inputs/source/`, and `iterations/` directories.
4. **Audit tool and MCP configuration.** Before optimization, confirm the agent's tool list is correct and that MCP skill routing instructions match the available skill descriptions. Record mismatches as steering context.
5. **Inspect existing datasets and evals.** Prefer reuse when train, validation, and authored eval assets already fit the agent target. Keep authored evals, train data, and validation data as separate artifacts.
6. **Run missing-data path if needed.** If any required dataset or eval is absent, pause optimization and gather them via the caller-supplied researcher and synthesizer.
7. **Infer judge mode.** Default to `llm_judge` for agent targets. Treat explicit row-level `scoring` as authoritative. Stop and report inconsistency if splits imply different modes.
8. **Run at least one optimization pass.** Pass the inferred judge mode, the tool/MCP configuration, and the known failure modes to the optimizer.
9. **Handle manual follow-up if returned.** Save the report as `manual-followup-report.json`, answer the model-facing prompt, persist the candidate artifact, and continue the loop.
10. **Run election if multiple candidates exist.** Use the caller-supplied elector when optimization produces more than one defensible candidate.
11. **Publish iteration artifacts.** Stage steering, candidate bundles, validation logs, and a decision summary under the active iteration directory.
12. **Write back only when validation passes.** Confirm tool routing correctness, handoff bounding, and validation success before writing the winning candidate back to the source agent contract.

## Blocker-first rule

Stop and report a clear blocker before any optimization or rewrite when:

- The workspace review artifact is absent.
- Required datasets or authored evals are missing.
- The agent's tool list or MCP skill configuration cannot be determined from the available context.
- Tracked artifact pointers from a resumed run are missing or inconsistent.

A blocker report must name the missing artifact or configuration gap, explain why the loop cannot advance, and leave `workflow-status.json` in a resumable checkpoint state.

## Output contract

Return:

1. Workspace status and any active blockers.
2. Current-turn decisions: optimization focus (routing, persona, handoff), judge mode, selected branch, blockers.
3. Tool and MCP routing audit results.
4. Optimization or manual follow-up status with artifact paths.
5. Validation status.
6. Write-back decision and justification.
7. Next required action to resume or continue the loop.
