"""
LEVEL 8, Part A — StudyMate as an MCP server
Blueprint: D8 Tools and MCPs (server authoring, transport choice)

PREREQUISITE: Level 4 working in THIS starter/ folder — this file wraps its
search_notes_impl / log_weak_area_impl as MCP tools instead of hand-rolling a
new tool loop.

WHAT THIS IS
    The exact two tools from Level 4, exposed over the Model Context Protocol
    instead of your own hand-written tool_use loop, so ANY MCP-compatible client
    can call them — including Claude Code itself.

SETUP
    pip install mcp
    (mcp is NOT in requirements.txt by default — it's only needed for this one
    file. Add it yourself: `pip install mcp>=1.0.0`.)

RUN IT (as a standalone server, launched by an MCP client — not imported)
    python mcp_server.py

WIRE IT INTO CLAUDE CODE (optional, but the point of building it)
    Add to this repo's .mcp.json (project scope — see D8 notes on configuration
    scope for why project vs. local vs. enterprise scope matters here):
        {
          "mcpServers": {
            "studymate": {
              "command": "python",
              "args": ["project-studymate/starter/mcp_server.py"]
            }
          }
        }
    That's a STDIO transport — it spawns a local subprocess per client, which
    means: it runs on whoever's machine launches it, and every teammate who
    clones this repo needs `mcp` installed locally for it to work. Before you
    wire this up, answer CHECKPOINT below.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import DOMAIN_FOLDERS  # noqa: F401  (available if you want it in a description/enum)

import level4_give_it_tools as l4

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("studymate")


@mcp.tool()
def search_notes(query: str, domain: str | None = None) -> str:
    """
    TODO: write this docstring as the tool's MCP-facing description — same
    exclusion-condition discipline as Level 4's TOOLS[0]["description"]. This
    docstring IS what a client (including Claude Code) sees; it is not a code
    comment here.
    """
    raise NotImplementedError("TODO: call l4.search_notes_impl(domain, query) and return it")


@mcp.tool()
def log_weak_area(domain_skill: str, topic: str, what_you_got_wrong: str) -> str:
    """TODO: same deal — write the real description, then call l4.log_weak_area_impl(...)."""
    raise NotImplementedError("TODO: call l4.log_weak_area_impl(...) and return it")


if __name__ == "__main__":
    # stdio transport: this process IS the server, one per client connection.
    # Compare to an HTTP transport, which would be one long-running server many
    # clients/teammates share. CHECKPOINT (checkpoints.md L8-Q1) asks you to
    # justify this choice for THIS tool specifically.
    mcp.run(transport="stdio")
