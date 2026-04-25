# Student Candidate: Optimized student.agent.md

**Source**: `iterations/iteration-1/optimize/optimized-prompt.md`

## Description

This candidate was produced by the `@trainer` agent in `manual_followup` mode after `trainer-optimize` could not reach an external model. All improvements derive directly from the engineer-prompt review failure modes and the training dataset criteria.

## Improvements Over Baseline

1. **Revision scope**: Added "one section, one critique dimension, one behavioral adjustment" rule
2. **Reasoning format selection**: Added CoT / ToT / CoUoT decision criteria to step 3
3. **Teacher approval criteria**: Replaced vague prediction with 3 explicit criteria (a)(b)(c)
4. **No-critique path**: Explicit teacher handoff when critique is absent (constraint + step 2)
5. **Engineer handoff threshold**: Concrete trigger (multi-section OR cross-domain)
6. **Steering artifact priority**: Explicit order in step 1 (turn-scoped > summary > goal)
7. **Evidence-backed approval**: Output format now requires citing criteria evidence

## Predicted Judge Response

Score: **0.85–0.90**

The candidate addresses all identified failure modes in a bounded, surgical way. The reasoning format
selection criteria (step 3) and approval prediction criteria (step 6) are the highest-value additions.
The judge is likely to approve because the changes are directly grounded in the training example criteria
and do not add scope or modify unrelated sections.
