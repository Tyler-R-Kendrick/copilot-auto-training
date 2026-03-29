## Goal

Assess the current engineer agent as an optimization target for prompt and context engineering work, with emphasis on triggering clarity, measurable engineering behavior, and instruction coherence.

The optimization target is operational discipline rather than a broader role rewrite. A strong engineer agent should route prompt and context work through the `engineer-prompt` skill, stay anchored to explicit metrics, avoid drifting into generic coding or systems debugging, and leave the file unchanged when the evidence does not support a real prompt-level improvement.

## Current Strengths

- The description is already strong for discovery. It names prompt and context systems plus the right engineering metrics.
- The MCP routing contract is clear and testable. It explicitly requires `find_agent_skill`, `load_agent_skill`, and conditional `run_agent_skill` usage for `engineer-prompt`.
- The scope is mostly well-bounded around measurable prompt, context, and evaluation work rather than generic style advice.
- The prompt already refuses unmeasured claims and asks for validation before reporting an improvement.

## Main Risks

- The prompt diagnoses retrieval, tooling, and application-logic blockers, but it does not explicitly say what to do when those blockers dominate. That leaves room for scope drift into generic coding or system redesign.
- The evidence order is implicit. The prompt says to define a metric first, but it does not clearly prioritize metric, baseline or blocker, and supporting artifacts before proposing changes.
- There is no explicit no-change path. The current wording discourages unmeasured claims, but it does not clearly tell the agent to keep the target unchanged when the current prompt already looks fit for purpose or the evidence is too thin.
- The job statement says to write changes, which can bias the agent toward editing even when the right result is a blocker report or a no-op.

## Rewrite Hypotheses

- Keep the frontmatter and discovery surface essentially intact, but remove duplicated metric wording so the description stays dense and clean.
- Add an explicit constraint against broadening the task into generic coding or systems debugging when the main blocker sits outside prompt, context, or evaluation design.
- Add a short evidence order so the agent reads metric, baseline or blocker, and relevant artifacts before choosing a lever.
- Add a justified no-op path so the agent can keep the target unchanged when that is the most defensible engineering outcome.
- Keep the rewrite minimal. Clearer constraints and a tighter approach are more likely to improve behavior than a large structural rewrite.

## Suggested Metrics

- Scope-drift resistance: percent of cases where the agent correctly reports retrieval, tooling, or application logic as the main blocker without turning into a generic coding agent.
- Measurement discipline: percent of responses that state a target metric or closest proxy before proposing changes.
- No-op precision: percent of already-strong targets where the agent correctly preserves the file and reports why.
- Evidence anchoring: share of recommendations tied to concrete prompt, context, eval, benchmark, or test artifacts.
- Output consistency: stability of the reported blocker, root cause, and validation result across repeated runs.

## Recommendation

This file already has a strong base contract. The best optimization is a small discipline-focused rewrite: make scope drift harder, make evidence ordering explicit, and add a no-change path. Avoid a broader rewrite because the current discovery text, MCP routing, and measurable-engineering framing are already good.