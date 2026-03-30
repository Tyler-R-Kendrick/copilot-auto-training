from __future__ import annotations

from agent_skills_mcp import build_mcp


def main() -> None:
    # The server rereads skills from disk on each tool or resource call so edits hotload without a watcher.
    build_mcp().run(transport="stdio")


if __name__ == "__main__":
    main()
