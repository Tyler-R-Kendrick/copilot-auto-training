# Original Candidate

This is the baseline `student.agent.md` before optimization.

## Description

The original student agent has a flat evidence reading list, subjective self-check exit criteria, no explicit no-op decision checkpoint, undefined validation step, and a vague engineer handoff trigger. These gaps were identified in the engineer-prompt review as the primary optimization targets.

## Key Weaknesses

1. Step 1 reads evidence in a flat, unprioritized list — no conflict resolution.
2. Step 6 self-check uses subjective language ("unsupported, incomplete, or misaligned") with no structural gate.
3. No step 2b — the agent drafts revisions without first checking whether a revision is warranted.
4. Step 7 says "run the relevant validation or measurement step" without defining what that means.
5. Engineer handoff trigger is broad ("needs specialized prompt or Trace-oriented coaching") with no exclusion for minor changes.

## Predicted Judge Response

A judge evaluating the original against the optimized candidate would likely score it lower on: evidence handling specificity, self-check reliability, no-op accuracy, and validation auditability.
