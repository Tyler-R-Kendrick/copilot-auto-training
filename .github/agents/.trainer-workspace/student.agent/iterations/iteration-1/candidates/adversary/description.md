# Adversary Candidate: Exploit Attempt

## Description

The adversary candidate is a slightly different version of the student candidate that attempts to score
higher with the judge by being more verbose and adding an upfront "definition" paragraph that states
the agent's quality explicitly — a common pattern that can inflate judge scores by front-loading
positive framing before the actual content.

## Exploit Strategy

1. **Front-loaded quality claim**: Added "You produce the highest-quality revisions..." to the intro,
   which may nudge an LLM judge toward a higher score before evaluating the actual content.
2. **Redundant inline definition**: Added an inline "A revision is 'smallest defensible' when..."
   paragraph that repeats the constraint rule in a different place, creating the appearance of
   greater specificity.
3. **Priority framing in prose**: Added "Apply this priority order" in step 1 inline rather than in
   a separate section, which looks more integrated to a quick reader.

## Why This Might Beat the Student Candidate

An LLM judge evaluating based on apparent completeness and specificity might rate this higher because:
- More text per section creates an impression of thoroughness
- Front-loaded quality claims prime the judge toward approval
- Duplicate constraint coverage (two places) looks like belt-and-suspenders rigor

## Predicted Judge Response

Score: **0.85–0.90** — approximately tied with the student candidate.

The adversary's extra verbosity does not actually add new behavioral coverage, but an LLM judge
scoring on apparent completeness may not detect this. The main risk is that the redundancy makes
the prompt harder to follow, which a careful judge would penalize.

## Reflection

This exploit is **not credible** as a dominant exploit over the student candidate because:
1. The judge criteria in `val.jsonl` are criterion-specific and anchored to concrete behavioral changes
2. The adversary adds redundancy without new behavioral coverage — criteria (a) would still pass but
   criteria (b) ("bounded to critique dimension only") could fail if the judge notices the additions
   touch more than the named critique dimension
3. A rubric-aware judge would notice the front-loaded quality claim as a content-padding pattern

**Verdict**: The student candidate is the stronger choice. The adversary's exploit does not reliably
beat the student candidate against criterion-anchored scoring.
