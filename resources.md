# Resources — CCDV-F

Official sources only (per project instructions). Links verified 2026-07-12 at the landing-page level; deep pages move — search docs.claude.com if one 404s.

## Program
- Exam Guide PDF (authoritative) — in this folder
- Anthropic Partner Academy — registration, renewal assessment
- Pearson VUE Anthropic page — scheduling, accommodations, support: pearsonvue.com/us/en/anthropic.html

## By domain

| Domain | Primary docs |
|--------|-------------|
| 1 — Agents and Workflows | docs.claude.com → Agent SDK; anthropic.com/engineering ("Building Effective Agents") |
| 2 — Applications and Integration | docs.claude.com → API reference (Messages, Batches, streaming, vision, prompt caching); client SDK docs (Python/TS) |
| 3 — Claude Code | docs.claude.com → Claude Code (CLAUDE.md hierarchy, settings.json, slash commands, headless mode, Skills, plugins). Permission modes + allow/deny rules: [Configure permissions](https://docs.claude.com/en/docs/claude-code/sdk/sdk-permissions), [Handling permissions](https://docs.claude.com/en/docs/agent-sdk/permissions), [settings.json reference](https://docs.claude.com/en/docs/claude-code/settings) — *mode names verified 2026-07-19* |
| 4 — Eval, Testing, Debugging | docs.claude.com → evals and testing guides; Console workbench |
| 5 — Model Selection | docs.claude.com → Models overview (tiers, pricing, extended/adaptive thinking); pricing page |
| 6 — Prompt/Context Engineering | docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview; context window docs |
| 7 — Security and Safety | docs.claude.com → security guidance; hooks docs (Claude Code); anthropic.com usage policies. **OS-level sandboxing** (filesystem + network isolation) — code.claude.com, configured via Claude Code settings. **ZDR eligibility per model/platform** — Anthropic Trust Center (trust.anthropic.com); check at scoping time, *verified 2026-07-19* |
| 8 — Tools and MCPs | docs.claude.com → Tool use; modelcontextprotocol.io (spec, server authoring, transports) |

## Cross-domain
- Anthropic engineering blog — agent patterns, context engineering, tool design posts
- Anthropic Academy / courses — hands-on API and Claude Code tutorials. Modules feeding the capstone: **Claude 101**, **Claude Code 101 In Action**, **AI Fluency Framework Foundations**, **Building with the Claude API**.
- Cross-domain review sheets, one per class module (read after the domain notes, in exam week):
  - [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md) — Module 2, routed across D1/D2/D5/D6/D8
  - [`capstone-claude-code-mcp-integration.md`](capstone-claude-code-mcp-integration.md) — Module 3, routed across D3/D7/D8 (+ D2)
  - [`capstone-production-engineering-evals-security.md`](capstone-production-engineering-evals-security.md) — Module 4, routed across D4/D5/D1/D6/D7
- [`project-studymate/`](project-studymate/README.md) — hands-on: an 8-level Claude API build (D2 spine, pulls in D1/D5/D6/D7/D8/D4), for learning by doing rather than reading

## Version-sensitive watch list
Re-verify before the exam: **ZDR eligibility by model and by platform** (varies; not guaranteed under an existing agreement), current model names and tiers, batch API pricing/window, prompt-caching mechanics, Claude Code feature names (Rules/Skills/Commands/Agents/Agent Memory), Claude Code permission mode names (`default`/`acceptEdits`/`plan`/`auto`/`dontAsk`/`bypassPermissions`) and settings-file paths, MCP transport options.
