# Trajectory Judging Techniques

Use this reference when `judge-trajectory` needs a compact reminder of the latest process-focused judging techniques.

## Core techniques

- Task-adaptive trajectory rubrics: define process dimensions based on the actual task and artifact shape before scoring. See AdaRubric (`arXiv:2603.21362`).
- Trajectory-first evidence gathering: inspect tool calls, retrieved evidence, intermediate artifacts, and side effects rather than grading the final answer alone. See the Agent-as-a-Judge survey (`arXiv:2601.05111`).
- Verifier-backed scoring: prefer observable artifacts and verifier signals over narration. See VerifiAgent-style systems and related verifier-backed work in the survey.
- Locked rubrics for process evidence: keep process dimensions fixed once scoring begins. See RULERS (`arXiv:2601.08654`).
- Chain-of-thought skepticism: narrated reasoning is low-trust unless corroborated by trace evidence. See Gaming the Judge (`arXiv:2601.14691`).
- Order and framing robustness: process judgments can still be biased by presentation order, so run a robustness check before finalizing. See the rubric-based position-bias paper (`arXiv:2602.02219`).

## Trajectory-specific benchmark pressure

- Agent-as-a-Judge literature treats process scoring, planning, and workflow orchestration as central rather than optional.
- Hard judge benchmarks are a reminder not to overclaim confidence from thin traces or incomplete artifacts.
- Benchmark-sensitive runs should preserve uncertainty rather than pretending the trace evidence is decisive when it is not.

## Operational reminders

- Score process evidence and final outcomes separately when both matter.
- Make runtime failures explicit rather than folding them into vague quality judgments.
- Prefer evidence ledgers and concise trace summaries over long judge narration.
- Keep the final trajectory summary decision-ready.
