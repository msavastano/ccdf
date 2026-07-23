"""
LEVEL 5 — Give It Judgment                                          difficulty: ****
Blueprint: D1 Agent Architecture & Patterns (workflow vs. agent, memory, HITL)

PREREQUISITE: Levels 2 and 4 working in THIS starter/ folder — this level imports
`generate_question` from your level2 file and the tool machinery from your level4
file. If those still raise NotImplementedError, finish them first.

WHAT YOU'RE BUILDING
    An actual interactive quiz session (you'll really use this to study) with
    three pieces, each testing a different D1 concept:

      1. plan_domain_budget(total_questions) — a WORKFLOW. Given a fixed question
         budget, deterministically split it across the 8 domains proportional to
         DOMAIN_WEIGHTS. Code decides the path; there's no judgment call here, so
         it shouldn't be an agent.

      2. The quiz loop itself — EXTERNAL MEMORY. Score-so-far lives in a plain
         dict you save to sandbox/session_state.json, not buried in the
         conversation transcript. If you re-ran this as a long chat, in-context
         memory would work at first and quietly degrade as the transcript grew;
         external memory doesn't have that failure mode.

      3. recommend_weak_area(...) — an AGENT decision with a HUMAN CHECKPOINT.
         After a wrong answer, Claude — not your code — judges whether this looks
         like a real gap worth logging or a one-off slip, and proposes a
         domain_skill/topic label. Your code then asks the ACTUAL human running
         this script to confirm before the write happens. That confirmation is
         the HITL checkpoint: it goes in front of the action, not as a fix after
         a bad write already landed in weak-areas.md.

WHY THIS IS THE RIGHT NEXT STEP
    Levels 1-4 built capability (call, shape, stream, act). This level is the
    first one that makes a workflow-vs-agent DECISION on purpose, in the same
    program, so you can see the boundary instead of just reading its definition.

RUN IT
    python level5_give_it_judgment.py
    (answer the questions for real — this is a working study tool now)
"""

import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import REPO_ROOT, DOMAIN_WEIGHTS, MODEL_SONNET, require_api_key

# Sibling imports — your own Level 2 / Level 4 solutions, not the reference ones.
import level2_give_it_a_job as l2
import level4_give_it_tools as l4

from anthropic import Anthropic

SESSION_STATE_PATH = REPO_ROOT / "project-studymate" / "sandbox" / "session_state.json"


def plan_domain_budget(total_questions: int) -> dict[str, int]:
    """
    TODO: split `total_questions` across DOMAIN_WEIGHTS proportional to weight,
    with the counts summing to EXACTLY total_questions (use the largest-remainder
    method: give each domain floor(share), then hand out the leftover questions
    one at a time to the domains with the largest fractional remainder).

    Why not just round each share independently? Because independent rounding
    can over- or under-shoot the total — exactly the kind of off-by-a-few bug
    that's invisible on a small budget and wrong every time on a big one.
    """
    raise NotImplementedError("TODO: implement plan_domain_budget()")


def load_session_state() -> dict:
    if SESSION_STATE_PATH.exists():
        return json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))
    return {"sessions_run": 0, "lifetime_correct": 0, "lifetime_total": 0, "by_domain": {}}


def save_session_state(state: dict) -> None:
    """TODO: write `state` back to SESSION_STATE_PATH as JSON (create parent dir if needed)."""
    raise NotImplementedError("TODO: implement save_session_state()")


def recommend_weak_area(client: Anthropic, question: dict, chosen_index: int) -> dict | None:
    """
    Ask Claude to judge whether this wrong answer is worth logging, and if so,
    propose the domain_skill/topic/what_you_got_wrong fields log_weak_area needs.

    TODO:
      1. Build a prompt describing the question, the correct answer, and what
         the student picked instead — include the rationale text so the model
         has the "why" to reason from.
      2. Call client.messages.create(...) with output_config JSON schema:
             {"should_log": bool, "domain_skill": str, "topic": str, "what_you_got_wrong": str}
         (should_log lets the model say "this was a careless slip, not a gap").
      3. Return the parsed dict if should_log is True, else return None.

    This is a JUDGMENT call, not a lookup — that's why it's a model call and not
    an if/else in your code.
    """
    raise NotImplementedError("TODO: implement recommend_weak_area()")


def confirm_and_log(recommendation: dict) -> None:
    """
    TODO: print the recommendation, then `input("Log this to weak-areas.md? [y/N] ")`.
    Only call l4.log_weak_area_impl(...) if the human typed y/yes. This is the
    HITL checkpoint — it must be BEFORE the write, not a way to undo it after.
    """
    raise NotImplementedError("TODO: implement confirm_and_log()")


def run_session(total_questions: int = 6) -> None:
    require_api_key()
    client = Anthropic()
    state = load_session_state()
    budget = plan_domain_budget(total_questions)

    print(f"Domain budget for this session: {budget}\n")
    correct = 0
    asked = 0

    for domain_folder, count in budget.items():
        for _ in range(count):
            q = l2.generate_question(f"a core testable concept in {domain_folder}", domain_folder)
            l2.print_question(q)
            asked += 1

            raw = input("Your answer (A-D): ").strip().upper()
            chosen_index = "ABCD".find(raw) if raw and raw[0] in "ABCD" else -1
            is_correct = chosen_index == q["correct_index"]
            correct += int(is_correct)

            state.setdefault("by_domain", {}).setdefault(domain_folder, {"correct": 0, "total": 0})
            state["by_domain"][domain_folder]["total"] += 1
            state["by_domain"][domain_folder]["correct"] += int(is_correct)

            if is_correct:
                print("Correct.\n")
            else:
                print(f"Incorrect — correct answer was {chr(65 + q['correct_index'])}.\n")
                rec = recommend_weak_area(client, q, chosen_index)
                if rec:
                    confirm_and_log(rec)

    state["sessions_run"] += 1
    state["lifetime_correct"] += correct
    state["lifetime_total"] += asked
    save_session_state(state)

    print(f"\nSession score: {correct}/{asked}")
    print(
        "CHECKPOINT: plan_domain_budget() is a WORKFLOW step (deterministic code) and\n"
        "recommend_weak_area() is an AGENT step (model judgment). If you swapped them —\n"
        "hardcoded which topics to log, and asked the model to decide the domain\n"
        "budget by 'vibes' each run — what would break, and why does the exam favor\n"
        "'the simplest pattern that solves it' over defaulting to an agent everywhere?"
    )


if __name__ == "__main__":
    run_session()
