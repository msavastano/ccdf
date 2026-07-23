"""
LEVEL 4 — Give It Tools                                             difficulty: ***
Blueprint: D8 Tool Implementation · D6 Context Engineering (retrieval)

WHAT YOU'RE BUILDING
    Two tools Claude can call:
      - search_notes(domain, query)   -> greps this repo's own domain notes/flashcards
      - log_weak_area(domain_skill, topic, what_you_got_wrong) -> a REAL side effect,
        appends a row to the real weak-areas.md
    ...and the tool_use / tool_result loop that lets Claude call them, see the
    results, and keep going until it has a final answer.

WHY THIS IS THE RIGHT NEXT STEP
    Everything before this was Claude alone. This is the level where Claude
    starts acting ON something outside itself — the loop you build here (call ->
    inspect stop_reason -> run the tool -> feed the result back -> repeat) is the
    single most reused piece of code in the rest of this project. Level 5's agent
    loop, Level 6's guardrail, and Level 8's MCP server all sit on top of this.

    This level also plants the exam's #1 tool-design trap on purpose: two tools
    that could plausibly both apply to a question. You'll write an EXCLUSION
    CONDITION into each description ("do NOT use this when...") because Claude
    routes tool choice on the description text, not on your intent.

RUN IT
    python level4_give_it_tools.py
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, REPO_ROOT, DOMAIN_FOLDERS, append_weak_area, require_api_key

from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Part A — the tool implementations (plain Python functions, no SDK involved)
# ---------------------------------------------------------------------------


def search_notes_impl(domain: str | None, query: str) -> str:
    """
    TODO: Search notes.md and flashcards.md across DOMAIN_FOLDERS (or just the
    one `domain` folder if given) for lines containing `query` (case-insensitive).
    Return up to 8 matches formatted like:
        domain-2-applications/notes.md:142: <the matching line, stripped>
    If nothing matches, return a string that says so explicitly — an empty
    string is easy to mistake for "no output yet" versus "confirmed no match."
    """
    raise NotImplementedError("TODO: implement search_notes_impl()")


def log_weak_area_impl(domain_skill: str, topic: str, what_you_got_wrong: str) -> str:
    """TODO: call common.append_weak_area and return its confirmation string."""
    raise NotImplementedError("TODO: implement log_weak_area_impl()")


# ---------------------------------------------------------------------------
# Part B — the tool schemas Claude sees. Fill in each "description".
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "search_notes",
        # TODO: write a description that tells Claude WHEN to use this tool
        # (needs a fact from the CCDV-F blueprint notes) AND an explicit
        # exclusion clause ("do NOT use this when...") for the other tool below.
        "description": "TODO",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "enum": DOMAIN_FOLDERS,
                    "description": "Restrict the search to one domain folder. Omit to search all.",
                },
                "query": {"type": "string", "description": "Keyword or short phrase to search for."},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
    {
        "name": "log_weak_area",
        # TODO: same deal — when to use it, and an explicit exclusion clause
        # ("do NOT use this when the student merely asked about a topic, only
        # after they've confirmed a wrong answer").
        "description": "TODO",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain_skill": {"type": "string", "description": "e.g. 'D8 · MCP transports'"},
                "topic": {"type": "string"},
                "what_you_got_wrong": {"type": "string"},
            },
            "required": ["domain_skill", "topic", "what_you_got_wrong"],
            "additionalProperties": False,
        },
    },
]

TOOL_IMPLS = {
    "search_notes": lambda **kwargs: search_notes_impl(kwargs.get("domain"), kwargs["query"]),
    "log_weak_area": lambda **kwargs: log_weak_area_impl(
        kwargs["domain_skill"], kwargs["topic"], kwargs["what_you_got_wrong"]
    ),
}


# ---------------------------------------------------------------------------
# Part C — the agentic loop
# ---------------------------------------------------------------------------


def run_with_tools(client: Anthropic, model: str, system: str, user_message: str) -> str:
    """
    TODO:
      1. messages = [{"role": "user", "content": user_message}]
      2. Loop:
           a. response = client.messages.create(model=model, max_tokens=1200,
              system=system, tools=TOOLS, messages=messages)
           b. Append the assistant turn to messages EXACTLY as returned:
              messages.append({"role": "assistant", "content": response.content})
           c. If response.stop_reason != "tool_use": return the text from the
              text block(s) in response.content — you're done.
           d. Otherwise, for EVERY block in response.content with
              block.type == "tool_use":
                 - look up TOOL_IMPLS[block.name], call it with **block.input
                 - wrap the call in try/except: on success, tool_result content
                   is the return value (a string); on exception, tool_result
                   content is str(exception) AND you set "is_error": True
                 - build one tool_result dict per tool_use block:
                     {"type": "tool_result", "tool_use_id": block.id,
                      "content": <string>, "is_error": <bool, only if True>}
              Append ALL of them in ONE user turn:
                 messages.append({"role": "user", "content": [tool_result, tool_result, ...]})
           e. Go back to (a).

    THE TRAP TO AVOID: if a tool raises, do NOT swallow it and return an empty
    string as the tool_result — that reads to the model as "the tool ran and
    found nothing," not "the tool failed." Set is_error: True so Claude knows
    to treat the result as a failure, not as data.
    """
    raise NotImplementedError("TODO: implement run_with_tools()")


def main() -> None:
    require_api_key()
    client = Anthropic()
    system = (
        "You are StudyMate, a CCDV-F tutor with access to this repo's own study notes. "
        "Use search_notes to ground factual claims in the notes before answering. "
        "Use log_weak_area only when the user has just told you they got a practice "
        "question wrong and named the topic."
    )

    answer = run_with_tools(
        client, MODEL_SONNET, system,
        "What does this repo's notes say is the difference between prompt caching "
        "and a static system prompt? Search the notes before answering.",
    )
    print(answer)
    print()

    answer2 = run_with_tools(
        client, MODEL_SONNET, system,
        "I just got a practice question wrong on 'stdio vs HTTP transport' in "
        "domain 8 — I picked stdio for a team-shared server. Please log that.",
    )
    print(answer2)

    print(
        "\nCHECKPOINT: open weak-areas.md — there should be one new real row. Then\n"
        "read your two tool descriptions out loud. If you handed BOTH descriptions to\n"
        "someone who'd never seen this file and asked 'which tool would you call for\n"
        "an off-topic general-knowledge question,' would they correctly say 'neither'?"
    )


if __name__ == "__main__":
    main()
