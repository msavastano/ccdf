"""LEVEL 2 — Give It a Job — reference solution. Read starter/level2_give_it_a_job.py first."""

import sys
import json
import pathlib
from typing import Any, cast

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, require_api_key

from anthropic import Anthropic

_client = Anthropic()

SYSTEM_PROMPT = """\
You are StudyMate, a tutor for the Claude Certified Developer - Foundations (CCDV-F) exam.
You write ONE original multiple-choice practice question at a time, scenario-based where
possible, with exactly 4 answer choices and a plausible distractor in every wrong choice.
Never claim a question is from the real exam. You are precise, concise, and a little
encouraging — this is a hard exam and the student is doing the work.
"""

QUESTION_SCHEMA = {
    "type": "object",
    "properties": {
        "question": {"type": "string"},
        # No fixed-length array in the schema: `maxItems` is rejected outright and
        # `minItems` only accepts 0 or 1 (a non-empty toggle, not a count). Both
        # verified against the live API 2026-07-23; see the 400 table in
        # ../domain-2-applications/structured-outputs-examples.md. Four named,
        # required properties is the schema-legal way to force exactly four items;
        # generate_question() reassembles them into choices/rationale lists below.
        "choice_a": {"type": "string"},
        "choice_b": {"type": "string"},
        "choice_c": {"type": "string"},
        "choice_d": {"type": "string"},
        # "minimum"/"maximum" aren't supported on integers either (verified 2026-07-23);
        # "enum" is the supported way to bound one.
        "correct_index": {"type": "integer", "enum": [0, 1, 2, 3]},
        "rationale_a": {"type": "string"},
        "rationale_b": {"type": "string"},
        "rationale_c": {"type": "string"},
        "rationale_d": {"type": "string"},
    },
    "required": [
        "question",
        "choice_a", "choice_b", "choice_c", "choice_d",
        "correct_index",
        "rationale_a", "rationale_b", "rationale_c", "rationale_d",
    ],
    "additionalProperties": False,
}


def generate_question(topic: str, domain_folder: str) -> dict:
    response = _client.messages.create(
        model=MODEL_SONNET,
        # 800 was too tight: Sonnet 5 sometimes emits a leading thinking block even
        # without extended thinking requested, sharing this budget with the JSON
        # output (observed 2026-07-23).
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Write a question about: {topic} (blueprint domain: {domain_folder}).",
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": QUESTION_SCHEMA}},
    )

    # content[0] isn't reliably the text block — Claude can emit a leading
    # ThinkingBlock even without extended thinking explicitly requested (observed
    # 2026-07-23). Find the text block by type instead of indexing.
    text_block = cast(Any, next(b for b in response.content if getattr(b, "type", None) == "text"))

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model refused: {text_block.text}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Truncated before completing the schema — raise max_tokens and retry.")

    parsed = json.loads(text_block.text)
    return {
        "question": parsed["question"],
        "choices": [parsed["choice_a"], parsed["choice_b"], parsed["choice_c"], parsed["choice_d"]],
        "correct_index": parsed["correct_index"],
        "rationale": [
            parsed["rationale_a"],
            parsed["rationale_b"],
            parsed["rationale_c"],
            parsed["rationale_d"],
        ],
    }


def print_question(q: dict) -> None:
    print(q["question"])
    for i, choice in enumerate(q["choices"]):
        marker = "*" if i == q["correct_index"] else " "
        print(f"  [{marker}] {chr(65 + i)}. {choice}")
    print("Rationale:")
    for i, r in enumerate(q["rationale"]):
        print(f"  {chr(65 + i)}. {r}")
    print()


def main() -> None:
    require_api_key()
    topics = [
        ("prompt caching breakpoints", "domain-2-applications"),
        ("workflow vs. agent selection", "domain-1-agents"),
    ]
    for topic, domain_folder in topics:
        q = generate_question(topic, domain_folder)
        assert len(q["choices"]) == 4
        assert len(q["rationale"]) == 4
        assert 0 <= q["correct_index"] <= 3
        print_question(q)


if __name__ == "__main__":
    main()
