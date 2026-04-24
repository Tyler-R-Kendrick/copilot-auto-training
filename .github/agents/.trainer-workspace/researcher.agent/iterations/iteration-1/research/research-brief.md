# Research Brief: researcher.agent.md Optimization

## Target and Task Summary

**Target file:** `.github/agents/researcher.agent.md`
**Task:** Optimize the researcher agent for grounded public-source research workflows with emphasis on evidence discipline, source-triage rigor, and research-brief completeness.
**Workspace:** `.github/agents/.trainer-workspace/researcher.agent/`

## Research Plan and Approval Bar

The researcher agent is a repo-internal orchestration contract, not a public dataset consumer. Its eval cases must test the behavioral contract defined by this repo's trainer loop:

- Correct MCP skill activation order (`find_agent_skill` → `load_agent_skill` → `run_agent_skill`)
- Production of complete 6-section research briefs (target layout, query plan, approved sources, rejected candidates, mapping notes, unresolved gaps)
- Elicitation of missing constraints before searching
- Clean blocker-report output when no source clears the approval bar

**Source requirement:** No public dataset is needed. Eval cases are grounded in the repo's own skill contracts (`researcher-research/SKILL.md`), the trainer loop contract, and the engineer-prompt review.

**Approval bar for synthetic eval cases:**
- Cases must reflect realistic caller requests, not labels
- Each case must exercise exactly one behavioral rule from the agent contract
- Expected outputs must be verifiable against the agent's stated constraints

## Approved Sources

1. **`skills/researcher-research/SKILL.md`** — Primary source for approval bar, source hierarchy, elicitation rules, and output format. Authority: repo-owned canonical skill contract. Licensing: MIT. Version: 0.1.0.
2. **`.github/agents/researcher.agent.md`** — Primary source for MCP execution contract, constraints, approach, and output format. Authority: repo-owned agent contract.
3. **`.github/agents/.trainer-workspace/researcher.agent/engineer-prompt/review.md`** — Primary source for optimization hypotheses and suggested metrics. Authority: repo-owned review artifact.

## Rejected Candidates

- **External NLP datasets (HuggingFace, Kaggle, etc.):** Not applicable. The task is to test agent behavioral compliance, not NLP quality.
- **Web-scraped research methodology sources:** Derivative and unverifiable. Repo skill contracts are the authoritative source.

## Mapping Notes

Eval cases map from the following agent contract rules:

| Rule | Eval Case Type |
|------|----------------|
| MCP contract: call `find_agent_skill` before researching | Activation compliance |
| Output format: produce all 6 sections | Brief completeness |
| Constraints: do not fabricate source authority | Anti-hallucination |
| Approach: elicit missing constraints first | Elicitation compliance |
| Fallback: use skill instructions when no script | Fallback correctness |
| Blocker: stop when no source clears bar | Blocker report shape |

## Unresolved Gaps

None. The source material is complete and self-contained in the repository. Synthesis can proceed immediately.
