"""
LEVEL 3 — Watch It Think                                            difficulty: ***
Blueprint: D2 Streaming · D5 Adaptive Thinking

WHAT YOU'RE BUILDING
    1. stream_answer(prompt) — prints tokens as they arrive AND returns the full
       text, but only commits that text to conversation history once the stream
       has truly finished.
    2. A 2-turn conversation built from repeated stream_answer() calls, to prove
       your commit timing is right (the follow-up question only makes sense if
       turn 1 was captured correctly).
    3. ask_with_thinking(prompt) — same question, but with adaptive thinking
       enabled, so you can see the thinking block and the answer block as two
       separate pieces of one response.

WHY THIS IS THE RIGHT NEXT STEP
    Levels 1-2 were single-shot request/response. Production traffic streams, and
    connections aren't as clean as your dev machine's. The exam's specific trap
    here: "a stream ending is not a message completing." There are multiple event
    types (content_block_start/delta/stop, message_delta, message_stop) and only
    ONE of them means "the whole turn, possibly multiple content blocks, is done."
    Get this wrong and you'll append a half-built assistant turn to history, then
    watch the NEXT request fail in a way that looks like a tool-schema bug but
    isn't.

RUN IT
    python level3_watch_it_think.py
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, require_api_key

from anthropic import Anthropic


def stream_answer(client: Anthropic, model: str, messages: list[dict]) -> str:
    """
    Stream a reply to `messages` (an already-built conversation history) and
    return the complete text once the stream is fully done — not before.

    TODO:
      1. Open `with client.messages.stream(model=model, max_tokens=600,
         messages=messages) as stream:`
      2. Iterate `for event in stream:` and inspect `event.type`.
           - "content_block_delta" with event.delta.type == "text_delta" ->
             print(event.delta.text, end="", flush=True) AND accumulate it into
             a local string. This is the part that makes output feel "live."
           - "message_stop" -> the WHOLE turn (every content block) is done.
             This is the only place it's safe to return the accumulated text.
      3. Print a newline after the loop ends and return the accumulated text.

    THE TRAP TO AVOID: do not return (or append to `messages`) as soon as you
    see "content_block_stop". A single assistant turn can have more than one
    content block (you'll see this directly in ask_with_thinking below, where
    a thinking block and a text block are TWO blocks in ONE turn). Committing
    on content_block_stop would cut the turn off after the first block.
    """
    raise NotImplementedError("TODO: implement stream_answer()")


def ask_with_thinking(client: Anthropic, model: str, prompt: str, effort: str = "high") -> tuple[str, str]:
    """
    Ask one question with adaptive thinking enabled. Return (thinking_text, answer_text).

    TODO:
      1. Call client.messages.create(
             model=model,
             max_tokens=2500,
             # The old fixed-budget knob — thinking={"type":"enabled","budget_tokens":N} —
             # is gone on current models (claude-sonnet-5 400s on it). Adaptive thinking
             # lets Claude decide how much to think; output_config.effort controls the
             # depth that budget_tokens used to. display:"summarized" makes the thinking
             # block carry readable text (the default, "omitted", leaves it empty).
             thinking={"type": "adaptive", "display": "summarized"},
             output_config={"effort": effort},
             messages=[{"role": "user", "content": prompt}],
         )
      2. response.content is a list of blocks. Walk it and pull out:
           - the block(s) with .type == "thinking" -> block.thinking (join if >1)
           - the block(s) with .type == "text"     -> block.text
      3. Return (thinking_text, answer_text)

    NOTE for later: if you were going to continue this conversation with another
    turn, you'd append the ENTIRE original content list (thinking block included,
    byte-for-byte) back into `messages` as the assistant turn. Stripping the
    thinking block before the next request is a documented way to break the call.
    You don't need to implement that continuation here — just know it's why you
    return the raw blocks instead of just the answer.
    """
    raise NotImplementedError("TODO: implement ask_with_thinking()")


def main() -> None:
    require_api_key()
    client = Anthropic()

    print("--- Turn 1 (streamed) ---")
    messages = [{"role": "user", "content": "Name the four content_block delta types you might see for a text-only reply, briefly."}]
    turn1_text = stream_answer(client, MODEL_SONNET, messages)
    messages.append({"role": "assistant", "content": turn1_text})  # committed AFTER message_stop only

    print("\n--- Turn 2 (streamed, references turn 1) ---")
    messages.append({"role": "user", "content": "Good. Now, of those, which one actually signals the reply is safe to store in history?"})
    turn2_text = stream_answer(client, MODEL_SONNET, messages)

    print("\n\n--- Extended thinking ---")
    thinking, answer = ask_with_thinking(
        client,
        MODEL_SONNET,
        "A support bot needs to pick between issuing a refund or escalating to a human, "
        "given a messy multi-paragraph complaint. Should this call use extended thinking? Decide, then answer.",
    )
    print("[thinking]\n" + thinking[:500] + ("..." if len(thinking) > 500 else ""))
    print("\n[answer]\n" + answer)

    print(
        "\nCHECKPOINT: turn2_text should show the model correctly identifying that only\n"
        "message_stop (not content_block_stop) signals a fully-committable turn — that's\n"
        "the behavior your commit-timing choice in Turn 1/2 was designed to make possible.\n"
        "If turn2's answer is confused, your history append in Turn 1 likely happened at\n"
        "the wrong event."
    )


if __name__ == "__main__":
    main()
