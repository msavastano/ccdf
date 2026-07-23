# Study Plan — CCDV-F

Exam date: _not yet scheduled_ (set this, then work backward)

## Suggested 4-week plan (weighted by blueprint)

| Week | Focus | Why |
|------|-------|-----|
| 1 | **Domain 2 — Applications and Integration** (33.1%) | Biggest domain by far; API mechanics + application design alone are 15.4% of the exam |
| 2 | **Domain 5 — Model Selection** (16.8%) + **Domain 1 — Agents** (14.7%) | Next two largest; heavy on tradeoff reasoning |
| 3 | **Domain 6 — Prompt/Context** (11.0%) + **Domain 8 — Tools/MCPs** (10.6%) + **Domain 7 — Security** (8.1%) | Mid-weight domains; lots of overlap (injection defense ties D6/D7, tool design ties D8/D1) |
| 4 | **Domains 3 + 4** (5.7% combined) + full review + timed practice sets | Light domains need only a pass; spend the week on weak areas and mixed quizzes |

Rule of thumb: ~53 items means Domain 2 ≈ 17–18 questions; Domains 3+4 combined ≈ 3. Budget effort accordingly.

> **Week 4 integration pass — four review sheets.** All are read *after* the domain notes, not instead of them; none is a ninth domain.
>
> 1. [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md) — maps the "Production-Grade Prompting, Agents & Tool-Use" module's 8 takeaways across **D1/D2/D5/D6/D8**, with one unified failure→technique diagnostic table and cross-domain scenario questions. Pairs with weeks 1–3.
> 2. [`capstone-claude-code-mcp-integration.md`](capstone-claude-code-mcp-integration.md) — maps the "Claude Code, MCP & Integration" module's 7 takeaways across **D3/D7/D8** (plus the AI-code-review triage rule in D2 · Software Engineering Foundations), with a requirement→mechanism decision table. Pairs with the D3 pass in week 4 and the D8/D7 work in week 3. **Weight caution:** D3 is only 3.1% (~1–2 items) — most of this sheet's value is D8 (10.6%) and D7 (8.1%), so study the judgment, not the CLI trivia.
> 3. [`capstone-production-engineering-evals-security.md`](capstone-production-engineering-evals-security.md) — maps the "Production Engineering, Evals & Security" module's 5 takeaways across **D4/D5/D1/D6/D7**, with a symptom→layer decision table, 10 scenario items, and the module's recurring shape (*development hides what production reveals*). Pairs with the D5/D1 work in week 2 and the D7 work in week 3. **Weight caution:** the domain it sounds like — D4 — is 2.6%; the weight is in **D5 (16.8%), D1 (14.7%), D6 (11.0%), D7 (8.1%)**, whose decision rules depend on evals as evidence.
> 4. [`capstone-accelerators-ip-contribution.md`](capstone-accelerators-ip-contribution.md) — maps the "Accelerators & IP Contribution" module's 5 takeaways, which land almost entirely in **D2** (with routes to D8/D7/D4/D1), plus a situation→move decision table, 10 scenario items, and the module's recurring shape (*the asset has to survive the people who built it*). **No weight caution needed — read this one at full weight.** Unlike the other three sheets, its material sits inside the **33.1%** domain and its two highest-weight skills (Claude Application Design 8.6%, Systems Life Cycle). Pairs with week 1.
>
> Shared term definitions from all four modules live in [`glossary.md`](glossary.md).

> **Learn by building.** [`project-studymate/`](project-studymate/README.md) is an
> optional hands-on track that runs alongside weeks 1–3: an 8-level coding project
> (real Claude API calls, escalating from a single request to a tool-using, guarded,
> evaluated, MCP-wrapped capstone) with D2 as the spine and D1/D5/D6/D7/D8/D4 pulled
> in as the build matures. Not a substitute for the domain notes — a way to feel the
> tradeoffs (model tiers, workflow vs. agent, tool description scoping, injection
> defense) instead of only reading about them. Its own checkpoint questions live in
> `project-studymate/checkpoints.md`, separate from the domain practice sets below.

## Progress Tracker

| Domain | Weight | Notes | Flashcards | Practice Qs | Last quiz % |
|--------|--------|:-----:|:----------:|:-----------:|:-----------:|
| 1 — Agents and Workflows | 14.7% | ☑ | ☑ | ☑ | — |
| 2 — Applications and Integration | 33.1% | ☑ | ☑ | ☑ | — |
| 3 — Claude Code | 3.1% | ◐ | ☐ | ☐ | — |
| 4 — Eval, Testing, Debugging | 2.6% | ☑ | ☑ | ☑ | — |
| 5 — Model Selection | 16.8% | ◐ | ☑ | ☑ | — |
| 6 — Prompt/Context Engineering | 11.0% | ☑ | ☑ | ☑ | — |
| 7 — Security and Safety | 8.1% | ☑ | ☑ | ☑ | — |
| 8 — Tools and MCPs | 10.6% | ☑ | ☑ | ☑ | — |

◐ = partial. **D4:** complete — the four-layer debug case study, the "Evals & Judges" module (design document, grader selection, judge calibration, iteration loop), and the "Testing & Tracing" module (four test levels, trace-based localization; the retrieval-router half of that module lives in D6); 20 practice items. Note the eval material is blueprint-*adjacent* — D4 names only "Debugging and Error Handling," but evals are the evidence D5's tier-change rule and D6's iteration loop depend on, so study it for those domains' sake. **D7:** complete — all four sections (AI Application Security, Guardrails and Safe Deployment, Claude Hooks, Identity/Secrets/Key Management), flashcards for each, and 7 practice items. **D3 notes:** all three sections written plus the code-modernization applied case; flashcards and practice Qs not started. **D8:** notes and flashcards complete through Enterprise Integration; 13 practice items (Q7–Q13 cover MCP server build/config). D5 notes: Model Selection & Tradeoffs, Cost & Token Management, Extended thinking, and the "Cost & Orchestration" module (observability, cache economics, batching-as-cost-lever, reliability floor) are written; Technical Fundamentals and the rest of LLM Fundamentals remain. **D1:** notes complete through the orchestrator-worker pattern; 15 practice items (18 scored decisions). The "Cost & Orchestration" class module split across three domains — instrumentation and cost levers to D5, orchestrator-worker to D1, the streaming tool-call accumulation snippet to D2 · Streaming (added 2026-07-19).

> **Module 4 ("Production Engineering, Evals & Security") is fully absorbed** as of 2026-07-19. Its four sub-lessons went into the domain notes as they landed — Evals & Judges + Testing & Tracing + Failure Handling → D4, Cost & Orchestration → D5/D1/D2, injection/least-privilege/hook boundary → D7 — and the module recap is routed in [`capstone-production-engineering-evals-security.md`](capstone-production-engineering-evals-security.md). Nothing from it is unfiled. **Module 5** (reusable accelerators: templates, MCP servers, portable eval suites; then deployment platform choice across first-party API / Bedrock / Vertex AI, version pinning, data residency) will land mainly in **D8** and **D2** — expect the most version-sensitive material of the series there.
>
> **Module 5 · lesson 1 — "Packaging for Reuse" — filed 2026-07-19.** As predicted, it landed in **D2**: new [Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator) section (Systems Life Cycle + Configuration Management), 13 flashcards, and practice items **Q17–Q21**. The three asset types route out to D1 (agent template), D8 (MCP server package — pointer added at the end of the D8 notes), and D4 (portable eval suite — pointer added to D4's cross-domain list). Its most exam-relevant idea: **the eval suite is also the model-promotion gate**, run against a pinned baseline before a new version goes live — that's the enforcement half of D2's model-pinning rule. Remaining Module 5 lessons (contribution channels; deployment platform choice across first-party API / Bedrock / Vertex AI; residency) are still unfiled.
>
> **Module 5 · lesson 2 — "Contributing Back" — filed 2026-07-19.** Filed alongside lesson 1 in **D2**, since it's the direct sequel and rides the same two skills: new [Contributing Back](domain-2-applications/notes.md#contributing-back--from-private-reuse-to-shared-infrastructure) section, 14 flashcards, practice items **Q22–Q25**, and exam traps 15–17. Two ideas carry the most exam weight: **channel mismatch** (a full application sent to the Cookbook stalls — the Cookbook takes one focused, self-contained pattern; tools and servers go to their own repos) and **gate order** (rights and attribution clear *before* technical review, and an unclearable engagement constraint means escalate, not contribute). The maintainer's bar is **verifiability** — one thing done, runnable example, test, stated assumptions — not code quality. Remaining Module 5: deployment platform choice across first-party API / Bedrock / Vertex AI, version pinning, and residency — expect that one in **D5/D2** and expect it to be the most version-sensitive material of the series.

> **Module 5 · lesson 3 — "Deployment & Versioning" — filed 2026-07-19. Module 5 is now fully absorbed.** It landed in **D2**, not D5: new [Deployment and Versioning](domain-2-applications/notes.md#deployment-and-versioning--where-the-workload-runs-and-what-ships) section (Configuration Management + Systems Life Cycle), 15 flashcards, practice **Supplement B (Q31–Q36)**, and exam traps 18–22. Three ideas carry the exam weight: **the customer's existing cloud, identity, and compliance posture decides the platform** — not features or benchmarks; **an alias is not a version** (pin the model *and* the prompt *and* the asset, and keep the prior version for rollback); and **promotion is partial traffic vs. a pinned baseline**, which is where D4's eval suite becomes the deployment gate. Sharpest distinction to drill: **Claude Platform on AWS** (customer's AWS account, but Anthropic-operated inference *outside* the AWS boundary, Anthropic's model IDs/lifecycle) vs. **Claude in Amazon Bedrock** (Messages API at `/anthropic/v1/messages`, data in the customer's AWS boundary, partner retirement dates differ) vs. **legacy Bedrock** (`InvokeModel`/`Converse`, ARN-versioned IDs). As predicted, this is the **most version-sensitive material in the repo** — every model name, hosting form, and pinning convention in it is dated 2026-07-19 and flagged to re-verify at `platform.claude.com` at build time.

> **Module 5 · lesson 4 — "Comparing Platforms" — filed 2026-07-19.** (Module 5 had one more lesson than the prior entry assumed.) Filed in **D2** alongside lesson 3, as its direct sequel: new [Comparing platforms — latency, compliance, cost](domain-2-applications/notes.md#comparing-platforms--latency-compliance-cost-class-notes-2026-07-19) subsection inside Deployment and Versioning, 14 flashcards, practice **Supplement C (Q37–Q41)**, exam traps **23–26**, and a new glossary term, [Data residency](glossary.md#data-residency). The framing to hold: lesson 3 said *the customer's cloud decides the platform*; lesson 4 says **that placement still isn't an argument procurement and security will sign off on** — you have to measure it on three dimensions. **Latency** must be measured **from the customer's actual region against their actual payload** (a laptop number hides the round trip), and on Bedrock the **global-vs-regional endpoint** choice is both the primary residency control and a cost lever. **Compliance** usually ends the debate and is **pass-or-fail** — EU-only residency typically requires **Bedrock or Vertex**, not the 1P API, and **Anthropic-hosted Foundry models don't satisfy EU regional residency**. **Cost** moves on **egress, platform fees, and integration effort**, not the per-token rate. The named exception is worth drilling because it inverts the lesson: when the compliance constraint is **already pass-or-fail, skip the comparison** — it has already decided.

> **Module 5 recap — "Accelerators & IP Contribution" — filed 2026-07-19. Module 5 is closed.** The recap introduced **no new mechanics** — all five lessons were already in D2 — so it was filed as the fourth capstone routing sheet, [`capstone-accelerators-ip-contribution.md`](capstone-accelerators-ip-contribution.md), plus one new glossary term ([Contribution readiness](glossary.md#contribution-readiness), previously folded into *Contributing back*) and a "Model alias vs. pinned ID" index pointer. **This is the first capstone that needs no weight caution** — its content sits in D2 (33.1%) and its two biggest skills, not in a 2–3% domain. Four framings are worth carrying in verbatim: **the expensive asset is the knowledge, not the code** (which is *why* you package while the build is fresh); **"configure" vs. "copy and diverge"** as the one-word test of correct packaging; **the maintainer's bar is verifiability, not quality** (five items, rights cleared first); and **trust does not carry over from the component that sent the data** — the sharpest security distractor in the module. The recap also states the alias metaphor cleanly: an alias asks for *the current edition of a book*, a pin *cites a fixed edition* — with an alias a model change **arrives**, with a pin you **adopt** it. Its 10 scenario items are cross-domain and untried; work them in exam week alongside D2's Q17–Q25 and Q31–Q45.

## Milestones

- [ ] Read the full Exam Guide PDF (done if you're reading this)
- [ ] Notes drafted for all 8 domains
- [ ] First full 53-question timed mock (120 min)
- [ ] Mock score ≥ 80% in every domain ≥ 10% weight
- [ ] Schedule exam (Pearson VUE via Anthropic Partner Academy)
- [ ] Work all four capstone integration sheets in exam week — `capstone-production-grade-prompting.md` (cross-domain diagnosis + scenario Qs), `capstone-claude-code-mcp-integration.md` (requirement→mechanism table + scenario Qs), `capstone-production-engineering-evals-security.md` (symptom→layer table + scenario Qs), and `capstone-accelerators-ip-contribution.md` (situation→move table + 10 scenario Qs — highest weight of the four)
- [ ] Final review of weak-areas.md in exam week
- [ ] (Optional, hands-on) Work through `project-studymate/`'s 8 levels and its `checkpoints.md`
