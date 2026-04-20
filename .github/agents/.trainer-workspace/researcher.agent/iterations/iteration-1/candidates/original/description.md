## Original Candidate

The baseline `researcher.agent.md` before any optimization.

### Key Limitations

1. No input-reading checklist or evidence order before MCP invocation.
2. No MCP fallback path when `find_agent_skill` or `load_agent_skill` fails.
3. Source approval bar not inlined — agent relies entirely on the loaded skill for standards.
4. No explicit stopping criteria distinguishing hard-stop missing inputs from soft-gap ones.
5. Output format underspecified — "Mapping notes" has no structure requirement.
6. `run_agent_skill` condition for "guidance only" skill not clarified.
