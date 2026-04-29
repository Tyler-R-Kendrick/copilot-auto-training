# Decision: student.agent.md — Iteration 1

## Selected Candidate
`iterations/iteration-1/candidates/student/prompt.md`

## Why Selected
Teacher approved after one review turn. All six precision gaps from the engineer-prompt review are addressed. Adversary found three credible exploit patterns; three targeted additions were applied to close the judge-evasion gaps before persistence.

## Changes from Baseline
1. **Evidence reading priority** added as numbered list in Approach step 1
2. **Conflict resolution rule** added: latest turn artifact is canonical; quote both excerpts to substantiate the claim (Approach steps 1–2)
3. **"Smallest defensible revision" bounded**: "minimal set of sentence-level or structural changes... without touching any lines not implicated by that gap" (Constraints)
4. **Approval prediction criterion** made concrete with per-condition MET/NOT MET enumeration (Constraints)
5. **Loop exit criteria** enumerated: four named conditions (Approach step 7)
6. **Validation** pointer added: `python -m pytest -q` with judge-mode note (Approach step 8)
7. **Engineer handoff trigger** narrowed: only for Trace-oriented framing or materially ambiguous reasoning (preamble paragraph)
8. **Change-count audit** added: state how many distinct changes and map each to a critique point (Approach step 6)

## Validation
`python -m pytest -q`: 856 passed, 0 failed

## Adversary Verdict
Exploit 2 (scope creep camouflage) was credible at predicted 0.90. Mitigated by adding explicit change-count mapping in Approach step 6. Judge steering blocks recorded in `iterations/iteration-1/steering/judge-exploit-blocks.md`.
