# Optimize Stage — Manual Followup

**Blocker:** External model unavailable. `trainer-optimize` returned `mode=manual_followup` because the inference session could not be created with authentication credentials.

**Optimize artifact path:** `iterations/iteration-1/optimize/manual-followup-report.json`

**Agent handoff:** The current `@trainer` agent answered the `model_prompt` from the report directly. The optimized candidate was authored by reviewing:
- `engineer-prompt/review.md` — 6 identified risks with rewrite hypotheses
- `inputs/source/researcher.agent.md` — baseline prompt
- Training dataset rows in `synthesize/train.jsonl` — 6 `llm_judge` rows covering MCP activation, blocker report accuracy, field-mapping completeness, workspace artifact paths, partial-approval classification, and missing-constraint handling
- Validation dataset rows in `synthesize/val.jsonl` — 2 rows covering sentiment classification with MCP activation and code-generation with custom scoring

**Changes made relative to baseline:**
1. Added `## Evidence Reading Order` section with 6 numbered items (prompt interface → task boundary → scoring rule → domain constraints → licensing → missing constraints).
2. Added MCP fallback instruction: record unavailability in `unresolved_gaps` and proceed with free-form discovery.
3. Added explicit partial-approval classification: **approved**, **conditional**, **rejected** — replacing the binary approved/rejected pattern.
4. Added `## Artifact Path` section: save as `research/research-brief.json` under active iteration directory in trainer loops.
5. Restructured `## Output Format` as a named JSON artifact (`research-brief.json`) with defined top-level keys: `target`, `research_plan`, `approved_sources`, `rejected_candidates`, `field_mapping`, `unresolved_gaps`, `stop_recommendation`.
6. Expanded field-mapping note to cover all four downstream eval fields: `input`, `reference`, `criteria`, `scoring`.
7. Added `stop_recommendation` field contract: `null` when approved sources exist; string explanation when issuing blocker report.

**Rerun command (for later automated pass):**
```
python skills/trainer-optimize/scripts/run_optimize.py --prompt-file .github/agents/researcher.agent.md --train-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/train.jsonl --val-file .github/agents/.trainer-workspace/researcher.agent/iterations/iteration-1/synthesize/val.jsonl --iterations 3 --algorithm apo --beam-width 4 --branch-factor 4 --n-runners 4 --judge-mode llm_judge
```
