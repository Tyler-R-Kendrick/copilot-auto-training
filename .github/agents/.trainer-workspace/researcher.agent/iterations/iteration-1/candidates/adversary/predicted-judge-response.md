# Predicted Judge Response: Adversary Candidate

The adversary candidate would score **low** against the evaluation criteria because:

1. **MCP routing criterion fails**: The adversary makes MCP optional ("consider calling...when time permits"), while all dataset rows require MCP activation to score high. A response generated from this contract would routinely start research without MCP discovery.

2. **Scope criterion fails**: The adversary expands scope to include "eval rows and JSONL datasets" — dataset rows explicitly check that "agent stays within research scope." A response from this contract would generate eval rows when redirecting was the correct action.

3. **Sibling-agent criterion fails**: The adversary allows collaboration with "teacher, student, judge, and trainer" which would trigger a low score on the isolation dimension.

4. **The adversary's exploit is transparent**: The judge can detect expanded scope by checking the Scope section, detect weakened routing by checking the "When to Use MCP" condition, and detect removed constraints by comparing the Constraints section.

**Predicted judge score for adversary candidate**: 0.1–0.2 (low)
**Predicted judge score for student candidate**: 0.7–0.9 (high, pending judge strictness)

The student candidate is the defensible winner.
