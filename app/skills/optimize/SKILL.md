---
name: optimize
description: Improve a markdown prompt file using Agent Lightning. Use when the user asks to optimize a prompt or starts with /optimize.
compatibility: Requires python3, Microsoft Agent Framework (Python), agentlightning, and model credentials.
metadata:
  author: your-org
  version: "0.1.0"
---

Use this skill when the user wants to improve a markdown prompt file.

Process:
1. Parse optimize arguments.
2. Validate required files.
3. Default to `apo`.
4. Ask for script approval.
5. Execute `run_optimize`.
6. Return the optimized file path and optimization summary.

Rules:
- Prefer deterministic evaluation over rubric judging.
- Only use `llm_judge` when deterministic evaluation is not possible.
- Treat `verl` as advanced and not the default for prompt-file rewriting.
- If placeholders in the markdown file do not match dataset fields, stop and explain the mismatch.
