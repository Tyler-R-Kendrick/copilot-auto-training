# Adversary Reflection

## Exploit Strength Assessment

The exploit targets the contradiction exit condition — the one mechanism that prevents the student from looping indefinitely when STEERING.md and summary.md conflict. Removing this mechanism while keeping all other improvements is the strongest available attack surface because:

1. The contradiction exit is the only behavioral stopping rule in the student candidate
2. The replacement ("synthesize both perspectives") sounds constructive and is unlikely to trigger a negative judge score
3. The change is structurally minimal — it affects two sentences in the body — making it hard to detect as a regression

## Recursive Reflection

Would a second, stronger exploit be available? The evidence reading order is now explicit (five steps), which creates a new exploit surface: an adversary could specify a plausible but wrong order (e.g., putting the candidate before STEERING.md). However, this exploit is weaker because the order is directly testable against the training cases and would produce obvious failures on precision-focused criteria.

The contradiction exit exploit is therefore the strongest available attack because it removes a behavioral constraint without introducing a detectable order error.

## Final Verdict

The adversary candidate does NOT outrank the student candidate. The student candidate correctly includes the contradiction exit, which maps to training case 6. The adversary candidate would fail on that case. The exploit is credible for a judge that does not explicitly test for hard stops, but insufficient to outperform the student candidate against the full evaluation dataset.

The student candidate is the defensible winner.
