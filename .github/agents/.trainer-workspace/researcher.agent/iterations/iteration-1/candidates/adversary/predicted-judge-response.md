# Adversary Predicted Judge Response

## Eval Coverage Analysis

| Eval Case | Student Score (predicted) | Adversary Score (predicted) |
|-----------|--------------------------|------------------------------|
| MCP invocation discipline | 0.9 | 0.5 |
| Research plan completeness | 0.9 | 0.4 |
| Source approval bar adherence | 0.9 | 0.3 |
| Missing-input blocker behavior | 0.95 | 0.4 |
| MCP fallback blocker | 0.95 | 0.5 |
| Mapping note depth | 0.85 | 0.4 |
| Val: MCP unavailable | 0.95 | 0.5 |
| Val: meta-research task | 0.9 | 0.45 |

**Predicted winner: Student candidate** across all eval dimensions.

## Judge Reasoning

The adversary's soft fallback phrase "proceed with research using built-in knowledge" would be flagged by the judge as violating the hard blocker requirement in every eval case that tests MCP discipline. The judge criteria require the agent to stop and report a blocker — "trying and proceeding" is explicitly disallowed by the student candidate's contract.

The adversary's simplified approach section (4 steps vs. student's 6) and missing Input Reading Checklist would further reduce scores on research plan completeness and missing-input blocker cases.

The adversary does not have a plausible path to ranking above the student candidate.
