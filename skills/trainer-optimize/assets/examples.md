# Usage Examples

## Example 0: Copy-paste first run from this repo

If you want a ready-to-run example without writing your own prompt first, use the files under `examples/first-run/`.

**Prompt template (`examples/first-run/prompts/classify_support.md`):**
```markdown
You are a support intent classifier.
Return exactly one label from this list: reset_password, update_email, refund_request.
Request: {input}
```

**Run a smoke test:**
```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --debug-only
```

**Run a small full optimization:**
```bash
python skills/trainer-optimize/scripts/run_optimize.py \
  --prompt-file examples/first-run/prompts/classify_support.md \
  --iterations 2 \
  --beam-width 2 \
  --branch-factor 2
```

---

## Example 1: Simple string input

**Prompt template (`prompts/support.md`):**
```markdown
You are a helpful support agent. Answer the following user question concisely.

Question: {input}
```

**Authored eval manifest (`prompts/evals/evals.json`):**
```json
{"skill_name": "support-skill", "evals": [{"id": 1, "prompt": "How do I reset my password?", "expected_output": "A support answer that explains the password reset steps clearly.", "assertions": ["The answer mentions the reset flow."]}]}
```

**Invocation:**
```
/trainer-optimize prompt=prompts/support.md iterations=3
```

---

## Example 2: Structured multi-field input

**Prompt template (`prompts/qa.md`):**
```markdown
Given the following context, answer the question accurately.

Context: {context}
Question: {question}
```

**Authored eval manifest (`prompts/evals/evals.json`):**
```json
{"skill_name": "qa-skill", "evals": [{"id": 1, "prompt": "Given geography facts, what is the capital of France?", "expected_output": "A direct answer that says Paris.", "assertions": ["The answer names Paris."]}]}
```

**Invocation:**
```
/trainer-optimize prompt=prompts/qa.md iterations=5 beam_width=4 judge_mode=custom
```

---

## Example 3: LLM judge fallback (open-ended tasks)

Use `judge_mode=llm_judge` only when exact scoring is not possible.

**Invocation:**
```
/trainer-optimize prompt=prompts/creative.md judge_mode=llm_judge judge_prompt_file=assets/judge-default.md
```

Dataset rows can use evaluator-only fields without leaking them into the prompt render path:

```json
{"input": "Draft a reply for a delayed shipment", "reference": "Reference answer here", "criteria": ["correctness", "policy compliance"], "scoring": "llm_judge"}
```

---

## Example 4: Alternative algorithm

Use `algorithm=verl` when you explicitly want the alternate optimization path.

**Invocation:**
```
/trainer-optimize prompt=prompts/support.md algorithm=verl
```

---

## Example 5: Generate explicit JSONL files from CSV

If you already have a CSV with `input` and `expected` columns, generate explicit datasets for APO:

```bash
python scripts/generate_jsonl.py \
  --prompt-file prompts/support.md \
  --csv-file examples.csv
```

This writes JSONL dataset files that you can pass explicitly to `run_optimize.py`.

---

## Example 6: Debug/smoke-test run

Run a quick sanity check without writing output files:

```
/trainer-optimize prompt=prompts/support.md debug_only=true
```

Equivalent CLI:
```bash
python scripts/run_optimize.py \
  --prompt-file prompts/support.md \
  --debug-only
```
