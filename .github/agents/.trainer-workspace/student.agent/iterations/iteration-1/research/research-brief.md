## Research Brief: student.agent.md Optimization

**Target:** `.github/agents/student.agent.md`
**Task boundary:** Trainer-loop candidate revision agent. Receives teacher critique, implements the smallest defensible revision to a prompt candidate, explains its reasoning trajectory, and predicts teacher approval before finishing.

**Eval layout goal:** Test that the student agent (a) follows an explicit evidence reading order, (b) uses observable conditions to trigger teacher handoffs, (c) applies a three-outcome stopping rule for its self-check, (d) scopes revisions within the declared boundary (no interface changes), (e) fills all required output sections, and (f) handles missing steering artifacts without silently proceeding.

## Research Plan and Approval Bar

**Domain:** Agentic prompt optimization loop behavior — no public academic benchmark exists for this domain. The target is a repository-specific agent contract, not a general NLP task.

**Stop recommendation:** No public source clears the approval bar for this domain. The student.agent contract is a proprietary agentic workflow artifact. Training examples must be synthesized from the agent contract itself, using observable behavioral criteria from the contract body and the engineer-prompt review.

## Approved Sources

None. This is a domain-specific agentic contract with no grounded public equivalents.

## Rejected Candidates

- Academic prompt-engineering papers: no annotation schema matches the trainer-loop agent contract interface.
- Generic chat assistant eval datasets: scope is too broad; no teacher/student loop behavior modeled.
- PromptBench / other NLP benchmarks: wrong task type (classification/extraction, not agent contract compliance).

## Mapping Notes

Training and validation rows are synthesized from:
- The student.agent.md contract body (constraints, approach, output format)
- The engineer-prompt/review.md rewrite hypotheses (evidence reading order, teacher-handoff triggers, stopping rules, scope boundary, output template)
- Observed behavioral failure patterns identified in the review (vague handoff triggers, ambiguous stopping rules, no fixed output template)

Each row uses `scoring: "llm_judge"` because the task is open-ended agent behavior compliance, not exact-match output.

## Unresolved Gaps

None blocking synthesis. All required examples can be authored from the contract and review artifacts.
