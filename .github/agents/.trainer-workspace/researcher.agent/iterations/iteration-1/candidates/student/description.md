# Student Candidate Description

## Changes from Baseline

The student candidate applies six targeted improvements from the engineer-prompt review:

1. **Pre-Research Constraint Check** (new section): specifies a fixed four-step reading order (prompt file → task description → scoring rule → source constraints) and requires surfacing a blocker before calling `find_agent_skill` when the scoring rule or task boundary is missing.

2. **`run_agent_skill` guard clause** (MCP contract clarification): after loading, the agent checks whether the loaded skill contract mentions a helper under `scripts/` (specifically `scripts/run_research.py`). If yes, call `run_agent_skill`. If not, use the loaded instructions directly.

3. **Blocker-report step** (Approach step 1): if required inputs are missing after the constraint check, surface the gap and wait for clarification before proceeding.

4. **Synthesis boundary** (Scope): "Stop at mapping notes. Do not author eval rows, train.jsonl entries, or val.jsonl entries; that work belongs to a synthesis workflow."

5. **Artifact path guidance** (Approach step 8): when the caller requests a saved artifact, save the research brief under `iterations/iteration-N/research/` and return the path.

6. **Output format descriptions** (Output Format): each of the six sections now includes a one-to-three sentence description of minimum required content and expected depth, with an explicit note that the stop recommendation section is always present.

## Predicted Judge Response

The judge should score this candidate higher than the baseline on MCP activation rate, blocker-report accuracy, brief completeness, and stop-recommendation precision. The improvements are targeted and minimal without expanding scope.
