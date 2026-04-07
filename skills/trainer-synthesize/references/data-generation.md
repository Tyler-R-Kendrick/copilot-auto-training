# Data Generation Reference

Use this skill to build explicit APO datasets from:

- user-provided CSV or example rows
- research notes or source shortlists from the `researcher` agent
- synthesized examples that cover missing edge cases

Keep the authored eval manifest and APO datasets separate:

- `evals/evals.json` stays under the prompt or skill directory for realistic human review cases.
- `datasets/train.jsonl` and `datasets/val.jsonl` hold the evaluator-facing APO rows.
- If the prompt file lives under a `prompts/` directory, write datasets as a sibling `datasets/` directory one level higher.
- Otherwise, write datasets under `<prompt-dir>/datasets/`.

Each JSONL row should preserve the prompt interface and carry only evaluator-facing fields such as `expected`, `expected_json`, `reference`, `criteria`, and `scoring` outside the prompt-visible input path.
