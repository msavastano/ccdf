"""LEVEL 7 — Prove It Works — reference solution. Read starter/level7_prove_it_works.py first."""

import sys
import json
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import REPO_ROOT, MODEL_HAIKU, MODEL_SONNET, require_api_key

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import level2_give_it_a_job as l2

from anthropic import Anthropic

TRACE_LOG_PATH = REPO_ROOT / "project-studymate" / "sandbox" / "trace_log.jsonl"

EVAL_CASES = [
    {"id": "shape-1", "topic": "prompt caching breakpoints", "domain_folder": "domain-2-applications", "check": "code"},
    {"id": "shape-2", "topic": "MCP transport choice (stdio vs HTTP)", "domain_folder": "domain-8-tools-mcps", "check": "code"},
    {"id": "shape-3", "topic": "retriable vs terminal tool failures", "domain_folder": "domain-4-eval-testing", "check": "code"},
    {"id": "shape-4", "topic": "extended thinking budget tradeoffs", "domain_folder": "domain-5-model-selection", "check": "code"},
    {"id": "quality-1", "topic": "workflow vs. agent selection", "domain_folder": "domain-1-agents", "check": "judge"},
]

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {"passes": {"type": "boolean"}, "reason": {"type": "string"}},
    "required": ["passes", "reason"],
    "additionalProperties": False,
}


def code_check(q: dict) -> tuple[bool, str]:
    if not q.get("question", "").strip():
        return False, "empty question"
    if len(q.get("choices", [])) != 4:
        return False, f"expected 4 choices, got {len(q.get('choices', []))}"
    if len(q.get("rationale", [])) != 4:
        return False, f"expected 4 rationale entries, got {len(q.get('rationale', []))}"
    if not (0 <= q.get("correct_index", -1) <= 3):
        return False, f"correct_index {q.get('correct_index')} out of range"
    if len(set(q["choices"])) != len(q["choices"]):
        return False, "two choices are identical (degenerate question)"
    correct_rationale = q["rationale"][q["correct_index"]]
    if correct_rationale.strip().lower() in q["question"].strip().lower():
        return False, "correct rationale is just a restatement of the question"
    return True, "ok"


def judge_check(client: Anthropic, q: dict) -> tuple[bool, str]:
    prompt = (
        "Here is a multiple-choice practice question:\n"
        f"Question: {q['question']}\n"
        + "\n".join(f"{chr(65+i)}. {c}" for i, c in enumerate(q["choices"]))
        + f"\nCorrect answer: {chr(65 + q['correct_index'])}\n\n"
        "Does the WORDING of the correct choice give itself away — e.g. is it "
        "noticeably longer, more specific/hedged, or more detailed than the "
        "distractors, in a way a test-taker could exploit without knowing the "
        "material? Fail it if so."
    )
    response = client.messages.create(
        model=MODEL_HAIKU,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": JUDGE_SCHEMA}},
    )
    result = json.loads(response.content[0].text)
    return result["passes"], result["reason"]


def run_eval_suite(client: Anthropic) -> dict:
    traces = []
    for case in EVAL_CASES:
        start = time.perf_counter()
        q = l2.generate_question(case["topic"], case["domain_folder"])
        elapsed = time.perf_counter() - start

        if case["check"] == "code":
            passed, reason = code_check(q)
        else:
            passed, reason = judge_check(client, q)

        traces.append(
            {"case_id": case["id"], "elapsed_s": elapsed, "passed": passed, "reason": reason}
        )

    TRACE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TRACE_LOG_PATH.open("w", encoding="utf-8") as f:
        for t in traces:
            f.write(json.dumps(t) + "\n")

    passed_count = sum(1 for t in traces if t["passed"])
    return {"pass_rate": passed_count / len(traces), "results": traces}


def main() -> None:
    require_api_key()
    client = Anthropic()
    report = run_eval_suite(client)

    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['case_id']}  ({r['elapsed_s']:.2f}s)  {r['reason']}")

    print(f"\nPass rate: {report['pass_rate']:.0%}")
    print(f"Trace written to {TRACE_LOG_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
