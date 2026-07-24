"""
Shared helpers for the StudyMate build levels.

Import this from any level script with:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from common import REPO_ROOT, MODEL_HAIKU, MODEL_SONNET, MODEL_OPUS, domain_notes_path, append_weak_area

Model IDs are version-sensitive (D5/D2 exam-trap territory) — verified against this
session's environment 2026-07-22. Re-check at platform.claude.com before an exam
run months from now; if a name has moved on, update it here once and every level
picks up the fix.
"""

from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent.parent

MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-5"
MODEL_OPUS = "claude-opus-4-8"

ALL_TIERS = {"haiku": MODEL_HAIKU, "sonnet": MODEL_SONNET, "opus": MODEL_OPUS}

DOMAIN_FOLDERS = [
    "domain-1-agents",
    "domain-2-applications",
    "domain-3-claude-code",
    "domain-4-eval-testing",
    "domain-5-model-selection",
    "domain-6-prompt-context",
    "domain-7-security",
    "domain-8-tools-mcps",
]

# Blueprint weights, for anything that wants to sample/weight by domain (Level 5+).
DOMAIN_WEIGHTS = {
    "domain-1-agents": 14.7,
    "domain-2-applications": 33.1,
    "domain-3-claude-code": 3.1,
    "domain-4-eval-testing": 2.6,
    "domain-5-model-selection": 16.8,
    "domain-6-prompt-context": 11.0,
    "domain-7-security": 8.1,
    "domain-8-tools-mcps": 10.6,
}


def domain_notes_path(domain_folder: str, filename: str = "notes.md") -> Path:
    """e.g. domain_notes_path('domain-2-applications') -> .../domain-2-applications/notes.md"""
    return REPO_ROOT / domain_folder / filename


def require_api_key() -> None:
    """Fail fast with a clear message instead of a raw SDK traceback."""
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY is not set.\n"
            "Set it for this shell before running a level script, e.g.:\n"
            "  PowerShell:  $env:ANTHROPIC_API_KEY = 'sk-ant-...'\n"
            "  bash:        export ANTHROPIC_API_KEY='sk-ant-...'\n"
            "Never hard-code the key in a script or commit it (Level 6 covers why)."
        )


def append_weak_area(domain_skill: str, topic: str, what_you_got_wrong: str) -> str:
    """
    Append one row to the real weak-areas.md, matching its existing table format.
    This is the one level-script function that touches real study content —
    everything else in sandbox/ or printed to stdout.
    """
    path = REPO_ROOT / "weak-areas.md"
    today = date.today().isoformat()
    row = f"| {today} | {domain_skill} | {topic} | {what_you_got_wrong} | ☐ |\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(row)
    return f"Logged to weak-areas.md: {topic} ({today})"


def first_text_block(response) -> str:
    """Return the first text block's ``.text`` from a Messages response.

    Do NOT assume ``response.content[0]`` is the text block: ``claude-sonnet-5``
    runs adaptive thinking by *default*, so a response can lead with a
    ``ThinkingBlock`` (which has ``.thinking``, not ``.text``) even when thinking
    was never requested. Index by block type, not by position.
    """
    for block in response.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError(
        f"No text block in response (stop_reason={getattr(response, 'stop_reason', None)})."
    )


def load_json_response(response) -> dict:
    """``first_text_block`` + a ``stop_reason`` guard + ``json.loads``.

    Use for structured-output calls (``output_config.format``). A schema is not a
    guarantee of success — a refusal or a ``max_tokens`` truncation returns output
    that won't parse, so check ``stop_reason`` before ``json.loads``.
    """
    import json

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model refused: {first_text_block(response)}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Truncated before completing the schema — raise max_tokens and retry.")
    return json.loads(first_text_block(response))


def cost_note() -> str:
    """
    Pricing changes independently of model names and is out of scope to hard-code
    here (it would go stale silently). Report token counts; multiply by the
    *current* per-token rate from anthropic.com/pricing yourself for a dollar figure.
    """
    return "See usage.input_tokens / usage.output_tokens on the response — price them at anthropic.com/pricing (verify; rates move)."
