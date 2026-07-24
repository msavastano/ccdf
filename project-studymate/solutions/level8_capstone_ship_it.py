"""LEVEL 8 — Capstone: Ship It — reference solution. Read starter/level8_capstone_ship_it.py first."""

import sys
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, DOMAIN_WEIGHTS, first_text_block, load_json_response, require_api_key

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import level2_give_it_a_job as l2

from anthropic import Anthropic


def _generate_question_with_usage(client: Anthropic, model: str, topic: str, domain_folder: str) -> tuple[dict, dict]:
    response = client.messages.create(
        model=model,
        # 800 shares its budget with a possible leading thinking block on Sonnet 5
        # (see level2's note) — too tight for the full schema. Match level2 at 2048.
        max_tokens=2048,
        system=l2.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Write a question about: {topic} (blueprint domain: {domain_folder})."}],
        output_config={"format": {"type": "json_schema", "schema": l2.QUESTION_SCHEMA}},
    )
    q = load_json_response(response)
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    return q, usage


def run_orchestrator(client: Anthropic, domains: list[str]) -> dict:
    total_input = 0
    total_output = 0
    questions = []

    with ThreadPoolExecutor(max_workers=len(domains)) as pool:
        futures = {
            pool.submit(
                _generate_question_with_usage, client, MODEL_SONNET,
                f"a core testable concept in {d}", d,
            ): d
            for d in domains
        }
        for future in as_completed(futures):
            q, usage = future.result()
            questions.append(q)
            total_input += usage["input_tokens"]
            total_output += usage["output_tokens"]

    briefing_prompt = (
        "Here are practice questions generated for a study session:\n"
        + "\n".join(f"- {q['question']}" for q in questions)
        + "\n\nIn 3 sentences, note which of these look hardest and why."
    )
    response = client.messages.create(
        model=MODEL_SONNET,
        max_tokens=300,
        messages=[{"role": "user", "content": briefing_prompt}],
    )
    briefing = first_text_block(response)
    total_input += response.usage.input_tokens
    total_output += response.usage.output_tokens

    return {
        "questions": questions,
        "briefing": briefing,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "call_count": len(domains) + 1,
    }


def main() -> None:
    require_api_key()
    client = Anthropic()

    domains = sorted(DOMAIN_WEIGHTS, key=DOMAIN_WEIGHTS.get, reverse=True)[:3]
    print(f"Fanning out to: {domains}\n")

    result = run_orchestrator(client, domains)

    for q in result["questions"]:
        print("-", q["question"])
    print("\nBriefing:\n" + result["briefing"])

    print(
        f"\nToken usage — {result['call_count']} calls total: "
        f"{result['total_input_tokens']} in / {result['total_output_tokens']} out."
    )


if __name__ == "__main__":
    main()
