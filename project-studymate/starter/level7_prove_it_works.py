"""
LEVEL 7 — Prove It Works                                            difficulty: *****
Blueprint: D4 Eval, Testing, and Debugging (evals, judges, tracing)

PREREQUISITE: Level 2 working in THIS starter/ folder — this level evals your
own generate_question().

WHAT YOU'RE BUILDING
    A tiny eval harness over generate_question() with THREE pieces:
      1. EVAL_CASES — a fixed, labeled set of inputs, written BEFORE you run
         anything, naming what "done" means for each one.
      2. code_check(q) — grades most cases by structural rules a human can read
         (right shape, no degenerate output). Deterministic, cheap, exact.
      3. judge_check(client, q) — grades the one case where "correct" is a
         quality judgment (does the wording give the answer away?), using a
         SEPARATE model call as an LLM judge, itself schema-constrained.
    Every call also writes one JSON line to sandbox/trace_log.jsonl — a trace,
    so if a case fails you can point at the exact step that produced it instead
    of re-reading the whole transcript.

WHY THIS IS THE RIGHT NEXT STEP
    Every prior level trusted you to eyeball the output. That doesn't scale, and
    it's not how you'd know a change to Level 2's schema or system prompt didn't
    quietly break something. An eval turns "looks right" into a score on a fixed
    set of cases; a trace turns "something's wrong somewhere" into "step 3, case
    'shape-2', took 4x normal latency and returned an empty rationale array."

RUN IT
    python level7_prove_it_works.py
"""

import sys
import json
import time
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from common import REPO_ROOT, MODEL_HAIKU, MODEL_SONNET, require_api_key

import level2_give_it_a_job as l2

from anthropic import Anthropic

TRACE_LOG_PATH = REPO_ROOT / "project-studymate" / "sandbox" / "trace_log.jsonl"

# 1. Written first, before running anything — naming what "done" means per case.
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
    """
    TODO: return (passed, reason). Check ALL of:
      - q["question"] is non-empty
      - exactly 4 choices, exactly 4 rationale strings (already true if Level 2's
        schema held, but an eval never assumes the thing it's testing)
      - 0 <= correct_index <= 3
      - no two choices are identical strings (a degenerate question)
      - the rationale for the correct choice isn't just the question restated
        (a cheap proxy: it shouldn't be a pure substring of the question)
    Return the FIRST failing reason you find, or (True, "ok").
    """
    raise NotImplementedError("TODO: implement code_check()")


def judge_check(client: Anthropic, q: dict) -> tuple[bool, str]:
    """
    TODO: ask a judge model whether the correct choice's WORDING gives itself
    away (e.g. suspiciously longer, more specific, or more hedged than the
    distractors — a real, common flaw in generated MC questions). Use
    output_config with JUDGE_SCHEMA. Return (result["passes"], result["reason"]).

    Use MODEL_HAIKU for the judge, not MODEL_SONNET. Deciding a model tier per
    call is itself part of this project (Level 1) — a judge call is short,
    single-purpose, and doesn't need your most capable tier.
    """
    raise NotImplementedError("TODO: implement judge_check()")


def run_eval_suite(client: Anthropic) -> dict:
    """
    TODO: for each case in EVAL_CASES:
      1. time l2.generate_question(case['topic'], case['domain_folder'])
      2. run code_check or judge_check depending on case['check']
      3. append one dict to a `traces` list:
           {"case_id":..., "elapsed_s":..., "passed":..., "reason":...}
      4. write `traces` to TRACE_LOG_PATH as JSON LINES (one json.dumps(...) per
         line, not one big JSON array — that's what makes it greppable/streamable
         in a real system)
    Return {"pass_rate": passed/total, "results": traces}
    """
    raise NotImplementedError("TODO: implement run_eval_suite()")


def main() -> None:
    require_api_key()
    client = Anthropic()
    report = run_eval_suite(client)

    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['case_id']}  ({r['elapsed_s']:.2f}s)  {r['reason']}")

    print(f"\nPass rate: {report['pass_rate']:.0%}")
    print(f"Trace written to {TRACE_LOG_PATH.relative_to(REPO_ROOT)}")
    print(
        "\nCHECKPOINT: if anything failed, don't re-read the whole eval output to find\n"
        "it — open trace_log.jsonl and find that case_id's line. What does the trace\n"
        "tell you that the pass/fail summary alone doesn't? And: this pass rate is\n"
        "exactly the kind of number Module 5's packaging material used as a\n"
        "promotion gate before shipping a model or prompt change — see\n"
        "domain-2-applications/notes.md, 'Packaging for Reuse'."
    )


if __name__ == "__main__":
    main()
