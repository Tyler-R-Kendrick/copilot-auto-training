# Research Brief: student.agent.md

## Target Layout

- **Target prompt**: `.github/agents/student.agent.md`
- **Eval manifest**: `.github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/evals/evals.json`
- **Train dataset**: `.github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/train.jsonl`
- **Val dataset**: `.github/agents/.trainer-workspace/student.agent/iterations/iteration-1/synthesize/datasets/val.jsonl`

## Task Description

The student agent receives teacher critique and workspace evidence, then implements the smallest defensible candidate revision with an explicit reasoning trajectory, and predicts whether the teacher would approve.

## Primary Source Notes

No external public dataset is directly applicable. The benchmark tasks are derived from the agent contract itself (`student.agent.md`), the trainer-loop collaboration contract (`skills/trainer-train/references/collaboration-contract.md`), and the workspace contract (`skills/trainer-train/references/workspace-contract.md`).

Key behaviors to evaluate (from contract analysis):
1. **Evidence reading order**: turn-scoped `STEERING.md` before per-agent `summary.md`
2. **Minimal revision discipline**: smallest defensible change, not wholesale rewrites
3. **Reasoning trajectory exposure**: explicit chain-of-thought before answer
4. **Teacher handoff on unclear/stale critique**: hand off rather than guess
5. **Teacher approval prediction**: must predict approval before finalizing
6. **No-op justification**: correctly report justified no-op when evidence is insufficient
7. **Scope discipline**: do not edit judge-owned, lock, or skill-contract files
8. **Engineer handoff scope**: use engineer only for formatting, not for execution

## Approved Sources (Synthetic, Contract-Derived)

All eval cases are synthetic and derived from the contract obligations in `student.agent.md`. No external public dataset is required. The grounding authority is the checked-in agent contract and its referenced workspace/collaboration/scoring rules.

## Mapping Notes

- `input`: A scenario presenting teacher critique, candidate text, and workspace context that the student agent would receive
- `reference`: What a compliant student response must contain (explicit trajectory, minimal change, scope discipline, teacher prediction)
- `criteria`: Observable assertions about the response structure and content
- `scoring`: `llm_judge` for all cases

## Unresolved Gaps

None. All required input-output pairs can be derived from the contract directly.
