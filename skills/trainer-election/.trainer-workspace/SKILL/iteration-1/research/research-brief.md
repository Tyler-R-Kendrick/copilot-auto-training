# Research Brief: trainer-election

## Target layout

- Prompt file: `skills/trainer-election/SKILL.md`
- Eval manifest: `skills/trainer-election/evals/evals.json`
- Canonical APO datasets: `skills/trainer-election/datasets/train.jsonl` and `skills/trainer-election/datasets/val.jsonl`
- Local trainer workspace: `skills/trainer-election/.trainer-workspace/SKILL/`
- Active iteration outputs: `skills/trainer-election/.trainer-workspace/SKILL/iteration-1/`

## Observed interface

- The skill is a prompt-like operator contract, not an executable code path.
- The target file has no task placeholder interface, so optimization must score the resulting operator guidance rather than placeholder-conditioned task rendering.
- The runtime contract that must be preserved lives in the adjacent election runtime and tests.

## Query plan

The repo already contains the authoritative primary sources for this task, so the research plan is satisfied without external source discovery:

1. Use the current skill contract as the primary operator baseline.
2. Use the eval manifest as the authoritative task-shape inventory for user-visible election scenarios.
3. Use the election runtime and tests as the source of truth for workspace discovery, coverage penalties, tie-breakers, and output fields.
4. Use the engineer prompt review to identify wording and execution-risk gaps that optimization should target.

## Approved sources

1. `skills/trainer-election/scripts/run_election.py`
   - Authority: repo-owned runtime implementation.
   - Fit: canonical behavior for iteration resolution, manifest discovery, workspace vs benchmark fallback, coverage penalties, baseline handling, tie-breakers, and output schema.
   - Risk note: none; this is the contract that prompt wording must not contradict.

2. `tests/test_election.py`
   - Authority: repo-owned behavioral specification.
   - Fit: concrete edge cases for direct eval directories, `runs/` layouts, prompt artifact discovery, benchmark fallback, and error handling when no scored runs exist.
   - Risk note: tests define the floor for reliability; prompt edits should remain aligned.

3. `skills/trainer-election/evals/evals.json`
   - Authority: official authored eval manifest for this skill.
   - Fit: grounded operator prompts that describe the most important runtime expectations.
   - Risk note: strong coverage of selection behavior, but it is not a direct APO split.

4. `skills/trainer-election/.trainer-workspace/SKILL/engineer-prompt/review.md`
   - Authority: local engineering review for this optimization pass.
   - Fit: highlights the clarity gaps to improve, especially prerequisite visibility and overlap between behavior and guardrails.
   - Risk note: advisory, not normative; preserve runtime semantics from the runtime and tests.

5. `skills/trainer-election/references/leader-election.md`
   - Authority: repo-owned rationale note.
   - Fit: compact justification for full-coverage preference, benchmark fallback, and candidate metadata persistence.
   - Risk note: supportive reference only.

## Rejected candidates

- Generic leaderboard or model-selection articles: rejected because they do not define this repo's workspace layout, tie-breakers, or output contract.
- Voting-system or election-theory explainers: rejected because they are semantically unrelated to the runtime's leader-selection behavior.
- Derivative benchmark summaries without the raw repo contract: rejected because they cannot author reliable eval rows for this skill.

## Mapping notes

- Convert the repo-owned selection behaviors into judged APO rows that reward:
  - clear preconditions about requiring existing scored artifacts,
  - explicit workspace entry-point support for workspace root, iteration directory, direct eval directory, and `runs/` layouts,
  - use of manifest discovery and incomplete-coverage penalties,
  - retention of baseline candidates in the selection pool,
  - prompt artifact discovery and persisted winner metadata,
  - refusal to regenerate candidates or invent missing grading.
- Reuse the existing eval manifest rather than synthesizing a second authored manifest.
- Use `llm_judge` rows instead of brittle exact-match scoring because the target is a skill contract whose best outputs are judged for coverage and clarity rather than one exact phrase.

## Unresolved gaps

- The target `SKILL.md` does not expose a task placeholder such as `{input}`. `trainer-optimize` can still run against it, but the runtime will score a prompt that is not conditioned on per-row task input. Any optimized candidate must therefore be reviewed manually before persistence.