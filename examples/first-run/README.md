# First Run Example

This example gives you the smallest realistic optimization target in the repository.

It uses a classification prompt instead of open-ended text generation, which keeps validation deterministic and easier to inspect on a first run.

Files:

- `prompts/classify_support.md`
- `prompts/.evals/classify_support/train.jsonl`
- `prompts/.evals/classify_support/val.jsonl`

Smoke test:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --debug-only
```

Small full optimization run:

```bash
python skills/optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

While the full run is active, open the dashboard at `http://localhost:4747`.