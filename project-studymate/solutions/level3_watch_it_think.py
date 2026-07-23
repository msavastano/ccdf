"""LEVEL 3 — Watch It Think — reference solution. Read starter/level3_watch_it_think.py first."""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, require_api_key

from anthropic import Anthropic


def stream_answer(client: Anthropic, model: str, messages: list[dict]) -> str:
    full_text = ""
    with client.messages.stream(model=model, max_tokens=600, messages=messages) as stream:
        for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                print(event.delta.text, end="", flush=True)
                full_text += event.delta.text
            elif event.type == "message_stop":
                pass  # the ONLY safe point to treat the turn as complete
    print()
    return full_text


def ask_with_thinking(client: Anthropic, model: str, prompt: str, budget_tokens: int) -> tuple[str, str]:
    response = client.messages.create(
        model=model,
        max_tokens=budget_tokens + 600,
        thinking={"type": "enabled", "budget_tokens": budget_tokens},
        messages=[{"role": "user", "content": prompt}],
    )
    thinking_parts = [b.thinking for b in response.content if b.type == "thinking"]
    text_parts = [b.text for b in response.content if b.type == "text"]
    return "\n".join(thinking_parts), "\n".join(text_parts)


def main() -> None:
    require_api_key()
    client = Anthropic()

    print("--- Turn 1 (streamed) ---")
    messages = [{"role": "user", "content": "Name the four content_block delta types you might see for a text-only reply, briefly."}]
    turn1_text = stream_answer(client, MODEL_SONNET, messages)
    messages.append({"role": "assistant", "content": turn1_text})

    print("\n--- Turn 2 (streamed, references turn 1) ---")
    messages.append({"role": "user", "content": "Good. Now, of those, which one actually signals the reply is safe to store in history?"})
    stream_answer(client, MODEL_SONNET, messages)

    print("\n\n--- Extended thinking ---")
    thinking, answer = ask_with_thinking(
        client,
        MODEL_SONNET,
        "A support bot needs to pick between issuing a refund or escalating to a human, "
        "given a messy multi-paragraph complaint. Should this call use extended thinking? Decide, then answer.",
        budget_tokens=2000,
    )
    print("[thinking]\n" + thinking[:500] + ("..." if len(thinking) > 500 else ""))
    print("\n[answer]\n" + answer)


if __name__ == "__main__":
    main()
