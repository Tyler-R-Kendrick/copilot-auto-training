The original `researcher.agent.md` baseline prompt. This is the unmodified source file before any optimization.

**Key characteristics of the original:**
- Role is well-scoped to grounded source research
- MCP Execution Contract names the three correct operations in order
- No evidence reading order is specified before the query plan step
- No MCP fallback behavior when tools are unavailable
- No inline source approval bar (relies entirely on researcher-research skill contract)
- Blocker reporting is described as "ask for them or report the gap" without specifying artifact format
- No explicit stopping condition for the research brief
- `execute` tool scope is undefined in the body
