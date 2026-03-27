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

## Election Behavior

1. Run the configured Agent Lightning search algorithm.
2. If multiple candidates exist, score them plus the baseline prompt.
3. If exactly one candidate exists, generate `n_variants` paraphrases and score those variants plus the baseline prompt.
4. Elect the leader with the highest adjusted validation score.