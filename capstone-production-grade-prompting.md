# Capstone — Production-Grade Prompting, Agents & Tool-Use

**What this is.** A cross-domain review sheet for the class module of the same name — the capstone that ties together the "Developer primitive library" (prompting craft, tool schemas, context engineering, agent construction, memory scoping, multimodal ingestion). It introduces **no new mechanics**; every technical fact below is already written up and verified in a domain `notes.md`, and this sheet points to where. Its job is the connective tissue the siloed domain notes can't give: the single failure-shape all eight takeaways share, one unified diagnostic table, and cross-domain scenario questions in the exam's real style.

**How to use it.** Read this after the domain notes for D1, D2, D5, D6, D8 — not before. It's an integration/review pass, best run in exam week. Version-sensitive facts (model tiers, beta headers, formulas) carry their verification dates in the domain notes; this sheet references rather than re-verifies. _Source: class module "Production-Grade Prompting, Agents & Tool-use"; cross-checked against the domain notes, 2026-07-18._

---

## The one idea

Every takeaway in this module has the **same shape**: a task that passes in development fails in production, because production changes one variable the test set held small — inputs get bigger, sessions get shorter and more numerous, connections drop, tool outputs balloon. The fix is never "reword and retry." It's a **design-time decision** made before the failure, chosen by diagnosing the failure *type*.

> 🔑 **The escalation ladder is the spine of the whole module:** **single API call → workflow → agent.** Start with the simplest pattern that solves the problem; move up only when the simpler one can't handle the variability. Every takeaway below is a decision you make *once* on that ladder, cheaply, instead of a patch you make *later*, expensively.

---

## Master crosswalk — the 8 takeaways, routed to where the mechanics live

| # | Production lesson | The dev illusion that hides it | The design-time fix | Lives in |
|---|-------------------|-------------------------------|---------------------|----------|
| 1 | **Prompt failures are structural, not phrasing.** The failure *type* names the missing technique. | It worked once in interactive use, so you reword and retry — and the prompt grows *longer*, not more precise. | Diagnose the type, add the **one** missing piece (system prompt / XML tags / few-shot / output constraint). When prompt-level control still breaks on untested inputs, move control into the API: **structured outputs** (JSON schema on the response) and **strict tool use** (validates tool arguments) — at the cost of first-call compile latency + added input tokens. | [D6 · Prompt Engineering + Output Handling](domain-6-prompt-context/notes.md); [D2 · structured-outputs-examples.md](domain-2-applications/structured-outputs-examples.md) |
| 2 | **Match reasoning depth to the task.** | Turning thinking on everywhere looks "safer," and dev tasks are easy enough that high effort never bites on latency/cost. | Enable reasoning only where a reasoning pass **changes the answer**; calibrate the effort setting per problem, not per call. Pass thinking blocks back **unchanged** or the next request fails. (Which *model* to run is a separate decision — MSO, D5.) | [D5 · LLM Fundamentals → Extended thinking](domain-5-model-selection/notes.md); [D2 · Thinking](domain-2-applications/notes.md) |
| 3 | **A stream ending is not a message completing.** | On clean dev connections the stream always finishes, so partial-event handling never gets exercised. | Act on a block only after **`content_block_stop`**; commit a turn to history only after **`message_stop`**; on an interrupted stream **discard the partial turn and retry**. The tell: a tool-use error on a retry that traces to a half-built block, not to the schema. | [D2 · Streaming](domain-2-applications/notes.md) |
| 4 | **Wrong-tool selection traces to the schema — usually the description.** | Two tools with different input schemas look obviously distinct to *you*; Claude routes on the **description**, and both may read "use this to find information." | Write an **exclusion condition** ("do **not** use this when…") into every description at design time. Merge near-duplicates behind a `type` param. With **MCP**, connect servers deliberately — each adds its tool definitions to context **whether or not the tools are used**. | [D8 · Tool Implementation + Agentic Customization](domain-8-tools-mcps/notes.md) |
| 5 | **Context is a fixed budget; tool outputs spend it fastest.** | 50 turns hold together in test; production tool outputs run **3–5× longer** than fixtures, so the same session hits the ceiling at turn 8. | Buy back headroom with **pruning / compaction / subagent handoff** — the right one depends on whether you still need the earlier state. When tool selection degrades after a fixed number of turns, look at the **window first**, not the schema. | [D6 · Context Engineering](domain-6-prompt-context/notes.md); [D1 · Agent memory](domain-1-agents/notes.md) |
| 6 | **Workflow-or-agent sets the cost of everything after; HITL belongs in the design.** | Either wrong choice runs fine on the happy path you tested. | **Workflow** when you can write the exact steps in code; **agent** when you can name the goal and tools but not the path. If a tool can take an **irreversible** action, the human checkpoint goes in **before the loop is wired** — not after the first bad write reaches a customer. | [D1 · Agent Architecture + Patterns](domain-1-agents/notes.md) |
| 7 | **Memory scope follows the shape of the session, not what's easiest to build.** | In-context memory is the simplest to write, and dev's long single session makes it look sufficient. | Choose **in-context / external / summarized / stateless** by session shape at design time. Carrying repeatable **instructions** across tasks is a *separate* problem from carrying **state** — that pattern is a **Skill** (a `SKILL.md` loaded on description match, not injected every session). | [D1 · Agent memory + Skills](domain-1-agents/notes.md) |
| 8 | **Cost multimodal input before writing the ingestion code; match the API to the workload.** | The test set is thumbnails; production sends high-res originals that cost many times more per image. | `tokens = ⌈w/28⌉ × ⌈h/28⌉`, and the per-image ceiling differs by tier — run the formula against your **largest expected** input. **Inline base64** (one-off) · **Files API** (assets reused across requests) · **Message Batches** (offline, lower per-token, non-deterministic latency). Calling the **sync API in a loop is not batching**. | [D2 · Vision + Message Batches](domain-2-applications/notes.md); [D5 · Cost & Token Management](domain-5-model-selection/notes.md) |

---

## Unified diagnostic table — symptom → missing piece → domain

The module's core skill is reading the failure *type* off the symptom. These are scattered across the domain notes by topic; here they're in one place, which is how a scenario question actually reaches you.

| What you observe | The missing piece (the fix) | Domain |
|------------------|-----------------------------|--------|
| Output in the **wrong shape** (a sentence where a label was expected) | Output constraint | D6 |
| **Drift across turns** — scope/tone widens deeper into the conversation | Underspecified system prompt (add/scope one) | D6 |
| Correct task but **hallucinated structure** | Missing few-shot example | D6 |
| Reworded five times, still breaks on **untested inputs**; prompt keeps getting longer | Stop padding — move control to **structured outputs / strict tool use** | D6 → D2 |
| Claude keeps **picking the wrong tool** | Exclusion condition in the description (or merge behind a `type` param) | D8 |
| **`tool_use` error on a retry** after a dropped stream | A half-built block was committed — discard the partial turn, don't blame the schema | D2 |
| Tool selection **degrades after ~N turns** | Context-window pressure — look at the window, not the schema | D6 |
| Holds for 50 turns in test, **dies at turn 8** in prod | Tool outputs 3–5× longer than fixtures — compaction / pruning / subagent handoff | D6 |
| Agent **loops forever** / won't stop | Missing exit conditions | D1 |
| An **irreversible action reached a customer** | HITL checkpoint wasn't placed before the destructive call | D1 |
| Follow-up needs **last session's state** and has none | Wrong memory scope — in-context where external was needed | D1 |
| **Token limit blown at scale** by images/PDFs | Multimodal cost wasn't run at design time on production-size inputs | D2 |

---

## What's genuinely new here vs. the domain notes

Most of this module is review. Four framings are the value-add worth carrying into the exam beyond what the domain notes already say:

1. **The single failure-shape.** Dev illusion (small inputs, short/clean sessions) → production stressor → failure → design-time fix. Recognizing that shape lets you answer a scenario you've never seen, because the question is always "which variable did production change, and which decision pre-empts it."
2. **Design-time is minutes; refactor-time is hours.** Choosing a memory scope deliberately at design time takes ~20 minutes; refactoring in-context → external under production pressure takes ~1 hour — and it lands under a deadline already in motion. The exam rewards "decide at architecture stage," and this is the concrete cost behind that.
3. **"Sync API in a loop" ≠ batching.** A loop of synchronous calls is still synchronous — you're paying full price and full latency. The **Message Batches API** is the batch path (offline, ~50% off, non-deterministic latency up to 24 h). This is a common distractor dressed up as an optimization.
4. **Two levers are separate, not interchangeable.** Tool **count** (over-tooling degrades routing — D1) and tool **description quality** (wrong-tool bugs — D8) are different fixes. Likewise memory carries **state**; Skills carry **instructions**. Scenario questions punish conflating them.

---

## Cross-domain practice questions

Blueprint-style, scenario-based, original (never real exam items). Answer key + per-option rationale follow the set. Tagged by domain · skill.

**Q1 · D2 · Claude API Mechanics / D5 · Cost & Token Management — select 1.**
A chat feature lets a user upload a photo and expects an immediate label back. To "save cost," the team routes the image through the Message Batches API, and because that felt slow to wire up, they wrote a loop that fires synchronous requests one after another. Which single change best fixes the design?

- A. Keep Batches but raise the batch's priority so it returns faster.
- B. Use the synchronous Messages API for the interactive request; reserve Batches for offline volume.
- C. Lower `max_tokens` so each response comes back sooner.
- D. Resize the images to cut visual tokens.

**Q2 · D6 · Context Engineering / D8 · Tool Implementation — select 1.**
An agent passes a 50-turn test suite. In production, tool selection starts going wrong around turn 8. The tool schemas haven't changed since the tests passed. Where do you look first?

- A. Rewrite the tool descriptions.
- B. The context window — production tool outputs run longer and fill it, degrading selection.
- C. Set `disable_parallel_tool_use`.
- D. Lower the temperature.

**Q3 · D2 · Claude API Mechanics — select 1.**
After a dropped stream, your agent retries and the next request fails with a `tool_use` / `tool_result` pairing error. What's the root cause?

- A. The tool's `input_schema` is invalid.
- B. A half-built `tool_use` block from the interrupted stream was committed to history; discard the partial turn and retry.
- C. `max_tokens` was too low.
- D. A required beta header is missing.

**Q4 · D8 · Tool Implementation / Agentic Customization — select 2.**
Two registered tools both open with "use this to find information," and Claude picks wrong on ambiguous inputs. Which are appropriate design-time fixes? (Select 2.)

- A. Add an exclusion condition to each description naming when **not** to call it.
- B. If they stay hard to separate, merge them into one tool with a `type` parameter.
- C. Mark all parameters `required` so Claude has to reason harder.
- D. Connect an additional MCP server for redundancy.

**Q5 · D1 · Agent Architecture / Patterns — select 1.**
A tool can issue refunds — irreversible, and it touches real customer accounts. When do you add the human-in-the-loop checkpoint?

- A. After the first mistaken refund reaches a customer, then patch it.
- B. In the design, before the loop is wired — a checkpoint before the destructive call.
- C. Only if evals later show more than a 5% error rate.
- D. Never; rely on the loop's exit conditions to catch it.

**Q6 · D1 · Agent Patterns (Memory) — select 1.**
In development you ran one long continuous session and stored everything in-context; it worked. Production turns out to be many short sessions per user across days, and follow-ups can't recall earlier ones. Best correction?

- A. Use a bigger-window model / raise `max_tokens`.
- B. Move state to external storage so it survives across sessions — in-context was the wrong scope for short, numerous sessions.
- C. Switch the agent to stateless.
- D. Summarize every turn as it happens.

**Q7 · D6 · Prompt Engineering — select 1.**
A prompt returns the right content but in the wrong shape — a full sentence where the downstream parser expects one label from a fixed set. You've reworded it five times and it's gotten longer each pass. What does the failure type tell you to add?

- A. A longer, more emphatic instruction.
- B. An output constraint — a fixed label set and "return only the label, no other text."
- C. A different system-prompt role.
- D. More few-shot examples showing tone.

### Answer key & rationale

**Q1 — B.** User-facing + image = **synchronous**; the user is waiting and Batches runs up to 24 h. A loop of sync calls was never batching, so the "cost save" was illusory too.
- A wrong: there's no priority tier that makes an async batch appropriate for a waiting user — it's a latency **misread**, not a speed knob.
- C wrong: solves a different requirement (output length), not the realtime-vs-batch error.
- D wrong: resizing is a real cost lever (takeaway 8) but doesn't fix the architecture mistake in front of you.

**Q2 — B.** Schemas were unchanged and passed the suite, so the regression isn't in the schema. The signature — **fine in test, degrades after a fixed number of turns in prod** — is context-window pressure from tool outputs 3–5× longer than fixtures.
- A wrong: the descriptions already routed correctly in testing; rewriting them chases the wrong layer.
- C wrong: parallel-tool settings don't cause turn-N degradation.
- D wrong: temperature doesn't explain a turn-count-linked failure.

**Q3 — B.** A stream ending isn't a message completing. An interrupted stream can leave a **half-built `tool_use` block**; committing it to history breaks the pairing on the next request. Discard the partial turn and retry.
- A wrong: the schema was valid before the drop; nothing changed it.
- C/D wrong: neither a token ceiling nor a header produces a pairing error that appears only after a dropped stream.

**Q4 — A and B.** The description is the routing signal; an **exclusion condition** gives Claude a decision rule, and when two tools resist separation you **merge them behind a `type` param**.
- C wrong: forcing everything `required` makes Claude **fabricate** values it has no basis for — a different bug.
- D wrong: adding an MCP server enlarges the tool surface (more context, more routing ambiguity), the opposite of a fix.

**Q5 — B.** For an irreversible action the checkpoint is a **design-time** insertion, placed **before the destructive call** and **before the loop is wired**.
- A wrong: "patch it after it reaches a customer" is the exact anti-pattern the module calls out.
- C wrong: an eval threshold doesn't protect the irreversible action in the meantime.
- D wrong: exit conditions stop the loop; they don't gate an individual destructive call.

**Q6 — B.** Memory scope follows session shape. Short, numerous sessions need state that **survives session end** → external storage. This is the ~20-min design-time decision that became a ~1-hr production refactor.
- A wrong: window size isn't the issue — in-context state is wiped at session end regardless of window.
- C wrong: stateless throws away the cross-session memory the feature needs.
- D wrong: per-turn summarization manages in-session budget; it doesn't persist across sessions by itself.

**Q7 — B.** Wrong **shape** with correct content maps to a missing **output constraint**. The "reworded five times, getting longer" tell is the signal you've skipped diagnosis and are padding.
- A wrong: more emphatic text is padding — it doesn't supply the missing structure.
- C wrong: a system-prompt change addresses drift/scope, not shape.
- D wrong: few-shot fixes hallucinated structure; here the issue is an unconstrained form, and tone examples don't pin the label set.

---

## Capstone flashcards (meta-lessons)

Synthesis one-liners unique to this module. _These live here for self-test; the per-domain mechanics cards already sit in the domain `flashcards.md` decks and flow into `study-hub.html`. If you want these in the app too, say so and I'll fold them into the right domain decks._

**Q:** What single shape do all eight production takeaways share?
**A:** A dev illusion (small inputs, short/clean sessions) hides a failure that only appears under production load; the fix is a design-time decision, not a reword-and-retry patch.

**Q:** State the module's escalation ladder.
**A:** Single API call → workflow → agent. Move up only when the simpler pattern can't handle the variability.

**Q:** "The failure type tells you which technique is missing" — give the three prompt mappings.
**A:** Wrong shape → output constraint; drift across turns → system prompt; hallucinated structure → few-shot.

**Q:** Design-time vs. refactor-time cost of a memory-scope choice?
**A:** ~20 minutes to choose deliberately at design time vs. ~1 hour to refactor in-context → external under production pressure.

**Q:** Is calling the synchronous API in a loop the same as batching?
**A:** No. That's the mistake to avoid — it's still synchronous (full price, full latency). The Message Batches API is the batch path: offline, ~50% off, non-deterministic latency.

**Q:** Tool selection degrades after a fixed number of turns — schema or context window first?
**A:** The context window, not the schema.

**Q:** What do Skills carry that memory scope does not?
**A:** Repeatable *instructions* across tasks (loaded on description match) — distinct from carrying *state* across sessions.

---

## Sources

- Class module: **"Production-Grade Prompting, Agents & Tool-use"** (capstone recap, 8 enabling-objective takeaways).
- Anthropic Academy course modules cited by the class: **Claude 101**, **Claude Code 101 In Action**, **AI Fluency Framework Foundations**, **Building with the Claude API**.
- **platform.claude.com** — canonical reference for tool-use, agents, context, MCP, API mechanics (re-verify at build time).
- **Anthropic blog, "Building Effective Agents"** — workflow sub-patterns (chaining, routing, parallelization, evaluator-optimizer) and agent design guidance.
- Repo domain notes (where each takeaway's mechanics are verified): D1, D2, D5, D6, D8 `notes.md` and `domain-2-applications/structured-outputs-examples.md`.
