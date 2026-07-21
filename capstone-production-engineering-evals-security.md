# Capstone — Production Engineering, Evals & Security

**What this is.** A cross-domain review sheet for **Module 4** of the class series, following [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md) (Module 2 — the developer primitive library) and [`capstone-claude-code-mcp-integration.md`](capstone-claude-code-mcp-integration.md) (Module 3 — configuration and governance). Where those covered *how to build* and *how to configure*, this one covers **how you know it works and how it survives contact with real traffic.** It introduces **no new mechanics** — every technical fact was written into a domain `notes.md` as the module's sub-lessons landed (Evals & Judges, Testing & Tracing, Failure Handling, Cost & Orchestration, each dated 2026-07-19). This sheet is the routing layer over them.

**How to use it.** Read after the domain notes for **D4** (Eval, Testing, Debugging), **D5** (Observability & Cost), **D1** (orchestrator-worker), and **D7** (AI Application Security + Guardrails) — not before. Integration pass, best run in exam week. _Source: class module "Production Engineering, Evals & Security" (Module 4 Recap screen, recorded 2026-07-19); cross-checked against the domain notes the same day._

> ⚖️ **Blueprint reality check.** The domain this module *sounds* like — **D4, 2.6%, ~1–2 items** — is the smallest on the exam. Do not budget study time by the volume of eval material here. The weight actually sits in the domains this module's content routes into: **D5 (16.8%)**, **D1 (14.7%)**, **D6 (11.0%)**, **D7 (8.1%)**. Evals, tests, and traces are the *instrument* those domains' decision rules depend on — D5 says change model tiers only when an eval set justifies it; D6's prompt-iteration loop is scored by one. Study them as evidence-production machinery for the big domains, not as a 2.6% topic.

---

## The one idea

Module 2's failure shape was *dev illusion → production stressor*. Module 3's was *convenience setting → governance boundary*. This module's:

> 🔑 **Development hides what production reveals, and every layer here exists to expose one hidden thing before traffic does.** An eval exposes whether "done" was ever defined. A test level exposes the seam two passing components fail at. A trace exposes *which* step produced the bad answer. Instrumentation exposes what the invoice only totals. A hook exposes — and blocks — the action a hidden instruction talked the agent into. The exam tests whether you reach for the layer that matches the specific thing being hidden.

The corollary the recap states outright: **each layer must be decided in advance.** An unhandled exception *is* a fallback — the worst one. An uninstrumented call *has* a cost — you just can't see it. A missing boundary between instructions and fetched data doesn't mean there's no boundary; it means the model draws none.

---

## Master crosswalk — the 5 takeaways, routed to where the mechanics live

| # | Takeaway | The development-time illusion | What production reveals | Lives in |
|---|----------|-------------------------------|-------------------------|----------|
| 1 | **Set the standard before you build it.** | "Done" is a feeling you get reading a few outputs. | An eval turns it into **a score on a fixed set of cases**. Grading must match output shape: **exact match** (one correct form), **code check** (structured output), **LLM judge** (open-ended quality) — and the judge is **calibrated against human-labelled cases before you trust it**. Write the eval **first**: naming expected behavior forces you to define success while the design can still change. | [D4 · Evals and Judges](domain-4-eval-testing/notes.md#evals-and-judges--defining-done-before-you-ship); the decisions it feeds — [D5 · tier-change rule](domain-5-model-selection/notes.md), [D6 · prompt iteration loop](domain-6-prompt-context/notes.md) |
| 2 | **Match the test to the failure, and trace so you know where it happened.** | Components pass their own tests, so the system works. | **Unit / functional / integration / end-to-end each catch a different break**, and most silent failures hide **at the integration seam** where two passing components hand off. A **trace** turns a day of investigation into a short fix by naming the step that produced the bad result. Same instinct governs retrieval: **fetch once** for single-fact lookups, **search across iterations** for genuinely multi-step questions — and the router's branch is itself a step the trace must record. | [D4 · Testing and tracing](domain-4-eval-testing/notes.md#testing-and-tracing--the-layer-underneath-the-eval); retrieval routing in [D6 · Context Engineering → RAG](domain-6-prompt-context/notes.md) |
| 3 | **Sort every failure, then handle them individually.** | The happy path works; errors are edge cases. | First question for any failure: **could waiting and retrying resolve it?** Retriable → **exponential backoff with a cap and a retry budget**, never an immediate loop (which deepens the problem it's reacting to). **Tool failures return to the model with the error flag set** — never hidden behind an empty result the model reads as data. Every failure retry can't fix needs **a named fallback**; otherwise **an unhandled exception becomes the default behavior**, and one bad response takes down the flow. | [D4 · Production failure handling](domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal); error classes and `is_error` mechanics also in [D2 · API mechanics](domain-2-applications/notes.md), [D8 · tool results](domain-8-tools-mcps/notes.md) |
| 4 | **Measure cost and latency per call, and fan out only when a task truly splits.** | The monthly invoice is the cost signal. | **You cannot budget what you don't measure** — instrument **token cost, latency, error rate per call**, then tune a **chosen lever** instead of guessing from a total. **Orchestrator-worker multiplies token cost by the number of subagents — ~15× in Anthropic's reported case** — and earns it **only on tasks that split into independent parallel parts**, never on tightly coupled work one agent handles for a fraction. | [D5 · Observability + the levers + batching](domain-5-model-selection/notes.md#observability--instrument-before-you-optimize); [D1 · Orchestrator-worker](domain-1-agents/notes.md#orchestrator-worker--parallel-exploration-at-a-15-token-multiplier) |
| 5 | **Treat fetched content as data and enforce the boundary with a hook.** | "We trust our users, so injection isn't our threat model." | **The model reads everything in context as one stream of tokens with no built-in line between trusted instruction and untrusted data** — so an instruction hidden in fetched content can steer the agent. **Trusting your users doesn't help: the injection arrives through the content the agent reads.** Four moves: examine untrusted input **as data**, scope agent identity to **least privilege**, keep **secrets out of committed config**, and enforce the action boundary with a **hook that blocks and logs before the tool runs**. That hook is what a regulated review can **control and inspect**. | [D7 · AI Application Security](domain-7-security/notes.md#ai-application-security-32) + [Guardrails and Safe Deployment](domain-7-security/notes.md#guardrails-and-safe-deployment-23) + [Identity, Secrets, Key Management](domain-7-security/notes.md#identity-secrets-and-key-management-16); hook lifecycle in [D3](domain-3-claude-code/notes.md) |

---

## Unified decision table — "which layer answers this?"

The module's core skill is mapping a stated symptom or requirement to **the one layer that addresses it**. Scattered by topic across the domain notes; consolidated here, which is how a scenario stem actually reaches you.

| The requirement or symptom in the stem | The layer / mechanism | Domain |
|---|---|---|
| "How do we know the new prompt is actually better?" | **Eval** — score on a fixed case set, not spot-checking | D4 → D6 |
| "There's exactly one right answer string" | **Exact-match grader** | D4 |
| "Output is JSON and must have these fields/ranges" | **Code check** (deterministic assertion) | D4 |
| "Quality is a judgment call — tone, helpfulness, faithfulness" | **LLM judge**, **calibrated against human labels first** | D4 |
| "The judge's scores don't match what reviewers say" | **Recalibrate the judge** — it isn't trustworthy until it agrees on labelled cases | D4 |
| "We're not sure the eval covers enough" | **Coverage beats perfection** — a partial eval today beats a perfect one after launch | D4 |
| "One function returns wrong values" | **Unit test** | D4 |
| "Feature does the wrong thing end to end, though every piece passes" | **Integration test** — the seam is where silent failures hide | D4 |
| "It failed — but which step?" | **Trace** | D4 |
| "The answer was bad and we can't tell if retrieval or generation caused it" | **Trace the router branch too** — a wrong path looks like a bad answer | D4/D6 |
| "Single-fact lookup, high volume" | **Fetch once** (retrieval index) | D6 |
| "Genuinely multi-step question" | **Search across iterations** (agentic search) | D6 |
| "Traffic is all one shape" | **Skip the router**, hardcode the fitting path | D6 |
| "429 / 500 / 529 / timeout" | **Retriable** → exponential backoff, **cap + retry budget** | D4/D2 |
| "400, unpaired `tool_result`, schema violation" | **Terminal** → fix how you build the request; retry reproduces it | D4/D2 |
| "The tool call raised — what goes back to the model?" | **`tool_result` with the error flag set**, never an empty result | D4/D8 |
| "Retry can't fix this one" | **A named fallback** — cached answer, degraded mode, human handoff | D4 |
| "We didn't decide what happens on failure" | You did: **the unhandled exception is your default** | D4 |
| "Which model tier / prompt change actually saved money?" | **Per-call instrumentation** (token cost, latency, error rate) → tune one lever | D5 |
| "Cost is high and the work is repetitive with a stable prefix" | **Prompt caching** | D5 |
| "Work is non-realtime and volume is large" | **Batching** as the cost lever | D5 |
| "Cheaper model would blow the error budget" | **Reliability has a floor** — tune cost *within* it | D5 |
| "Task splits into independent parallel parts" | **Orchestrator-worker**, accepting **~15× tokens** | D1 |
| "Subtasks depend on each other's results" | **Single agent** — coupling defeats the fan-out | D1 |
| "An instruction was hidden in a fetched web page" | **Prompt injection** — treat fetched content as **data**, not instruction | D7 |
| "We only serve internal, trusted users" | **Irrelevant** — the injection rides in on the content, not the user | D7 |
| "This action must be blocked before it runs, and logged" | **`PreToolUse` hook** — deterministic, inspectable | D7/D3 |
| "Auditors need a record of every tool call" | **`PostToolUse` hook** → audit store | D7/D3 |
| "The agent has broader access than the task needs" | **Least privilege on the agent's identity**, scoped per path | D7 |
| "The API key is in the committed config file" | **Secret to environment / secret store**; config holds the address only | D7 |

---

## What's genuinely new here vs. the domain notes

Most of this is review. Five framings are the value-add worth carrying into the exam:

1. **"Write the eval first" is a design argument, not a testing one.** The stated reason isn't rigor — it's that **identifying expected behavior forces you to define success while the design can still change.** An eval written after the build documents whatever you happened to ship. If a stem asks *when* to write the eval, the answer is before, and the rationale is design leverage.
2. **The grader is chosen by output shape, and the judge has a prerequisite.** Three-way mapping (exact match / code check / judge) is easy to memorize and easy to test. The distractor-resistant part: **a judge you haven't calibrated against human-labelled cases is not yet evidence.** "Use an LLM judge" is only correct with the calibration step attached.
3. **The seam is the default suspect.** "Most silent failures hide at the integration seam where two passing components hand off" is the single most reusable line in the module — it explains why unit-test-green systems fail, and why the fix for an agent bug is rarely inside one component.
4. **An unhandled exception is a fallback decision you made by not making it.** Reframing failure handling as *sorting* — retriable, terminal, and terminal-with-a-named-fallback — beats memorizing status codes. The one question that starts it: **could waiting and retrying resolve this?**
5. **Trusting your users doesn't defend against injection.** The cleanest disqualifier on the exam. Any answer that reasons about *who the user is* has misread the threat: the payload arrives in **content the agent reads**. The defense is the data/instruction boundary plus a hook that enforces the action boundary deterministically — which is also the only version of this a regulated review can inspect.

---

## Cross-domain practice questions

Blueprint-style items written to these objectives. Each states how many to select. Answer key and per-option rationale follow.

**1. (D4 · Debugging and Error Handling — select ONE)**
A team is adding an eval to a summarization feature that has been in production for two months. A reviewer argues the eval should have been written before the feature. What is the strongest stated reason?

A. Evals written later cost more to run.
B. Defining expected behavior early forces a definition of success while the design can still change.
C. An eval written after launch cannot use an LLM judge.
D. Post-launch evals require human labels; pre-launch evals do not.

**2. (D4 · Debugging and Error Handling — select ONE)**
A feature returns JSON with `status`, `amount`, and `currency`. Requirements say `amount` must be positive and `currency` must be a 3-letter ISO code. Which grading method fits?

A. LLM judge, because the output is machine-generated.
B. Exact match against a golden JSON string.
C. A code check asserting the field constraints.
D. Human review, because financial data is sensitive.

**3. (D4 — select TWO)**
Every unit test passes and the feature still returns wrong results in staging. Which two moves are most likely to locate the problem?

A. Add an integration test covering the handoff between the retrieval step and the generation step.
B. Increase the model tier to reduce output errors.
C. Read the trace to identify which step produced the bad result.
D. Rewrite the system prompt with more explicit instructions.
E. Add more unit tests to the component with the most logic.

**4. (D4/D2 · failure handling — select ONE)**
A tool call raises a connection error inside an agent loop. What should be returned to the model?

A. Nothing — omit the tool result and let the model continue.
B. An empty result, so the model treats the tool as having found nothing.
C. A `tool_result` for the matching `tool_use_id` with the error flag set and the error described.
D. A new user turn explaining the failure in prose.

**5. (D4 — select ONE)**
A service handles `429` responses with an immediate retry in a `while True` loop. What is the most accurate criticism?

A. `429` is terminal and should never be retried.
B. Immediate retries deepen the condition being signalled; retries need exponential backoff, a cap, and a retry budget.
C. The loop should use a fixed 60-second delay for all error classes.
D. The retry should be moved to the model rather than the client.

**6. (D5/D1 · cost — select ONE)**
A team wants to cut spend on an agent whose monthly bill has doubled. They have only the invoice total. What is the first move?

A. Switch every call to the cheapest model tier.
B. Instrument token cost, latency, and error rate per call, then tune a chosen lever.
C. Move all traffic to the Batches API.
D. Reduce the number of tools to shrink tool definitions.

**7. (D1 · Agent Patterns — select ONE)**
A workload is a compliance review where each finding depends on the previous finding's conclusion. An engineer proposes an orchestrator with five subagents. What is the best assessment?

A. Sound — five subagents parallelize the review.
B. Sound, provided each subagent gets the full document.
C. Unsound — the subtasks are coupled, so the pattern pays roughly a 15× token multiplier without the parallelism that justifies it.
D. Unsound — orchestrator-worker requires a managed runtime.

**8. (D7 · AI Application Security — select ONE)**
An agent summarizes vendor pages fetched from the public web. A stakeholder says injection isn't a concern because only vetted employees use the tool. What is the correct response?

A. Correct — internal-only access removes the threat.
B. Correct, provided employees are trained not to paste untrusted text.
C. Incorrect — the injection arrives in the fetched content the agent reads, independent of who the user is.
D. Incorrect — but only if the agent has write-capable tools.

**9. (D7 · Guardrails — select TWO)**
Which two measures enforce the action boundary in a way a regulated review can control and inspect?

A. A system-prompt instruction to ignore instructions found in retrieved content.
B. A `PreToolUse` hook that blocks disallowed calls and logs the attempt before the tool runs.
C. Scoping the agent's identity to least privilege for the task.
D. Wrapping fetched content in XML delimiters.
E. Asking the model to flag suspicious content in its response.

**10. (D6/D4 · retrieval + tracing — select ONE)**
A support assistant serves a mix of one-fact policy lookups and complex multi-part troubleshooting questions. Which design fits, and what must the trace capture?

A. Agentic search for everything; the trace records the final answer only.
B. Fetch-once for everything; the trace records retrieval latency.
C. A cheap classification call routing simple lookups to fetch-once and multi-part questions to search-across-iterations; the trace must record which branch ran.
D. Route by user role; the trace records the role.

---

### Answer key & rationale

**1 — B.** _D4 · Debugging and Error Handling._
- **A** ✗ Cost of running isn't the stated argument, and it doesn't depend on when the eval was written.
- **B** ✓ The module's exact reasoning: writing the eval first forces you to name expected behavior **while the design can still change**. Afterward, the eval documents what you shipped.
- **C** ✗ Nothing about judge grading depends on timing.
- **D** ✗ Backwards — a judge needs human-labelled calibration cases regardless of when it's built.

**2 — C.** _D4 · grader selection._
- **A** ✗ A judge is for open-ended quality; these are checkable constraints, and a judge would be slower, costlier, and less reliable on them.
- **B** ✗ Exact match fits **one correct form**; here many valid outputs satisfy the constraints.
- **C** ✓ Structured output with assertable rules → **code check**.
- **D** ✗ Sensitivity may warrant review elsewhere; it doesn't make a deterministic constraint un-checkable.

**3 — A and C.** _D4 · test levels + tracing._
- **A** ✓ Components pass individually and fail together → the **integration seam** is the default suspect.
- **B** ✗ Tier change without evidence; the symptom hasn't been localized, and D5's rule requires an eval to justify the move.
- **C** ✓ The trace names **which step** produced the bad result — a day of investigation becomes a short fix.
- **D** ✗ A prompt rewrite is a fix applied before localization — the classic distractor.
- **E** ✗ More unit tests re-test the layer already passing.

**4 — C.** _D4/D8 · tool errors._
- **A** ✗ Omitting the result breaks `tool_use`↔`tool_result` pairing and produces a structural error.
- **B** ✗ The specific trap the module names: an empty result reads as **data** ("nothing found"), and the model reasons from a false premise.
- **C** ✓ Return the result **with the error flag set** so the model knows the tool failed and can adapt or escalate.
- **D** ✗ Prose in a new turn isn't the tool-result channel; pairing still breaks.

**5 — B.** _D4 · retriable handling._
- **A** ✗ `429` is retriable — that's why backoff exists.
- **B** ✓ Immediate looping adds load to the exact condition being signalled. Retriable failures need **exponential backoff, a cap, and a retry budget**.
- **C** ✗ A fixed delay for all classes ignores both `retry-after` and the retriable/terminal split.
- **D** ✗ Retry is client-side orchestration; the model doesn't own it.

**6 — B.** _D5 · observability._
- **A** ✗ A guess from the invoice, and it risks the reliability floor without eval evidence.
- **B** ✓ **You can't budget what you don't measure** — instrument per call, then move a chosen lever.
- **C** ✗ Batching is a real lever but only for non-realtime work; picking it first is still guessing.
- **D** ✗ May help context cost marginally; not the diagnosis step.

**7 — C.** _D1 · orchestrator-worker._
- **A** ✗ Sequential dependency means the subagents can't actually run in parallel.
- **B** ✗ Giving each the full document raises cost further without removing the coupling.
- **C** ✓ The pattern earns **~15×** only on tasks that split into **independent parallel parts**. Coupled work belongs to a single agent.
- **D** ✗ No runtime requirement — the constraint is task shape.

**8 — C.** _D7 · prompt injection._
- **A** ✗ The module states this directly: trusting your users doesn't help.
- **B** ✗ Training addresses pasted text; the payload here arrives via **fetched pages**.
- **C** ✓ The model reads context as **one token stream** with no built-in instruction/data line. The threat rides the content, not the user.
- **D** ✗ Write tools raise severity; they don't create the exposure.

**9 — B and C.** _D7 · guardrails._
- **A** ✗ A prompt instruction is probabilistic guidance, not enforcement.
- **B** ✓ A hook runs **deterministically before the tool**, blocks, and logs — controllable and inspectable in review.
- **C** ✓ Least privilege bounds what a successful injection can *do*; it's a design principle, not a setting.
- **D** ✗ Delimiters are a **soft** boundary — they help, they don't enforce.
- **E** ✗ Asking the possibly-compromised reasoning to police itself is not a boundary.

**10 — C.** _D6/D4 · retrieval routing + tracing._
- **A** ✗ Pays iteration cost on lookups one fetch answers; an answer-only trace can't localize a bad branch.
- **B** ✗ Fetch-once under-serves genuinely multi-step questions.
- **C** ✓ Mixed traffic is exactly when the router earns its one cheap classification call — and **the branch taken is a step the trace must record**, because a wrong path choice looks identical to a bad answer.
- **D** ✗ Role doesn't predict query shape.

---

## Capstone flashcards (meta-lessons)

**Q:** Why write the eval before you build?
**A:** Naming expected behavior forces you to **define success while the design can still change**. Written later, it just documents what shipped.

**Q:** Three grading methods and the output shape each fits?
**A:** **Exact match** — one correct form. **Code check** — structured output with assertable rules. **LLM judge** — open-ended quality.

**Q:** What must happen before you trust an LLM judge?
**A:** **Calibrate it against human-labelled cases.** An uncalibrated judge isn't evidence.

**Q:** Where do most silent failures hide?
**A:** **At the integration seam** — where two individually passing components hand off. It's why unit-green systems still fail.

**Q:** What does a trace buy you?
**A:** It names **which step** produced the bad result — a day of investigation becomes a short fix.

**Q:** The first question for any production failure?
**A:** **Could waiting and retrying resolve this?** That sorts retriable from terminal and dictates everything after.

**Q:** How do retriable failures get handled?
**A:** **Exponential backoff with a cap and a retry budget** — never an immediate loop, which deepens the condition being signalled.

**Q:** What comes back to the model when a tool fails?
**A:** The `tool_result` with the **error flag set** — never an empty result the model mistakes for data.

**Q:** What happens if you don't name a fallback for a non-retriable failure?
**A:** **The unhandled exception becomes your default behavior** — one bad response takes down the flow.

**Q:** Why instrument per call rather than read the invoice?
**A:** **You can't budget what you don't measure.** Per-call token cost, latency, and error rate let you tune a **chosen lever** instead of guessing from a total.

**Q:** When does orchestrator-worker earn ~15× tokens?
**A:** Only when the task **splits into independent parallel parts.** Tightly coupled work belongs to one agent at a fraction of the cost.

**Q:** Why doesn't "we trust our users" defend against prompt injection?
**A:** The injection **arrives through the content the agent reads.** The model sees instructions and data as one undifferentiated token stream.

**Q:** The four security moves in this module?
**A:** Treat untrusted input **as data**; scope identity to **least privilege**; keep **secrets out of committed config**; enforce the action boundary with a **hook that blocks and logs before the tool runs**.

**Q:** Why a hook rather than a prompt instruction for the action boundary?
**A:** The hook is **deterministic and inspectable** — the only version a regulated review can control and audit. A prompt instruction is probabilistic; delimiters are a soft boundary.

**Q:** Fetch-once or search-across-iterations?
**A:** **Fetch once** for single-fact lookups; **search across iterations** for genuinely multi-step questions. Route only when traffic is mixed — and **record the branch in the trace**.

---

## What comes next

Per the class, **Module 5** turns production-ready builds into **reusable accelerators and contributed IP**: packaging a working build as a **parameterized template, MCP server, or portable eval suite**, contributing it back through a channel a maintainer accepts, then **choosing, version-pinning, and defending where it runs** across the **first-party API, Amazon Bedrock, and Google Vertex AI** — so a model change or a residency review doesn't break production.

Repo-wise that lands mostly in **[D8 · Tools and MCPs](domain-8-tools-mcps/notes.md)** (10.6% — server authoring and distribution), **[D2 · Applications and Integration](domain-2-applications/notes.md)** (33.1% — deployment platform choice, model version pinning), and the **data-residency** thread already open in [D7](domain-7-security/notes.md) and [D1](domain-1-agents/notes.md). Module 4 deliberately set the deployment-platform specifics aside; expect them there. Flag every model name and platform capability that module states with a verification date — that's the most version-sensitive material in the series.

---

## Sources

- Class module: **"Production Engineering, Evals & Security"** — Module 4 Recap screen (5 key takeaways + "What comes next"), recorded 2026-07-19.
- Anthropic public references the class cites: **platform.claude.com/docs** (eval tooling and grading methods, test levels, API error/status codes, retry and backoff, tool-result error flag, observability and prompt caching, IAM and prompt-injection defenses); **code.claude.com** (hook lifecycle events incl. `PreToolUse`, guardrail patterns); **anthropic.com** engineering and multi-agent research writing (orchestrator-worker and its ~15× token cost, agentic search vs. RAG, prompt-injection defenses); Anthropic Academy — **Building with the Claude API** (eval pipeline, code and model graders, RAG and retrieval mechanics, workflow patterns, prompt caching) and **Claude Code 101 In Action** (hooks and configuration, carried from Module 3).
- Repo domain notes where each takeaway's mechanics are written and verified: `domain-4-eval-testing/notes.md`, `domain-5-model-selection/notes.md`, `domain-1-agents/notes.md`, `domain-6-prompt-context/notes.md`, `domain-7-security/notes.md`, `domain-2-applications/notes.md`, `domain-8-tools-mcps/notes.md`.
- Term definitions from this module are merged into the repo-wide [`glossary.md`](glossary.md).

_Version-sensitive: the ~15× orchestrator-worker multiplier is **Anthropic's reported figure for one specific case**, not a constant — never quote it as a universal rate. Retry/status-code behavior, SDK built-in retry defaults, hook event names, and prompt-caching mechanics were current per the class recorded **2026-07-19**. Re-verify against platform.claude.com and code.claude.com before relying on exact strings._
