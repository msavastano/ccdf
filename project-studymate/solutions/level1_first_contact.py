"""LEVEL 1 — First Contact — reference solution. Read starter/level1_first_contact.py first."""

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import ALL_TIERS, require_api_key

from anthropic import Anthropic

_client = Anthropic()


def ask(question: str, model: str) -> tuple[str, dict]:
    response = _client.messages.create(
        model=model,
        max_tokens=300,
        messages=[{"role": "user", "content": question}],
    )
    text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
    }
    return text, usage


def main() -> None:
    require_api_key()
    question = "In one paragraph, what is the difference between a workflow and an agent?"

    print(f"Question: {question}\n")
    for tier_name, model_id in ALL_TIERS.items():
        start = time.perf_counter()
        text, usage = ask(question, model_id)
        elapsed = time.perf_counter() - start

        print(f"--- {tier_name} ({model_id}) ---")
        print(f"latency: {elapsed:.2f}s   input_tokens: {usage['input_tokens']}   output_tokens: {usage['output_tokens']}")
        print(text)
        print()


if __name__ == "__main__":
    main()
