"""LEVEL 2 — Give It a Job — reference solution. Read starter/level2_give_it_a_job.py first."""

import sys
import json
import pathlib

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
        "choices": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
        "correct_index": {"type": "integer", "minimum": 0, "maximum": 3},
        "rationale": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 4},
    },
    "required": ["question", "choices", "correct_index", "rationale"],
    "additionalProperties": False,
}


def generate_question(topic: str, domain_folder: str) -> dict:
    response = _client.messages.create(
        model=MODEL_SONNET,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Write a question about: {topic} (blueprint domain: {domain_folder}).",
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": QUESTION_SCHEMA}},
    )

    if response.stop_reason == "refusal":
        raise RuntimeError(f"Model refused: {response.content[0].text}")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Truncated before completing the schema — raise max_tokens and retry.")

    return json.loads(response.content[0].text)


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
