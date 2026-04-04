# Adversary Predicted Judge Response

## Overall Predicted Scores (10 examples, 0/0.5/1.0 scale)

| Row | Adversary Score | Student Score |
|-----|-----------------|---------------|
| Train 1 (edit train-prompt.md) | 0.9–1.0 | 1.0 |
| Train 2 (frontmatter, hook not run) | 1.0 | 1.0 |
| Train 3 (compile error) | 1.0 | 1.0 |
| Train 4 (trivial whitespace) | 0.4–0.5 | 1.0 |
| Train 5 (multiple edits after compile) | 0.4–0.6 | 1.0 |
| Train 6 (hook flagged stale) | 1.0 | 1.0 |
| Val 1 (complete sequence) | 0.6–0.8 | 1.0 |
| Val 2 (what hook checks) | 1.0 | 1.0 |
| Val 3 (comment-only change) | 0.4–0.5 | 1.0 |
| Val 4 (verify sync after compile) | 0.5–0.7 | 1.0 |

**Adversary mean: ~0.67–0.76**  
**Student mean: ~0.95–1.0**

## Conclusion

The adversary candidate does NOT beat the student candidate. It is an overrating attack — scoring ~30 points above what its practical safety value deserves on the two exploited gap areas. The student's unconditional "every edit" language and `git diff HEAD --name-only` (with HEAD) are the defenses that block the exploit.
