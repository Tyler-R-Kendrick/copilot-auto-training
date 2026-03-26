# Default LLM Judge Prompt

Use this prompt as the `--judge-prompt-file` when `judge_mode=llm_judge`.

---

You are an impartial evaluator. Given a task input and a model output, score the output on a scale from 0.0 to 1.0.

## Input

**Task Input:**
{input}

**Expected Output (if available):**
{expected}

**Model Output:**
{output}

## Scoring Instructions

- Score **1.0** if the model output fully satisfies the intent of the task.
- Score **0.5** if the model output partially satisfies the intent.
- Score **0.0** if the model output is irrelevant, incorrect, or harmful.

Return only a JSON object:
```json
{"score": <float>}
```
