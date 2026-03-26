# Usage Examples

## Example 1: Simple string input

**Prompt template (`prompts/support.md`):**
```markdown
You are a helpful support agent. Answer the following user question concisely.

Question: {input}
```

**Dataset row (`data/train.jsonl`):**
```json
{"input": "How do I reset my password?", "expected": "Visit the account settings page and click 'Forgot password'."}
```

**Invocation:**
```
/optimize prompt=prompts/support.md train=data/train.jsonl val=data/val.jsonl iterations=3
```

---

## Example 2: Structured multi-field input

**Prompt template (`prompts/qa.md`):**
```markdown
Given the following context, answer the question accurately.

Context: {context}
Question: {question}
```

**Dataset row (`data/qa_train.jsonl`):**
```json
{"input": {"question": "What is the capital of France?", "context": "Geography facts."}, "expected": "Paris"}
```

**Invocation:**
```
/optimize prompt=prompts/qa.md train=data/qa_train.jsonl val=data/qa_val.jsonl iterations=5 beam_width=4
```

---

## Example 3: LLM judge fallback (open-ended tasks)

Use `judge_mode=llm_judge` only when exact scoring is not possible.

**Invocation:**
```
/optimize prompt=prompts/creative.md train=data/creative_train.jsonl val=data/creative_val.jsonl judge_mode=llm_judge judge_prompt_file=assets/judge-default.md
```

---

## Example 4: Debug/smoke-test run

Run a quick sanity check without writing output files:

```
/optimize prompt=prompts/support.md train=data/train.jsonl val=data/val.jsonl debug_only=true
```

Equivalent CLI:
```bash
python scripts/run_optimize.py \
  --prompt-file prompts/support.md \
  --train-file data/train.jsonl \
  --val-file data/val.jsonl \
  --debug-only
```
