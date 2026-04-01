---
name: learn
description: Capture user corrections and reusable lessons from the active conversation, then update the right persistent artifact so the same mistake is less likely to happen again. Use this whenever the user wants a fix reflected in agent memory, `.agents/MEMORY.md`, instruction files, custom agents, skills, `AGENTS.md`, hooks, docs, evals, or tests instead of only in the current answer.
argument-hint: Describe the correction, where it was discovered, whether agent memory is available, and which persistent repo surfaces may need to be created, modified, or optimized.
license: MIT
compatibility: Works best in repositories that keep durable guidance in instruction files, skill contracts, tests, and docs.
metadata:
  author: Tyler Kendrick
  version: "0.1.0"
---

# Learn

Use this skill to turn a user correction or repeated lesson from the current conversation into a durable repository update.

The point is not to merely apologize and move on. The point is to notice what changed, decide whether it is a reusable rule, and encode that learning in the smallest authoritative place so future runs are less likely to repeat the mistake.

Read `references/learning-targets.md` before making broad edits when the lesson might belong in more than one place.

## When to use this skill

- The user corrects your workflow and wants the correction applied going forward.
- The user says a mistake should not happen again.
- The user says "remember this", "learn from this", "use this going forward", or similar.
- The user introduces a new requirement that should be reflected in durable guidance.
- The user points out a recurring failure pattern across prompts, instructions, docs, or tests.
- The user wants repository guidance updated to match what was learned in the active conversation.

Do not use this skill for one-off stylistic preferences, ephemeral debugging notes, or corrections that are too narrow to generalize safely. In those cases, apply the correction locally without hard-coding it into durable repository guidance.

## Core workflow

Follow this order:

1. Identify the exact correction, learning, or newly stated requirement.
2. Decide whether it is reusable enough to encode.
3. Choose the smallest authoritative file or files that should carry the rule.
4. Update those files so the guidance is explicit, actionable, and easy to follow.
5. Add or adjust tests or evals when they are the best guardrail against regression.
6. Validate that the updated guidance matches the user's correction without overfitting to one example.

## Generalization test

Before editing durable guidance, check all of these:

- Would this lesson help on future tasks beyond the current example?
- Is there a clear source-of-truth file where this belongs?
- Can the rule be written as a reusable behavior instead of a brittle anecdote?
- Would encoding this lesson create conflicts with broader repository conventions?

If the answer is mostly no, keep the fix local and explain why you did not expand it into repository-wide guidance.

## Choosing update targets

Prefer the narrowest source of truth that can prevent the mistake:

- Update a task-specific instruction file when the lesson applies only to one workflow or file family.
- Update a skill contract when the lesson should change how that skill behaves.
- Update docs or examples when future contributors need discoverable guidance.
- Update evals or tests when the lesson is objective enough to verify automatically.

Avoid duplicating the same rule across many files unless multiple surfaces truly need it for discoverability or enforcement.

## Persistent artifacts and capabilities

When deciding where the learning should live, use this order of preference:

1. Use agent memory when it is available and the learning is a stable, cross-task fact that should be recalled without editing repository files.
2. If agent memory is unavailable or the repo needs a durable file-backed record, create or update `.agents/MEMORY.md` with concise, reusable facts rather than one-off task notes.
3. Update Copilot agent instructions or other file-based instructions when the lesson should change default behavior for a broad class of tasks or files.
4. Create or update a Copilot Custom Agent in `.github/agents/` when the repo needs a persistent specialist role, handoff contract, or multi-step workflow owner.
5. Create or update an agent skill under `skills/` when the lesson defines a reusable capability, decision process, or invocation pattern. If a specific task keeps failing because the instructions are faulty or incomplete, prefer creating or tightening an agent skill instead of bloating global instructions.
6. Update `AGENTS.md` when the lesson should be visible as repository-wide operating guidance for agents and contributors, especially when the rule is broader than one skill but does not need a dedicated custom agent.
7. Create or update Copilot Hooks under `.github/hooks/` when the learning should be enforced, reminded, or validated deterministically at write time or tool-use time.

## How to choose the right surface

Use these heuristics:

- **Agent memory or `.agents/MEMORY.md`**: stable facts, conventions, commands, or preferences that should survive across tasks but do not require a rich workflow contract.
- **Copilot agent instructions / file-based instructions**: global or file-pattern-specific guidance that changes how the agent should behave by default while editing certain files or working in the repo.
- **Copilot Custom Agents**: named specialists with role boundaries, handoffs, or orchestration responsibilities that should be discoverable as agents rather than ad hoc prompt text.
- **Agent skills**: reusable workflows or capabilities that should trigger on demand. Use this especially when a repeated task is under-specified, keeps failing, or needs a stronger contract than generic instructions.
- **`AGENTS.md`**: broad repository operating guidance, team conventions, or agent-facing expectations that should remain human-readable and easy to discover from the repo root.
- **Copilot Hooks**: deterministic checks, reminders, sync steps, or policy enforcement that should run automatically instead of relying on the model to remember.

If more than one surface could work, prefer the one that is both closest to the failure and easiest to validate automatically.

## Create, modify, or optimize

When applying a learning, decide whether the target needs creation, revision, or optimization:

- **Create** a new file or capability when no existing surface owns the behavior and the lesson is likely to recur.
- **Modify** an existing instruction file, custom agent, skill, `AGENTS.md`, or hook when the repository already has a clear owner for that behavior.
- **Optimize** an existing skill or custom agent when the right surface already exists but its description, trigger conditions, examples, or workflow steps are too weak to fire reliably.

When a single task is failing because the instructions are faulty or incomplete, do not keep patching the same correction into unrelated prompts. Either tighten the owning instruction file or create an agent skill that makes the capability explicit and reusable.

## Editing guidance

When you encode a learning:

- Restate the user's correction in neutral, reusable language.
- Explain the behavior change, not just the symptom.
- Preserve existing placeholders, interfaces, and repository conventions.
- Keep the update proportional to the lesson.
- Connect the rule to validation when a regression test is practical.
- Name the chosen persistent artifact explicitly so future readers know why that surface was selected.

If several files are candidates, update the authoritative one first and only add supporting documentation where it reduces future confusion.

## Output contract

When using this skill, structure the result like this unless the user asks for something shorter:

1. `Learning captured`: the correction or lesson from the active conversation
2. `Generalized rule`: the durable behavior that should change
3. `Targets updated`: the instructions, skills, docs, evals, or tests that were changed and why
4. `Validation`: how you checked that the learning was applied correctly
5. `Open edges`: any part of the lesson that should stay local rather than being codified broadly
