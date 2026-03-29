# Decision: trainer-election optimization pass

## Target

- Prompt file: `skills/trainer-election/SKILL.md`
- Goal: improve operator clarity and execution reliability while preserving the runtime contract and output schema.

## Outcome

- Research completed using repo-owned primary sources: the runtime, tests, eval manifest, engineering review, and reference note.
- Synthesis completed: explicit `train.jsonl` and `val.jsonl` were created under `skills/trainer-election/datasets/` and copied into `iteration-1/synthesize/`.
- The patched MCP runner path now resolves the repository virtualenv, so the previous `ModuleNotFoundError: opto` blocker is gone.
- The first patched optimize retry showed that the synthesized trainer-election datasets are `llm_judge` rows, not deterministic `expected` rows. A corrected low-concurrency retry with `judge_mode=llm_judge`, `beam_width=1`, `branch_factor=1`, and `n_runners=1` reached live Agent Lightning execution.
- Live optimization still failed before candidate generation because GitHub Models returned `openai.RateLimitError` during rollout and APO critique requests.
- No optimized candidate was produced, so no prompt content was persisted back to `skills/trainer-election/SKILL.md`.

## Validation

- Repository validation succeeded after the MCP fix: `314 passed`, with the active log saved at `iteration-2/validation/pytest.txt`.

## Concrete blocker

- The remaining blocker is external rate limiting from GitHub Models, not the MCP interpreter path.
- Once quota is available again, rerun the optimize stage with `judge_mode=llm_judge` for the synthesized trainer-election datasets.

## Notes

- The synthesized trainer-election datasets remain valid for optimization, but they must be paired with `llm_judge` because they use `reference` and `criteria` fields instead of deterministic `expected` fields.