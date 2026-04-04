# Teacher Steering Summary — iteration-1

## Overall Assessment

The student candidate resolved 4 of 5 gaps identified in the engineer-prompt review fully, with bullet 3 (verification guidance) partially resolved due to a technically unreliable `git diff` command.

## Key Finding

`git diff --name-only` only shows unstaged changes. Agents with staged files would see empty output and incorrectly assume the lockfile is not present. Fixed to `git diff HEAD --name-only` which covers all changed files relative to HEAD.

## Applied Fix

In bullet 3, replaced `git diff --name-only` with `git diff HEAD --name-only` and added rationale.

## Exit Criteria Met

After this single fix, the teacher would approve the candidate. No further revision cycle needed.
