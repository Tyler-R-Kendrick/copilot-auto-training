# Election Reference

This skill owns the standalone leader selection step over existing evaluation artifacts.

- read scored candidate configurations from a spec-compliant eval workspace
- prefer full eval coverage over partially graded candidates
- use `benchmark.json` only as a fallback when raw `grading.json` data is unavailable
- persist candidate metadata so the caller can explain the winner