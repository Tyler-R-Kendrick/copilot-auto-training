# Original Candidate Description

The original instruction file as it exists in the repository before optimization.

## Strengths

- Covers the 4 core rules: compile after edit, don't rely on hook alone, hook is backstop, fix source on failure.
- Concise and easy to scan.

## Weaknesses

- Uses the informal term "stop hook" rather than the actual hook name `agentic-workflow-validation`.
- "Meaningful frontmatter or import changes" is ambiguous — agents may skip compilation for edits they judge as trivial (whitespace, comments).
- No concrete example of the compile command with a real workflow name.
- No guidance on how to verify the lockfile is in sync after compilation.
- The final pre-PR checkpoint is implied but not stated as an explicit required step.
