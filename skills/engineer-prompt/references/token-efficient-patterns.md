# Token-Efficient Prompt Patterns

Read this file when the user is asking about prompt length, context pressure, repeated instructions, large schemas, or verbose workflow definitions.

The goal is not to make prompts short at any cost. The goal is to spend tokens on decision-critical information and stop spending them on repeated scaffolding that could live elsewhere.

## Interspersed repetition

Use interspersed repetition when one or two requirements are important enough that they should still be salient at the exact point where the model acts on them.

Good pattern:
- state the rule once near the task definition
- restate it briefly near the action, output block, or tool-using step where it matters
- repeat the invariant, not the whole surrounding paragraph

Bad pattern:
- copying the full policy block into multiple places
- repeating every instruction, which makes none of them feel special

Good example:

```md
Task:
Summarize only documented remediation steps from the incident log.

Critical rule:
Do not add remediation steps that are not in the log.

Output:
Return 3 bullets only.
Before finalizing, verify each bullet is supported by the log.
```

This works because the second mention is short and placed exactly where compliance tends to break.

## Schema placement

Inline schemas are useful when they are small enough to act as the active output contract.

Move the schema out of the main prompt when:
- the schema is long enough that it dominates the instruction budget
- the schema is canonical and reused across runs
- the model only needs a few inline reminders to stay on track

Preferred pattern:
- keep the full schema in a referenced JSON Schema file or URL
- keep only the most failure-prone constraints inline
- name the reference clearly so the model can anchor to it

Example:

```md
Return valid JSON that conforms to: references/customer-intake.schema.json

Keep these inline invariants in mind:
- `ticket_id` is required
- `priority` must be `low`, `medium`, or `high`
- `contact.email` may be null but must be a string when present
```

This keeps the prompt focused while preserving a single source of truth for the full contract.

## Workflow formalization

Long workflows often waste tokens because the same branching logic gets rewritten in prose every time.

When the workflow is stable, move the durable structure into a referenced artifact:
- use Mermaid when a lightweight flowchart or sequence diagram is enough
- use BPMN when the workflow needs explicit gateways, handoffs, or business-process semantics

Keep the inline prompt short:
- what the model is doing right now
- which workflow artifact to follow
- what output or decision it must produce

Example:

```md
Follow the escalation workflow in references/escalation-flow.mmd.
You are executing only the classification and routing step.
Return the chosen route and the evidence that triggered it.
```

This is better than rewriting the whole escalation tree in paragraph form.

## Sketch-of-thought and mathematical language

Use compact notation when the task already has a structured state space.

Good fits:
- scoring rules
- optimization tradeoffs
- routing logic
- invariants, constraints, or state transitions
- proofs, math, symbolic logic, or algorithm design

Bad fits:
- user-facing prose where the notation would need to be unpacked anyway
- ambiguous tasks where shorthand hides assumptions instead of clarifying them

Useful pattern:
- let the model reason with variables, sets, inequalities, or compact state labels
- ask it to translate the final answer into plain English if the audience is non-technical

Example:

```md
Reason compactly using:
- state labels `S0`, `S1`, `S2`
- cost function `C(plan)`
- hard constraints `H`

Choose the plan that minimizes `C(plan)` while satisfying all constraints in `H`.
Then explain the result in plain English for the operator.
```

## Compression checklist

When rewriting a prompt for token efficiency, check these in order:

1. Remove repeated prose before removing task-critical context.
2. Keep one canonical source for large schemas or workflows.
3. Restate only the highest-risk instruction near the step where it matters.
4. Convert repetitive prose workflows into diagrams when the diagram is clearer and reusable.
5. Use symbolic shorthand only when the task domain already supports it.
6. Preserve correctness first, then optimize for brevity.