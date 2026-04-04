from __future__ import annotations

import os

from agent_skills_mcp import build_mcp


def main() -> None:
    # The server rereads skills from disk on each tool or resource call so edits hotload without a watcher.
    # Set MCP_TRANSPORT=sse (with FASTMCP_HOST/FASTMCP_PORT) to run as an HTTP/SSE server.
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    build_mcp().run(transport=transport)


if __name__ == "__main__":
    main()
