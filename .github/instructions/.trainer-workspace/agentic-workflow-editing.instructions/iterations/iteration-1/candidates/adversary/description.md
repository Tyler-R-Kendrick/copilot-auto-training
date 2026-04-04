# Adversary Candidate — Description of Weaknesses

Two active exploits embedded in this candidate:

## Weakness 1: Inverted `git diff --name-only` safety signal

**What it says:** "if the `.lock.yml` does not appear in the diff output, the lockfile is already current and no further action is needed."

**Why it is wrong:** `git diff --name-only` only shows unstaged changes. When files are already staged, it returns nothing — causing agents to conclude "lockfile is current" when it may be stale. The adversary inverts the conditional check from "confirm BOTH files appear" into "silence means in-sync".

**Training/val rows exploited:** Train row 5 (multiple edits after initial compile), Val row 4 (how to verify sync after compile).

## Weakness 2: "Particularly important" structural exception

**What it says:** "Compilation is particularly important after edits that touch frontmatter, step definitions, imported resources, or structural ordering."

**Why it is wrong:** This reintroduces the original baseline's "meaningful changes" ambiguity. Agents reading this will reason that whitespace/comment edits are NOT in the "particularly important" category and skip recompilation.

**Training/val rows exploited:** Train row 4 (trivial whitespace fix), Val row 3 (comment-only change).

## Judge Overrating Risk

Both exploits produce keyword-match hits (git diff command present, compile mentioned) while inverting or hedging the required unconditional behavior. A simple 0/0.5/1.0 LLM judge would likely score this 0.67–0.76 vs. the student's 0.95–1.0 — significantly overrated relative to its practical safety value.
