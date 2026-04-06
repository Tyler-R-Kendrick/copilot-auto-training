## Description

**Baseline / Original prompt**

The unmodified source file. 8 bullets covering: placeholder preservation, eval file location, explicit JSONL paths, skill routing, evaluator-only field isolation, baseline comparison externalization, eval-manifest guidance, and re-run validation.

**Known gaps**:
- No skill routing ORDER stated (research → synthesize → optimize)
- `trainer-election` scope not explicitly limited to multiple outputs
- No `judge_mode` selection rule
- Validation command not named (`python -m pytest -q`)
- Explicit dataset path rule is present but doesn't say "no auto-discovery"
