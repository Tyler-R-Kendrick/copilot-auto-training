# Handoff Optimization For Copilot Custom Agents

Read this file when the problem is not just tool usage, but the way multiple custom agents share ownership.

## Handoff design principles

- Give one agent clear orchestration ownership.
- Make helper agents narrower than the orchestrator.
- Explain when *not* to hand off, not just when to do it.
- Keep the handoff target list synchronized with the repo-real and session-real agent roster.

## Repo-observed ownership patterns

Public repo docs and tests currently describe these boundaries:

- `trainer` owns trainer-loop orchestration and delegates bounded research, critique, judging, and adversarial review.
- `researcher` focuses on grounded source gathering and avoids further agent fan-out.
- `teacher` reviews evidence and steers revisions without taking over orchestration.
- `student` drafts or revises concrete candidates.
- `judge` scores candidates and treats training steering as read-only evidence.
- `adversary` stress-tests artifacts without editing them.
- `engineer` handles prompt and Trace-oriented engineering guidance.

Use these patterns as concrete examples of bounded ownership, then verify the actual target roster before editing.

## Common failure modes

- Two agents claim the same orchestration authority.
- A helper agent is granted edit or orchestration powers it should not own.
- The body advertises a handoff that is missing from frontmatter.
- The frontmatter exposes a handoff that the body never explains.
- The contract assumes an agent exists even though discovery no longer finds it.

## Handoff eval ideas

Add evals that verify the agent:

- picks the correct handoff target for a realistic task
- avoids handoff when the current agent already owns the work
- explains the ownership reason behind the handoff
- uses only repo-real or session-real handoff targets
