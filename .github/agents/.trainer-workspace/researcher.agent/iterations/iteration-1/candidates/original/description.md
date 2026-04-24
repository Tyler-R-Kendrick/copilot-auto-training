# Original Candidate

The baseline `researcher.agent.md` as it existed before this optimization run.

## Key Properties
- Strong MCP routing contract with `find_agent_skill` / `load_agent_skill` / conditional `run_agent_skill`
- Clear scope bounded to grounded discovery
- Explicit fabrication prohibition
- Stop condition when no source clears the bar

## Known Gaps
- No explicit no-op path for already-satisfied tasks
- Missing-constraint handling says "ask or report" but does not specify when to ask vs. proceed
- No MCP fallback for server unavailability
- "DO NOT involve any other agents" constraint is ambiguous about agent-skills MCP tools
- No inline vs. saved artifact guidance in output format
