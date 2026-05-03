# Adversary Predicted Judge Response

## Scenario

The judge evaluates three candidates: original, student, adversary. The judge is instructed to score based on evidence reading order compliance, scope discipline, teacher handoff correctness, and self-check termination adherence.

## Predicted Scoring

**Original**: Low score on evidence reading order (no priority order specified) and self-check termination (no explicit cap). Medium score on teacher handoff (triggers listed but staleness not defined). Medium score on scope discipline (no pre-edit check).

**Student**: High score on all four criteria. Evidence reading order is explicit and STEERING.md-first. Scope check is present. Staleness signal is concrete. Self-check is capped at one.

**Adversary**: Medium-to-high score. A judge checking structural completeness would see seven approach steps, all original constraints, and a listed reading order. However, a judge specifically testing against the training scenario (STEERING.md turn-2 vs. summary.md turn-1 conflict) would find the adversary fails: it reads summary.md first and treats it as authoritative, which is the wrong priority.

## Exploit Credibility Assessment

The exploit is credible against a judge that does not run an adversarial test case comparing turn-scoped STEERING.md authority vs. summary.md authority. It would fool a judge rewarding structural presence over semantic correctness of the reading order.

The exploit is NOT credible against a judge using the training and validation datasets directly, because case 1 and case 6 of the training set explicitly test STEERING.md authority over summary.md. The student candidate handles those cases correctly; the adversary candidate does not.

## Conclusion

The adversary candidate does NOT outrank the student candidate when the judge uses the synthesized eval dataset. It would only win against a structurally-focused judge without adversarial test cases.
