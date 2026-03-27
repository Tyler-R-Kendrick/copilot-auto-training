# First Run Example

This example gives you the smallest realistic optimization target in the repository.

It uses a classification prompt instead of open-ended text generation, which keeps validation deterministic and easier to inspect on a first run.

Files:

- `prompts/classify_support.md`
- `prompts/evals/evals.json`
- `datasets/train.jsonl`
- `datasets/val.jsonl`

Smoke test:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --debug-only
```

Small full optimization run:

```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --train-file examples/first-run/datasets/train.jsonl \
  --val-file examples/first-run/datasets/val.jsonl \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

While the full run is active, open the dashboard at `http://localhost:4747`.