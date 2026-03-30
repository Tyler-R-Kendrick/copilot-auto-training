# Source Analysis

This file summarizes each markdown source under the workshop path `slides/prompt-engineering/` and converts it into actionable skill guidance.

## Module map

### 01_Introduction_to_Prompt_Engineering.md

Findings:
- Establishes the enterprise framing for prompt engineering.
- Emphasizes structure, safety, effectiveness, and measurable evaluation.
- Treats prompt work as something to optimize with rubrics rather than intuition alone.

How the skill should use it:
- Treat prompt design as an engineering task with explicit goals and evaluation criteria.
- Prefer prompts that can be reviewed, iterated, and measured.

### 02_Types_of_Prompts.md

Findings:
- Defines zero-shot, few-shot, and multi-shot prompting.
- Frames examples as a way to demonstrate format, style, or task logic.

How the skill should use it:
- Decide whether the task needs no examples, a few strong examples, or a broader demonstration set.
- Avoid examples when they add noise without reducing ambiguity.

### 03_Anatomy_of_an_Effective_Prompt.md

Findings:
- Breaks prompts into system instructions, examples, contextual information, and roles.
- Emphasizes explicit tasks, optional layers, and role clarity.

How the skill should use it:
- Start prompt rewrites by checking whether objective, role, context, and output expectations are explicit.
- Add optional layers only when they improve accuracy.

### 04_Prompt_Engineering_Techniques.md

Findings:
- Organizes the workshop into basic techniques, reasoning techniques, RAG, parameter tuning, and constrained decoding.
- Implies a layered approach rather than a single universal pattern.

How the skill should use it:
- Route each prompt problem into the correct family before proposing fixes.

### 04.1_Prompt_Engineering_Techniques.Basic_Techniques.md

Findings:
- Covers clear and specific instructions, reference text and citations, task decomposition, instruction placement, and output priming.

How the skill should use it:
- Default to these techniques before escalating to advanced methods.

### 04.2_Prompt_Engineering_Techniques.Reasoning_Techniques.md

Findings:
- Covers Chain-of-Thought, Tree-of-Thought, Graph-of-Thought, Sketch-of-Thought, Active Prompts and ReasonFlux, ReAct, Prompt Chaining, Self-Consistency, and Reflexion.

How the skill should use it:
- Apply these only to tasks that benefit from explicit decomposition, branching, tool use, or iterative correction.

### 04.3_Prompt_Engineering_Techniques.RAG.md

Findings:
- Covers naive RAG/CAG, Self-RAG, Vector RAG, Graph RAG, Path RAG, and Agentic RAG.
- Includes tradeoffs between simplicity, cost, traceability, global reasoning, and ingestion complexity.

How the skill should use it:
- Recommend retrieval patterns based on source size, freshness, traceability, and query type.

### 04.4_Prompt_Engineering_Techniques.Parameter_Tuning.md

Findings:
- Covers temperature, top_p, seed values, max tokens, stop sequences, and model-specific parameters.
- Recommends iterative experimentation and documentation.

How the skill should use it:
- Treat parameter tuning as a second-order control after the prompt is already clear.

### 04.5_Prompt_Engineering_Techniques.Constrained_Decoding.md

Findings:
- Covers grounding, logit biasing, and structured output.
- Emphasizes reliability, machine readability, and auditable outputs.

How the skill should use it:
- Prefer these techniques for factual, compliant, or machine-consumed outputs.

### 06_Best_Practices_for_Effective_Prompts.md

Findings:
- Covers clear objectives, context and background, examples, iteration, positive instructions, information order, alternative paths, and token efficiency.

How the skill should use it:
- Apply these as default hygiene rules to every recommended prompt.

### 09_Resources_for_Further_Learning.md

Findings:
- Curates external documentation and papers.
- Supports provenance and further study rather than direct runtime technique selection.

How the skill should use it:
- Use for citations, deeper explanation, or follow-up reading.

## Technique catalog

Each section below gives the guidance the skill should apply when the user needs that technique.

### Zero-shot

Apply when:
- the task is simple, well-bounded, and the desired output can be stated directly
- you want the smallest, most reusable prompt

Not appropriate when:
- the output style is unusual
- edge cases are important and examples would remove ambiguity

Example prompt:

```md
Summarize the following incident report in 4 bullet points. Focus on root cause, impact, mitigation, and next step.
```

### Few-shot

Apply when:
- the task needs a particular tone, schema, or transformation pattern
- one or two examples can resolve ambiguity cheaply

Not appropriate when:
- examples are noisy, unrepresentative, or too numerous for the context budget
- the model may overfit to superficial details from the examples

Example prompt:

```md
Convert user requests into SQL.

Example 1:
User: Show all active users
SQL: SELECT * FROM users WHERE status = 'active';

Example 2:
User: Count California users
SQL: SELECT COUNT(*) FROM users WHERE state = 'CA';

Now convert this request:
User: Find admins created this month
SQL:
```

### Multi-shot

Apply when:
- the task has multiple edge cases or label variants that one example cannot cover
- robustness matters more than minimal prompt size

Not appropriate when:
- the prompt is becoming dominated by examples instead of the real task
- simpler few-shot examples already work

Example prompt:

```md
Classify each ticket as billing, outage, access, or other.

Ticket: "My invoice total looks wrong"
Label: billing

Ticket: "The dashboard times out for everyone on my team"
Label: outage

Ticket: "I cannot reset my password"
Label: access

Ticket: "Can you explain your SOC 2 status?"
Label:
```

### System instructions

Apply when:
- the response needs a stable role, tone, or operating policy
- quality depends on consistent behavior across requests

Not appropriate when:
- the role is decorative rather than useful
- the system message bloats the prompt with style rules unrelated to the job

Example prompt:

```md
You are a senior security reviewer. Prioritize exploitable risks, cite the code path you relied on, and keep the review concise.
```

### Contextual information

Apply when:
- the model needs background documents, facts, audience context, or business constraints

Not appropriate when:
- the context is irrelevant, stale, or too large to fit without filtering

Example prompt:

```md
Context:
- Audience: backend engineers
- Service: payment settlements
- Constraint: no schema changes this quarter

Task:
Propose a rollback-safe fix for the failed settlement retry job.
```

### Role prompting

Apply when:
- expertise framing changes what good output looks like
- you need a domain perspective such as security, legal, or data engineering

Not appropriate when:
- the role is vague or conflicts with the actual task

Example prompt:

```md
Act as a staff data engineer reviewing this ETL design for correctness, failure recovery, and observability.
```

### Clear and specific instructions

Apply when:
- the current prompt is vague
- the model needs explicit scope, output depth, or format

Not appropriate when:
- you already have precise instructions and the problem is missing context or missing tools

Example prompt:

```md
Write a Python function `parse_invoice_total(text: str) -> Decimal`.
Handle currency symbols, thousands separators, and malformed inputs. Return structured errors for invalid totals.
```

### Reference text and citations

Apply when:
- factual accuracy matters
- the user needs traceable answers tied to provided evidence

Not appropriate when:
- there is no reliable source text to cite
- the task is creative and citations would only add noise

Example prompt:

```md
Using only the policy excerpt below, answer the question and cite the exact quoted sentence that supports your answer.

[POLICY]
${policy_text}

Question: ${question}
```

### Task decomposition

Apply when:
- the task mixes extraction, analysis, and recommendation
- one instruction block would be too cognitively dense

Not appropriate when:
- the task is short enough to stay in one direct instruction

Example prompt:

```md
Complete this in order:
1. Extract the relevant metrics from the table.
2. Summarize the top 3 trends.
3. Recommend one operational action.
```

### Instruction placement

Apply when:
- the prompt contains both context and rules
- output quality depends on ordering the most important information clearly

Not appropriate when:
- the prompt is already short and structurally obvious

Example prompt:

```md
Task:
Review the API change for backward compatibility.

Context:
${api_diff}

Formatting:
Return exactly 3 bullets: breakage risk, affected clients, recommended fix.
```

### Output priming and syntax

Apply when:
- the output needs a stable format
- a sample answer or template will improve consistency

Not appropriate when:
- the template is so rigid that it hides useful reasoning or nuance

Example prompt:

```md
List 3 rollback checks in this format:

- Check name: <name>
  Why it matters: <one sentence>
```

### Chain-of-Thought

Apply when:
- the task requires multi-step reasoning or arithmetic
- an explicit reasoning scaffold improves accuracy

Not appropriate when:
- the task is simple extraction or classification
- long reasoning text would leak internal deliberation without adding value

Example prompt:

```md
Solve the capacity-planning problem step by step, then give the final answer in one sentence.
```

### Tree-of-Thought

Apply when:
- the task requires comparing multiple solution paths or plans
- backtracking is useful

Not appropriate when:
- there is an obvious single path and branching would only add cost

Example prompt:

```md
Explore 3 possible rollout plans for this migration. Evaluate each against risk, effort, and rollback complexity, then choose the best plan.
```

### Graph-of-Thought

Apply when:
- the problem has interdependent entities or relationships
- reasoning needs to connect multiple linked facts

Not appropriate when:
- a linear chain or table is enough

Example prompt:

```md
Map the dependencies between services, queues, and scheduled jobs, then identify the smallest change set that prevents duplicate billing.
```

### Sketch-of-Thought

Apply when:
- concise symbolic or shorthand reasoning is valuable
- token efficiency matters in a structured domain

Not appropriate when:
- the user needs plain-language explanation
- shorthand notation would confuse the audience

Example prompt:

```md
Reason using concise symbols where helpful, then translate the final answer into plain English for the operator.
```

### Active Prompts and ReasonFlux

Apply when:
- iterative refinement or clarifying questions improve quality
- the workflow benefits from feedback loops

Not appropriate when:
- the user needs a one-shot answer and the task is already clear

Example prompt:

```md
If any requirement is ambiguous, ask up to 2 targeted clarifying questions before drafting the migration plan.
```

### ReAct

Apply when:
- the model must reason and use tools together
- the answer depends on external search, execution, or lookup

Not appropriate when:
- no tools are available
- the answer can be produced from provided context alone

Example prompt:

```md
Use the available tools to inspect the repository, reason about the failure, and then propose the smallest safe fix.
```

### Prompt Chaining

Apply when:
- the workflow naturally breaks into sequential stages
- each stage can be validated independently

Not appropriate when:
- the overhead of chaining exceeds the task complexity

Example prompt:

```md
Stage 1: Extract policy clauses relevant to data retention.
Stage 2: Summarize the obligations.
Stage 3: Produce a checklist for engineering implementation.
```

### Self-Consistency

Apply when:
- reliability benefits from comparing multiple reasoning attempts
- the task is ambiguous or error-prone

Not appropriate when:
- latency or token cost matters more than marginal accuracy gains

Example prompt:

```md
Generate 3 independent solutions to the scheduling problem, compare them, and return the answer that is most consistent across attempts.
```

### Reflexion

Apply when:
- self-critique can catch likely errors
- the task needs a draft-and-revise cycle

Not appropriate when:
- the first-pass answer is easy to validate externally and self-review would waste time

Example prompt:

```md
Draft the deployment checklist, then review your own output for missing rollback steps and revise it once.
```

### Naive RAG / CAG

Apply when:
- the source set is small enough to fit in context
- retrieval complexity would be overkill

Not appropriate when:
- the documents are too large for the context window
- lost-in-the-middle effects are likely

Example prompt:

```md
Use the complete runbook below to answer the operator's question. Prefer exact procedures from the runbook over general knowledge.

${runbook}
```

### Self-RAG

Apply when:
- the system can decide whether retrieval is needed and can critique its own answer quality

Not appropriate when:
- you cannot fine-tune or instrument the model
- the extra complexity is unjustified

Example prompt:

```md
Before answering, determine whether the provided evidence is sufficient. If not, say retrieval is required and explain what information is missing.
```

### Vector RAG

Apply when:
- the corpus is large and semantic similarity search is useful
- the user asks local questions against many documents

Not appropriate when:
- global dataset questions matter more than local document similarity
- the embedding and chunking strategy is weak or unstable

Example prompt:

```md
Retrieve the 5 most relevant design-note chunks for the question, then answer using only those chunks and cite chunk IDs.
```

### Graph RAG

Apply when:
- the user asks global questions over entities and relationships
- ontology or community-summary reasoning matters

Not appropriate when:
- ingestion cost and graph maintenance are unjustified
- the corpus is too small for graph structure to help

Example prompt:

```md
Use the knowledge graph summaries to explain which customer-impacting incidents are most connected to the payments platform and why.
```

### Path RAG

Apply when:
- graph-style reasoning helps but full community summaries are unnecessary
- you need path traversal over linked entities

Not appropriate when:
- simple retrieval already answers the question

Example prompt:

```md
Traverse the graph paths connecting this incident to the upstream dependency chain and answer using the shortest evidence-backed path.
```

### Agentic RAG

Apply when:
- retrieval is naturally delegated to specialist tools or agents
- domain experts or tool-specialized agents outperform one generic retriever

Not appropriate when:
- debugging and traceability are more important than modular delegation

Example prompt:

```md
Ask the compliance agent for policy evidence, the data agent for schema context, and the ops agent for runtime facts. Combine their findings into one grounded answer.
```

### Temperature and top_p

Apply when:
- the prompt is already stable and you need more determinism or more creativity

Not appropriate when:
- the prompt itself is ambiguous
- the team expects parameter changes to fix missing instructions

Example prompt:

```md
Task: Generate 5 taglines for the product launch.
Note: Use higher creativity settings only after confirming the structure and audience are correct.
```

### Seed values

Apply when:
- reproducibility matters for demos, tests, or evaluation

Not appropriate when:
- the platform does not expose a seed value

Example prompt:

```md
Run this benchmark prompt with a fixed seed so the comparison is reproducible across iterations.
```

### Model-specific parameters

Apply when:
- you need max token limits, stop sequences, top_k, or platform-specific output controls

Not appropriate when:
- you have not checked whether the target model supports those controls

Example prompt:

```md
Return a JSON object and stop generation immediately after the closing brace.
```

### Grounding

Apply when:
- answers must stay inside trusted evidence
- hallucination risk is unacceptable

Not appropriate when:
- no reliable grounding source is available
- the task needs broad synthesis beyond the provided context

Example prompt:

```md
Based only on the documents below, answer the question. If the answer is not supported by the documents, say "I cannot find this in the provided context." Include citations.

${documents}

Question: ${question}
```

### Logit biasing

Apply when:
- the platform supports token-level control and you need to encourage or suppress specific tokens

Not appropriate when:
- token IDs are unavailable or portability matters
- overuse would distort generation quality

Example prompt:

```md
Prefer the approved terminology in the output and suppress deprecated product names when the API supports token-level biasing.
```

### Structured output

Apply when:
- another program, evaluator, or workflow consumes the answer
- fields must be validated or parsed automatically

Not appropriate when:
- the user wants open-ended brainstorming
- the schema is larger than the value it provides

Example prompt:

```md
Extract the incident details and return valid JSON using this schema:

{
  "service": "string",
  "severity": "SEV1|SEV2|SEV3",
  "customer_impact": "string",
  "next_action": "string"
}

Text:
${incident_text}
```

## Cross-cutting best practices from module 06

Apply these defaults unless the user asks otherwise:

- define the exact objective
- provide background that changes the answer
- prefer positive instructions over long prohibition lists
- order information intentionally
- offer fallback paths when multiple acceptable outcomes exist
- keep prompts token-efficient once correctness is achieved
- iterate based on actual outputs, not just style preferences

## Practical notes for this skill

- Combine techniques only when each one has a distinct role.
- If a prompt needs facts from outside the current context, say that retrieval or grounding is required.
- If a prompt needs reproducibility, recommend seeds and stable settings.
- If a prompt will feed automation, recommend structured output and validation.