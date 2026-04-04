# Student Candidate Description

The optimized candidate produced by the `@trainer` agent answering the `manual_followup` model_prompt.

## Changes Made

1. **Concrete compile example**: Added `gh aw compile train-prompt` as a concrete illustration.
2. **Removed "meaningful changes" ambiguity**: Changed to "every edit — including minor formatting or comment changes".
3. **Added verify step**: `git diff --name-only` check to confirm both files are present before committing.
4. **Explicit final pre-PR checkpoint**: "Run `gh aw compile` one final time before opening a pull request".
5. **Named the hook correctly**: Changed "stop hook" to `agentic-workflow-validation` hook.
6. **Described hook purpose**: Added what the hook checks (lockfile presence and freshness).
7. **Added 5th rule**: Kept the compile-failure rule from the original, preserving all original intent.

## Trade-offs

- Slightly longer (5 bullets vs 4) due to the explicit verify + final-PR step being surfaced.
- The concrete command example adds clarity at the cost of some brevity.
