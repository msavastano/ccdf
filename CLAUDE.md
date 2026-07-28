# Project Instructions — Claude Certified Developer Foundations (CCDV-F) Study Repo

## Purpose
This project is a study guide and resource repository for the **Claude Certified Developer – Foundations** exam (code CCDV-F, v1.0, effective July 2026). The authoritative source is the official Exam Guide PDF in this folder. All study materials created here must trace back to the blueprint in that guide or to official Anthropic documentation.

## How to Help Me
- I'm preparing for this exam. Act as a study partner: explain concepts, quiz me, build study materials, and track my progress.
- Ground technical answers in official Anthropic docs (docs.claude.com). If unsure whether a feature or behavior has changed, search the docs before answering — this exam covers a fast-moving platform.
- Weight everything by the blueprint. Don't spend equal effort on all domains — Domain 2 alone is a third of the exam; Domains 3 and 4 combined are under 6%.
- When quizzing me, match the real item style: multiple-choice and multiple-response, scenario-based, with plausible distractors and a rationale for every option (like Section 8 of the guide).
- Never claim to have real exam questions. All practice items are original, written to blueprint objectives. Exam content is NDA-protected — if I paste something that looks like a live exam item, flag it and don't work from it.

## Exam Facts (quick reference)
- 53 items · 120 minutes · proctored (Pearson VUE, online or test center)
- Scaled score 100–1,000; **pass = 720**
- Fee $125 · credential valid 12 months · free non-proctored renewal if done on time
- Retake waits: 14 / 30 / 90 days; max 4 attempts per rolling 12 months

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

Highest-yield skills (by exam share): Claude Application Design (8.6%), Software Engineering Foundations (7.4%), Claude API Mechanics (6.8%), Technical Fundamentals (6.1%), Agent Construction with Claude (5.3%), LLM Fundamentals (5.2%).

## Repo Conventions
- One folder per domain: `domain-1-agents/` through `domain-8-tools-mcps/`
- Inside each: `notes.md` (concept summaries), `flashcards.md` (Q/A pairs), `practice-questions.md` (blueprint-style items with answer key + rationale)
- Top level: `study-plan.md` (schedule + progress tracker), `weak-areas.md` (topics I've missed in practice), `resources.md` (links to official docs per domain)
- Create these files/folders as needed; don't wait to be asked when producing material that belongs in them.
- Markdown for everything unless I ask for another format. Keep notes scannable — short sections, tables for comparisons (e.g., Opus vs. Sonnet vs. Haiku; built-in tools vs. custom tools vs. Skills vs. MCPs).
- `study-hub.html` (the single-file quiz/exam/flashcards/dashboard app) is generated — rebuild it with `python build-study-hub.py` after editing any domain's `flashcards.md` or `practice-questions.md`. Don't hand-edit `study-hub.html` itself.
- `notes-pack.html` (all eight domains' `notes.md` in one searchable, printable file) is generated the same way — rebuild it with `python build-notes-pack.py` after editing any `notes.md`. Don't hand-edit it either.
- Deploying is a separate, explicit step — building never publishes. `python deploy.py [hub|notes|all] [--build] [--prod] [--stage-only]` stages each page as `deploy/<project>/index.html` and hands that folder to the Vercel CLI, so the two pages are two independent Vercel projects. Don't hand-edit `deploy/*/index.html` — it's a staged copy, overwritten on every run. Never deploy without asking me first.

## Content Standards
- Practice questions: state how many responses to select, always include answer key and per-option rationale, tag with domain and skill (e.g., "D5 · Cost and Token Management").
- Notes: emphasize tradeoffs and decision criteria — the exam tests "which approach best fits," not trivia. Recurring tradeoff axes: workflow vs. agent, realtime vs. batch, model tier selection (quality/latency/cost), built-in vs. custom vs. Skill vs. MCP, client-side vs. server-side tools.
- Flag anything version-sensitive (model names, API features, pricing) with the date it was verified.

## Session Habits
- Read `MEMORY.md` (if present) and `weak-areas.md` at the start of a session before generating new material.
- When I get a practice question wrong, log the topic to `weak-areas.md` with the date.
- End quiz sessions with a score by domain, mirroring the real score report format.
