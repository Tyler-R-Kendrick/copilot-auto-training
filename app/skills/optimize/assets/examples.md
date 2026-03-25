# Optimization Examples

## Example 1: Simple string input

**Invocation:**
```
/optimize prompt=prompts/support.md train=data/train.jsonl val=data/val.jsonl iterations=3
```

**Dataset row:**
```json
{"input": "How do I reset my password?", "expected": "Visit the account settings page and click 'Forgot password'."}
```

**Prompt template (`prompts/support.md`):**
```markdown
You are a helpful support agent. Answer the following user question concisely.

Question: {input}
```

---

## Example 2: Structured input

**Invocation:**
```
/optimize prompt=prompts/qa.md train=data/qa_train.jsonl val=data/qa_val.jsonl iterations=5 beam_width=4
```

**Dataset row:**
```json
{"input": {"question": "What is the capital of France?", "context": "Geography facts."}, "expected": "Paris"}
```

**Prompt template (`prompts/qa.md`):**
```markdown
Given the following context, answer the question accurately.

Context: {context}
Question: {question}
```

---

## Example 3: LLM judge fallback

**Invocation:**
```
/optimize prompt=prompts/creative.md train=data/creative_train.jsonl val=data/creative_val.jsonl judge_mode=llm_judge judge_prompt_file=skills/optimize/assets/judge-default.md
```

Use `llm_judge` only when exact or rule-based scoring is not possible (e.g., open-ended creative tasks).
