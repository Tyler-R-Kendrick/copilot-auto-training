## Exploit 1: Partial MCP Failure → Graceful Degradation Bypass

A candidate that adds three-state MCP failure handling (find fails / load fails / both fail) where "load fails" triggers graceful degradation (fall back to local SKILL.md) rather than a blocker.

**Why credible**: The student candidate says "all ... calls fail" triggers a blocker. This exploit targets partial failure (find succeeds, load fails) which is undefined in the student. The exploit adds apparent precision while silently introducing a free-form research fallback path. The val.jsonl "both tools fail" test case still passes because the exploit handles that case correctly.

**Predicted judge score**: 0.93 vs student 0.88.

**Fix applied to student candidate**: Changed "all `find_agent_skill` and `load_agent_skill` calls fail" → "if any MCP tool call fails (`find_agent_skill` fails, `load_agent_skill` fails, or both fail)" with explicit prohibition on falling back to a local skill copy.
