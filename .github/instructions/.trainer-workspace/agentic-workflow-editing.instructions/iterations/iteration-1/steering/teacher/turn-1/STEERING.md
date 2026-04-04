# Turn 1 — Teacher Steering

**Agent**: teacher  
**Evidence**: Direct artifact analysis against the 6 train + 4 val examples; no automated judge scores (APO run hit session error, manual_followup path).

## Assessment

| Gap (from engineer-prompt review) | Original | Student Candidate | Verdict |
|------------------------------------|----------|-------------------|---------|
| 1. No concrete compile example     | ❌       | ✅ Adds `gh aw compile train-prompt` | Fully resolved |
| 2. "Meaningful changes" ambiguity  | ❌       | ✅ "Recompile after every edit — including minor formatting or comment changes" | Fully resolved |
| 3. No verification guidance        | ❌       | ⚠️ Adds `git diff --name-only` — technically unreliable | Partially resolved |
| 4. "Stop hook" naming unclear      | ❌       | ✅ Correctly names `agentic-workflow-validation` | Fully resolved |
| 5. Pre-PR compile not explicit     | ❌       | ✅ "Run `gh aw compile` one final time before opening a pull request" | Fully resolved |

## Required Fix

**Bullet 3 verification command is unreliable.**  
`git diff --name-only` only shows **unstaged** changes. If an agent has already staged files, the command returns nothing, causing a false sense of safety.

Replace with:
```
git diff HEAD --name-only
```
Or use `git status --short` which always shows the full picture (staged + unstaged vs HEAD).

Brief rationale: "this shows both staged and unstaged changes relative to HEAD."

## Predicted Student Mistake

Student will keep `git diff --name-only` unchanged because it appears in the training example and is syntactically plausible. Must be explicitly told to change it and why.

## Stop/Continue Decision

**Continue** — apply the one surgical fix, then this candidate is approvable. No structural changes needed.

## Exit Criteria

After fixing the verification command, no further revision needed. Candidate is ready for application to the target file.
