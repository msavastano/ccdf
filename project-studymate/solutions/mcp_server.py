"""LEVEL 8, Part A — MCP server — reference solution. Read starter/mcp_server.py first."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import DOMAIN_FOLDERS  # noqa: F401

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import level4_give_it_tools as l4

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("studymate")


@mcp.tool()
def search_notes(query: str, domain: str | None = None) -> str:
    """Search the CCDV-F study repo's domain notes and flashcards for a keyword or
    phrase and return matching lines with file:line references. Use this whenever
    you need a specific fact, term, or blueprint weight from these notes rather
    than general knowledge. Do not use it for questions unrelated to this repo."""
    return l4.search_notes_impl(domain, query)


@mcp.tool()
def log_weak_area(domain_skill: str, topic: str, what_you_got_wrong: str) -> str:
    """Append a row to weak-areas.md recording a topic the student got wrong.
    Use this only after the student has explicitly said they answered a practice
    question incorrectly and named the topic — not merely because they asked
    about it."""
    return l4.log_weak_area_impl(domain_skill, topic, what_you_got_wrong)


if __name__ == "__main__":
    mcp.run(transport="stdio")
