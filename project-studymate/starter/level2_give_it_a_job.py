"""
LEVEL 2 — Give It a Job                                              difficulty: **
Blueprint: D6 Prompt & Context Engineering (system prompts) · D2 Structured Outputs

WHAT YOU'RE BUILDING
    generate_question(topic, domain_folder) -> dict
    Give Claude a persona via a SYSTEM prompt ("you are StudyMate, a CCDV-F tutor"),
    then force its reply into a fixed shape — one multiple-choice practice question
    with a rationale per option — using output_config.format (a JSON schema), the
    SAME mechanism documented in ../domain-2-applications/structured-outputs-examples.md.
    Read that file section "Example 1" before starting if you haven't already.

WHY THIS IS THE RIGHT NEXT STEP
    Level 1 proved you can talk to Claude. This level proves you can make Claude
    reliably talk back in a shape YOUR CODE can consume without a parse-and-pray
    step — the exact distinction the exam calls out as a trap: "respond only in
    JSON" is a request the model can slip; output_config.format is enforced per
    token. You'll feel the difference because you'll assert on the parsed dict
    with zero defensive coercion.

RUN IT
    python level2_give_it_a_job.py
"""

import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, require_api_key

from anthropic import Anthropic

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
        "choices": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 4,
            "maxItems": 4,
        },
        "correct_index": {"type": "integer", "minimum": 0, "maximum": 3},
        "rationale": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 4,
            "maxItems": 4,
            "description": "One rationale string per choice, same order as `choices`.",
        },
    },
    "required": ["question", "choices", "correct_index", "rationale"],
    "additionalProperties": False,
}


def generate_question(topic: str, domain_folder: str) -> dict:
    """
    TODO:
      1. Build an Anthropic() client.
      2. Call client.messages.create(...) with:
           - model=MODEL_SONNET
           - max_tokens=800
           - system=SYSTEM_PROMPT              <-- new: system prompts are a top-level
                                                    param, NOT a message with role="system"
           - messages=[{"role": "user", "content": f"Write a question about {topic} ..."}]
           - output_config={"format": {"type": "json_schema", "schema": QUESTION_SCHEMA}}
      3. Check response.stop_reason before parsing:
           - "refusal"    -> raise RuntimeError with the refusal text
           - "max_tokens" -> raise RuntimeError telling the caller to raise max_tokens
           - otherwise    -> json.loads(response.content[0].text) and return it

    Why check stop_reason at all, if the schema is "guaranteed"? Because the
    guarantee only covers a completed, non-refused turn — see
    structured-outputs-examples.md, "A guaranteed schema is NOT a guaranteed success".
    """
    raise NotImplementedError("TODO: implement generate_question()")


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

        # Sanity-check the shape you should get for free from the schema.
        assert len(q["choices"]) == 4
        assert len(q["rationale"]) == 4
        assert 0 <= q["correct_index"] <= 3

        print_question(q)

    print(
        "CHECKPOINT: Comment out output_config= and instead put 'Respond ONLY with\n"
        "JSON matching this shape: ...' in the user message. Run it 5 times. Did it\n"
        "ever produce something json.loads() couldn't parse, or a `choices` list\n"
        "that wasn't length 4? That gap is the point of this level."
    )


if __name__ == "__main__":
    main()
