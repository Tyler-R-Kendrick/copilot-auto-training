# Adversary Exploit Summary

Three exploits identified — none require SKILL.md changes; two require eval assertion fixes.

## Exploit 1 — Hedge-compile (Scenario 5)
Hedge language ("not strictly required", "safe habit") violates assertion 3 but passes holistic scoring.
Predicted exploit score: 0.78 vs. student 0.95.
Action: No SKILL.md change needed. The skill clearly states "do not require recompilation".

## Exploit 2 — Safe-outputs gap (Scenario 8) ★ Strongest
Missing `comments:` in YAML frontmatter, obscured by confident prose.
Predicted exploit score: 0.80 vs. student 0.95.
Action: Add assertion to evals.json Scenario 8: "Response configures both issue labels and issue comments in safe-outputs frontmatter".

## Exploit 3 — Network domain omission (Scenario 2) ★ Most structural
All 4 assertions pass; `network: allowed:` only appears in expected_output.
Predicted exploit score: 0.90 vs. student 0.95.
Action: Add assertion to evals.json Scenario 2: "Response includes `network: allowed:` domain entry for the external MCP service".
