"""LEVEL 5 — Give It Judgment — reference solution. Read starter/level5_give_it_judgment.py first."""

import sys
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import REPO_ROOT, DOMAIN_WEIGHTS, MODEL_SONNET, load_json_response, require_api_key

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import level2_give_it_a_job as l2
import level4_give_it_tools as l4

from anthropic import Anthropic

SESSION_STATE_PATH = REPO_ROOT / "project-studymate" / "sandbox" / "session_state.json"

RECOMMENDATION_SCHEMA = {
    "type": "object",
    "properties": {
        "should_log": {"type": "boolean"},
        "domain_skill": {"type": "string"},
        "topic": {"type": "string"},
        "what_you_got_wrong": {"type": "string"},
    },
    "required": ["should_log", "domain_skill", "topic", "what_you_got_wrong"],
    "additionalProperties": False,
}


def plan_domain_budget(total_questions: int) -> dict[str, int]:
    total_weight = sum(DOMAIN_WEIGHTS.values())
    raw_shares = {d: (w / total_weight) * total_questions for d, w in DOMAIN_WEIGHTS.items()}
    budget = {d: int(share) for d, share in raw_shares.items()}
    remainder = total_questions - sum(budget.values())

    by_fractional_part = sorted(raw_shares.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for domain_folder, _ in by_fractional_part[:remainder]:
        budget[domain_folder] += 1

    return budget


def load_session_state() -> dict:
    if SESSION_STATE_PATH.exists():
        return json.loads(SESSION_STATE_PATH.read_text(encoding="utf-8"))
    return {"sessions_run": 0, "lifetime_correct": 0, "lifetime_total": 0, "by_domain": {}}


def save_session_state(state: dict) -> None:
    SESSION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSION_STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def recommend_weak_area(client: Anthropic, question: dict, chosen_index: int) -> dict | None:
    chosen_text = question["choices"][chosen_index] if 0 <= chosen_index < 4 else "(no valid answer given)"
    correct_text = question["choices"][question["correct_index"]]
    correct_rationale = question["rationale"][question["correct_index"]]

    prompt = (
        f"Question: {question['question']}\n"
        f"Student picked: {chosen_text}\n"
        f"Correct answer: {correct_text}\n"
        f"Why the correct answer is right: {correct_rationale}\n\n"
        "Judge whether this reflects a real knowledge gap worth logging for spaced "
        "review, versus a careless misread. If it's worth logging, propose a "
        "domain_skill label (e.g. 'D8 · MCP transports'), a short topic, and a "
        "one-sentence description of what the student got wrong."
    )

    response = client.messages.create(
        model=MODEL_SONNET,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": RECOMMENDATION_SCHEMA}},
    )
    # load_json_response finds the text block by type (Sonnet 5 can lead with a
    # thinking block) and guards stop_reason before json.loads.
    rec = load_json_response(response)
    return rec if rec["should_log"] else None


def confirm_and_log(recommendation: dict) -> None:
    print(
        f"StudyMate recommends logging: [{recommendation['domain_skill']}] "
        f"{recommendation['topic']} — {recommendation['what_you_got_wrong']}"
    )
    answer = input("Log this to weak-areas.md? [y/N] ").strip().lower()
    if answer in ("y", "yes"):
        print(
            l4.log_weak_area_impl(
                recommendation["domain_skill"],
                recommendation["topic"],
                recommendation["what_you_got_wrong"],
            )
        )
    else:
        print("Skipped.")


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


if __name__ == "__main__":
    run_session()
