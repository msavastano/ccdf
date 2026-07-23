"""
LEVEL 1 — First Contact                                              difficulty: *
Blueprint: D2 Claude API Mechanics (6.8%) · D5 Model Selection & Tradeoffs

WHAT YOU'RE BUILDING
    A function that sends one message to Claude and gets text back, then a small
    harness that calls the SAME question against all three model tiers so you can
    SEE the quality/latency/cost tradeoff instead of reading about it.

WHY THIS IS THE RIGHT FIRST STEP
    Every other level in this project is a variation on one request/response
    exchange. If you don't have the shape of `messages.create()` cold — model,
    max_tokens, messages, and what comes back on `response` — nothing after this
    will make sense. The exam tests this shape directly (D2 · API Mechanics).

RUN IT
    pip install -r ../requirements.txt
    (set ANTHROPIC_API_KEY in your shell — see ../.env.example)
    python level1_first_contact.py
"""

import sys
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import ALL_TIERS, require_api_key

from anthropic import Anthropic


def ask(question: str, model: str) -> tuple[str, dict]:
    """
    Send ONE user message to `model` and return (answer_text, usage_dict).

    usage_dict should have at least: input_tokens, output_tokens
    (these live on response.usage).

    TODO:
      1. Construct an Anthropic() client.
      2. Call client.messages.create(...) with:
           - model=model
           - max_tokens=300          (small on purpose — you're paying for every one)
           - messages=[{"role": "user", "content": question}]
      3. Pull the text out of response.content[0].text
      4. Return (text, {"input_tokens": ..., "output_tokens": ...})

    HINT — the messages list is a list of turns, each a dict with "role" and
    "content". "role" is "user" or "assistant" — there's no "system" role in the
    messages list itself (system prompts are a separate top-level param you'll
    meet in Level 2).

    HINT — response.content is a LIST of content blocks (a model detail that
    matters a lot once you add tools/thinking in later levels). For a plain text
    reply there's exactly one block, so response.content[0].text is the answer.
    """
    raise NotImplementedError("TODO: implement ask()")


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

    print(
        "CHECKPOINT: Look at the three latencies and output_tokens counts you just printed.\n"
        "Which tier would you actually ship for a real-time chat widget? For an\n"
        "overnight batch summarization job? Write one sentence for each before\n"
        "moving to checkpoints.md Q1-Q2."
    )


if __name__ == "__main__":
    main()
