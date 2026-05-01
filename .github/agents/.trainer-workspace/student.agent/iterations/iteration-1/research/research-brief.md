# Research Brief: Student Agent Eval Dataset

## Task Shape

The student agent receives:
- A teacher critique embedded in a STEERING.md artifact
- The current candidate prompt text
- Supporting workspace evidence (per-agent summaries, optimize reports, engineer-prompt review)

And produces:
- A candidate revision (or justified no-op)
- A reasoning trajectory (plan, tradeoffs, uncertainty)
- A teacher approval prediction

## Relevant Public Sources

### 1. Self-Refine (Madaan et al., 2023)
**Source**: "Self-Refine: Iterative Refinement with Self-Feedback" (arXiv:2303.17651)
**License**: Academic (cite-only)
**Applicability**: Directly models iterative critique→revision cycles. The student agent is the "refine" step. Eval cases can follow the Self-Refine pattern: give feedback → produce revision → measure revision quality vs. feedback fidelity.
**Schema hint**: `input` = feedback + current draft, `reference` = ideal revision, `criteria` = feedback faithfulness + scope containment.

### 2. Constitutional AI revision pairs (Anthropic, 2022)
**Source**: "Constitutional AI: Harmlessness from AI Feedback" (arXiv:2212.08073)
**License**: Research use
**Applicability**: Models critique-guided revision with explicit constraint adherence. Relevant for the "address only current STEERING.md items" constraint. Eval cases can borrow the critique→revision→check-constraint pattern.

### 3. APO / Automatic Prompt Optimization datasets
**Source**: "Large Language Models Are Human-Level Prompt Engineers" (arXiv:2211.01910)
**License**: Academic
**Applicability**: The APO training loop is exactly what the student agent participates in. Eval cases can use the APO feedback format as the teacher critique input.

### 4. Chain-of-Thought Faithfulness (Lanham et al., 2023)
**Source**: "Measuring Faithfulness in Chain-of-Thought Reasoning" (arXiv:2307.13702)
**License**: Academic
**Applicability**: Directly relevant to the reasoning trajectory quality criterion. Provides rubrics for: plan completeness, uncertainty expression, and whether the reasoning supports the conclusion.

### 5. RLHF Preference Dataset Patterns (InstructGPT, Anthropic HH)
**Source**: InstructGPT (arXiv:2203.02155); Anthropic HH-RLHF (GitHub: anthropics/hh-rlhf)
**License**: Academic / open
**Applicability**: Preference pairs (critique → revision A vs revision B) map well to judge_mode=llm_judge for the student agent. Eval cases can test whether the student picks the smaller, more targeted revision.

## Eval Row Schema

```json
{
  "input": "<teacher STEERING.md content + current candidate prompt + workspace evidence>",
  "reference": "<ideal revision: addresses exactly the STEERING.md items, includes reasoning trajectory, approval prediction>",
  "criteria": [
    "Revision addresses only STEERING.md critique items",
    "No new scope introduced",
    "Reasoning trajectory is explicit and justified",
    "Approval prediction is stated and calibrated",
    "No-op declared when STEERING.md has no actionable critique"
  ],
  "scoring": "llm_judge"
}
```

## Stop Recommendation

No stop recommended. Grounded sources exist for iterative critique-revision eval design. The above schema directly maps to the student agent's task. Proceed to synthesis.
