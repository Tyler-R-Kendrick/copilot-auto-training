## Student Candidate Reflection

**What changed from original to student**:
- Added MCP `run_agent_skill` deterministic-helper check (scripts/run_research.py existence test).
- Added explicit Constraint Resolution section with required/elicitable split and prescriptive elicitation rules.
- Added Source Approval Bar section with five embedded criteria.
- Updated Output Format to list six required sections and added a Blocker Report template.
- Updated Approach step 2 to integrate the `run_agent_skill` check; step 3 to use the Constraint Resolution contract.

**Why these changes are defensible**:
- All five are direct responses to the engineer-review priorities.
- No scope expansion: the role remains "research only," no synthesis steps added.
- The contract additions are prescriptive (not advisory), matching the tone of other agent files in this repo.

**Risk self-assessment**:
- Low risk: `run_agent_skill` threshold — explicit and unambiguous.
- Low risk: constraint split — clear taxonomy with examples.
- Medium risk: approval bar wording — "do not downgrade to partially approved" could be clearer as "partial matches that fail any criterion are rejected, not approved."
- Low risk: blocker-report template — provides the minimum required structure.
- Low risk: required sections mandate — directly addresses the completeness gap.
