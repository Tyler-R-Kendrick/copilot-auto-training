# Research Brief: researcher.agent.md Optimization

**Target:** `.github/agents/researcher.agent.md`
**Task:** Optimize the agent contract for correctness, clarity, and MCP-routing discipline

## Target Layout

- **Eval manifest:** `skills/researcher-research/evals/evals.json` (reusable as proxy for agent behavior)
- **Agent-level eval files:** `evals/files/` (shared with skill evals)
- **Train dataset:** `.github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/train.jsonl`
- **Val dataset:** `.github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/val.jsonl`

## Observed Interface

The `researcher.agent.md` contract has:
- **Frontmatter**: `name`, `description`, `tools`, `argument-hint`, `user-invocable`, `disable-model-invocation`
- **Placeholders**: None explicit — this is a system agent contract, not a data-driven prompt template
- **Inputs (via argument-hint)**: target file path, task description, scoring rule, constraints, desired artifact location

## Research Questions

1. What behaviors should the researcher agent reliably exhibit?
2. What failure modes does the current contract allow?
3. What scoring criteria distinguish a strong vs. weak research handoff?
4. What existing examples from researcher-research evals can inform the agent-level test cases?

## Approval Bar

A dataset row is approved when it:
1. Contains a realistic user request that would trigger the researcher agent
2. Has clear criteria for evaluating the quality of the research response
3. Distinguishes between correct MCP-routing behavior vs. free-form guessing
4. Covers at least one of the identified failure modes

## Approved Sources

### 1. researcher-research evals.json (existing)
- **Authority**: Repo-owned, authored by maintainer
- **Fit**: High — the 3 existing cases (support ticket, bug extraction, grounded QA) test the skill that the agent routes to
- **Provenance**: Internal, no licensing issues
- **Reuse**: Can be adapted to agent-level cases by adding routing and behavior assertions

### 2. Agent contract failure mode analysis (internal)
- **Authority**: Derived from engineer-prompt/review.md analysis
- **Fit**: High — directly derived from the target file's identified failure modes
- **Provenance**: Internal analysis, no licensing issues

## Rejected Candidates

- Public NLP research datasets (e.g., BEIR, MS MARCO): Not relevant — agent behavior testing requires request-response pairs about research routing, not NLP benchmark tasks
- OpenAI Evals datasets: Not applicable to agent contract testing

## Mapping Notes

Use the 3 existing researcher-research eval cases as seeds for agent-level cases:
- Convert skill evals into agent-invocation scenarios
- Add routing assertions (expect MCP tool use to be referenced)
- Add failure mode cases (no acceptable source → blocker report)
- Add scope boundary cases (synthesis request → redirect)

For `judge_mode=llm_judge`:
- Each row needs `reference` (expected behavior description) and `criteria` (quality rubric)
- Row-level `scoring: "llm_judge"` marks these explicitly

## Unresolved Gaps

None blocking synthesis. The existing researcher-research evals provide sufficient seeds.
Internal failure-mode analysis from review.md covers the remainder.
