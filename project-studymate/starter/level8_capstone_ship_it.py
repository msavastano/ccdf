"""
LEVEL 8 — Capstone: Ship It                                        difficulty: ******
Blueprint: D1 Orchestrator-Worker · D5 Cost & Observability · D2 Deployment & Versioning
(Part A of this level, MCP, lives in mcp_server.py — read it too.)

PREREQUISITE: Level 2 working in THIS starter/ folder.

WHAT YOU'RE BUILDING
    Part B — run_orchestrator(domains): fan out ONE generate-a-question worker
    call PER DOMAIN, concurrently, then ONE more orchestrator call that reads
    all the generated questions and writes a short briefing. You instrument
    token usage across every one of the N+1 calls, so the ~N x cost multiplier
    this pattern carries is a number you measured, not a fact you memorized.

    Part C — no code. Answer, in your own words, the deployment questions at
    the bottom of this file, using domain-2-applications/notes.md's "Deployment
    and Versioning" section (already in this repo) as your reference.

WHY THIS IS THE RIGHT LAST STEP
    Every domain this project touches shows up here at once: D1 (is this task
    independent enough to fan out?), D5 (what did that fan-out actually cost?),
    D2 (where would this actually run, and how would you pin it?), D8 (the MCP
    server you built in Part A). This is the level that asks you to make the
    call, not just recognize the concept in a multiple-choice option.

RUN IT
    python level8_capstone_ship_it.py
"""

import sys
import json
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import MODEL_SONNET, DOMAIN_WEIGHTS, require_api_key

import level2_give_it_a_job as l2

from anthropic import Anthropic


def _generate_question_with_usage(client: Anthropic, model: str, topic: str, domain_folder: str) -> tuple[dict, dict]:
    """
    Same call Level 2's generate_question makes, but also returns token usage —
    you need the raw response for that, which generate_question() doesn't expose.
    Already implemented for you; the TODOs below are the orchestration around it.
    """
    response = client.messages.create(
        model=model,
        max_tokens=800,
        system=l2.SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Write a question about: {topic} (blueprint domain: {domain_folder})."}],
        output_config={"format": {"type": "json_schema", "schema": l2.QUESTION_SCHEMA}},
    )
    q = json.loads(response.content[0].text)
    usage = {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
    return q, usage


def run_orchestrator(client: Anthropic, domains: list[str]) -> dict:
    """
    TODO:
      1. Open a ThreadPoolExecutor(max_workers=len(domains)). Submit one
         _generate_question_with_usage(client, MODEL_SONNET, f"a core testable
         concept in {d}", d) call PER domain in `domains` — this is the WORKER
         fan-out, running concurrently.
      2. Collect every (question, usage) result as futures complete, and sum
         input_tokens/output_tokens across all of them.
      3. Build one more prompt for the ORCHESTRATOR call: hand it the list of
         generated `question` strings and ask for a 3-sentence briefing on which
         ones look hardest and why. Make this ONE more client.messages.create
         call (plain text, no schema needed) and add ITS usage to your running
         total.
      4. Return {
             "questions": [...],           # the N generated question dicts
             "briefing": "...",            # the orchestrator's text
             "total_input_tokens": ...,
             "total_output_tokens": ...,
             "call_count": len(domains) + 1,
         }

    THE QUESTION THIS ANSWERS: is quiz-question generation across independent
    domains the kind of task that justifies this pattern? Contrast with asking
    one worker to draft a paragraph and a second worker to "improve" that same
    paragraph — that's NOT independent, and fanning it out wouldn't help.
    """
    raise NotImplementedError("TODO: implement run_orchestrator()")


def main() -> None:
    require_api_key()
    client = Anthropic()

    # Pick the 3 highest-weighted domains — deliberately not all 8, to keep this
    # capstone run's cost bounded while you're first testing it.
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
    print(
        "Price these at the CURRENT per-token rate from anthropic.com/pricing — do not\n"
        "hard-code a dollar figure in this project; rates move independently of model names."
    )

    print(
        "\n--- Part C: Deployment (answer in your own words, no code) ---\n"
        "1. A study group of 30 people wants to run StudyMate together. Same-API-key\n"
        "   1P API, Bedrock, or Vertex? What does the group's existing infrastructure\n"
        "   (if any) decide here, versus what a feature comparison would decide?\n"
        "2. You pin MODEL_SONNET's exact ID in common.py today. Eight months from now\n"
        "   that ID may be retired. What's your rollback plan, and what do you need to\n"
        "   have kept from Level 7's eval suite to know the replacement is safe to promote?\n"
        "3. If this group is in the EU and data residency is a hard requirement, does\n"
        "   that decide the platform question before cost or latency even get compared?\n"
        "See domain-2-applications/notes.md, 'Deployment and Versioning', if you get stuck."
    )


if __name__ == "__main__":
    main()
