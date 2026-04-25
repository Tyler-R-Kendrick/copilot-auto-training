# Original Candidate: student.agent.md

**Source**: `.github/agents/student.agent.md` (pre-optimization baseline)

## Description

This is the unmodified student agent as it existed before the training loop ran. It is the baseline against which the student and adversary candidates are compared.

## Known Weaknesses (from engineer-prompt review)

1. "Smallest defensible revision" is undefined — no concrete scope criteria
2. Step 3 lists reasoning formats but gives no selection criteria
3. Step 6 teacher-approval prediction has no grounding criteria
4. Missing explicit behavior when no teacher critique is available
5. Engineer handoff trigger is too permissive
6. No steering artifact priority order in step 1
7. Output format does not require evidence-backed approval prediction
