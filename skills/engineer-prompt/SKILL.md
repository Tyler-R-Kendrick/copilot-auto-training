---
name: engineer-prompt
description: Improve broken prompts and context plans by choosing the smallest prompt-engineering technique that fits. Use this whenever the user asks how to rewrite or debug a prompt, compare prompt-design options, choose between grounding, structured output, examples, chaining, reasoning, or RAG for a prompt, or reduce prompt length by moving schemas, workflow specs, and repeated instructions into better structures.
license: MIT
compatibility: Requires Python 3.11+. Designed for markdown-first prompt work in VS Code agents.
metadata:
  author: Tyler Kendrick
  version: "0.2.0"

---

# Engineer Prompt

Use this skill to improve prompt design without defaulting to flashy techniques or empty prompt jargon.

Your job is to diagnose the task, decide whether the problem is actually prompt-related, recommend the smallest technique set that will help, explain the tradeoffs, and provide a concrete markdown prompt when a rewrite is useful.

Prompt engineering is not just naming a technique. Start with the failure mode. If the real problem is stale retrieval, missing tools, bad context, or unclear business requirements, say so directly instead of pretending a prompt pattern will fix it.

When the user is fighting token budget, prompt sprawl, schema-heavy output contracts, or instructions that keep getting dropped in long workflows, read `references/token-efficient-patterns.md` before recommending a rewrite.

## When to use this skill

- The user wants to improve a prompt.
- The user asks which prompt engineering technique to use.
- The user wants to compare multiple prompt patterns or prompting families.
- The user needs a concrete markdown prompt example.
- The user wants to debug why a prompt is underperforming.
- The user mentions grounding, examples, output schemas, reasoning style, prompt chaining, RAG, or determinism and needs help choosing among them.
- The user wants to reduce prompt length without losing critical instructions, or wants help placing schemas, workflow specs, or repeated constraints more effectively.

Do not use this skill when the core problem is clearly application logic, retrieval freshness, source quality, tool availability, or missing product requirements rather than prompt design. In those cases, say that prompt changes are secondary.

## Core workflow

Follow this order:

1. Diagnose the task shape and failure mode.
2. Decide whether prompt changes are enough.
3. Recommend the smallest effective technique or technique set.
4. Explain why it fits and what would be overkill.
5. Provide a markdown prompt or prompt rewrite when useful.

If multiple techniques could work, recommend one default and one fallback. Prefer the default that is easier to operate, validate, and maintain.

## Output contract

When responding, use this structure unless the user asks for something shorter:

1. `Task shape`: what the model is being asked to do
2. `Primary recommendation`: the default technique or technique set
3. `Why it fits`: why this is the right level of complexity
4. `Limits or bad fits`: when not to use it, or what it will not solve
5. `Markdown prompt`: a concrete prompt example or rewrite if prompt changes are appropriate

If prompt changes are not the main fix, say that explicitly before offering any prompt rewrite.

## Diagnose first

Check these failure modes before recommending a technique:

- unclear task objective
- missing domain context or evidence
- missing output schema or format contract
- too few examples for edge cases
- unnecessary examples that waste context
- the prompt is bloated by repeated policy text, giant schemas, or long workflow prose
- reasoning path is unclear and needs decomposition
- retrieval is missing, stale, or badly scoped
- tools are required but unavailable
- determinism or reproducibility matters more than creativity
- the prompt is over-constrained and suppresses useful output

If the root cause is not mainly prompt design, say what the real blocker is.

## Default selection heuristic

Use these defaults before escalating:

- Simple classification, rewriting, or summarization: clear instructions plus output priming.
- Extraction into JSON or fields: structured output first, then few-shot if edge cases are messy. Keep large schemas in referenced JSON Schema files when inline schema text starts to dominate the prompt.
- Multi-step transformation: task decomposition or prompt chaining.
- Grounded answering over provided evidence: grounding first.
- Large-document QA: vector RAG only when the evidence cannot fit directly in context.
- Long, stateful workflows: keep the prompt inline summary short and move the durable workflow representation into a referenced Mermaid or BPMN artifact when that reduces ambiguity and token load.
- Global relationship questions over a corpus: graph RAG only if relationships or communities matter.
- Tool-using workflows: ReAct when the model must inspect, search, or act.
- Hard reasoning with alternative paths: Tree-of-Thought or Graph-of-Thought only when branching is materially useful.
- Reliability-sensitive ambiguous tasks: self-consistency or reflexion only if the extra cost is justified.

Default against advanced patterns when basic prompt hygiene solves the problem.

## Response modes

### Rewrite mode

Use when the user already has a prompt and wants it improved.

- Diagnose what is missing.
- Keep the task intact unless the user asks to change the workflow.
- Rewrite the prompt in markdown.
- Explain only the changes that materially affect quality.

### Selection mode

Use when the user wants help choosing a technique.

- Name one primary technique.
- Name one fallback or complementary technique if relevant.
- Explain why the alternatives are weaker, costlier, or conditional.

### Debug mode

Use when the user asks why a prompt is failing.

- Identify whether the failure is prompt, context, retrieval, tooling, or requirements.
- Do not force a prompt-only answer when the system design is the main problem.
- Offer the smallest prompt change that still helps if prompt work is only part of the fix.

## Response pattern

When helping the user, follow this order:

1. Identify the task shape.
2. Recommend the smallest effective technique or technique set.
3. Explain why it fits.
4. Explain limitations or when not to use it.
5. Provide a markdown prompt example.

If multiple techniques could work, recommend a default and briefly note the next-best alternative.

## Prompt building blocks

Use these before moving to advanced techniques.

### Core task

Use when:
- the prompt needs a clear anchor
- the user has not stated exactly what the model must do

Avoid when:
- there is no real avoid case; every prompt needs a core task

Example:

```md
Summarize the main points from the following article.
```

### System instructions

Use when:
- the answer needs a stable role, standard, or format
- consistency matters across requests

Avoid when:
- the role is decorative and does not change the work
- the instruction block becomes a dumping ground for unrelated preferences

Example:

```md
You are a senior security reviewer. Prioritize exploitable risks and keep the review concise.
```

### Examples

Use when:
- the task is ambiguous without a pattern
- the user cares about style, structure, or edge-case handling

Avoid when:
- the examples are weak, noisy, or likely to overfit the model to superficial patterns

Example:

```md
Input: What is the capital of France?
Output: Paris
```

### Contextual information

Use when:
- the model needs background documents, definitions, tables, or assumptions

Avoid when:
- the added context is stale, irrelevant, or too large to be useful as-is

Example:

```md
Based on the attached project brief document, summarize the deliverables.
```

## In-context learning techniques

### Zero-shot

Use when:
- the task is straightforward
- you want a quick baseline

Avoid when:
- the task requires a very specific format, style, or unusual reasoning pattern

Example:

```md
Translate the following sentence to French: "Where is the library?"
```

### Few-shot

Use when:
- one or two examples can resolve ambiguity cheaply

Avoid when:
- the examples are not representative
- structured output alone would already solve the problem

Example:

```md
Q: What is the capital of France?
A: Paris
Q: What is the capital of Italy?
A: Rome
Q: What is the capital of Germany?
A:
```

### Multi-shot

Use when:
- several examples are needed to cover variation or edge cases

Avoid when:
- the prompt becomes dominated by demonstrations instead of the real task

Example:

```md
Translate the following:
English: Hello | French: Bonjour
English: Good morning | French: Bonjour
English: Good night | French:
```

## Basic techniques

### Clear and specific instructions

Use when:
- the current prompt is vague or underspecified

Avoid when:
- the real issue is missing data or missing context rather than wording

Example:

```md
Summarize the primary causes of climate change in three bullet points, each with a one-sentence explanation.
```

### Reference text and citations

Use when:
- factual accuracy matters
- the user wants traceability to a source

Avoid when:
- no trustworthy source text is available

Example:

```md
Based on the information provided in the following text, answer the question and include a citation for your sources.
```

### Task decomposition

Use when:
- the task has multiple stages
- the model is more reliable when steps are explicit

Avoid when:
- the task is simple enough to solve directly

Example:

```md
1. Pull data from the attached table.
2. Summarize key trends.
3. Suggest one actionable next step.
```

### Instruction placement

Use when:
- the prompt contains a mix of task, context, and formatting requirements
- information ordering is likely to influence output quality

Avoid when:
- the prompt is so short that additional structure adds no value

Example:

```md
Context:
[Relevant content]

Task:
[Instruction statement]

Formatting:
[How you want the answer structured]
```

### Interspersed repetition

Use when:
- one or two instructions are genuinely high-risk and easy to forget by the time the model reaches the output stage
- the prompt has distinct phases such as retrieval, transformation, and final formatting

Avoid when:
- you repeat whole paragraphs or policies verbatim
- every instruction gets repeated and the repetition stops carrying signal

Example:

```md
Task:
Review the incident notes and return only confirmed causes.

Critical rule:
Do not invent causes that are not supported by the notes.

Output:
Return JSON only.
Before emitting the final JSON, re-check that every cause is directly supported by the notes.
```

### Output priming and syntax

Use when:
- the model needs a concrete output pattern
- formatting consistency matters

Avoid when:
- the requested template is so rigid that it suppresses useful content

Example:

```md
List three types of renewable energy. Answer in the following format:

- Solar
- Wind
- Hydroelectric
```

## Reasoning techniques

### Chain-of-Thought

Use when:
- the task benefits from stepwise reasoning or decomposition

Avoid when:
- the task is simple extraction or direct lookup
- long visible reasoning adds cost without improving the answer

Example:

```md
When I was 3 years old, my partner was 3 times my age. Now, I am 20 years old. How old is my partner? Let's think step by step.
```

### Tree-of-Thought

Use when:
- the task requires comparing alternatives or branching search paths

Avoid when:
- there is an obvious linear path and branching would only add latency

Example:

```md
Explore three possible rollout strategies for this migration. Evaluate tradeoffs for risk, cost, and rollback complexity before choosing one.
```

### Graph-of-Thought

Use when:
- the problem has interdependent subproblems or linked ideas

Avoid when:
- a chain or tree structure is already sufficient

Example:

```md
Analyze climate change as an interconnected problem. Map economic impacts, renewable energy adoption, and policy options, then show how those ideas influence one another before proposing a solution.
```

### Sketch-of-Thought

Use when:
- concise symbolic reasoning is useful
- token efficiency matters in a structured domain
- mathematical language, variable names, or compact invariants would compress the reasoning without hiding the result

Avoid when:
- the audience needs plain-language explanation
- shorthand notation would make the answer harder to use
- the notation would be more expensive to explain than the natural-language reasoning it replaces

Example:

```md
Reason about the logic puzzle using concise symbolic notation where useful, then translate the final answer into plain English.
```

### Active Prompts and ReasonFlux

Use when:
- iterative clarification improves the result
- the application is interactive

Avoid when:
- the user wants a one-shot response and the task is already clear

Example:

```md
If the request is ambiguous, ask up to two clarifying questions before answering. Use each response to refine the next step of your analysis.
```

### ReAct

Use when:
- the model needs to reason and use tools together
- the answer depends on external information or actions

Avoid when:
- no tools are available
- the answer can be produced entirely from the provided context

Example:

```md
Use available tools to answer this question. Alternate between reasoning about what you need and acting to gather the missing facts before giving the final answer.
```

### Prompt chaining

Use when:
- a large task can be split into clear sub-prompts
- each stage benefits from separate validation

Avoid when:
- the coordination overhead outweighs the task complexity

Example:

```md
Step 1: Extract the relevant clauses.
Step 2: Summarize the obligations.
Step 3: Convert them into an implementation checklist.
```

### Self-consistency

Use when:
- the task is ambiguous and reliability matters
- multiple reasoning attempts can be aggregated

Avoid when:
- latency and token cost are tighter constraints than accuracy gains

Example:

```md
Classify this email three separate times using independent reasoning, then return the label that appears most consistently.
```

### Reflexion

Use when:
- self-critique is likely to catch mistakes
- the task benefits from draft, review, and revision

Avoid when:
- the answer is trivial or easily validated externally in one pass

Example:

```md
Draft the answer first. Then review your own response for errors, missing assumptions, or weak reasoning, and provide a corrected final version.
```

## Retrieval-augmented generation techniques

### Naive RAG / Cache Augmented Generation

Use when:
- the full source document fits comfortably in context
- simplicity matters more than retrieval sophistication

Avoid when:
- the context is too large
- lost-in-the-middle effects are likely

Example:

```md
Use the complete document below to answer the question. Prefer details from the document over general knowledge.

${document}
```

### Self-RAG

Use when:
- the system should determine whether retrieval is needed and critique its own groundedness

Avoid when:
- you cannot instrument the model or workflow for retrieve-generate-critique behavior

Example:

```md
Before answering, determine whether your current context is sufficient. If it is not, say retrieval is needed and explain what information is missing.
```

### Vector RAG

Use when:
- semantic similarity search over a large corpus is the main requirement
- the user asks local questions about documents

Avoid when:
- global dataset questions matter more than local chunk similarity
- chunking or embeddings are poorly designed

Example:

```md
Retrieve the most semantically relevant chunks for the question, then answer using only those chunks and cite them.
```

### Graph RAG

Use when:
- the user asks global or relationship-heavy questions over a dataset

Avoid when:
- ingestion cost is too high for the value
- the corpus is small enough that graph construction is unnecessary

Example:

```md
Use the knowledge graph summaries to answer this global question about relationships across the dataset, not just one document.
```

### Path RAG

Use when:
- graph-style traversal is helpful but full graph summaries are unnecessary

Avoid when:
- a simpler vector or grounded approach already answers the question well

Example:

```md
Traverse the most relevant node and edge paths for this question, then answer using the strongest path-supported evidence.
```

### Agentic RAG

Use when:
- retrieval is best delegated across domain-specialized agents
- a mixture-of-experts approach improves coverage

Avoid when:
- traceability and debugging simplicity are more important than delegation

Example:

```md
Ask the relevant specialist agents for retrieval support, combine their findings, and synthesize a final answer that reflects the strongest evidence from each agent.
```

## Parameter tuning techniques

### Temperature and top_p

Use when:
- the prompt is already clear and you need to control creativity versus determinism

Avoid when:
- the prompt itself is poorly designed
- you expect parameter changes to compensate for missing requirements

Example:

```md
Extract the invoice total and currency from the text below. Return a deterministic JSON object.

Recommended settings: temperature=0, top_p=1
```

### Seed values

Use when:
- reproducibility matters for demos, tests, or evaluations

Avoid when:
- the platform does not expose a seed parameter
- exact repeatability is not important

Example:

```md
Generate the response using a fixed seed so this prompt can be evaluated reproducibly across runs.
```

### Model-specific parameters

Use when:
- you need max token control, stop sequences, top_k, or platform-specific formatting controls

Avoid when:
- you have not verified what the target model actually supports

Example:

```md
Return a JSON object with exactly these fields and stop immediately after the closing brace.
```

## Constrained decoding techniques

### Grounding

Use when:
- factual accuracy is critical
- the answer must stay inside provided evidence

Avoid when:
- source material is weak or incomplete
- the task requires broader synthesis beyond the supplied context

Example:

```md
Based ONLY on the following provided documents, answer the user's question. If the answer cannot be found in the provided context, respond with "I cannot find this information." Include citations.

[PROVIDED DOCUMENTS]
${documentContext}

User Question: ${userQuestion}
```

### Logit biasing

Use when:
- the API supports token-level controls
- you need to encourage or suppress particular tokens or phrases

Avoid when:
- token IDs are unavailable
- overuse would distort generation quality

Example:

```md
Use the approved terminology consistently and avoid deprecated wording. If the platform supports token-level controls, pair this prompt with logit biasing for the critical terms.
```

### Structured output

Use when:
- the response feeds a downstream system, API, evaluator, or automation pipeline

Avoid when:
- the user wants open-ended creative output
- the schema is so large that it overwhelms the task
- the prompt is carrying a large canonical schema inline when a referenced JSON Schema file or URL would keep the active instructions much smaller

Example:

```md
Extract the order details and return valid JSON.

Canonical schema: references/order.schema.json
Critical inline constraints:
- `order_id` is required
- `status` must be one of `pending`, `shipped`, `delivered`, `cancelled`
- `customer_email` may be null

Input:
${orderText}
```

## Technique combinations that usually work

- Clear instructions plus output priming: default for most rewrites.
- Structured output plus few-shot: extraction tasks with messy inputs.
- Grounding plus vector RAG: evidence-based QA when the corpus is too large for direct context.
- Task decomposition plus ReAct: tool-using workflows.
- Prompt chaining plus structured output: multi-stage pipelines where intermediate outputs matter.

Combine techniques only when each one has a distinct job.

Example:

```md
Extract the following information from the text and return valid JSON:

{
  "name": "string",
  "email": "string",
  "phone": "string",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip": "string"
  }
}

Text to extract from:
${inputText}
```

## Best-practice overlay

Apply these rules across all techniques:

- Define clear objectives.
- Provide the right context and background.
- Demonstrate with examples when examples add real signal.
- Be precise and descriptive.
- Iterate and experiment instead of assuming the first prompt is optimal.
- Use positive instructions before piling on constraints.
- Order information deliberately.
- Offer alternative paths when multiple outputs are acceptable.
- Optimize token usage after correctness is achieved.
- Treat prompt engineering as iterative diagnosis, not one-shot style polishing.

## Token-budget guidance

When token budget or instruction persistence is part of the problem, use these defaults:

- Keep the live prompt focused on the task, the few constraints that truly matter, and the output contract.
- Put bulky canonical schemas in referenced JSON Schema documents instead of pasting large schemas inline.
- Put durable workflow structure in a referenced Mermaid or BPMN file when the workflow is long, stateful, or easier to verify as a diagram than as prose.
- Use interspersed repetition for the smallest possible restatement of the highest-risk rule near the step where the rule matters.
- Use sketch-of-thought or compact mathematical language only when the task is structured enough that notation shrinks the reasoning instead of obscuring it.
- Read `references/token-efficient-patterns.md` when the user explicitly asks about token optimization, instruction persistence, schema placement, or workflow formalization.

## Decision heuristic

Use this escalation path by default:

1. Start with a clear core task.
2. Add system instructions, context, or examples if needed.
3. Use basic techniques like decomposition or output priming.
4. Move to reasoning, retrieval, or constrained decoding only when the task actually requires them.
5. Tune parameters only after the prompt itself is doing the right job.

## Final rule

Do not recommend advanced techniques just because they sound sophisticated. Prefer the simplest technique that reliably solves the user's task, and say when prompting is not the real fix.