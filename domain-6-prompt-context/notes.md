# Domain 6: Prompt and Context Engineering — Notes

**Exam weight: 11.0%**

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Context Engineering | 3.8% | Context window management; preventing drift/bloat (tool output pruning, compaction); context isolation via subagents |
| Prompt Engineering | 4.6% | Instruction clarity; few-shot examples; system vs. user placement; output constraints; iterative refinement; input sanitization |
| Output Handling | 2.6% | Structured output patterns; response validation; defensive parsing; skepticism toward confident output |

---

## Context Engineering (3.8%)

_Source: class module "Context Engineering — model selection and keeping multi-turn sessions in budget." The module also covered model-tier selection and the caching/token-counting levers; per the blueprint those map to D5 and are written up there, cross-referenced below. API mechanics cross-checked against docs.claude.com, verified 2026-07-18._

**One-line definition.** Context engineering is deciding *in advance* what enters the context window, what comes back out as a summary, and what never enters at all. Model choice sets the price and speed floor (see [D5 · Model Selection and Tradeoffs](../domain-5-model-selection/notes.md)); within that floor, the context window is the binding constraint on any multi-turn agent.

### The context window is not a free resource

Treat the window as Claude's **working memory**: every message you send, every tool result you return, every document you inject, and every response Claude generates occupies space in it. **Every tool result stays in the window for the rest of the session** — invisible in a single-turn prompt, decisive in an agent running ten or twenty tool calls.

Two consequences, both exam-relevant:

1. **Cost + latency.** Every token in the window is billed on input *and* adds latency to the response; a long session compounds both. Moving state out of the live window is a budget decision, not only a correctness one.
2. **The ceiling is enforced, not silent.** Current models never quietly drop your oldest content. There are two distinct failure paths (verified 2026-07-18):

| Situation | What the API does | Stop reason |
|-----------|-------------------|-------------|
| Request is **already larger** than the window | Rejected **before generation** with a validation error | — (never runs) |
| Request fits but generation **hits the ceiling partway** | Returns the output generated so far | `model_context_window_exceeded` |

Because neither path truncates history for you, **if you want a session to outlive the window limit your application must trim or summarize history itself** before the next request goes out.

### Why this breaks in production but not in development

The trap the module's postmortem is built around: in development the window rarely fills — test inputs are small and sessions are short. In production, **tool outputs are often 3–5× longer than test fixtures** and sessions run more turns, so the window that held twenty turns cleanly in testing **fills at turn eight**. The workload passes every dev test and then fails in prod for one reason — the data got bigger and the sessions got longer. The cost of not planning for it is a production outage, which is why context budgeting is an **architecture-stage** decision rather than a production patch.

### Four strategies for staying in budget

Each fits a different shape of conversation. The columns that matter for the exam are *when to apply* and *what continuity you lose*.

| Strategy | What it does | When to apply | Continuity lost |
|----------|--------------|---------------|-----------------|
| **Pruning** | Jump back to an earlier message and continue from there, dropping everything after that point | Claude went down an unproductive path, or debugging back-and-forth piled up that won't help the next step | The work after the rewind point is gone; anything useful learned there must be relearned |
| **Compaction** | Summarize the history into a condensed version that keeps the key learnings; the summary costs fewer tokens than the original turns | Approaching the ceiling but you want to keep working on the **same** task with the knowledge built up so far | Any detail the summary didn't capture |
| **Clearing** | Start a fresh conversation with empty context | The next task is **completely different**; prior context would only add bias or confusion | All session context — anything needed later must be persisted somewhere (e.g., a `CLAUDE.md`) |
| **Subagent handoffs** | Spawn a subagent with its own isolated window holding only the task + system prompt it needs; it works and returns a summary | A subtask is self-contained enough to delegate — especially **exploration** where the journey clutters the main context but the answer is short | Visibility into *how* the subagent reached its answer; intermediate steps die with its context |

Mechanism names to recognize: **`/compact`** and **`/clear`** in Claude Code; in the API, clearing = a new session, and compaction has a documented **server-side compaction (beta)** the platform performs for you, with **manual (client-side) summarization** as the alternative.

### Compaction: the summary is only as good as the summarizer

The single most testable point: **what survives compaction depends entirely on how the summarizer prompt is written.** With `/compact` the tool decides what to include; with API server-side compaction (beta) the platform decides; but when you write a **manual** summarizer, that prompt determines what the agent knows on every subsequent turn.

- Under-specified: *"summarize the conversation so far."*
- Specified: *"summarize the conversation, preserving all file paths modified, all decisions made, and any errors encountered and their resolutions."*

Task-critical state loss from an under-specified summarizer is **one of the most common sources of multi-session agent failure** — not an edge case. When you rely on compaction, engineer the summarizer against the state your task cannot afford to lose.

### Subagent handoffs: decompose, don't enlarge the window

When a task is too big for one window, **increasing the window is not the fix — decomposition is.** Give each subagent only what it needs: a **scoped task**, the **minimum context** (only the prior results directly relevant), the **tools** required to finish, and clear **exit conditions**. The parent agent collects the results. This keeps per-turn cost low and makes long-horizon tasks tractable. Like pruning and compaction it adds implementation overhead, so apply it only where context cost is a **real** constraint.

| | |
|---|---|
| **Handles well** | Multi-step sessions that exceed the token budget and need decomposition — best designed at the architecture stage, not patched in later |
| **Use a different approach** | Pipelines that never approach the window limit — measure actual token usage against your model's limit before adding management overhead |

### Two more levers: caching and token counting

The four strategies manage *what enters* the window; two API features reduce what you *pay* for what is already there. Per the blueprint both map to **D5 · Cost and Token Management**, where they're written up in full: **prompt caching** reuses the processing on a stable prefix (system prompt, tool schemas, a reference doc) across turns, and **token counting** (`count_tokens`) measures context pressure *before* a request goes out so you can gate one that would exceed the window instead of letting it error. See [D5 · Cost and Token Management](../domain-5-model-selection/notes.md).

### Getting the right content in: the RAG path and its three break points

When the knowledge a task needs lives outside the window, you retrieve it. A retrieval-augmented path has **three places it can break**:

| Stage | What it decides | How it fails |
|-------|-----------------|--------------|
| **Chunking** | What counts as one retrievable unit | Too small → a chunk lacks the surrounding context to be useful; too large → one chunk dilutes the match with unrelated text. Sentence-/section-based chunking **with a little overlap** is a reasonable default; the overlap keeps facts that cross a boundary retrievable |
| **Embedding match** | Which chunks come back | Similarity search returns what is **semantically close**, not necessarily what contains the **exact term** — a query for a specific identifier can miss its chunk if a more semantically similar one outranks it. Running a **lexical match alongside** the semantic one (hybrid) covers this |
| **Assembly** | How retrieved chunks reach the model | If they don't arrive in the structure the prompt expects, the model answers **from memory instead of from the retrieved text** |

**Own an index vs. search at query time** — one clean tradeoff:

| | Fetch-once (retrieval index) | Search-across-rounds (agentic search) |
|---|------------------------------|----------------------------------------|
| **What it is** | Pre-built embedding index you query | Model reads the current files at query time via tools |
| **You gain** | Inspectable, testable retrieval — you can see exactly which chunks a query returned | No index infrastructure and **no staleness** — it reads what's there now |
| **You pay** | Building, storing, syncing, and securing the index | More tokens and time per query; a less inspectable process |
| **Best for** | A **stable** reference corpus queried with **simple lookups** | A **changing** corpus or **multi-step** questions |

⚠️ Any headline "agentic search beats the index by X%" figure is **version-pinned** — confirm it against the reference layer at build time rather than quoting a number. Agentic search is tool-driven file reading; see [D8 · Tools and MCPs](../domain-8-tools-mcps/notes.md) for the tool-call mechanics and the context cost of tool definitions.

**Two properties of retrieval worth stating plainly** _(added from class module "MCP Servers", 2026-07-19)_:

- **It scales.** As source material grows, **cost per request stays flat** — the model only ever receives the slice relevant to that question, never the whole library. A knowledge base can reach thousands of documents and a single question still pulls back roughly the same amount of text. **The source can keep growing without the request growing with it.** That property — not accuracy — is the reason to reach for retrieval in the first place.
- **It's only as good as what it finds.** The model reasons over the slice it receives; if the retrieval step **misses** the document, the model never sees it, and nothing downstream recovers. 🔑 This makes **how you organize your source material a retrieval-quality decision**, not housekeeping: `notes_final_v3.pdf` is hard to surface, `Q3 refund policy, updated August 2024` is easy. **Descriptive names and grouped related files are part of the retrieval system.**

**Where you've already seen agentic search without the name:** Claude Code deferring MCP **tool definitions** and loading only the tools a task needs (see [D8](../domain-8-tools-mcps/notes.md)), and Claude.ai **Projects** surfacing only the relevant document sections once a knowledge base outgrows the active window. Same pattern, different payload — tools in one case, documents in the other.

**One-line distinction for the exam:** classical RAG and agentic search both **find a relevant slice and generate from it**. The difference is **timing** — classical RAG matches against an index **built in advance**; agentic search finds the slice **at the moment of need**.

**You don't have to pick one strategy for everything — route** _(added from class module "Testing & Tracing", 2026-07-19)_. A **cheap classification call** reads the query and sends single-fact lookups down the fetch-once path and multi-part questions down the search-across-rounds path, so you **pay for iteration only when the query needs it**:

```python
def route(query):
    kind = classify(query)        # cheap call: "lookup" or "multi_step"
    if kind == "lookup":
        return fetch_once(query)  # static retrieval, one pass
    return agentic_search(query)  # search across rounds
```

| Default everything to… | What it costs you |
|---|---|
| **Iterative search** | Inflated cost and latency on questions a single fetch would have answered |
| **A static index** | Shallow answers on questions that needed several passes |

> 🔑 **When the router earns its cost:** only when **traffic is mixed** — some simple lookups, some multi-pass questions. The one classification call costs far less than running agentic search on a query one retrieval would have answered. **If every query is the same shape, skip the router and hardcode the path that fits** — that's the distractor-resistant half of the rule. (Same shape as the D5 model-routing pattern: a cheap call picks the expensive path only when warranted. The router is also a step your **trace** must record — see [D4 · Testing and tracing](../domain-4-eval-testing/notes.md#testing-and-tracing--the-layer-underneath-the-eval).)

### Related (already written)

Accumulated model reasoning is itself a source of context bloat in tool-use loops. Extended/adaptive thinking — and why you fix that bloat with context engineering rather than by stripping thinking-block signatures mid-loop — is written up in [Domain 5 · LLM Fundamentals → Extended thinking](../domain-5-model-selection/notes.md). The class taught extended thinking within this same module; per the blueprint those notes live in D5.

## Prompt Engineering (4.6%)

_Source: class notes on system prompts, XML, few-shot, and output constraints. API syntax cross-checked against the Domain 2 structured-outputs file, verified 2026-07-18._

### The core mental model: diagnose, don't pad

A prompt that works once in interactive use often breaks in production against untested inputs. The fix is **not** more words — it's identifying which **structural piece** is missing and adding that one piece. Rewording changes *how* you say something; it does not supply the missing structure. If Claude is crossing the boundary between your instructions and your data, clearer phrasing won't fix it. If the format keeps drifting, "please format this correctly" won't fix it either.

The rule: **name the failure → add the one technique that matches it → re-run.** If it still fails, diagnose again. A prompt that keeps getting *longer* with each pass (rather than *more precise*) is the tell that you're skipping the diagnosis step and just adding text.

### The four techniques

| Technique | What it does | Reach for it when |
|-----------|--------------|-------------------|
| **System prompt** | Sets the behavioral contract (role, scope, format) that applies to **every** response regardless of the user turn | Content is off: scope drifts, tone shifts, or Claude answers a wider question — and it worsens deeper into the conversation |
| **XML tags** | Marks unambiguous boundaries between instructions and input data (or between multiple inputs) | The prompt **mixes inputs with instructions** — e.g., "debug this code using these docs"; without tags the code and docs look identical to Claude |
| **Few-shot examples** | **Shows** the exact pattern instead of describing it — one correct input→output pair pins down a shape a written instruction can't | The task is right but Claude **invents the structure** — it understood the task but produced a shape you never asked for |
| **Output constraint** | Controls the **form** of the response (fields, label set, stopping point) independent of its content | The result comes back in the **wrong shape** — a sentence where you expected a label, prose where you expected JSON |

XML tag detail: use **descriptive** names that match your content (`<my_code>`, `<docs>`) — you do **not** need official/reserved tag names. The descriptive name is what makes the boundary clear.

### Diagnostic mapping (the heart of this domain)

The failure mode tells you which technique is absent. Match the symptom, add exactly that one:

| What you observed | Missing piece | Why that technique is the fix |
|-------------------|---------------|-------------------------------|
| Wrong **shape** — sentence instead of a label, prose instead of JSON | **Output constraint** | The prompt never specified form/field names/stopping point, so Claude returns plausible text the parser wasn't built to accept |
| Wrong **content / scope drift**, worsening across turns | **System prompt** (or a more specific one) | Nothing is holding role, scope, and format steady as the conversation runs on |
| Correct task but **hallucinated structure** | **Few-shot examples** | Claude can't infer an exact structure from a description alone; one pair shows it |
| Clean on tested inputs, **breaks on a variant** (edge case, unusual field) | **A constraint covering the variant** | The prompt handled the happy path; naming the variant (or adding an example for it) closes the gap the test inputs never exposed |

### Worked example — a classification prompt before and after

**Before (bare instruction, no constraint):**

```
System: "You are a support classifier. Classify the ticket."
User: <ticket>I was charged twice for the same month.</ticket>
```

Claude returns `"Billing"` on some runs, `"billing"` on others, sometimes a full sentence like *"This looks like a billing issue."* The content is right; the **form** varies, so the downstream router (which expects one of a fixed label set) breaks. This matches row 1 of the table → the missing piece is an **output constraint**.

**After (constraint, plus the two techniques that lock the label set and show the format):**

```
System: "You are a support classifier. Classify each ticket into exactly one of:
BILLING, TECHNICAL, ESCALATION. Return only the label. No other text."
<sample_input>My account shows two charges for April.</sample_input>
<ideal_output>BILLING</ideal_output>
<sample_input>The API keeps returning a 429 error.</sample_input>
<ideal_output>TECHNICAL</ideal_output>
User: <ticket>I was charged twice for the same month.</ticket>
```

Three techniques do **distinct** work here:

- **System prompt** — sets the output contract: exactly one label from a fixed set, nothing else.
- **XML tags** — mark where each example ends and the next begins, so Claude doesn't read the examples as part of the instruction.
- **Few-shot pairs** — show the exact casing and format rather than describing it.

Together they produce output consistent enough to route programmatically.

### Stack, simplify, or diagnose?

| Situation | Guidance |
|-----------|----------|
| **Stack all four** | Tasks with a clearly defined output contract and edge cases coverable by examples — stack all four against that contract |
| **Simplify** | Don't add all four to a task that needs one. "Summarize this paragraph" needs neither few-shot examples nor an output schema |
| **Diagnose before adding more** | If the prompt grows longer each iteration instead of more precise — if you've re-prompted five times and it's still wrong — stop and diagnose the failure **type** before adding text |

## Output Handling (2.6%)

_Structured-outputs API mechanics live in full in [`../domain-2-applications/structured-outputs-examples.md`](../domain-2-applications/structured-outputs-examples.md) (JSON outputs vs. strict tool use, `stop_reason` handling, costs, incompatibilities). This section covers the **pattern and the defensive-handling angle** the exam tests under Output Handling — the deep API syntax is not repeated here._

### Prompt request vs. API guarantee

Everything in the Prompt Engineering section shapes output by **writing instructions and hoping Claude follows them** — the prompt is a *request*, so the model can still return a stray sentence, a wrong field name, or malformed JSON that breaks a downstream parser. A prompt-level "return only JSON" holds on the cases you tested and slips on an edge case you didn't — the exact failure the classification example walks through.

**Structured outputs** remove that gap for production code: you hand the API a **JSON schema** and the model is constrained at generation time. This is **constrained decoding** — as Claude generates each token, only tokens that keep the output valid against the schema are allowed, so a schema-violating response can't be produced in the first place. That moves output correctness from something you *verify after the fact* to something the API *rules out before it happens*.

Two mechanisms constrain different halves of the exchange (full detail in the Domain 2 file):

| Mechanism | Parameter | Constrains |
|-----------|-----------|------------|
| **JSON outputs** | `output_config.format` (`type: "json_schema"`) | Claude's **final response text** |
| **Strict tool use** | `strict: true` on a tool definition | The **arguments Claude passes to your tools** |

### Defensive parsing: a guaranteed schema is NOT a guaranteed success

The Output Handling skill is about **validation, defensive parsing, and skepticism toward confident output** — not just requesting a shape. Even with a schema, two outcomes return non-conforming output, so production code checks `stop_reason` rather than assuming every response parses:

| `stop_reason` | What happened | What to do |
|---------------|---------------|------------|
| `end_turn` | Complete, schema-valid output | Parse it |
| `refusal` | Safety refusal; the refusal text overrides the schema | Handle as a refusal — don't parse |
| `max_tokens` | Truncated mid-structure; JSON is incomplete | Raise `max_tokens` and retry |

Two more defensive habits: **enum casing isn't guaranteed** (Claude may return `"High"` for enum `"high"` — compare case-insensitively; never define two enum values differing only in capitalization), and structured outputs are **not** free — they *add* input tokens (an injected format-describing prompt) and the first request on a new schema pays a grammar-compile latency (cached 24 h). "Structured outputs are always slower / cheaper" are both wrong.

### Skepticism toward confident output

Confident-sounding output is not validated output. Defensive parsing means: constrain what you can at the API layer, still check `stop_reason`, validate values you can't schema-constrain (ranges, referential integrity, business rules), and never let a fluent response substitute for a checked one. When a malformed tool argument would crash a function or trigger a wrong action in an agentic loop, prefer `strict: true` at the API over trusting a prompt instruction.
