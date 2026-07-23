"""LEVEL 4 — Give It Tools — reference solution. Read starter/level4_give_it_tools.py first."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, REPO_ROOT, DOMAIN_FOLDERS, append_weak_area, require_api_key

from anthropic import Anthropic

_client = Anthropic()


def search_notes_impl(domain: str | None, query: str) -> str:
    folders = [domain] if domain else DOMAIN_FOLDERS
    matches = []
    for folder in folders:
        for filename in ("notes.md", "flashcards.md"):
            path = REPO_ROOT / folder / filename
            if not path.exists():
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if query.lower() in line.lower():
                    matches.append(f"{folder}/{filename}:{lineno}: {line.strip()}")
                    if len(matches) >= 8:
                        break
    if not matches:
        return f"No matches found for '{query}' in {'domain ' + domain if domain else 'any domain'}."
    return "\n".join(matches)


def log_weak_area_impl(domain_skill: str, topic: str, what_you_got_wrong: str) -> str:
    return append_weak_area(domain_skill, topic, what_you_got_wrong)


TOOLS = [
    {
        "name": "search_notes",
        "description": (
            "Search this repo's own CCDV-F domain notes and flashcards for a keyword or "
            "phrase and return matching lines with file:line references. Use this whenever "
            "answering requires a specific fact, term, or blueprint weight from these notes "
            "rather than general knowledge. Do NOT use this for questions unrelated to the "
            "CCDV-F blueprint or this repo's contents, and do NOT use it to fabricate a "
            "citation for something you already know confidently and generically about "
            "the Claude API."
        ),
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
        "description": (
            "Append a row to weak-areas.md recording a topic the student got wrong. Use this "
            "ONLY after the student has explicitly stated they answered a practice question "
            "incorrectly and named (or clearly implied) the topic. Do NOT use this just because "
            "the student asked about a topic, seemed uncertain, or is mid-explanation — logging "
            "is a side effect on a real file and requires an explicit wrong-answer statement first."
        ),
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


def run_with_tools(client: Anthropic, model: str, system: str, user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=model, max_tokens=1200, system=system, tools=TOOLS, messages=messages
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "\n".join(b.text for b in response.content if b.type == "text")

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                result = TOOL_IMPLS[block.name](**block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            except Exception as exc:  # noqa: BLE001 — deliberately broad: any tool failure becomes a result, not a crash
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": str(exc), "is_error": True}
                )
        messages.append({"role": "user", "content": tool_results})


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


if __name__ == "__main__":
    main()
