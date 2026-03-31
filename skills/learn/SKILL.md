---
name: learn
description: Capture user corrections and reusable lessons from the active conversation, then update the most relevant instructions, skills, docs, evals, or tests so the same mistake is less likely to happen again. Make sure to use this whenever the user corrects your workflow, says "remember this", "learn from this", or "don't do this again", asks you to apply a new requirement broadly, or wants today's fix reflected in repository guidance instead of only in the current answer.
argument-hint: Describe the correction, where it was discovered, what future behavior should change, and which repo surfaces may need updates.
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

## Editing guidance

When you encode a learning:

- Restate the user's correction in neutral, reusable language.
- Explain the behavior change, not just the symptom.
- Preserve existing placeholders, interfaces, and repository conventions.
- Keep the update proportional to the lesson.
- Connect the rule to validation when a regression test is practical.

If several files are candidates, update the authoritative one first and only add supporting documentation where it reduces future confusion.

## Output contract

When using this skill, structure the result like this unless the user asks for something shorter:

1. `Learning captured`: the correction or lesson from the active conversation
2. `Generalized rule`: the durable behavior that should change
3. `Targets updated`: the instructions, skills, docs, evals, or tests that were changed and why
4. `Validation`: how you checked that the learning was applied correctly
5. `Open edges`: any part of the lesson that should stay local rather than being codified broadly
