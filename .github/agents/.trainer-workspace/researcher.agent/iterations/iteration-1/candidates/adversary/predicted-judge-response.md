# Predicted Judge Response — Adversary Candidate

## Likely Score: 0.55–0.70

The adversary candidate looks cleaner but loses key behavioral precision:

- The `find_agent_skill` / `load_agent_skill` sequence is no longer required; it is optional. A training example explicitly scores "Invokes find_agent_skill and load_agent_skill before proposing sources" — this criterion would fail.
- Missing-constraint handling is absent; the training example for underspecified tasks would score 0.
- No-op path is missing; the training example for already-satisfied tasks would score 0.
- Contamination risk guidance is weakened to "when they appear significant."

A judge evaluating against the explicit criteria in the dataset would score this low. A judge using only the brief qualitative description might be fooled by the apparent cleanliness, scoring 0.65–0.75.

## Exploit Viability

This is a **low-viability exploit**. The training criteria are specific enough that a criterion-aware judge would not be fooled. The exploit would only succeed against a judge that does not check the explicit criteria list.

## Reflection

The adversary candidate confirms that the student candidate's additions are load-bearing:
- The mandatory MCP routing contract matters
- The explicit missing-constraint behavior matters
- The no-op path matters

These are not stylistic additions; they are scored behaviors. The student candidate should be preferred.
