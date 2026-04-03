# DSPy Prompt Artifact Patterns

Use this reference when the task is about optimizing prompt-like markdown with DSPy and still exporting a stable checked-in artifact.

## Practical default

DSPy is strongest when you describe prompt behavior as code and let the optimizer improve the prompt strategy around that code.

The practical pattern is:

1. define a `dspy.Signature` or `dspy.Module`
2. compile it with an optimizer such as `MIPROv2`
3. save the compiled DSPy program
4. export the optimized content into a deterministic markdown artifact

Treat DSPy as the optimizer and your renderer as the packaging step.

## Instruction-only optimization

Prefer instruction-only optimization when the final goal is a clean checked-in prompt artifact.

Why:

- demo-heavy optimization can improve runtime quality but often exports poorly as one neat markdown file
- zero-demo settings bias the result toward a reusable instruction artifact
- deterministic rendering gives cleaner diffs and a more stable repository contract

## Smallest useful DSPy surfaces

### `dspy.Signature`

Use for:

- one prompt template
- one instruction body
- one prompt artifact writer with a clear input/output contract

### `dspy.Module`

Use for:

- a prompt plus a critique step
- a planner plus renderer pair
- a small artifact-writing workflow with helper predictors

Keep the boundary small enough that the feedback still points at one coherent prompt behavior.

## Export choices

### DSPy writes the full file

Use when:

- formatting variance is acceptable
- strong evals already enforce the final file shape
- flexibility matters more than stable diffs

### DSPy writes only the trainable body

Use when:

- front matter must remain fixed
- section layout must remain fixed
- the repository expects stable markdown artifacts
- reviewers care about small readable diffs

This is the default for `SKILL.md`-style artifacts.

## Metric guidance

Prefer downstream evals when they already exist.

When you need structural checks, verify:

- valid front matter
- explicit trigger conditions
- concrete instructions
- a clear output contract
- forbidden behaviors or boundaries
- compatibility with actual runtime tools and file shape

## Risks

Call out these tradeoffs before recommending DSPy:

- no repeatable feedback means weak optimization pressure
- overly broad trainable surfaces make exported artifacts harder to trust
- few-shot-heavy optimized programs may not map cleanly to one neat checked-in file
- stale retrieval, missing tools, or weak source material are not prompt-optimization problems first
