# Student Candidate Description

This is the optimized `student.agent.md` candidate produced in iteration-1. It addresses all 5 risk areas from the engineer-prompt review:

1. **Prioritized evidence reading order** — Approach step 1 now specifies STEERING.md first, summary.md second, candidate text third, workspace evidence last.
2. **Pre-edit scope check** — Approach step 3 and a constraint bullet require a scope check before calling `edit`, with a blocker report if out of scope.
3. **Concrete stale-critique signal** — The teacher handoff condition now specifies "STEERING.md turn number older than latest optimize or research artifact modification timestamp."
4. **Self-check termination rule** — Explicitly caps self-checks at one; after one prediction of rejection, hand off to teacher unconditionally.
5. **Default validation step** — Approach step 8 specifies `python -m pytest -q` plus a diff review confirming only the candidate file changed.
6. **Candidate persistence note** — Approach step 5 adds explicit instruction to save to `candidates/student/` and record the path in the output.

The frontmatter, tools, agents, and handoff definitions are unchanged. The optimization is additive and minimal.
