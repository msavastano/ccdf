# CCDV-F Study Guide

Study materials for the **Claude Certified Developer – Foundations** exam (CCDV-F, v1.0), organized by the official blueprint's eight domains, plus a generated study app.

## Quick start: generate the Study Hub

```bash
python build-study-hub.py
```

That's it — this reads every domain's `flashcards.md` and `practice-questions.md` and produces **`study-hub.html`**, a single self-contained file with no other dependencies. Open it directly in any browser (double-click it, or drag it into a browser window). No server, no install, no internet connection required.

Requires only Python 3 (no packages to install).

### What the Study Hub does

- **Mock Exam** — a full 53-question simulation sampled to match the real blueprint weights, with a 120-minute timer, flagging, and a score report (estimated scaled score vs. the 720 pass line).
- **Quiz** — untimed practice by domain, with immediate rationale for every answer option.
- **Flashcards** — spaced-repetition review (Leitner system) over every domain's flashcard deck.
- **Dashboard** — tracks your weak areas over time, weighted against how much each domain counts on the real exam, with a one-click export to `weak-areas.md`.

All progress is saved locally in your browser (`localStorage`) — nothing leaves your machine.

### Regenerating after edits

If you edit any `flashcards.md` or `practice-questions.md`, rerun the build command above to refresh `study-hub.html`. Don't hand-edit `study-hub.html` itself — it's generated output.

The build validates the practice-question markdown as it parses and will fail loudly, naming the exact file and question number, if a file doesn't match the expected format (documented at the top of [build-study-hub.py](build-study-hub.py)).

## Repo layout

```
domain-1-agents/              ... domain-8-tools-mcps/
    notes.md                  concept summaries
    flashcards.md             Q/A pairs (source for the Study Hub's Flashcards mode)
    practice-questions.md     scenario questions + answer key + rationale (source for Quiz/Exam)

study-plan.md                 schedule + progress tracker
weak-areas.md                 topics missed in practice, logged with date
glossary.md                   cross-referenced term index
resources.md                  links to official Anthropic docs, by domain
capstone-*.md                 cross-domain review sheets (exam-week reading)

build-study-hub.py            generates study-hub.html — run this after editing content
study-hub-template.html       the app shell/logic the build script fills in
study-hub.html                generated output — open this to study
```

## Exam facts

- 53 items · 120 minutes · proctored (Pearson VUE, online or test center)
- Scaled score 100–1,000 · **pass = 720**
- Fee $125 · credential valid 12 months
- Retake waits: 14 / 30 / 90 days · max 4 attempts per rolling 12 months

## Blueprint (domain weights)

| # | Domain | Weight |
|---|--------|--------|
| 1 | Agents and Workflows | 14.7% |
| 2 | Applications and Integration | **33.1%** |
| 3 | Claude Code | 3.1% |
| 4 | Eval, Testing, and Debugging | 2.6% |
| 5 | Model Selection and Optimization | 16.8% |
| 6 | Prompt and Context Engineering | 11.0% |
| 7 | Security and Safety | 8.1% |
| 8 | Tools and MCPs | 10.6% |

All content traces back to the official Exam Guide PDF and Anthropic's docs (docs.claude.com). None of it is drawn from real exam questions — exam content is NDA-protected.
