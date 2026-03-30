# Research Brief: judge-rubric

## Target layout

- Prompt file: `skills/judge-rubric/SKILL.md`
- Reused eval manifest: `skills/judge-rubric/evals/evals.json`
- Canonical APO datasets: `skills/judge-rubric/datasets/train.jsonl` and `skills/judge-rubric/datasets/val.jsonl`
- Local trainer workspace: `skills/judge-rubric/.trainer-workspace/SKILL/`
- Active iteration outputs: `skills/judge-rubric/.trainer-workspace/SKILL/iterations/iteration-1/`

## Observed interface

- The skill is a prompt-like rubric-authoring contract, not an executable scoring runtime.
- The target file has no task placeholders, so optimization will use the implicit task-context path.
- The judging policy core that must remain stable is already specified locally: locked 3 to 7 dimensions, pass-partial-fail anchors, blocker-first behavior, explicit evidence ledgers, and low trust in unsupported chain-of-thought.

## Query plan

The repo already contains the authoritative sources needed for this optimization pass, so the research requirement is satisfied without external source discovery:

1. Use the current skill contract as the baseline operator prompt.
2. Use the local eval manifest as the official scenario inventory for user-facing rubric requests.
3. Use the deterministic helper, sample contract, and tests as the source of truth for the structured-contract branch.
4. Use the engineer review as the source of rewrite hypotheses for structure, output shape, and retention.

## Approved sources

1. `skills/judge-rubric/SKILL.md`
   - Authority: current repo-owned skill contract.
   - Fit: canonical policy and existing rubric workflow.

2. `skills/judge-rubric/evals/evals.json`
   - Authority: official authored eval manifest.
   - Fit: grounded user-facing rubric scenarios for outcome-focused, hybrid, and blocker-heavy tasks.

3. `skills/judge-rubric/scripts/render_rubric.py`
   - Authority: deterministic helper implementation.
   - Fit: exact section order, accepted contract fields, and 3 to 7 dimension enforcement.

4. `skills/judge-rubric/assets/sample-contract.json`
   - Authority: repo-owned structured helper fixture.
   - Fit: representative structured-contract input for the helper-first path.

5. `tests/test_judge_rubric.py`
   - Authority: repo-owned behavior checks.
   - Fit: validates helper output shape, contract validation behavior, and missing-field failure mode.

6. `skills/judge-rubric/.trainer-workspace/SKILL/engineer-prompt/review.md`
   - Authority: local engineering review for this optimization pass.
   - Fit: rewrite targets for earlier helper routing, tighter output structure, compact constraint retention, and explicit blocker handling.

## Rejected candidates

- Generic rubric-writing blog posts: rejected because they do not define this repo's helper contract or judging-policy invariants.
- External prompt-optimization examples: rejected because the task already has authoritative repo-owned evals, helper code, and tests.
- Free-form grading templates without evidence-ledger requirements: rejected because they would weaken the existing judging contract.

## Mapping notes

- Reuse the existing eval manifest rather than authoring a second manifest.
- Synthesize explicit APO rows from repo-owned sources only.
- Keep one structured-contract row so optimization can reward early recognition of the deterministic helper path.
- Keep one incomplete-contract row in validation so blocker-first behavior is tested without allowing invented thresholds.
- Use `judge_mode=llm_judge` because the target artifact is a prompt-like skill contract whose outputs are better judged for coverage, structure, and retained policy than by exact string match.

## Unresolved gaps

- The prompt uses implicit task context rather than named placeholders. `trainer-optimize` supports that path, but any optimized candidate should still be reviewed before persistence.