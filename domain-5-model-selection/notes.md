# Domain 5: Model Selection and Optimization — Notes

**Exam weight: 16.8%**

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| LLM Fundamentals | 5.2% | Tokens, context windows, sampling, non-determinism; fast mode, extended/adaptive thinking, effort levels; zero/single/multi-shot |
| Technical Fundamentals | 6.1% | Integrating with SDKs that wrap REST APIs; websockets; basic engineering practices |
| Model Selection and Tradeoffs | 2.7% | Opus vs. Sonnet vs. Haiku use cases; quality/latency/cost tradeoffs; breaking changes across releases |
| Cost and Token Management | 2.8% | Token usage tracking; cost modeling; prompt caching and cache check-pointing |

---

## LLM Fundamentals (5.2%)

Spans tokens, context windows, sampling/non-determinism, fast mode, **extended/adaptive thinking + effort levels**, and zero/single/multi-shot prompting. Extended thinking is written up first (it's the largest subtopic); the rest follow below it.

### Extended thinking (adaptive thinking + effort)

**What it is.** Extended thinking makes Claude write out step-by-step reasoning *before* the final answer. In the API response the reasoning arrives as `thinking` content block(s) positioned just ahead of the `text` block that holds the answer. It buys accuracy on hard problems by forcing the model to work through dependencies it would otherwise skip — at the cost of extra tokens (thinking tokens bill at the **output** rate).

Keep it separate from model choice: *whether to reason* (this topic) is a different decision from *which model to run* (see **Model Selection and Tradeoffs** below). Don't enable it by default — match the tool to the task.

**Turning it on (current mechanism).** On current models reasoning is **adaptive**: set `thinking: {type: "adaptive"}` and Claude decides *whether* and *how much* to think per request. Tune depth with the **`effort`** setting, not a fixed token budget.

- The older **manual** mode — `thinking: {type: "enabled", budget_tokens: N}` — is deprecated and, on the newest generations, **rejected with a 400 error**.

Model-by-model _(verified 2026-07-18, docs.claude.com)_:

| Model | Manual `budget_tokens` | How to get thinking |
|-------|:----------------------:|---------------------|
| Opus 4.8, Opus 4.7, Sonnet 5, Fable 5, Mythos 5 | ❌ 400 error | Adaptive — Sonnet 5 on by default; Opus 4.8/4.7 set `type:"adaptive"` explicitly; Fable/Mythos always on |
| Opus 4.6, Sonnet 4.6 | ⚠️ Deprecated (still works) | Adaptive + `effort` (recommended) |
| Opus 4.5, Haiku 4.5, earlier Claude 4 | ✅ Supported | Manual `budget_tokens` |

**Effort levels** — soft guidance on how much to think; default is `high`. Passed via `output_config={"effort": "..."}`:

| Effort | Behavior |
|--------|----------|
| `max` | Always thinks, no cap on depth. All adaptive-capable models. |
| `xhigh` | Always thinks deeply, extended exploration. Fable 5, Mythos 5, Opus 4.8/4.7, Sonnet 5. |
| `high` *(default)* | Almost always thinks; deep reasoning on complex tasks. |
| `medium` | Moderate; may skip thinking on simple queries. |
| `low` | Minimizes thinking; skips it where speed matters most. |

`max_tokens` is the **hard** cap on total output (thinking + answer); `effort` is **soft** guidance. Use both for cost control. Track spend via `usage.output_tokens_details.thinking_tokens`.

**When to use it — decision table:**

| Task shape | Extended thinking? | Why |
|------------|:-----------------:|-----|
| Multi-step reasoning holding several constraints at once (math derivation, multi-hop logic, planning dependent actions) | **On**, effort matched to depth | The reasoning pass is where the model works through dependencies it would otherwise skip |
| Mechanical / lookup tasks (classification, format conversion, field extraction, short factual answers) | **Off** | Won't improve the answer; you'd pay more tokens for nothing — a well-constrained prompt is the right tool |
| Agentic loops planning across several tool calls | **On**, budget for the planning step (not per call) | Reasoning before a plan reduces wrong-tool selection downstream. Adaptive auto-enables *interleaved thinking* (reasoning between tool calls) |

**Reading it back — the carry-back rule (tool-use loops).** ⚠️ When thinking is on *and* the conversation uses tools, every `thinking` block you receive must return to the API **exactly as it arrived** on the next turn. Each block carries a `signature` (encrypted full reasoning) proving it was Claude-generated; edit, summarize, or drop it and the signature no longer matches — the API returns **400 `invalid_request_error`** ("`thinking` or `redacted_thinking` blocks in the latest assistant message cannot be modified").

- `redacted_thinking` blocks (safety-redacted; encrypted `data` field, no readable text) follow the same rule — return them untouched.
- Most common bug: filtering content blocks by `type == "thinking"` silently drops `redacted_thinking` and breaks the next request.
- On newest models `display` defaults to `"omitted"` (empty `thinking` field; signature still present) — set `display: "summarized"` to actually read the reasoning. Omitting cuts **latency, not cost**: you're billed for full thinking tokens either way. _(verified 2026-07-18)_
- Structural requirement, not a prompting choice. Strictly required only when tools are in the loop; without tools you may drop prior-turn thinking blocks.

If accumulated reasoning is bloating context, the fix is context engineering — not stripping signatures mid-loop. See [Domain 6 · Context Engineering](../domain-6-prompt-context/notes.md).

**Exam framing (which-approach-fits):**

| | |
|---|---|
| **Handles well** | Hard reasoning/planning where a wrong answer is expensive and extra tokens buy accuracy |
| **Adds cost/complexity** | The carry-back requirement in tool loops, plus an `effort` level you must calibrate |
| **Use a different approach** | Classification, extraction, format tasks → a well-constrained prompt is cheaper and just as accurate |

**Cross-references:** model choice vs. reasoning toggle → *Model Selection and Tradeoffs* (this domain); context bloat from accumulated reasoning → [D6 · Context Engineering](../domain-6-prompt-context/notes.md); preserving thinking blocks across tool calls → [D8 · Tool Implementation](../domain-8-tools-mcps/notes.md).

> **Placement note:** the source class lesson taught extended thinking inside the *Prompt & Context Engineering* module, but the CCDV-F blueprint maps "extended/adaptive thinking, effort levels" to **D5 · LLM Fundamentals**, so it lives here with cross-refs from D6/D8.

### Tokens and tokenization

_Verified 2026-07-27, docs.claude.com._

A **token** is the unit the model actually reads and writes — roughly a word fragment, not a word and not a character. Everything downstream is denominated in them: **pricing** (input and output priced separately, output several times higher), **rate limits**, and the **context window**.

🔑 **Tokenization is model-specific, and token counts are not portable.** The same text tokenizes differently across model generations — Sonnet 5 produces roughly **30% more tokens** than Sonnet 4.6 for identical input, and Opus 4.7's tokenizer produces ~1×–1.35× the count of Opus 4.6's. A count measured on one model is not a count on another.

Three consequences the exam can test:

- **Re-baseline on a model change.** Token budgets, `max_tokens` values, compaction triggers, and cost dashboards calibrated on the old model can be wrong on the new one — including truncating output that used to fit. Don't apply a blanket multiplier; re-measure.
- **Per-token price ≠ per-request price.** A cheaper model that needs more tokens for the same job can cost more. Compare **cost per completed task**.
- 🚨 **Never use a third-party tokenizer.** `tiktoken` is OpenAI's; it undercounts Claude tokens by ~15–20% on prose and much more on code or non-English text. The only correct measurement is `count_tokens`, called with the **same model ID** you'll run inference on.

**`count_tokens`** takes the same request body as a Messages call and returns the input count **without running inference** — see *Cost and Token Management* below for how it's used as a pre-flight gate.

### Context windows

_Verified 2026-07-27, docs.claude.com. Window sizes are version-sensitive._

The context window is **everything the model can reference when generating a response, including the response itself** — a working memory, distinct from training data.

**What counts toward it** — the exam likes this list because people under-count it:

| Counts | Notes |
|---|---|
| The **system prompt** | |
| **Every message** in `messages` | Including tool results, images, and documents |
| **Tool definitions** | The schemas themselves, before any tool is called |
| **The output Claude generates** this turn | Including its **thinking tokens** |

⚠️ **Cached tokens still occupy the window.** Prompt caching changes what you *pay* for those tokens, not whether they take up space. "We enabled caching so context isn't a problem" is a wrong answer.

**Current sizes** _(verified 2026-07-27)_: **1M tokens** on Fable 5, Opus 5, Opus 4.8/4.7/4.6, Sonnet 5, and Sonnet 4.6 — the **default**, no beta header, billed at standard pricing. **200K** on Haiku 4.5 and Sonnet 4.5. Max output per request is **128K** on the 1M-context models (**64K** on Haiku 4.5). A single request holds up to **600 images or PDF pages** (100 on 200K-context models) — large document sets can hit **request size limits before the token limit**.

🚨 **Bigger is not automatically better — *context rot*.** As token count grows, accuracy and recall **degrade**. Curating what's in the window matters as much as how much room is left, which is why the fix for a bloated agent is context engineering rather than a bigger model → [D6 · Context Engineering](../domain-6-prompt-context/notes.md).

**Overflow behavior** — two distinct failures, and the exam separates them:

| Situation | Result |
|---|---|
| **Input alone** exceeds the window | `400 invalid_request_error` — "prompt is too long." Every model. Nothing ran. |
| Input **+ `max_tokens`** exceeds the window (Claude 4.5+) | Request is **accepted**; if generation reaches the limit it stops with `stop_reason: "model_context_window_exceeded"` |

Distinguish `model_context_window_exceeded` (ran out of *window*) from `max_tokens` (hit your *requested output cap*) — the fixes differ: compact or split the conversation vs. raise `max_tokens`.

**Context awareness** _(verified 2026-07-27)_: Sonnet 5, Sonnet 4.6, Sonnet 4.5, and Haiku 4.5 are given their remaining token budget automatically by the API, so they pace long tasks against real remaining space. It is automatic — you never send those tags. Opus 4.7 and later Opus models, Fable 5, and Mythos 5 do **not** receive them; give those an explicit budget with **task budgets** (beta) instead.

### Sampling and non-determinism

_Verified 2026-07-27, docs.claude.com._

The model produces a **probability distribution** over next tokens and **samples** from it. That sampling step is why **identical requests can return different outputs** — non-determinism is a property of how the model generates, not a bug or a configuration mistake.

Historically `temperature`, `top_p`, and `top_k` shaped that distribution. ⚠️ **On the newest models they are removed and return a `400`** — Fable 5, Opus 5, Opus 4.8, and Opus 4.7 reject them outright, and Sonnet 5 rejects non-default values. **Steer behavior with prompting instead.** _(verified 2026-07-27; check the model's docs at build time.)_

🚨 **`temperature = 0` never guaranteed identical output** on any model — it reduced variance, it did not eliminate it. Any design that depends on byte-identical responses is built on a false premise.

**What follows for engineering:**

| Implication | What to do |
|---|---|
| Tests can't assert exact string equality | Grade against **criteria** — schema validity, required facts present, constraints honored → [D4 · Evals](../domain-4-eval-testing/notes.md) |
| One passing run isn't evidence | Run the eval set; a single sample tells you almost nothing about the distribution |
| Output shape must be enforced, not hoped for | **Structured outputs** constrain the response to a schema; defensive parsing handles the rest → [D6 · Output Handling](../domain-6-prompt-context/notes.md) |
| Reproducibility comes from pinning, not sampling | Pin the model **version**; an unpinned alias adds a second source of variation → [D2 · Deployment and Versioning](../domain-2-applications/notes.md) |

### Fast mode

_Research preview — verified 2026-07-27. Availability and pricing are highly version-sensitive._

Fast mode runs **the same model** at up to **2.5× higher output tokens per second**, at premium pricing. It is a **latency** lever, not a quality or capability lever — the model does not change.

| | |
|---|---|
| **Models** | Claude Opus 5 and Opus 4.8 only. Opus 4.7 fast mode was **removed** — requesting it now errors |
| **Platforms** | Claude API only (including Managed Agents) — **not** Bedrock, Google Cloud, or Microsoft Foundry |
| **Price** | $10 / $50 per MTok on Opus 5 (vs. $5 / $25 standard) |
| **How** | Three things together: the **beta** messages endpoint, the beta flag `fast-mode-2026-02-01`, and `speed: "fast"` as a **top-level request parameter** |
| **Not available with** | Batch API, Priority Tier, Claude Platform on AWS, third-party platforms |

Operational details worth knowing: fast mode has its **own rate limit**, separate from standard Opus — on a `429` you either wait out `retry-after` or drop `speed` and fall back to standard. ⚠️ **Switching speed invalidates the prompt cache**, so a fallback path that flips `speed` per request destroys cache hits. `response.usage.speed` reports which speed actually served the request.

> **Don't confuse the three latency levers.** *Fast mode* speeds up the same model at a price premium. *Model tier* trades capability for speed and cost. *Effort* controls how much the model thinks before answering. They compose, and a stem describing "we need lower latency" can point at any of them — read for whether quality can move.

### Zero-, single-, and multi-shot prompting

_Verified 2026-07-27. See [D6 · Prompt Engineering](../domain-6-prompt-context/notes.md) for the full prompting craft; this is the D5 framing._

The "shot" count is simply **how many worked examples you put in the prompt**:

| Approach | What's in the prompt | Reach for it when |
|---|---|---|
| **Zero-shot** | Instructions only, no examples | The task is common and the output format is easy to describe in words |
| **Single-shot** (one-shot) | Instructions + **one** example | One example pins down a format that prose describes awkwardly |
| **Multi-shot** (few-shot) | Instructions + **several** examples | Output format is intricate, or edge cases and boundaries need to be *shown* rather than described |

🔑 **The load-bearing idea:** examples **demonstrate** what instructions can only **describe**. When a prompt keeps producing almost-right formatting, adding two or three examples usually fixes it faster than another paragraph of rules — and examples are where you encode the edge cases ("here's what to emit when the field is missing").

**The tradeoff is context and cost.** Every example occupies the window on **every request**, forever. Two mitigations:

- **Cache the examples.** A fixed example block is exactly the stable prefix prompt caching is for → *Cost and Token Management* below.
- **Stop adding examples when they stop earning.** More is not monotonically better — a long example block competes for attention with the actual request (context rot again).

⚠️ Exam trap: **few-shot examples are not a substitute for a schema.** If the requirement is *guaranteed* valid JSON, use structured outputs; examples make the right shape *likely*, not *guaranteed* → [D6 · Output Handling](../domain-6-prompt-context/notes.md).

| | |
|---|---|
| **Handles well** | Format control, edge-case handling, and tone matching — cheaply, with no code change |
| **Adds cost or complexity** | Permanent context occupancy on every request; examples must be maintained as the task drifts |
| **Use a different approach** | **Guaranteed** output structure → structured outputs. Knowledge the model lacks → retrieval, not examples ([D6 · Context Engineering](../domain-6-prompt-context/notes.md)) |

## Technical Fundamentals (6.1%)

_Verified 2026-07-27 against platform.claude.com (Streaming, Context windows, Errors, Token counting). SDK defaults are version-sensitive — re-verify at build time._

The blueprint names three things: **integrating with SDKs that wrap REST APIs**, **websockets**, and **basic engineering practices**. The through-line is that the SDK is a *convenience layer over an HTTP endpoint you could call yourself* — knowing what it does for you (and what it doesn't) is what the skill tests.

### The SDK is a wrapper, not a different API

Everything goes through one endpoint: **`POST /v1/messages`**. Tools, streaming, vision, thinking, caching, and structured outputs are all **parameters on that one request**, not separate APIs. The official SDKs (`anthropic` for Python, `@anthropic-ai/sdk` for TypeScript, plus Java, Go, Ruby, C#, PHP) build the JSON body, set headers, parse the response, and add the ergonomics below — but a raw `curl` sending the same body gets the same result.

🔑 **Why this framing matters on the exam:** a stem describing "the SDK doesn't support X" is almost always wrong. If the REST API supports it, the SDK does — and if a binding is missing, raw HTTP is the escape hatch, not a blocker.

**What the SDK adds over hand-rolled HTTP:**

| Concern | What the SDK does |
|---|---|
| **Auth** | Resolves credentials from the environment (`ANTHROPIC_API_KEY`, then an auth token, then a stored login profile) — a zero-arg client works without you passing a key |
| **Retries** | Automatic retry with exponential backoff on transient failures |
| **Timeouts** | A default request timeout, raised automatically for large-output requests |
| **Streaming** | Accumulates SSE events into a complete message object for you |
| **Typed errors** | One exception class per HTTP status, so you branch on type rather than string-matching messages |
| **Pagination** | List endpoints auto-paginate when you iterate the result |

### Retries and backoff — mostly already done for you

The SDKs retry **connection errors, 408, 409, 429, and 5xx** automatically with exponential backoff, defaulting to **2 retries**. Configure with `max_retries`; `0` disables it.

⚠️ **The exam-relevant asymmetry: retry the transient class, fix the permanent class.**

| Class | Codes | Retry? |
|---|---|---|
| Transient | `429` rate limit, `500` server error, `529` overloaded, network failures | ✅ Exponential backoff **+ jitter**; honor the `retry-after` header on a 429 |
| Permanent | `400` invalid request, `401` auth, `403` permission, `404` bad model/endpoint, `413` too large | ❌ Retrying re-sends the same broken request — fix it instead |

🚨 The classic wrong answer is **writing a custom retry loop that the SDK already provides**, or worse, one that retries `400`s. Reach for custom retry logic only when you need behavior beyond the built-in policy.

**Jitter is not decoration.** Plain exponential backoff synchronizes every rate-limited client onto the same retry schedule, so they collide again on the next attempt. Randomized jitter spreads them out.

### Timeouts

Default request timeout is **10 minutes**. Two traps:

- ⚠️ **Units differ by SDK** — Python and Ruby take **seconds**, TypeScript takes **milliseconds**, Go takes a `Duration`, Java a `Duration`, C# a `TimeSpan`. A "60" meant as seconds is 60 *milliseconds* in TypeScript.
- ⚠️ **Timeouts are retried**, so worst-case wall-clock is `timeout × (max_retries + 1)` — not `timeout`. Size upstream deadlines against the product, not the single value.

### Streaming is SSE — and the API does not use websockets

**This is the contrast the blueprint is pointing at.** Set `stream: true` and the response arrives as **server-sent events (SSE)** over the same HTTP request. The Claude API does **not** expose a websocket transport for the Messages API.

| | SSE (what the API uses) | Websockets (what it doesn't) |
|---|---|---|
| Direction | **Server → client only**, one direction | Full-duplex, both directions |
| Transport | Ordinary HTTP response, stays open | Separate protocol after an HTTP upgrade |
| Fit | A response streaming back token by token | Interactive bidirectional sessions |

The fit is the reason: a Messages request is **one request, one streamed response**. Nothing needs to travel client→server mid-response, so the full-duplex channel would buy nothing and cost infrastructure complexity.

**Event flow of a stream:** `message_start` → for each content block, `content_block_start` → one or more `content_block_delta` → `content_block_stop` → then `message_delta` (carries `stop_reason` and **cumulative** usage) → `message_stop`. `ping` events can appear anywhere, and **errors can arrive inside the stream** (e.g. `overloaded_error`) rather than as an HTTP status.

⚠️ Two details that produce bugs:

- **Usage counts on `message_delta` are cumulative**, not per-event — summing them double-counts.
- **Tool-use deltas are partial JSON strings** (`input_json_delta`), not objects. Accumulate the string and parse once `content_block_stop` arrives; never match on the partial text.

**Streaming is sometimes mandatory, not optional.** Large `max_tokens` values on a non-streaming request risk exceeding HTTP timeouts, and the SDKs refuse those requests rather than let the connection drop. Use `.get_final_message()` / `.finalMessage()` to stream for timeout protection while still receiving one complete message object — you get the safety without handling individual events.

### Basic engineering practices that show up as items

- **The API is stateless.** There is no server-side conversation. You resend the full `messages` array every turn, and the model has no memory of prior requests beyond what you send. Session state is *your* responsibility.
- **Concurrency ≠ batching.** Async clients and connection pooling let many requests be in flight at once (still realtime, still per-request priced). The **Batch API** is one asynchronous job at ~50% cost with up to 24-hour turnaround. Choose by latency tolerance, not by volume alone → [D2 · Claude API Mechanics](../domain-2-applications/notes.md).
- **Never hardcode API keys.** Environment variables or a secrets manager; a key in source is a `401` waiting to happen once it's rotated after the leak → [D7 · Identity, Secrets, and Key Management](../domain-7-security/notes.md).
- **Log the request ID.** Every response carries one; it's what lets Anthropic trace a failure end to end.
- **Handle unknown event and `stop_reason` types gracefully** — new ones are added under the versioning policy, and a `switch` with no default breaks on the next release.
- **Pin the model version** rather than tracking an alias, so an upstream model update isn't an untracked change to your output → [D2 · Deployment and Versioning](../domain-2-applications/notes.md).

| | |
|---|---|
| **Handles well** | Any Claude integration — the SDK removes auth, retry, timeout, streaming-accumulation, and error-typing boilerplate for free |
| **Adds cost or complexity** | A dependency and its defaults; SDK units and behaviors differ per language, so a pattern copied across languages can silently change meaning |
| **Use a different approach** | **Raw HTTP** when the language has no official SDK, the project is a shell/cURL pipeline, or the user explicitly asks for REST — never mix the two in one codebase |

**Cross-references:** error families and the batch/realtime decision → [D2 · Claude API Mechanics](../domain-2-applications/notes.md) and [D2 · Software Engineering Foundations](../domain-2-applications/notes.md); measuring before sending → *Cost and Token Management* (this domain); defensive parsing of what comes back → [D6 · Output Handling](../domain-6-prompt-context/notes.md).

## Model Selection and Tradeoffs (2.7%)

_Sources: class modules "Context Engineering" and "Model Selection in Production" (added 2026-07-19). Model identifiers are version-sensitive — confirm the current lineup against platform.claude.com at build time. Family framing verified 2026-07-18._

**The one early choice.** Before any context-engineering decision, you pick which model runs the workload. That choice sets the **price and speed floor** every later decision moves within — so it's made first and changed deliberately.

> **The distinction the exam leans on:** *cost management* optimizes spend **within** a model. *Model selection* sets the **baseline** that optimization works from. Caching and token trimming can't rescue a workload running on the wrong tier.

**The family (four tiers).** Each tier trades cost, latency, and capability differently:

| Tier | Positioned for |
|------|----------------|
| **Haiku** | Speed and cost efficiency on tasks that fit its capability envelope |
| **Sonnet** | The **balanced default** for most production workloads |
| **Opus** | Demanding work **above** the Sonnet envelope |
| **Fable** | Anthropic's **most capable** model — maximum-intelligence tasks: complex reasoning, advanced coding, research synthesis, sophisticated agentic workflows |

_Current identifiers (verified 2026-07-18): Fable 5, Opus 4.8, Sonnet 5, Haiku 4.5. The lineup changes — re-verify at build time._

**Model choice is a per-workload lever, not an architecture commitment.** The same prompt runs on any tier, so you can change the model without rewriting the application. That's what makes the eval-driven approach practical: switching is cheap, so there's no excuse for guessing.

### The latency / cost / quality trade-off

| Direction | You gain | You pay |
|-----------|----------|---------|
| **Up a tier** | Quality on the hardest cases | Higher per-token cost, *usually* higher latency |
| **Down a tier** | Speed and lower cost | Risk of a quality drop |

Two refinements the exam can test:

- ⚠️ **"Usually" is doing work.** A higher-tier model can finish **faster and cheaper** if it reaches a conclusion in **fewer tokens** than a lower tier would. Per-token price is not per-request price — a cheap model that flails, retries, or over-explains can cost more end-to-end. Compare cost per *completed task*, not per token.
- 💰 **Price in the cost of a mistake.** Saving a few dollars a day is not a sound trade if the quality drop introduces errors with significant downstream cost (bad data written to a system of record, a wrong answer to a customer, a failed agent run that has to be redone). The trade-off calculation includes error cost, not just token spend.

**There is no globally correct choice — only the right choice for a task at a quality standard.** The discipline is to make the trade-off *measurable* rather than reaching for the most capable model by default. 🚨 Reaching for the most capable model by default is **the most common and most expensive model-selection mistake in production** — a likely stem for a "what went wrong here" item.

**The decision rule: start at Sonnet, move on evidence.**

- **Default to Sonnet.**
- Move **up to Opus** only when an **eval set** shows Sonnet isn't meeting your quality bar.
- Move **down to Haiku** only when an **eval set** shows the quality regression is **acceptable for your task** — not merely to save money.

The load-bearing idea for the exam: **every model move is a measured decision backed by an eval, in both directions.** "Switch to Haiku to cut costs" with no eval is the wrong answer; so is "jump to Opus/Fable to be safe" without evidence Sonnet fell short.

**Step up** when an eval shows the current model failing on **the hardest cases your traffic actually contains** *and* the cost of a wrong answer is high. **Step down** when an eval shows a cheaper model holding the quality bar on **the bulk of traffic**, freeing budget and latency. In both directions the **eval is the instrument** — a model change is promoted on a measured score against your cases. This is why the eval built in [D4 · Eval, Testing, and Debugging](../domain-4-eval-testing/notes.md) doubles as the **gate for a model decision**.

> **Separate axis:** *which tier to run* is independent of *whether to turn on reasoning*. Don't conflate "use a bigger model" with "enable extended thinking" — see **Extended thinking** above under LLM Fundamentals. A mechanical task on Sonnet with a tight prompt often beats a reflexive jump to Opus.

### Routing: one default model plus an override

A system does not have to use one model for everything. The common production pattern is **a default model with an override**: route the bulk of traffic to a balanced default, and send specific request types to a larger or smaller model based on a **cheap signal read from the request**.

Typical signals: **task type**, **input length**, or a **difficulty classification**.

This is the same routing idea used for retrieval, applied to model choice — you pay for the more capable model **only on the requests that need it**.

| | |
|---|---|
| **Handles well** | Matching each workload to the **cheapest model that meets its quality bar**, measured on an eval rather than assumed |
| **Adds cost or complexity** | Routing adds a **classification step** and a **second model path** to maintain |
| **Use a different approach** | **Uniform traffic at one quality bar → pin a single model and skip the router.** The classifier's cost and failure modes buy nothing when every request is the same shape |

⚠️ Exam trap: routing is *not* a default best practice. It's justified by **variance in request difficulty**. Homogeneous traffic → one pinned model.

## Cost and Token Management (2.8%)

_Source: class module "Context Engineering." Verified 2026-07-18 against docs.claude.com._

Two API features cut what you pay for the tokens already in the window. They pair with the four context-budget strategies in [D6 · Context Engineering](../domain-6-prompt-context/notes.md): those manage *what enters* the window; these reduce the *cost of what's there*.

### Prompt caching (the cost angle)

Prompt caching stores the processing done on a **stable prefix** of your request so later requests reuse it instead of reprocessing the same tokens. The first request **writes** the prefix to cache; subsequent requests that send identical content up to that point pay a **fraction** of the original cost.

- **What to cache:** the parts that rarely change across turns — a long **system prompt**, a large **tool-definition set**, a **reference document** you query repeatedly.
- **How:** mark a **cache breakpoint** with a `cache_control` field of `type: "ephemeral"` on the last block you want cached. Up to **four** breakpoints.
- **Highest-leverage move:** for a multi-turn session with a stable system prompt and tool schemas, cache those prefixes once and reuse them every turn — the single biggest cost reduction available.
- **Caching is opt-in per request.** There is **no global setting** that turns it on — a breakpoint must be marked, or nothing is cached.
- **Exact match required:** a **single changed character before the cache point** invalidates the cache and forces a fresh write. Never put a breakpoint after content carrying timestamps or per-request data.
- **Breakpoint placement follows the fixed processing order** (tools → system → messages): a breakpoint **after the tools** caches the tool definitions while keeping the messages dynamic.

**Choosing a TTL by workload shape** _(added from class module "MCP Servers", 2026-07-19)_:

| Workload | TTL | Why |
|----------|-----|-----|
| **Back-and-forth** — requests arrive every few minutes | **5-min default** | Each read **resets the clock**, so an active conversation keeps the cache alive for free |
| **Long gaps between requests** — e.g. an agent that **pauses between steps** | **1-hour** (`ttl: "1h"` on the breakpoint, opt-in) | The 5-minute window would expire before the next request |

🚨 **The failure mode to recognize:** if the window expires before the next request arrives, you pay the **write cost again with no read benefit** — strictly worse than not caching. Match TTL to the actual gap between requests, not to how important the content feels.

⚠️ Caching applies only **above a minimum token threshold** (1,024 tokens for most current models; higher on Haiku tiers). **Short prompts are not cached even with a breakpoint set** — and this fails **silently**, with no error.

**Cache economics — a write is more expensive than a normal input token** _(added from class module "Cost & Orchestration", 2026-07-19; multipliers are version-sensitive — re-verify at build time)_:

| Token class | Priced at (× base input) |
|---|---|
| Cache **write**, 5-min TTL | **1.25×** |
| Cache **write**, 1-hour TTL | **2×** |
| Cache **read** | **0.1×** |
| Ordinary input | 1× |

🚨 **The economics only work when reads outnumber writes.** A prefix written once and read once is a *loss*, not a saving. This is the arithmetic behind the TTL table above and behind the "cache stable, high-volume prefixes" rule: the more requests hitting the same cached content, the lower the blended cost across the batch.

**Three conditions, all required, for caching to pay:**

1. **Identical content** — matched on an exact prefix. Adding a single word like "please" before the breakpoint invalidates it and forces a full reprocess. Anything that must reflect live state never produces a hit.
2. **Recurrence inside the TTL** — a prefix reused several times a minute pays off; one reused hourly does not under the 5-min default.
3. **Length above the model's minimum** — shorter prompts see no benefit regardless of stability.

**Automatic vs. explicit breakpoints.** Automatic mode takes a single cache flag at the **top level of the request** and manages breakpoints as the conversation grows — the **recommended starting point for most use cases**. Explicit mode puts `cache_control` on a specific block and caches everything up to and including it. Either way, **content after the last breakpoint is processed normally**.

⚠️ **The one consistency tradeoff.** Caching assumes the cached prefix is still *correct* on the later request. If the prefix carries data that can change, the cache holds a possibly stale version for as long as it lives — a consistency window your use case must tolerate. A fixed system prompt and a stable tool schema have nothing to go stale, which is why they're the safe, high-value targets.

> Cache **mechanics** — prefix hierarchy (tools → system → messages), automatic vs. explicit breakpoints, 5-min / 1-h TTL — are written up under [D2 · Claude API Mechanics → Prompt caching](../domain-2-applications/notes.md). This section is the *cost / when* angle the D5 skill tests; the D2 note is the *how*. (Related: [D6 · Context Engineering](../domain-6-prompt-context/notes.md) frames caching as one of the "two more levers" alongside the budget strategies.)

### Token counting

`count_tokens` lets you measure context pressure **before** a request goes out rather than after it fails. It takes the **same request body** as a Messages call and returns the token count **without running inference**.

- **In development:** verify your context budget holds against **real tool outputs**, not just small test fixtures — the 3–5× dev-to-prod gap is exactly what sinks sessions in production.
- **In production:** **gate** requests that would exceed the window *before* they error with `model_context_window_exceeded`.

---

## Observability — instrument before you optimize

_Source: class module "Cost & Orchestration" (added 2026-07-19). Sits downstream of [D4 · Production failure handling](../domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal): retries and fallbacks keep the system **reliable**; this section keeps it **affordable and fast**._

**Cost and latency are invisible in development and decisive in production.** A handful of dev calls never shows a bill. The same calls at volume become the constraint.

**Instrument three metrics on every call:**

| Metric | Captured from |
|---|---|
| **Token usage** — input and output separately | `response.usage` — the API already returns it |
| **Latency** | Wall-clock around the call |
| **Error rate** | Per call *and* per dependency |

```python
import time
def instrumented_call(make_call, step_name):
    start = time.perf_counter()
    resp = make_call()                       # raises on any API error
    latency_ms = (time.perf_counter() - start) * 1000
    log_metric(step=step_name,
               input_tokens=resp.usage.input_tokens,
               output_tokens=resp.usage.output_tokens,
               latency_ms=latency_ms)
    return resp
```

🚨 **Instrument from the start, not after the first surprise bill.** Treating observability as a later step means the invoice arrives before the explanation. In code it's a thin wrapper around the call — cheap to add on day one, expensive to retrofit under incident pressure.

**What per-call logging buys you is a better question.** Without it, a cost spike admits only one question: *why is the bill high?* With it: *which step, on which request type, is responsible* — and the answer is a row you can sort, not a guess.

- A flow that looks uniformly expensive usually has **one step doing ~90% of the spend**. That step is where every optimization dollar goes.
- The same holds for latency: **the slow step is rarely the one you expected.** Per-call timing plus a trace names it, instead of letting you optimize the wrong thing. (Trace mechanics → [D4 · Tracing](../domain-4-eval-testing/notes.md#tracing--turning-it-failed-into-step-4-failed).)

### The levers that move the budget

Identify the lever *before* tuning it — that's what separates optimization from guesswork.

| Lever | How it moves cost / latency | Where it's written up |
|---|---|---|
| **Model selection** | Reserve the most capable tier for steps that need it; route simpler work down. Sets the price/speed **floor** everything else works within. | [Model Selection and Tradeoffs](#model-selection-and-tradeoffs-27) above |
| **Prompt & context size** | Fewer tokens in = less to process on every call. | [D6 · Context Engineering](../domain-6-prompt-context/notes.md) |
| **Number of tool calls** | Each round trip is a full request plus a tool result back into the window; over-tooling multiplies both. | [D1 · Tool orchestration](../domain-1-agents/notes.md#tool-orchestration--over-tooling-vs-under-tooling) |
| **Prompt caching** | Reuses processing on a stable prefix — reads at 0.1×. | [Prompt caching](#prompt-caching-the-cost-angle) above |
| **Streamed vs. batched** | Streaming improves *perceived* latency; batching trades latency for a lower bill. | [D2 · Streaming](../domain-2-applications/notes.md#streaming-verified-2026-07-18) · [Batches](../domain-2-applications/notes.md#message-batches-api-verified-2026-07-12) |

> ⚠️ **Streaming and batching never compete for the same request.** Streaming optimizes how fast a response *feels* to a user in the loop; batching optimizes the bill for work no user is waiting on. A request is either user-facing or it isn't — that single fact decides which lever applies.

### Batching as the cost lever

Some work doesn't need an immediate answer: an overnight classification run, a backfill over a large dataset, a scheduled report. The **Message Batches API** processes those asynchronously and costs less per request than the same calls made one at a time. For any **non-urgent, high-volume** task, that discount is the deciding lever.

- The trade is **latency for cost** — results return within an asynchronous completion window, not immediately.
- Wrong tool for anything a user is waiting on; right tool for anything driven by a schedule.
- The current discount is **version-pinned** — confirm it against the docs at build time. _(Prior note in this repo: ~50% off, verified 2026-07-12.)_

💡 **Batching and caching compound.** A scheduled job that reuses the same long system prompt across many requests gets the batch discount on each request *and* the cache read price on the repeated prefix inside it. Recognizing that both apply to one workload is a likely exam stem.

⚠️ Recurring distractor: **a loop of synchronous calls is not batching.** Full price, full latency — see [`capstone-production-grade-prompting.md`](../capstone-production-grade-prompting.md).

### Reliability has a floor; you tune cost *within* it

Cost is only half the budget. Reliability is the other half, and it sets a baseline you don't optimize below.

**Define the floor first, then optimize above it.** A concrete floor looks like: *a user-facing request must complete within 4 seconds and may retry a failed dependency up to 3 times.* Every cost change then has to clear that bar:

| Proposed saving | Verdict |
|---|---|
| Switch to a smaller, cheaper model | ✅ Fine **if** it still fits the latency ceiling and doesn't raise the error rate enough to burn the retry budget |
| Cut retries from 3 to 2 on a slow dependency | ❌ Not acceptable if it pushes failure rate past the floor — that's trading lower cost for more failed requests |

🚨 **Order matters because the two pressures are not equally loud.** A high bill shows on a dashboard *daily* and generates constant pressure. A reliability problem shows as occasional failures easy to dismiss as noise — until they accumulate into an incident. Optimize cost first and the louder pressure wins; you find the floor only after crossing it. Set the floor first and reliability becomes the fixed constraint with cost optimized underneath.

> **What makes the floor enforceable:** the eval set from [D4](../domain-4-eval-testing/notes.md#evals-and-judges--defining-done-before-you-ship). A pinned baseline score states the minimum acceptable reliability in a *checkable* form, so any cost-saving change that drops the score below baseline **fails the gate before it ships**. Without that, "we cut costs and nothing broke" is an assertion, not a measurement.

⚠️ The cheapest configuration is rarely the most reliable. Cutting beneath the floor replaces a **visible expense** with **silent failures** — usually the worse trade, because a slightly higher bill is easier to defend than a system that doesn't work.

### Tradeoff summary — observability & cost

| | |
|---|---|
| **Handles well** | Makes spend and latency **visible per call**, so a cost problem traces to a **named lever** instead of a monthly total |
| **Adds cost or complexity** | A logging path on every call, plus the storage and dashboards to make it useful |
| **Use a different approach** | Nothing replaces it — but note the metrics are **diagnostic, not corrective**. Instrumentation tells you *which* lever; the lever table above tells you *what to pull* |

---

## Cross-domain pointer — model *version* pinning lives in D2

Model **selection** (which tier, which router, which cost lever) is this domain. Model **version pinning and platform choice** — aliases vs. pinned snapshots, `anthropic.`-prefixed Bedrock IDs vs. Vertex IDs vs. legacy ARNs, and promoting a new snapshot against a pinned baseline on partial traffic — are filed in **[D2 · Deployment and Versioning](../domain-2-applications/notes.md#deployment-and-versioning--where-the-workload-runs-and-what-ships)** (class module, 2026-07-19).

The join between the two domains: **selecting a model is only half the decision — the other half is pinning the snapshot you selected**, so an upstream update doesn't quietly replace the model your eval qualified.
