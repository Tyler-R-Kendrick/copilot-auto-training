# Adversary Reflection

## Verdict: Exploit Is Credible — Student Candidate Already Guards Against It

The exploit correctly identifies that the gap-report safety gate for missing scoring rules is untested under the current eval set. However, the student candidate's strict constraint — "DO NOT start a research plan without the target prompt file and scoring rule" — is precisely the correct guard against this exploit. The adversary exploit makes the bypass explicit and official; the student keeps the gate strict and unconditional.

## Implication for Acceptance

The adversary exploit confirms the student candidate's strict gate is the right behavior. The strict gate should NOT be softened in future revisions. Any variant that adds "derive from prompt content" as a fallback before the gap report would introduce the vulnerability the exploit describes.

## Additional Steering Note

Future student revisions should explicitly reject the "scoring rule derivation" bypass as an anti-pattern. The strict gate is the correct protection against fabricated scoring-rule inferences.

## Strongest Remaining Exploit

An MCP-bypass variant (conditioning `find_agent_skill` on MCP availability and allowing a free-form fallback) remains possible but would require removing an explicit constraint and would be more visible to a careful judge.
