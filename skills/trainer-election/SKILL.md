---
name: trainer-election
description: Elect the strongest prompt candidate from an optimization field using baseline-aware leader election. Use when a prompt search step has produced one or more candidates that need final selection.
license: MIT
compatibility: Requires Python 3.11+, agentlightning, and openai packages. Works with the trainer-optimize skill in this repository.
metadata:
  author: your-org
  version: "0.1.0"

---

# Election

Use this skill to run the search-and-selection stage that elects a winning prompt from an optimization field.

## When to use this skill

- The optimizer already has a prompt plus train and validation datasets.
- Agent Lightning should search for improved prompt candidates.
- The final winner should be selected against the validation set with the original prompt included as a baseline.

Do not use this skill to gather datasets or validate prompt placeholders. That remains the responsibility of [skills/trainer-optimize/SKILL.md](../trainer-optimize/SKILL.md).

## Inputs

- `prompt_text`: baseline markdown prompt content
- `train_dataset`: parsed training tasks
- `val_dataset`: parsed validation tasks
- `algorithm`: search algorithm, currently `apo` or `verl`
- `iterations`, `beam_width`, `branch_factor`, `n_runners`: search controls
- `judge_mode`: validation scoring mode
- `n_variants`: fallback variant count when search yields a single candidate
- `steering_text`: optional carry-forward guidance from prior runs

## Election Behavior

1. Run the configured Agent Lightning search algorithm.
2. If multiple candidates exist, score them plus the baseline prompt.
3. If exactly one candidate exists, generate `n_variants` paraphrases and score those variants plus the baseline prompt.
4. Elect the leader with the highest adjusted validation score.
5. Persist candidate metadata so callers can write reports and summaries.

## Naming rationale

`election` is the right public name here because the skill owns the act of electing a winner from a field of candidates. It is direct, commonly understood, and still aligns with the academic framing of leader election. The helper `topk_select` still exists inside the runtime as one scoring primitive.