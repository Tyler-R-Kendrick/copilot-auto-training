# Research Brief: `create-workflow` Skill — GitHub Agentic Workflow Authoring

## Approved Sources

1. **Internal Skill Documentation Corpus** (MIT) — `SKILL.md`, `gh-aw-authoring.md`, `workflow-template.md` — exact fit, only authoritative source for `gh aw` compilation model
2. **GitHub Docs: Cloud Agent + MCP** (CC BY 4.0) — grounding for MCP conceptual scenarios  
3. **GitHub Docs: Actions Workflow Syntax + Events** (CC BY 4.0) — trigger event vocabulary
4. **Repo peer eval corpus** (MIT) — schema authority only

## Key Scoring Dimensions

| Dimension | What the judge checks |
|---|---|
| **Compilation awareness** | Correctly distinguishes when frontmatter changes require `gh aw compile` vs. markdown body changes that do not |
| **Safe-output correctness** | Write operations configured through `safe-outputs:` frontmatter; body produces expected output format |
| **MCP configuration accuracy** | Syntactically correct `mcp-servers:` block; scoped `allowed:`; secrets-backed credentials; network allow-list |
| **Response contract accuracy** | Names changed files; summarizes trigger/behavior/tools; states compile status; calls out prerequisites |

## Stop Recommendation

Proceed with synthesis using simulated examples grounded in the skill's own documentation. The `gh aw` CLI extension is not a public open-source repository (HTTP 404). The internal corpus is the sole authoritative source and clears the full approval bar.

## 8 Benchmark Scenarios (summary)

1. New scheduled workflow with `safe-outputs: issues: create`
2. MCP server addition requiring frontmatter recompile
3. Draft-only request with initialization deferred
4. Frontmatter edit — recompilation required
5. Markdown body edit — no recompilation needed
6. Debugging a compilation failure (YAML parse error)
7. Runtime tool-not-found failure (MCP tools not exposed)
8. Write-action safe-output setup (labels + comments)
