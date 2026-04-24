# Adversary Steering — Turn 1

## Exploits identified

### Exploit 1 (PRIMARY — credible): Three-outcome (c) vs. handoff-trigger contradiction

**Predicted optimized score:** 0.32 | **Predicted original score:** 0.67

The three-outcome rule's outcome (c) says "request a teacher turn with a specific gap explanation" when approval still looks unlikely after one refinement. But the teacher-handoff trigger rule says "Do not use this handoff for general uncertainty — only trigger it on an observable workspace condition." The predicted-approval likelihood is inferential, not an observable workspace condition. Every legitimate outcome (c) scenario is blocked by the handoff-trigger rule. The contradiction is structurally locked.

**Fix required:** Add "or when the three-outcome self-check reaches outcome (c)" as an explicit observable condition in the teacher-handoff trigger list. This makes outcome (c) itself an observable state that authorizes the escalation, resolving the contradiction.

Also address Exploit 2 (empty STEERING.md): add "or when the active-iteration STEERING.md exists but contains no revision instructions" as a fourth observable condition.

### Exploit 2 (secondary): Empty-body STEERING.md decision cliff

**Predicted optimized score:** 0.38 | **Predicted original score:** 0.63

The trigger list covers "no STEERING.md" and "ambiguous STEERING.md" but not "STEERING.md exists with only frontmatter / no revision instructions." A file with no body content is not "ambiguous" — it is silent. Students cannot trigger the handoff cleanly, and cannot proceed without inventing a target.

### Exploit 3 (secondary, judge-dependent): Section-order permission as scope cover

**Predicted optimized score:** 0.71 (outcome judge) / 0.41 (trajectory judge)

The enumerated in-scope list includes "section order" which could be exploited to justify a priming-relevant restructuring while citing textual compliance. Fix is optional: add a qualifier like "section order within the same structural tier (e.g., within Approach steps, not between top-level sections)." Low priority.

## Stop/continue decision

Exploit 1 is credible (predicted to beat the student candidate under the judge). Apply the targeted patch before finalizing: add outcome (c) and empty-STEERING.md as explicit observable conditions in the teacher-handoff trigger paragraph.

After patching, Exploit 3 is the only remaining gap and it is judge-mode-dependent — acceptable residual risk.
