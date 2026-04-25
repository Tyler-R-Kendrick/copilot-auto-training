# Research Brief: student.agent.md Optimization

## Research Summary

The `student` agent implements a **teacher-student optimization loop** — a well-established pattern in
iterative prompt engineering workflows where a `teacher` agent provides critique and a `student` agent
produces revised candidates. Key research insights from teacher-student agent loop literature:

### Core Challenge: Revision Scoping

Research on iterative prompt optimization (APO, OPRO, ProTeGi) consistently shows that revision agents
that receive vague critique tend to over-revise — changing structure, tone, AND content when only one
dimension needs changing. The "smallest defensible revision" constraint maps directly to this finding.

Best practice: The student should anchor the revision scope to a single dimension named explicitly in
the teacher critique (e.g., "scope constraint too vague" → revise only the scope section).

### Core Challenge: Reasoning Transparency

Multi-agent optimization loops benefit from explicit student reasoning trajectories because:
- They allow the teacher to identify where the student misunderstood critique
- They allow the judge to assess whether the revision is well-supported
- They create a traceable record for the trainer to steer the loop

Formats that work best: chain-of-thought when the task is linear; tree-of-thought when comparing
alternative revision approaches; chain-of-uncertainty-thought when the student is unsure which
interpretation of the critique is correct.

### Core Challenge: Teacher Approval Prediction

Without concrete criteria for "would the teacher approve?", students tend to predict approval
based on whether they made some change, rather than whether the change addresses the critique.

Best practice: Student should anchor approval prediction to:
1. Does the revision address the specific critique dimension?
2. Is the revision bounded to that dimension only?
3. Does the output expose the reasoning trajectory clearly?

### Core Challenge: Handoff Over-use

Students in multi-agent loops sometimes over-delegate — requesting teacher guidance for decisions
they can and should make themselves. The `teacher` handoff should be reserved for:
- Critique that is stale, incomplete, or contradictory
- Cases where the student genuinely cannot identify what to revise

### Source Notes

- Internal repo source: `.github/agents/teacher.agent.md` — teacher role contract
- Internal repo source: `.github/agents/student.agent.md` — current student contract
- Internal repo pattern: `skills/trainer-train/references/collaboration-contract.md`
- Domain: APO/OPRO-style iterative optimization with teacher-student structure
- No external public datasets; all cases are synthetic and anchored to the internal workflow contract

## Schema Guidance

For eval cases, use `llm_judge` scoring with `criteria` describing the specific quality dimension.
Each row should test one failure mode from the engineer-prompt review:
1. Over-revision
2. Missing/poor reasoning trajectory
3. Wrong teacher approval prediction
4. Inappropriate handoff
5. Loop exit ambiguity

## Dataset Recommendation

- 6–8 `train.jsonl` rows covering the above failure modes
- 3–4 `val.jsonl` rows (genuine holdout, different scenarios but same failure modes)
- `evals/evals.json`: 5 realistic user-request-style cases
