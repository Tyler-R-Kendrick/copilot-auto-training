# Decision: agentic-workflow-editing.instructions.md — iteration-1

## Selected Candidate: student

## Summary of Changes Applied

The following improvements were made to `.github/instructions/agentic-workflow-editing.instructions.md`:

| # | Change | Engineer Gap Addressed |
|---|--------|----------------------|
| 1 | Added concrete compile example: `gh aw compile train-prompt` for `train-prompt.md` | Gap 1: no concrete example |
| 2 | Clarified "Recompile after every edit — including minor formatting or comment changes" | Gap 2: "meaningful changes" ambiguity |
| 3 | Added verify step: `git diff HEAD --name-only` to confirm both files appear before committing | Gap 3: no verification guidance |
| 4 | Named the hook correctly: `agentic-workflow-validation` instead of "stop hook" | Gap 4: unclear hook name |
| 5 | Added explicit final pre-PR checkpoint: "Run `gh aw compile` one final time before opening a pull request" | Gap 5: pre-PR step implied but not explicit |
| 6 | Added hook description: "it checks that the `.lock.yml` is present and matches the compiled output" | Bonus: agents now understand what the hook enforces |

## Adversary Review

The adversary found two exploits (git diff inversion, "particularly important" exception), but both were blocked by the student's defenses:
- `git diff HEAD --name-only` (teacher-directed fix) closes the staged-files vulnerability
- "Every edit — including minor formatting or comment changes" closes the structural-exception window

**Adversary verdict**: overrating attack only (~0.70 vs student ~0.97). No extra judge steering required.

## Validation Result

`python -m pytest -q`: **856 passed, 0 failures** (2026-04-30). The test suite includes `test_agentic_workflow_instruction_exists_with_scalar_applyto`, which was updated to match the improved instruction text.

## Workspace Path

`.github/instructions/.trainer-workspace/agentic-workflow-editing.instructions/iterations/iteration-1/`
