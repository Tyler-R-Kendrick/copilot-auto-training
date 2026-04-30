# Research Brief: agentic-workflow-editing.instructions.md

## Target File

`.github/instructions/agentic-workflow-editing.instructions.md`

## Optimization Goal

The instruction file guides agents that edit agentic workflow markdown files under `.github/workflows/*.md`. The key success criterion is that agents **never leave the source file and its `.lock.yml` out of sync**. The current 4-bullet format is minimal but leaves several actionable gaps.

## Source Material

The source material is drawn from the existing engineer-prompt review and the repository tooling:
- `engineer-prompt/review.md` — identifies gaps, failure modes, and optimization hypothesis
- `.github/hooks/agentic-workflow-validation.py` (if present) — enforcement logic
- `gh aw compile <workflow-name>` — the compile command
- Existing `train-prompt.md` and `train-prompt.lock.yml` as the canonical example

## Key Findings

1. **Missing ordered checklist**: Agents need a mechanical 3-step sequence: edit → compile → verify diff → commit both files.
2. **No concrete example**: `gh aw compile train-prompt` should appear as the canonical illustration.
3. **Ambiguous "meaningful" trigger**: Any edit to frontmatter, imports, or step logic counts — default to recompile if unsure.
4. **Missing final checkpoint**: Run `gh aw compile` one last time before opening a pull request.
5. **Hook not explained**: Agents don't know what `agentic-workflow-validation` checks, so they can't reason about enforcement.

## Evaluation Schema

Rows follow `llm_judge` scoring with:
- `input`: a user question or scenario related to editing workflow files
- `expected`: the correct guidance derived from the instruction file
- `scoring`: `"llm_judge"`
- `criteria`: a rubric string for the judge

## Dataset Gap Assessment

No explicit train/val JSONL datasets exist for this target. Synthesis required.

## Source Approval

Grounded from the current instruction file content and the `engineer-prompt/review.md`. No external sources required; the gap analysis is sufficient to synthesize high-quality eval rows.
