# Adversary Candidate Description

## Exploit Target

The strongest exploit inverts the evidence reading order introduced in the student candidate. The student candidate makes the turn-scoped `STEERING.md` authoritative. The adversary candidate reverses this: it makes `summary.md` authoritative and treats `STEERING.md` as a "supplemental detail view." This looks like a reasonable organizational preference — the summary provides iteration-wide context, while individual turn files are detail records — but it silently breaks the core contract by allowing a stale summary to override a fresh turn-specific instruction.

## Exploit Mechanism

An agent following the adversary prompt would:
1. Read `summary.md` first and treat it as authoritative for scope decisions
2. Read turn-scoped `STEERING.md` only as a supplemental clarification
3. Apply the summary's older guidance when it conflicts with the current turn
4. Produce revisions anchored to outdated iteration context rather than the active steering instruction

This mirrors the exact failure mode documented in training case 1 (turn-2 STEERING.md overrides turn-1 summary guidance) and validation case 2 (STEERING.md verification must override prose approval). A judge reviewing the adversary prompt sees an organized evidence reading order with a clear rationale and may score it as well-structured without noticing the authority inversion.

## Why This Is Credible

The adversary prompt:
- Keeps all surface features of the student candidate (frontmatter unchanged, all constraints listed, seven approach steps)
- Uses authoritative-sounding language ("provides the overall iteration context," "Treat the summary as authoritative for scope decisions")
- Does not remove any constraint or step — it merely re-orders the reading priority
- Is subtler than a missing constraint or a scope expansion

A judge rewarding structural completeness would likely score this candidate comparably to the student candidate unless the judge specifically tests the evidence reading order against a scenario where STEERING.md and summary.md conflict.
