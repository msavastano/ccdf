#!/usr/bin/env python3
"""Regenerate study-hub.html from every domain-*/flashcards.md and practice-questions.md.

Run from the repo root:  python build-study-hub.py

Flashcard format expected in the md files (unchanged from build-flashcards.py):
    ## Skill Name
    **Q:** question text (may span lines)
    **A:** answer text (may span lines)

Practice-question format expected (canonical "Variant A" grammar — all
domain practice-questions.md files must be normalized to this before the
build will succeed):

    **Q<n> · D<d> · <Skill>** (select ONE|TWO|THREE)
    <stem, until first option line>

    A. <option text>
    B. <option text>              (contiguous A.. letters, 4-5 options)
    ...

    ## Answer Key ...              (any heading text; a file may contain
                                     several such sections — e.g. domain-2's
                                     supplements — the parser does not key
                                     off the heading, only off the entries
                                     below, so it doesn't matter)
    **Q<n>: B.**        or        **Q<n>: A and C.**
    - A — <rationale> ✗
    - B — <rationale> ✓
    ...

The build fails loudly (collects every problem, then exit(1)) rather than
silently emitting a partial/incorrect study hub.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "study-hub.html"
TEMPLATE_FILE = ROOT / "study-hub-template.html"

DOMAIN_META = {
    "domain-1-agents": ("D1", "Agents and Workflows", 14.7),
    "domain-2-applications": ("D2", "Applications and Integration", 33.1),
    "domain-3-claude-code": ("D3", "Claude Code", 3.1),
    "domain-4-eval-testing": ("D4", "Eval, Testing, and Debugging", 2.6),
    "domain-5-model-selection": ("D5", "Model Selection and Optimization", 16.8),
    "domain-6-prompt-context": ("D6", "Prompt and Context Engineering", 11.0),
    "domain-7-security": ("D7", "Security and Safety", 8.1),
    "domain-8-tools-mcps": ("D8", "Tools and MCPs", 10.6),
}

# ---------------------------------------------------------------------------
# Flashcards — identical to build-flashcards.py's parse_cards()
# ---------------------------------------------------------------------------


def parse_cards(md_text):
    cards, skill, cur, field = [], "", None, None
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if line.startswith("## "):
            skill = line[3:].strip()
            continue
        if line.startswith("**Q:**"):
            if cur and cur["q"] and cur["a"]:
                cards.append(cur)
            cur = {"skill": skill, "q": line[6:].strip(), "a": ""}
            field = "q"
            continue
        if line.startswith("**A:**"):
            if cur is not None:
                cur["a"] = line[6:].strip()
                field = "a"
            continue
        if cur is not None and field and line.strip() and not line.startswith("#"):
            cur[field] += " " + line.strip()
    if cur and cur["q"] and cur["a"]:
        cards.append(cur)
    return cards


# ---------------------------------------------------------------------------
# Practice questions — canonical Variant A parser
# ---------------------------------------------------------------------------

Q_HEADER_RE = re.compile(
    r"^\*\*Q(\d+) · (D\d) · (.+?)\*\*\s*\(select (ONE|TWO|THREE)\)\s*$"
)
OPTION_RE = re.compile(r"^([A-E])\. (.*)$")
KEY_RE = re.compile(r"^\*\*Q(\d+): ([A-E](?:(?:,| and|, and) [A-E])*)\.?\*\*\s*$")
RATIONALE_RE = re.compile(r"^- ([A-E]) — (.*?)\s*([✓✗])\s*$")

SELECT_N = {"ONE": 1, "TWO": 2, "THREE": 3}

OLD_VARIANT_MARKERS = ["_Tag:", "### Q", "**Select"]


def parse_question_blocks(md_text, domain_code, filename, errors):
    """First pass: pull every **Qn · Dd · Skill** (select N) block + its options."""
    lines = md_text.splitlines()
    questions = {}
    order = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i].rstrip()
        m = Q_HEADER_RE.match(line)
        if not m:
            i += 1
            continue
        num = int(m.group(1))
        dcode = m.group(2)
        skill = m.group(3)
        selword = m.group(4)
        if dcode != domain_code:
            errors.append(
                f"{filename}:Q{num} — header domain tag {dcode} doesn't match file's domain {domain_code}"
            )
        i += 1
        stem_lines = []
        while i < n and not OPTION_RE.match(lines[i].rstrip()):
            s = lines[i].strip()
            if s:
                stem_lines.append(s)
            i += 1
        stem = " ".join(stem_lines)
        options = []
        expected = ord("A")
        while i < n:
            om = OPTION_RE.match(lines[i].rstrip())
            if not om:
                break
            letter, text = om.group(1), om.group(2).strip()
            if ord(letter) != expected:
                errors.append(
                    f"{filename}:Q{num} — options not contiguous starting at A "
                    f"(expected {chr(expected)}, got {letter})"
                )
            options.append({"letter": letter, "text": text})
            expected += 1
            i += 1
        if len(options) < 4:
            errors.append(f"{filename}:Q{num} — fewer than 4 options ({len(options)})")
        if num in questions:
            errors.append(f"{filename}:Q{num} — duplicate question number")
        questions[num] = {
            "num": num,
            "domain": dcode,
            "skill": skill,
            "select": SELECT_N.get(selword, 0),
            "stem": stem,
            "options": options,
            "correct": [],
            "rationales": {},
        }
        order.append(num)
    return questions, order


def parse_answer_keys(md_text, filename, questions, errors):
    """Second pass: walk the whole file for **Qn: X[, Y and Z].** entries plus the
    '- L — text mark' rationale bullets that follow, and join by question number.
    Not gated on any particular '## Answer...' heading text — domain-2 has
    several differently-worded headings across its supplements, so the join
    is done purely off the entry/bullet patterns themselves."""
    lines = md_text.splitlines()
    i, n = 0, len(lines)
    current_num = None
    seen_keys = set()
    while i < n:
        line = lines[i].rstrip()
        km = KEY_RE.match(line)
        if km:
            num = int(km.group(1))
            letters = re.findall(r"[A-E]", km.group(2))
            current_num = num
            if num in seen_keys:
                errors.append(f"{filename}:Q{num} — duplicate answer key entry")
            seen_keys.add(num)
            if num not in questions:
                errors.append(
                    f"{filename}:Q{num} — answer key entry has no matching question block"
                )
            else:
                questions[num]["correct"] = letters
            i += 1
            continue
        rm = RATIONALE_RE.match(line)
        if rm and current_num is not None:
            letter, text, mark = rm.group(1), rm.group(2).strip(), rm.group(3)
            if current_num in questions:
                questions[current_num]["rationales"][letter] = {
                    "text": text,
                    "correct": mark == "✓",
                }
            i += 1
            continue
        i += 1
    return seen_keys


def parse_questions(md_text, domain_code, filename, errors):
    questions, order = parse_question_blocks(md_text, domain_code, filename, errors)
    parse_answer_keys(md_text, filename, questions, errors)

    for marker in OLD_VARIANT_MARKERS:
        if marker in md_text:
            errors.append(f"{filename} — leftover old-variant marker {marker!r} found")

    for num in order:
        q = questions[num]
        tag = f"{filename}:Q{num}"
        option_letters = [o["letter"] for o in q["options"]]

        if not q["correct"]:
            errors.append(f"{tag} — missing answer key entry")
        else:
            if len(q["correct"]) != q["select"]:
                errors.append(
                    f"{tag} — correct-letter count ({len(q['correct'])}) != "
                    f"select count ({q['select']})"
                )
            invalid = set(q["correct"]) - set(option_letters)
            if invalid:
                errors.append(
                    f"{tag} — answer key references non-existent option letter(s) "
                    f"{sorted(invalid)}"
                )

        for letter in option_letters:
            if letter not in q["rationales"]:
                errors.append(f"{tag} — option {letter} missing rationale")

        if q["correct"]:
            marked_correct = {l for l, r in q["rationales"].items() if r["correct"]}
            if marked_correct and marked_correct != set(q["correct"]):
                errors.append(
                    f"{tag} — rationale checkmarks {sorted(marked_correct)} don't "
                    f"match answer key {q['correct']}"
                )

    return questions, order


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def main():
    errors = []
    domains_payload = []
    total_cards = 0
    total_questions = 0

    for folder, (code, name, weight) in DOMAIN_META.items():
        cards_file = ROOT / folder / "flashcards.md"
        cards = (
            parse_cards(cards_file.read_text(encoding="utf-8"))
            if cards_file.exists()
            else []
        )

        questions_list = []
        q_file = ROOT / folder / "practice-questions.md"
        if q_file.exists():
            md = q_file.read_text(encoding="utf-8")
            questions, order = parse_questions(md, code, f"{folder}/{q_file.name}", errors)
            for num in order:
                q = questions[num]
                questions_list.append(
                    {
                        "id": f"{code}-Q{num}",
                        "num": num,
                        "domain": code,
                        "skill": q["skill"],
                        "select": q["select"],
                        "stem": q["stem"],
                        "options": q["options"],
                        "correct": q["correct"],
                        "rationales": q["rationales"],
                    }
                )

        domains_payload.append(
            {
                "code": code,
                "name": name,
                "weight": weight,
                "cards": cards,
                "questions": questions_list,
            }
        )
        total_cards += len(cards)
        total_questions += len(questions_list)

    for d in domains_payload:
        print(f"  {d['code']}: {len(d['cards'])} cards, {len(d['questions'])} questions")
    print(
        f"Total: {total_cards} cards, {total_questions} questions across "
        f"{len(domains_payload)} domains."
    )

    if errors:
        print(f"\n{len(errors)} validation error(s) — study-hub.html NOT written:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    if not TEMPLATE_FILE.exists():
        print(f"\nTemplate file {TEMPLATE_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    payload = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "passScaled": 720,
        "examSize": 53,
        "examMinutes": 120,
        "domains": domains_payload,
    }

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    if "__DATA_JSON__" not in template:
        print(f"\n{TEMPLATE_FILE.name} has no __DATA_JSON__ placeholder.", file=sys.stderr)
        sys.exit(1)

    html = template.replace("__DATA_JSON__", json.dumps(payload, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUT.name} ({len(html):,} bytes).")


if __name__ == "__main__":
    main()
