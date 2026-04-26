# Research Brief: Student Agent Evaluation Design

**Target**: `.github/agents/student.agent.md`
**Stage**: Research — iteration-1
**Date**: 2026-04-26

## Objective

Identify public-source patterns, benchmark tasks, and schema guidance for evaluating a teacher-guided candidate revision agent in an iterative prompt optimization loop. The evaluation should measure: revision targeting fidelity, reasoning trajectory quality, teacher approval prediction accuracy, no-op precision, and appropriate handoff behavior.

## Approved Public Sources

### 1. APE / OPRO / ProTeGi — Iterative Prompt Refinement Benchmarks
- **Type**: Academic benchmark systems
- **Relevance**: APE (Automatic Prompt Engineer, Zhou et al. 2022), OPRO (Yang et al. 2023), ProTeGi (Pryzant et al. 2023) all evaluate iterative prompt revision quality. ProTeGi explicitly uses a "teacher-student" metaphor: a feedback agent critiques and a proposer agent revises.
- **Key pattern**: Evaluation rows pair `(current_prompt, critique, expected_revision_direction)`. Success is measured by whether the revision addresses the specific critique without regressing other criteria.
- **License**: Academic / open source. ProTeGi: Apache 2.0.
- **Approved**: Yes — provides the structural scaffold for input/expected-output pairs.

### 2. TextGrad (Yuksekgonul et al. 2024)
- **Type**: Framework for gradient-based text optimization
- **Relevance**: TextGrad formalizes the notion of "textual feedback" as a gradient signal; the student's job is to implement the minimal change that satisfies that gradient without changing unrelated parts. This aligns with the "smallest defensible revision" principle.
- **Key pattern**: Test cases expose `(artifact, feedback, revised_artifact)` triples where scoring checks adherence to feedback without unnecessary changes.
- **License**: MIT
- **Approved**: Yes — supports the "minimum effective change" principle.

### 3. ReAct / Chain-of-Thought revision quality literature
- **Type**: Empirical NLP benchmarks (Wei et al. 2022, Yao et al. 2022)
- **Relevance**: Chain-of-thought benchmarks evaluate whether the reasoning trajectory (not just the final answer) is coherent and grounded. For the student agent, the reasoning trajectory is a first-class output alongside the revision itself.
- **Key pattern**: Rows assess whether intermediate reasoning steps are logically connected, sufficiently detailed, and avoid hidden shortcuts.
- **License**: Public / research
- **Approved**: Yes — informs criteria for reasoning trajectory quality.

### 4. RLHF / Constitutional AI: Preference Prediction
- **Type**: Alignment research (Bai et al. 2022)
- **Relevance**: The student agent must predict teacher approval before finalizing. Preference prediction accuracy (how often the student correctly forecasts whether a human/teacher would approve) is a measurable outcome in RLHF datasets.
- **Key pattern**: Rows expose `(candidate, predicted_verdict, actual_verdict)` and measure calibration.
- **License**: Public / research
- **Approved**: Yes — provides the schema for approval prediction evaluation.

## Rejected Sources

- **Generic QA benchmarks (SQuAD, MMLU)**: Not relevant — these test factual recall, not iterative revision behavior.
- **Code generation benchmarks (HumanEval)**: Not applicable — the student agent revises natural language prompts, not code.
- **Single-shot prompt datasets**: Not applicable — the student agent is an iterative loop component, not a single-shot responder.

## Schema Guidance for Eval Rows

Based on the approved sources and the student agent's task contract, each eval row should:

```json
{
  "input": "A scenario description providing: (1) the current candidate/prompt, (2) the available steering artifact(s) (STEERING.md excerpt or summary.md), (3) the revision task or clarification question. The student agent receives this as its operating context.",
  "reference": "The expected student agent output: specific revision or justified no-op, explicit reasoning trajectory, predicted teacher approval verdict, and any handoff rationale.",
  "criteria": ["Observable assertions about the output."],
  "scoring": "llm_judge"
}
```

**Key observable criteria patterns:**
1. Revision targets the primary critique and nothing else (steering fidelity)
2. Reasoning trajectory is explicit (chain-of-thought, tree-of-thought, or sketch-of-thought format)
3. Prediction of teacher approval is stated with rationale
4. No-op is justified with enumerated conditions, not just "no change needed"
5. Handoff to teacher is triggered by an explicit criterion (missing/stale/contradictory steering)
6. Engineer handoff is limited to formatting or domain expertise, not delegation of the revision itself

## Gaps and Caveats

- No public benchmark precisely matches the iterative teacher-student agent loop format used in this repository. All patterns are adapted from related literature.
- Approval prediction accuracy cannot be verified deterministically; llm_judge scoring is appropriate.
- "Smallest defensible revision" is inherently comparative; eval rows should include context sufficient to judge whether the student scoped appropriately.
- Stale steering scenarios require date or iteration metadata to be realistic; for synthesis, use iteration references in the scenario description.

## Recommendation for Synthesis

Create 8 training rows and 2 validation rows covering:
1. Standard targeted revision (clear steering)
2. No-op case (steering already satisfied)
3. Missing STEERING.md fallback to summary.md
4. Multiple competing critiques (pick primary)
5. Vague critique (hand off to teacher)
6. Stale steering (hand off to teacher)
7. Engineer handoff for formatting complex reasoning
8. Validation step required (report pytest result)

Val rows:
1. Approval prediction accuracy (should approve)
2. No-op precision (all points already addressed)

All rows: `scoring: "llm_judge"`.
