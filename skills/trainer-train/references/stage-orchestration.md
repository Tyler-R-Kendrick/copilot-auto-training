# Stage orchestration

This skill owns the loop behavior around caller-supplied stage capabilities.

## Default stage order

When required support data is missing, use this order:

1. grounded research
2. dataset and eval synthesis
3. optimization
4. optional winner selection
5. validation

Always require at least one optimization pass for the selected target.

## Reuse rules

- Reuse train, validation, and authored eval assets when they already fit the selected target.
- Synthesize missing assets before optimization instead of guessing.
- Keep evaluation manifests, datasets, and workspace artifacts as separate outputs.

## Judge-mode inference

Infer the scoring mode from representative dataset rows:

- exact-match mode only for genuine exact `expected` tasks
- structured or normalization-aware mode when rows expose structured expectations or custom scoring
- open-ended judge mode when rows expose a reference answer plus grading criteria

## Manual follow-up branch

When optimization returns `mode=manual_followup`:

1. save the payload as `manual-followup-report.json`
2. answer the returned `model_prompt`
3. save the answer as `optimized-prompt.md`
4. continue the workflow with that candidate rather than treating the branch as a hard failure

## Validation and selection

- Validate after every meaningful candidate revision.
- Use a separate selection stage only when multiple optimization outputs need comparison.
- Persist the chosen candidate back to the selected source file only when validation passes and the decision summary justifies the write-back.
