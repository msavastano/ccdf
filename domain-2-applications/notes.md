# Domain 2: Applications and Integration — Notes

**Exam weight: 33.1%** — largest domain; ~17–18 of 53 items. Version-sensitive facts verified against platform.claude.com docs **2026-07-12**.

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Understanding Requirements | 3.4% | Functional and infrastructure requirements from business requirements and solution architecture |
| Systems Life Cycle | 2.8% | Life cycle management concepts: develop, implement, operate, maintain |
| Claude API Mechanics | 6.8% | Messages, tools, streaming, vision, thinking, caching; third-party vendors; batch API; realtime vs. batch tradeoffs |
| Software Engineering Foundations | 7.4% | REST APIs, JSON, async programming, version control, SDLC integration, code review, refactoring |
| Claude Application Design | 8.6% | Instruction interpretation across interfaces; content boundaries; schema design; session hygiene; plugin management |
| Configuration Management | 4.1% | CLAUDE.md files, settings.json, model version pinning, prompt versioning, plugin dependencies |

---

## Understanding Requirements (3.4%)

**Translate business requirements → solution architecture → functional + infrastructure requirements.**

- **Functional requirements**: what the system does — inputs/outputs, features, tool integrations, output format, accuracy targets.
- **Infrastructure (non-functional) requirements**: how well it must do it — latency, throughput, availability, cost ceilings, data residency, compliance, scalability.

Decision criteria the exam loves (map the scenario to the constraint that dominates):

| Business signal | Requirement it implies |
|---|---|
| "Results by tomorrow morning" / "overnight" | Latency-tolerant → batch processing |
| "Customer-facing chat" | Low latency → realtime, streaming, possibly Haiku/fast mode |
| "Handles PII / regulated data" | Security, data-retention, residency requirements before feature work |
| "Cost is the primary concern" | Model tier, caching, batch — not just "smaller model" |
| "Must be reusable across teams/apps" | Shared service boundary → MCP server, not per-app logic |

**Trap:** distractors that solve the wrong requirement (e.g., cutting `max_tokens` when the real issue is realtime-vs-batch selection).

### From business problem → functional requirement (class notes, 2026-07-19)

A **business problem is not a requirement**. "Help support agents answer faster" is a goal; it can't be designed against, verified, or reviewed. A functional requirement names *what the system must do*, stated specifically enough to check.

| Business problem | Derived functional requirements |
|---|---|
| "Help support agents answer faster" | Classify each ticket into one of four queues · Draft a reply citing the relevant policy · Never auto-send without human approval |

The discipline: **write each requirement as a checkable statement of behavior.** The payoff is downstream — a specific requirement becomes *a line in an eval* and *a criterion at review*. A vague one becomes neither.

### Deriving infrastructure requirements — the four questions

Infrastructure requirements are usually **not stated in the business problem**. You derive them by asking the questions the problem implies. These four most often decide the deployment platform:

| Axis | The question to ask | Why it decides platform |
|---|---|---|
| **Latency** | How fast must a response be, *measured where the user is*? | Region/edge placement, realtime vs. batch |
| **Scale** | How many requests, and at what peak? | Throughput, rate limits, batch vs. sync |
| **Residency** | Where must data be processed, under which regulation? | 1P API vs. Bedrock vs. Vertex; region pinning |
| **Identity** | Who acts, under what credentials, what must be auditable? | Auth model, service accounts, audit logging |

**Capture these first.** They are easiest to elicit at the start — before a platform gets chosen for reasons of familiarity, and then retrofitted with justifications.

### Documenting requirements so the decision can be defended

The deployment decision **will be reviewed by people who did not gather the requirements**. A short requirements record covers three things:

1. The functional behaviors
2. The infrastructure constraints
3. **The regulation each constraint comes from** — the constraint alone isn't defensible; its source is

That record is the input the deployment decision reads from. With it, you defend a platform choice as *following from the requirements*. Without it, the choice looks like it followed from familiarity.

**Tradeoff summary — requirements-first**

| | |
|---|---|
| **Handles well** | Turning a business problem into checkable functional + infrastructure requirements *before* any platform is chosen |
| **Adds cost/complexity** | Eliciting infrastructure constraints up front requires a scoping conversation teams under deadline skip |
| **Use a different approach** | Throwaway prototype, no review, no regulated data → lightweight notes suffice |

## Systems Life Cycle (2.8%)

Standard SDLC phases applied to Claude systems: **plan → analyze → design → build → test → deploy → operate → maintain → retire**.

### The seven-phase arc for a Claude application (class notes, 2026-07-19)

The class framing collapses this into the arc a Claude app actually travels. The value isn't the phase names — it's that **each engineering task belongs to exactly one phase, with a defined artifact and gate**. Work that arrives without a phase arrives as an unrelated task.

| # | Phase | What happens | Artifact |
|---|---|---|---|
| 1 | **Requirements** | Capture functional + infrastructure needs | Requirements record |
| 2 | **Design** | Choose platform, model, and trust boundaries | Architecture / boundary decision |
| 3 | **Build** | Write the agent, tools, and prompts | Working system |
| 4 | **Test** | Evals + unit, integration, end-to-end checks | Eval suite + baseline |
| 5 | **Deploy** | Pin the version; gate promotion on the eval | Pinned release |
| 6 | **Operate** | Instrument cost, latency, errors; enforce guardrails | Telemetry + guardrails |
| 7 | **Iterate** | Feed production findings back into requirements | Updated requirements → loop to 1 |

Note phase 7 closes the loop to phase 1 — the lifecycle is a cycle, not a line.

### Gates — where a regulated engagement keeps control

A **gate** is the decision to move from one phase to the next. Two canonical gates the exam can test:

- **Design → Build:** you do not start building until the platform satisfies the **residency requirement**.
- **Deploy → full production:** you do not promote until the new version **clears the eval against the pinned baseline**.

Placing work in the right phase and **refusing to skip a gate** is what keeps a Claude application reviewable.

**Tradeoff summary — lifecycle with gates**

| | |
|---|---|
| **Handles well** | Every piece of engineering work sits in its phase, with a defined artifact and gate |
| **Adds cost/complexity** | Gates add checkpoints a team under deadline is tempted to skip |
| **Use a different approach** | A one-off experiment may collapse phases — a regulated deployment cannot |

Claude-specific lifecycle concerns:

- **Test/deploy gate**: evals run before promotion, not after incidents.
- **Operate**: monitor token usage, error rates, output quality drift.
- **Maintain**: model deprecations and retirements are routine (e.g., Opus 4 and Sonnet 4 retired, Opus 4.1 deprecated as of mid-2026) — plan migration paths; a pinned model version will eventually be sunset.
- **Change management**: prompt changes are production changes — version, review, and eval them like code.

## Claude API Mechanics (6.8%) — highest-yield API skill

### Messages API structure
- `system` (top-level parameter) vs. `messages` (alternating `user`/`assistant` roles). Content is a list of typed blocks (text, image, document, tool_use, tool_result, thinking).
- You send the **full conversation history** each request — the API is stateless.
- Key params: `model`, `max_tokens` (required), `temperature`, `stop_sequences`, `tools`, `tool_choice`, `stream`.
- Stop reasons: `end_turn`, `max_tokens`, `stop_sequence`, `tool_use`, `pause_turn` (server-tool loop paused — resubmit to continue).

### Streaming (verified 2026-07-18)
- Server-sent events (SSE); `stream: true`. Use for: user-facing UX (time-to-first-token) and long generations where non-streamed connections risk timeouts. Not available in batches.
- Streaming assembles the **same final `Message`** a non-streamed call returns. The only new work is (a) reassembling the blocks yourself and (b) handling a stream that stops early. It changes **perceived latency only** — not cost, not output content.

**Event sequence** — each SSE event names a type and carries JSON; your handler applies it to the partial message it's building:

| Event | Signals | Handler does |
|---|---|---|
| `message_start` | Message shell: empty `content`, initial `usage` | Initialize an empty content array |
| `content_block_start` | A block opens at an `index` (`text` / `tool_use` / `thinking`); a `tool_use` block arrives with `name` + `id` but **no input yet** | Create a slot at that index |
| `content_block_delta` | An incremental fragment: `text_delta`, `input_json_delta` (a `partial_json` string), or `thinking_delta` | Append the fragment to the block at that index |
| `content_block_stop` | The block at this index is complete | Finalize it — **first moment** a `tool_use` block's accumulated JSON is parseable |
| `message_delta` | Top-level changes: `stop_reason` and **cumulative** `usage` | Record the `stop_reason` |
| `message_stop` | Stream complete | The assembled content array is now the finished message — treat it exactly like a non-streamed response |

*(A `ping` event may appear at any time and carries nothing; `error` events can arrive mid-stream.)*

**The rule that prevents state corruption — never act on a partial block:**
- A `tool_use` block's `input` arrives as **partial JSON strings** spread across many `input_json_delta` events; it is **not valid JSON until `content_block_stop`**. Parse the input or run the tool **only after** `content_block_stop` for that block. Acting early = malformed JSON or missing arguments.
- Add a streamed assistant turn to conversation history **only after `message_stop`**, with every block fully assembled. A turn built from a cut-off stream is incomplete, and a **half-built `tool_use` block breaks the tool_use/tool_result pairing** on your next request.
- Before continuing an agent loop, check the `stop_reason` from `message_delta`: `tool_use` means your assembled calls are ready to run; **any other value is a different path**, not the tool path.

**When the stream stops early** (dropped connection, timeout, client disconnect):
- Track completion on purpose — a turn is usable **only once `message_stop` has arrived**. Until then, treat what you've accumulated as provisional.
- **Discard the partial assistant turn; do not save it to history**, then retry the request. Committing a half-built turn is exactly what breaks the following request.
- Severity differs by block: a partial **text** block shown to a user is a cosmetic glitch; a partial **`tool_use`** block written into history is **structural corruption** of the next turn.

**The accumulation pattern in code** _(added from class module "Cost & Orchestration", 2026-07-19)_ — accumulate deltas **keyed by `index`** until the stream closes, then reconstruct the tool calls from the completed blocks:

```python
def stream_with_tools(client, **kwargs):
    tool_blocks = {}          # index -> accumulated block
    text_chunks = []
    with client.messages.stream(**kwargs) as stream:
        for event in stream:
            if event.type == "content_block_start":
                block = event.content_block
                tool_blocks[event.index] = {
                    "type": block.type,
                    "id": getattr(block, "id", None),
                    "name": getattr(block, "name", None),
                    "input_json": ""
                }
            elif event.type == "content_block_delta":
                delta = event.delta
                if delta.type == "input_json_delta":
                    tool_blocks[event.index]["input_json"] += delta.partial_json
                elif delta.type == "text_delta":
                    text_chunks.append(delta.text)
            elif event.type == "message_stop":
                break
    # reconstruct completed tool calls only after the stream closes
    tool_calls = []
    for block in tool_blocks.values():
        if block["type"] == "tool_use":
            tool_calls.append({
                "id": block["id"],
                "name": block["name"],
                "input": json.loads(block["input_json"])   # parseable only now
            })
    return "".join(text_chunks), tool_calls
```

⚠️ The `json.loads` sits **after** the loop for a reason: a `tool_use` block is not safe to act on until the full `input_json` has accumulated. And a stream that breaks mid-response is a **transient failure** — retry the whole request rather than passing the partial output downstream ([D4 · retriable vs. terminal](../domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal)).

### Vision / multi-format input (multimodal ingestion) (verified 2026-07-18)

Images and PDFs are content blocks in user turns (base64, URL, or Files API reference). Vision requests work in batches too. **Every image and PDF consumes context budget before Claude reads a single character of your prompt** — measure token cost on production-scale inputs *at design time*. The fix for an over-budget pipeline is usually a ten-minute resize step; discovering it after deploy costs far more.

**Image token cost — Claude views images in 28×28-pixel patches, one visual token per patch:**

> `tokens = ⌈width / 28⌉ × ⌈height / 28⌉`

- A 1,000 × 1,000 image = ⌈1000/28⌉ × ⌈1000/28⌉ = 36 × 36 = **~1,296 visual tokens**. Ten high-res screenshots ≈ a detailed system prompt.
- Each model tier has a **max long-edge** limit *and* a **max visual-token** limit. Images over either limit are **downscaled first**, so the formula runs on the *scaled* dimensions.
- Per-tier limits (verified 2026-07-18; confirm on the Vision page at build time — these change across model generations): **standard tier** ≈ 1,568 px edge / 1,568 tokens; **newest tier (Opus 4.7+)** ≈ 2,576 px edge / 4,784 tokens. Newer models accept substantially larger images.

**Three ways to send an image — choose by reuse and size:**

| Method | How | Overhead | Best when |
|---|---|---|---|
| **Inline base64** | Encode the bytes into the request | Full bytes on **every** request | One-off image; simple pipeline; no reuse |
| **URL reference** | Point to a hosted URL; Claude fetches it | You host it; no re-encoding | Asset already hosted somewhere reachable |
| **Files API** | Upload once → get a `file_id`, reference the ID afterward | One-time upload; later requests carry only the ID (≈ zero payload) | Same asset across **many requests/turns**, or a large asset; keeps asset management separate from inference calls. **Beta; not on Bedrock or Vertex — verify your platform.** |

The Files API `file_id` **carries no payload weight as history grows**, which is why it's the clean choice for an image referenced across multiple conversation turns.

**PDFs use a `document` block, not `image`:**
- Same `source` pattern as images (`base64`, `url`, or Files API `file_id`), with `media_type: "application/pdf"`.
- **No required `name` field.** Optional `title` (readable name) and optional `context` (extra metadata) — neither is required to send a PDF.
- Token-cost and Files-API-reuse considerations apply identically.

```json
{
  "type": "document",
  "source": { "type": "base64", "media_type": "application/pdf", "data": "<base64-pdf-bytes>" },
  "title": "contract_review.pdf"
}
```

**Prompting multimodal inputs:** the same techniques from text apply — a bare "describe this image" underperforms for the same reason a bare text prompt does (Claude has no target structure to aim for). The difference is that images carry ambiguity text can't: overlapping objects, depth/spatial relationships, partial occlusion. A good visual prompt **names how Claude should handle each** — e.g., "if objects overlap, describe each separately and note the overlap" — a constraint a text-only prompt would never need.

**Vision + Batch — when they fit, and the two ways it breaks:**
- **Fits:** offline workloads that reuse assets and need structured output across thousands of inputs — the textbook case is a nightly pipeline classifying images against a fixed taxonomy. Files API removes redundant uploads, the Batches API absorbs latency, structured-output techniques keep results machine-readable. (Mechanics of the Batch API are in the [Message Batches API](#message-batches-api-verified-2026-07-12) section below.)
- **Failure 1 — misreading latency:** reaching for batch in a **user-facing** flow with an image. It passes tests and fails in production because the user is *waiting* and the batch isn't (up to 24 h). "User uploads a photo and expects an immediate classification" → **synchronous, always.**
- **Failure 2 — underestimating context cost:** images and PDFs eat budget before any text, so pipelines loading multiple large assets per request blow past token limits at scale. Measure on production-size inputs *before* you build.

### Thinking
- **Extended thinking**: explicit thinking budget for hard problems; thinking tokens billed as output.
- **Adaptive thinking / effort levels**: model decides how much to think; effort tunes quality vs. latency/cost.
- Thinking blocks can't be `cache_control`-marked directly but are cached alongside other content in prior assistant turns.

### Prompt caching (verified 2026-07-12)
- Cache prefix order is a **hierarchy: tools → system → messages**. A change at one level invalidates that level and everything after it.
- Two modes: **automatic caching** (one top-level `cache_control`; system moves breakpoint to last cacheable block) and **explicit breakpoints** (up to 4 `cache_control` markers).
- **TTL**: 5 min default; 1 h available at higher write cost. Cache refreshes free on each hit.
- **Pricing multipliers**: 5-min write = 1.25× base input; 1-h write = 2×; cache read = **0.1×**. Stacks with the batch discount.
- **Minimum cacheable length varies by model** (e.g., 1,024 tokens for Opus 4.8 and Sonnet tiers; 4,096 for Haiku 4.5). Below minimum → silently not cached, no error.
- Usage fields: `cache_creation_input_tokens`, `cache_read_input_tokens`, `input_tokens` (only tokens *after* the last breakpoint). Total input = sum of all three.
- Put the breakpoint on the **last block identical across requests** — never on content containing timestamps/per-request data.
- Exact-match required; caches isolated per organization (and per workspace on the Claude API as of Feb 2026).

### Message Batches API (verified 2026-07-12)
- Asynchronous; **50% off** standard prices for both input and output. Discount stacks with caching.
- Limits: **100,000 requests or 256 MB** per batch; most complete **< 1 h**; hard expiry **24 h**; results downloadable **29 days**.
- Each request: unique `custom_id` + standard Messages params. **Results return in any order — match by `custom_id`.**
- Result types: `succeeded`, `errored`, `canceled`, `expired` — you're only billed for `succeeded`.
- Not supported in batches: `stream: true`, fast mode. One request failing doesn't affect the rest of the batch.
- Caching in batches is best-effort (30–98% hit rates); prefer the 1-h TTL for shared context.

### Realtime vs. batch — the classic exam tradeoff

| Choose | When |
|---|---|
| **Realtime (Messages API)** | User is waiting; interactive apps; results feed an immediate next step |
| **+ Streaming** | Perceived latency matters; long outputs |
| **Batch** | Large volume, latency-tolerant (overnight reports, bulk evals, moderation backlogs, mass generation); cost is a driver |

### Errors, retries, and rate-limit headers (verified 2026-07-19)
- **Retriable:** `429` (rate limit), `529` (Anthropic-side overload), `5xx` (500/502/503/504). **Terminal:** `400`, `401`, `403`, `404` — the cause is in the request, so an identical retry reproduces it.
- The **SDKs auto-retry transient failures** with progressive delays, up to a configurable max attempts. Don't wrap your own loop around them — two loops multiply attempts against a rate limit instead of capping them.
- Responses carry **rate-limit headers**; `retry-after` on a `429`/`529` is **authoritative** over your own backoff. Use exponential backoff + jitter only when the header is absent. ⚠️ Header names/values are version-pinned — confirm at build time.
- A **refusal is HTTP `200`** with `stop_reason: "refusal"` — invisible to a status-code classifier. Check `stop_reason`, then fail fast.
- Failed tool executions return a `tool_result` with **`is_error: true`**, never an empty result.
- Full treatment (decision table, fallback behavior, code) → [Domain 4 · Production failure handling](../domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal).

### Third-party vendors
- Claude is also available via **Amazon Bedrock**, **Google Cloud (Vertex AI)**, and **Microsoft Foundry**. Same models, different auth/endpoints, and **feature gaps exist** (e.g., Bedrock lacks automatic caching and has different cache minimums/isolation). Choose a vendor for cloud commitments, procurement, or residency — not for features.

> ⚠️ **Reconcile with the newer class material (2026-07-19).** The Module 5 lesson describes **Claude in Amazon Bedrock** (Messages API at `/anthropic/v1/messages`) as having **broad feature parity** with the first-party API, with a **features-not-supported list** to check per feature — a softer claim than "feature gaps exist." Both can be true: parity is broad, gaps are specific. **Treat any specific gap (caching behavior, Files API, betas) as something to verify against the Bedrock docs at build time**, not as a memorized fact. The exam-safe generalization is unchanged: **the first-party API typically gets new features first, and platform choice is a procurement/compliance decision.** Full treatment → [Deployment and Versioning](#deployment-and-versioning--where-the-workload-runs-and-what-ships).

## Software Engineering Foundations (7.4%)

_Second-largest skill on the exam, behind only Claude Application Design. Expanded 2026-07-27; error families and SDK behavior verified against docs.claude.com the same day._

The framing to hold: **an LLM application is an ordinary distributed system that happens to call a probabilistic API.** Almost every item in this skill is a normal engineering practice applied to a component whose output varies — the AI part changes *what you assert*, not *whether you engineer*.

### REST and HTTP

The Claude API is **REST + JSON over HTTPS**, one endpoint (`POST /v1/messages`) with features expressed as request parameters. Two structural properties drive most design consequences:

| Property | Consequence |
|---|---|
| **Stateless** | No server-side conversation. You resend the full `messages` array every turn; session state is yours to store. Context growth is therefore *your* bug to manage, not the API's |
| **Versioned by header** | `anthropic-version` pins the wire contract; new event types and `stop_reason` values are added under that policy — code must tolerate unknown values |

**The error family** — memorize the split, not just the numbers:

| Code | Meaning | Retry? | Typical cause |
|---|---|:--:|---|
| `400` | Invalid request | ❌ | Malformed body, bad parameter, unsupported feature for that model, prompt too long |
| `401` | Authentication | ❌ | Missing/invalid/revoked key; both `ANTHROPIC_API_KEY` and an auth token set at once |
| `403` | Permission | ❌ | Key lacks access to that model or feature |
| `404` | Not found | ❌ | Typo'd or retired model ID, wrong endpoint |
| `413` | Request too large | ❌ | Body over the size limit (e.g. a >256 MB batch, oversized images) |
| `429` | Rate limited | ✅ | RPM / ITPM / OTPM exceeded — honor `retry-after` |
| `500` | Server error | ✅ | Anthropic-side fault |
| `529` | Overloaded | ✅ | Capacity — back off, or shift load to a less-contended model |

🚨 **The rule the exam tests: retry the transient class, fix the permanent class.** Retrying a `400` re-sends the same broken request forever. And ⚠️ **the SDKs already retry** transient failures with exponential backoff (default 2 attempts) — wrapping your own loop around them **multiplies** attempts against the rate limit rather than capping them.

⚠️ **HTTP status is not the whole story.** A **refusal is HTTP `200`** with `stop_reason: "refusal"`, and a **stream can carry an error event** (e.g. `overloaded_error`) after a `200` header. A classifier that branches only on status code silently mishandles both → [Errors, retries, and rate-limit headers](#errors-retries-and-rate-limit-headers-verified-2026-07-19) above.

### JSON and schema-first thinking

- **Schema-first.** Define the shape you need before you prompt for it. Tool `input_schema` and structured-output schemas are contracts — `additionalProperties: false` plus an explicit `required` list is what makes validation meaningful.
- **Defensive parsing.** Model output is untrusted input until it validates. Parse, don't string-match; handle the failure path → [D6 · Output Handling](../domain-6-prompt-context/notes.md).
- ⚠️ **Never string-match a serialized tool input.** Tool-call `input` may differ in JSON escaping (Unicode, forward slashes) between models. Parse it into an object and read fields.
- 🚨 **Unstable key ordering silently breaks prompt caching.** Serializers in several languages don't guarantee order (and iterating a set is worse). Caching is an **exact prefix match**, so a re-ordered JSON blob in the cached prefix produces a full-price miss with **no error** — the only symptom is `cache_read_input_tokens` sitting at zero. Sort keys deterministically.

### Async programming and concurrency

Three things that get conflated on exam stems, and the signal that separates them:

| Pattern | What it is | Reach for it when |
|---|---|---|
| **Concurrency** | Many independent requests in flight at once (async client, connection pooling) | Throughput on realtime traffic; each caller still waits for its own response |
| **Streaming** | One request whose response arrives incrementally as SSE | A user is watching, or `max_tokens` is large enough to risk an HTTP timeout |
| **Batching** | One asynchronous job of many requests, ~50% cost, up to 24h | Nobody is waiting; volume is high and latency-tolerant |

⚠️ **Concurrency is not batching.** Firing 1,000 parallel realtime requests is still realtime pricing and will hit rate limits; the Batch API is a different endpoint with different economics → [Realtime vs. batch](#realtime-vs-batch--the-classic-exam-tradeoff) above.

⚠️ **Claude streaming is SSE, not websockets** — one-directional, over the same HTTP request → [D5 · Technical Fundamentals](../domain-5-model-selection/notes.md).

**Concurrent requests can't read each other's cache.** A cache entry is only readable once the first response *begins*, so N parallel requests with the same prefix all pay full price. Fan-out pattern: send one, wait for first token, then fire the rest.

### Version control and SDLC integration

🔑 **Prompts, evals, tool schemas, and model pins are source code.** Treat them that way or you lose the ability to explain a behavior change:

| Artifact | In the repo | Why |
|---|---|---|
| **Prompts** | ✅ Versioned files, not database rows or console edits | A prompt change is a behavior change; you need diff, blame, and rollback |
| **Eval sets** | ✅ | The regression suite for a non-deterministic component |
| **Model version pin** | ✅ | An unpinned alias makes every upstream model update an **untracked change to your output** → [Deployment and Versioning](#deployment-and-versioning--where-the-workload-runs-and-what-ships) |
| **Tool schemas / configs** | ✅ | Changing a tool description changes tool selection — that's a code change |
| **API keys** | ❌ Never | Environment or secrets manager → [D7 · Identity, Secrets, and Key Management](../domain-7-security/notes.md) |

**Code review applies to prompt changes.** A one-word edit to a tool description can flip which tool the model selects; a reviewer who waves through "just a prompt tweak" is waving through a behavior change.

**CI runs the evals.** This is the LLM-specific SDLC step: because output is non-deterministic, a unit test asserting exact strings is the wrong instrument. The gate is an **eval scored against criteria**, run in CI, on the same cases that justified the current configuration → [D4 · Evals](../domain-4-eval-testing/notes.md).

⚠️ Exam trap: "we tested it manually and it looked good" is never the right answer for promoting a prompt or model change. The right answer names an **eval set** and a **measured comparison**.

### Refactoring

Behavior-preserving change, backed by tests that prove the behavior was preserved.

| Scale | Examples | What makes it safe |
|---|---|---|
| **Small** | Rename, extract function, inline variable | A test suite that already covers the touched paths |
| **Large** | Module boundaries, dependency swaps, codebase modernization — a stated Claude Code use case | Characterization tests **first**, then change; the tests are what distinguish a refactor from a rewrite |

🚨 **Refactoring without tests isn't refactoring — it's rewriting and hoping.** When the stem describes an agent or assistant making sweeping changes to unfamiliar code, the missing control is almost always *tests that would catch a behavior change*, not more review.

| | |
|---|---|
| **Handles well** | Everything above is ordinary engineering discipline — it transfers directly, and most of it is what makes an LLM app operable at all |
| **Adds cost or complexity** | Non-determinism means the usual assertion style doesn't work; you pay for eval sets and criteria-based grading instead of cheap exact-match tests |
| **Use a different approach** | When the failure is in *what the model produced* rather than *how you called it*, the fix is prompt/context/schema work, not more retry logic → [D4 · Debugging](../domain-4-eval-testing/notes.md) |

### AI-assisted code review — triage, don't apply

_Source: class module "Claude Code, MCP & Integration" (recorded 2026-07-19). Review sheet: [`capstone-claude-code-mcp-integration.md`](../capstone-claude-code-mcp-integration.md) takeaway 2._

> 🔑 **An AI code review produces a set of findings to triage, not a verdict to apply.** The reviewer writes every finding in the same confident register, so severity language is not evidence. The triage question is: **does the evidence for this claim exist in the artifact the reviewer was actually given?**

| Finding type | Example | How to treat it |
|---|---|---|
| **Provable from the diff** | A file handle opened and never closed on the error path; a missing null check; an unhandled branch | **Trust it — and confirm on the lines it cites.** The evidence is in front of you. |
| **Claim about runtime behavior or another system** | "This will deadlock under concurrent load"; "this breaks the billing service" | **Hypothesis to test.** The reviewer had no runtime trace and no cross-service context — it inferred. |

**Two design decisions around the reviewer:**

1. **Place the human gate where a finding becomes a hard-to-reverse action** — an auto-applied fix, a merge, a blocked deploy. Reading findings is cheap; acting on them is where the cost lands. (Same worst-case-cost logic as [D1 · HITL insertion points](../domain-1-agents/notes.md), and it applies whether the reviewer runs interactively or unattended in CI.)
2. **Raise accuracy by supplying what it would otherwise guess** — project conventions, naming rules, error-handling patterns. In Claude Code that's [`CLAUDE.md` / rules files](../domain-3-claude-code/notes.md); on the API it's the system prompt. A reviewer left to infer conventions from surrounding code will flag *your* house style as a defect and miss violations of it.

**Exam angle:** the distractor is an option that applies both a provable finding and an inferred one because both were stated with equal confidence — or that rejects both pending independent human re-derivation (over-correction; the provable one is checkable in seconds). Severity ranking is another trap: **a high-severity claim with no evidence is still a hypothesis.**

## Claude Application Design (8.6%) — single biggest skill on the exam

### Instruction interpretation across interfaces
The same instruction lands differently depending on surface:

| Surface | Where instructions live | Notes |
|---|---|---|
| **API/SDKs** | `system` parameter | Full developer control; nothing implicit |
| **Claude Code** | CLAUDE.md hierarchy + settings.json + slash commands | Instructions persist across sessions; hierarchy merges |
| **claude.ai / Desktop** | Project instructions, preferences, styles | Anthropic's own system prompt is also present |

Instructions in `system` (or CLAUDE.md) carry more authority than text inside user content. Design so trusted instructions and untrusted data never share a channel.

### Content boundaries
- Separate **trusted instructions** from **untrusted input** (user text, retrieved documents, tool outputs) with explicit structure — XML tags are the Claude convention (`<document>`, `<user_input>`).
- Untrusted content should be *described as data* ("summarize the text in `<document>`") — never allowed to act as instructions. This is the design-level defense against prompt injection (ties to D7).

### Schema design
- Define output structure up front: structured outputs / tool schemas beat "please respond in JSON" prose. Keep schemas flat and typed; validate on receipt.
- **Structured outputs = constrained decoding**: `output_config.format` constrains the response; `strict: true` constrains tool inputs. Worked code + edge cases in `structured-outputs-examples.md`.
- For tools: precise names, thorough descriptions, constrained parameter types (ties to D8).

### Session hygiene
- Long sessions accumulate stale context → drift and contamination. Start fresh sessions per task; use compaction/context editing deliberately; don't let debugging detours pollute a working session.
- Statelessness means *you* control what history is resent — prune aggressively.

### Plugin management
- Plugins bundle MCPs, skills, and commands. Treat as dependencies: review what they add to context, least privilege for what they can touch, remove unused ones (context cost is real).

## Configuration Management (4.1%)

- **CLAUDE.md hierarchy** (Claude Code): enterprise/managed → user/global (`~/.claude/CLAUDE.md`) → project root → subdirectory. More specific levels add to or override broader ones; a checked-in project CLAUDE.md shares conventions with the team.
- **settings.json**: scoped similarly (user vs. project vs. local); controls permissions, hooks, model defaults, environment.
- **Model version pinning**: aliases (latest) auto-upgrade — convenient in dev, risky in prod. **Pin dated snapshots in production**; upgrade deliberately after running evals, because behavior changes across releases can break prompts (ties to D5).
- **Prompt versioning**: prompts are artifacts — version them, tie eval results to prompt+model version pairs, roll back like code.
- **Plugin dependencies**: pin/review plugin versions like any dependency; a plugin update can change model-visible context and silently alter behavior.

---

## Packaging for Reuse — turning a working build into an accelerator

> **Central idea:** a build that runs is not yet an asset. **Packaging for reuse** means separating engagement-specific code from the reusable core and **parameterizing the rest**, so the next engagement *configures* the asset instead of rewriting it. The exam judgment is the **asset-type choice** — agent template vs. MCP server package vs. eval suite — plus what must be **parameterized, documented, and bundled for audit** in each case.

_Source: class module "Packaging for Reuse" (Module 5, first lesson; recorded 2026-07-19). Sits on **Systems Life Cycle** (2.8%) and **Configuration Management** (4.1%); the asset types themselves route to D1, D8, and D4._

### What an accelerator is

An **accelerator** is a solution packaged so future engagements start from a working foundation rather than a blank repository. Take a build that works, pull out the customer-specific values, and expose them as **parameters with documented defaults**.

**Why timing matters:** package while the build is fresh. Reconstructing intent months later — after the person who knew *why* a value was hardcoded has moved on — costs far more than documenting it now. This is the same rationale as writing the [design document](../domain-4-eval-testing/notes.md) before the code: capture intent at the moment it exists.

### The three asset types — each packages differently

| Asset type | What it bundles | What correct packaging requires | Mechanics live in |
|---|---|---|---|
| **Agent template** | The system prompt, tool schemas, and loop structure of a working agent | Pull domain-specific values into **configuration with documented defaults**, so a new team **sets values rather than editing the loop** | [D1 · Agent Construction](../domain-1-agents/notes.md) |
| **MCP server package** | The tools the server exposes, their inputs, and the **scope the installing team controls** | **Document each tool input** and let the installing team **set the scope**, so it installs into a new environment **without code edits** | [D8 · Building and Configuring an MCP Server](../domain-8-tools-mcps/notes.md) |
| **Eval suite** | The graded test set **and** the judge rubric that prove the asset works | Ship **dataset and rubric together** so a new team can run them **in their own context** and confirm the asset still works there | [D4 · Evals and Judges](../domain-4-eval-testing/notes.md) |

🔑 **The eval suite does double duty.** It is both the portable proof that the asset works *and* the **deployment gate**: when you promote a new model version to production, run it against a **pinned baseline score** before the version goes live. That is the missing enforcement half of [model version pinning](#configuration-management-41) above — pinning tells you *what* runs; the baseline tells you whether the *next* thing may.

### The wrong approach the exam will offer

**Shipping the agent as a set of loose scripts instead of a template.** The scripts run, so they *look* reusable — but every customer-specific value is buried in a different file. The next team **copies and diverges** them instead of configuring one asset. Reaching for the wrong asset type makes work look reusable while remaining hard to apply.

### Document the assumptions, not just the behavior

Code describes behavior. Documentation covers **what a future builder cannot infer from reading the source**:

- the **assumptions** the asset makes about its environment
- the **inputs** it expects
- the **failure modes** it already handles
- the **eval** that defines whether it still works

Without these, the next team treats the asset as a black box and rebuilds it — the exact outcome packaging exists to prevent.

### Bundle the audit log as part of the package

A regulated customer's reviewer asks three questions: **what data does the asset touch, what identity does it act under, and what log does it leave?** An accelerator without answers passes a demo and **stalls at the first security review**. Treat the audit log as a shipped component, not an operational afterthought (ties to [D7 · least privilege and identity](../domain-7-security/notes.md)).

### The packaging checklist

Each column is a decision made **once per asset**.

| Asset type | Parameterize | Document | Bundle for audit |
|---|---|---|---|
| **Agent template** | Every per-customer value: prompts, paths, scopes, **credentials by reference**, thresholds | Environment assumptions, expected inputs, handled failure modes, the eval that defines "working" | Data touched · identity acted under · log of what it did |
| **MCP server** | Scopes, **credentials by reference**, per-customer paths | Expected inputs **per tool**, scope boundaries, handled failure modes | Data touched · identity acted under · log of what it did |
| **Eval suite** | Thresholds, dataset paths that change per customer/environment | Rubric logic, what the scores mean, the **baseline** the asset is pinned to | Data touched · identity acted under · log of what it did |

Note "credentials **by reference**" — the parameter names a secret; it never carries the secret value. Same rule as [D7 · secrets management](../domain-7-security/notes.md).

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Parameterizing while the build is fresh turns one delivery into an asset the next engagement configures in **hours**. |
| **Adds cost or complexity** | Separating generalizable from customer-specific parts and documenting assumptions adds **real time to the first build**. |
| **Use a different approach** | For a **one-off the customer will never reuse**, packaging overhead isn't worth it — ship the build and move on. |

**Exam angle:** the stem describes a build that works and a second engagement arriving. The distractors are (a) *"ship the scripts, they already run"* — reusable-looking, unconfigurable; (b) *"rewrite it generically for all future customers"* — over-generalization on a one-off; (c) *"document it later, after delivery"* — the intent-decay trap. The correct answer names the **asset type that matches what's being reused** and parameterizes the customer-specific values. When the scenario adds a **regulated** customer, the audit bundle (data · identity · log) becomes part of the right answer.

---

## Contributing Back — from private reuse to shared infrastructure

> **Central idea:** the packaged asset is already most of the way there. **Contributing back** moves it from private reuse into shared infrastructure through a **documented channel**, so a team that never spoke to you installs it and gets the same working setup. The exam judgment is two gates in order: **channel match first, then acceptance** — and **rights and attribution clear before technical review**.

_Source: class module "Contributing Back" (Module 5, second lesson; recorded 2026-07-19). Direct sequel to [Packaging for Reuse](#packaging-for-reuse--turning-a-working-build-into-an-accelerator) above; same skills (Systems Life Cycle 2.8% · Configuration Management 4.1%)._

### Packaging already did most of the work

The three things you produced for internal reuse map straight onto what a maintainer needs:

| What packaging produced | What it proves to a maintainer |
|---|---|
| **Parameters** | The asset can be **configured**, not rewritten |
| **Documented assumptions** | What **environment** the asset expects |
| **Bundled eval** | A way to **confirm it still works** |

The contribution channel carries the **version, installation steps, and components as a single unit** — that's what lets a stranger install it and land on the same working setup.

### Match the contribution to the channel built for it

Each channel is built for a specific kind of contribution.

| Channel | Built to receive |
|---|---|
| **Claude Cookbook** (GitHub repo of focused reference implementations) | A **self-contained single- or multi-pattern implementation**, demonstrated clearly and working end to end |
| **Open-source MCP servers and tools** (each its own repo, its own conventions) | A tool, a server, or a fix — following **that repo's** contribution conventions |

🔑 **The named mismatch:** sending a **full multi-component application to the Cookbook**. The repo is set up to review *one focused pattern*, not an entire application — a submission that large doesn't fit what reviewers look for and **stalls**. Putting a full application where a focused example belongs is **one of the most common reasons a contribution never gets reviewed**.

### What makes verifying a contribution possible

A maintainer accepts what they can **verify**. The bar is set by what they need to check, not by how clever the code is:

1. **The code does one thing.** A sprawling contribution forces a reviewer to reconstruct your intent before evaluating it.
2. **An example shows it running.** A reviewer should not have to build a harness to see the behavior.
3. **A test proves it works.** A test lets a maintainer verify the result without reproducing the reasoning themselves.
4. **A short statement names the assumptions.** Otherwise the first failure becomes the maintainer's problem.

Note the pairing: **example + test**, not a description of the behavior. A README claiming the pattern works is not the bar.

### Rights and attribution come *before* technical review

Licensing and attribution decide whether a contribution **can be accepted at all** — which is why they gate ahead of the code review. Code carried in from a customer engagement may have constraints on where it can go.

- **Confirm you have the right to contribute it.**
- **Attribute anything you built on.**

Skipping this turns a contribution into a problem the **legal team must unwind later**.

⚠️ **When a licensing constraint can't be cleared, do not contribute — escalate to the owner.** This is the module's "use a different approach" case, and it's the answer the exam will hide behind three plausible technical fixes.

### The contribution-readiness reference

| Channel | What a maintainer checks | Licensing and attribution | The example and test bar |
|---|---|---|---|
| Cookbook for a **focused example**; the tool's or server's **own repo** for a tool or fix | That the code **does one thing** and that they can **read it in full** | Confirm the **right to contribute** engagement code, with **prior work attributed** | A **runnable example** plus a **test that proves the behavior** — not just a description of it |

### The worked case

A reusable **conversation-handling pattern** built during a customer service agent engagement: strip the customer specifics, prepare it as a **general example for the Cookbook**. Note what got contributed — the *pattern*, not the application.

The contribution-back motion is shared across all three roles in the curriculum. **The Developer's job is technical readiness**: the focused code, the example, the test, the assumptions, and the rights check. Engagement context comes from the broader team — don't answer as if the Developer owns the customer relationship.

### Tradeoff summary

| | |
|---|---|
| **Handles well** | A packaged asset needs only the **example, test, and rights check** to become shared infrastructure others build on. |
| **Adds cost or complexity** | Clearing the **maintainer bar** and the **licensing gate** is real work **on top of** making the code run for you. |
| **Use a different approach** | When engagement code carries a **licensing constraint you cannot clear**, do not contribute it — **escalate to the owner**. |

**Exam angle:** the stem describes a working, packaged asset and a desire to share it. Distractors are (a) *"send the whole application to the Cookbook"* — channel mismatch, the top stall cause; (b) *"the code is clean, so it's ready"* — skips the example/test bar; (c) *"clear licensing after the maintainer approves it"* — inverts the gate order; (d) *"strip the license header to avoid the attribution question"* — makes it worse. The correct answer **matches the channel to the contribution type** and clears **rights before** technical review.

---

## Deployment and Versioning — where the workload runs and what ships

> **Central idea:** a packaged or contributed asset is **merely code until something runs it**. Two decisions turn it into a deployment: **where it runs** (the platform — decided mostly by the customer's existing cloud, identity, and compliance posture, *not* by technical merit) and **how the version is locked** (pin the model, prompt, and asset so an **upstream change never becomes an untracked production change**).

_Source: class module "Deployment & Versioning" (Module 5, third lesson; recorded 2026-07-19). Sequel to [Packaging for Reuse](#packaging-for-reuse--turning-a-working-build-into-an-accelerator) and [Contributing Back](#contributing-back--from-private-reuse-to-shared-infrastructure). Skills: **Configuration Management (4.1%)** + **Systems Life Cycle (2.8%)**, with the platform half touching **Claude API Mechanics (6.8%)**._
>
> ⚠️ **Most version-sensitive material in the repo.** Model names, hosting forms, and API-surface details below are as stated in class on **2026-07-19**. Confirm at `platform.claude.com` and the partner's own docs at build time — the class itself says to.

### The customer's cloud usually decides the platform

The **deployment platform** is the environment where the Claude workload runs. The same model runs in several environments; the first question is **which platform the customer already trusts and operates on** — where they already have cloud infrastructure, identity management, and compliance agreements.

| Environment | What it is |
|---|---|
| **First-party Claude API** | Anthropic's own environment. **Typically receives new features first.** |
| **Claude Platform on AWS** | Accessed **through the customer's AWS account**, but using **Anthropic's own model IDs and lifecycle**. Inference is **Anthropic-operated, outside the AWS boundary**. |
| **Claude in Amazon Bedrock** | **Messages API** at `/anthropic/v1/messages`, **broad feature parity** with the first-party API. A features-not-supported list exists — confirm feature-specific requirements against the Bedrock docs. |
| **Claude on Amazon Bedrock (legacy)** | The older **`InvokeModel` / `Converse`** APIs with **ARN-versioned** model identifiers. |
| **Google Vertex AI** | The same motion inside **Google Cloud**. |
| **Third-party platform** (e.g. **Microsoft Foundry**) | Claude **embedded inside a product the customer already uses**. |

🔑 **Microsoft Foundry has two hosting forms** — and they answer residency differently:

| Hosting form | Models (as stated 2026-07-19) | Where inference runs |
|---|---|---|
| **Hosted on Azure** | Claude Opus 4.8, Claude Sonnet 5, Claude Haiku 4.5 — **generally available** | End-to-end on **Azure** infrastructure |
| **Hosted on Anthropic** | **All other** Foundry Claude models | **Anthropic-operated** infrastructure |

For a regulated customer, **residency assumptions depend on the hosting form of the specific model**. Confirm the hosting form and the current model split **with Microsoft at build time**.

### Identity and residency are answered by the platform, not your code

- **Bedrock** → AWS identity; data stays inside the **customer's AWS boundary**.
- **Vertex** → Google Cloud identity, IAM, and boundary.
- Both offer **regional routing** when residency is a constraint.
- **Claude Platform on AWS** is the exception to read carefully: it goes *through* the AWS account but inference is **Anthropic-operated outside the AWS boundary** — so it is **not** the same residency story as Bedrock.

**Matching the platform to the customer's existing compliance agreement avoids a data-residency review from scratch.** That is the actual argument for platform choice on the exam — not features, not latency.

_Cross-reference: the regulation-by-regulation table lives in [D1 · notes](../domain-1-agents/notes.md) (HIPAA / GDPR / FedRAMP routes) and retention/ZDR in [D7 · notes](../domain-7-security/notes.md)._

### Pin the version so an upstream change isn't a silent production change

Every Claude model ID points to a **specific model snapshot**. Aliases (`Opus`, `Sonnet`) are convenient but **evolve over time** and **may resolve to different versions across deployment platforms**. A pinned full model ID resolves to a **fixed snapshot**.

```python
# Pre-4.6 example: a convenience alias can resolve to a new
# version without you knowing
model = "claude-haiku-4-5"

# Pre-4.6 pinned snapshot: the version is fixed until you change this line
model = "claude-haiku-4-5-20251001"
```

> **Convention shift (stated in class 2026-07-19):** for **Claude 4.6 and later**, the **model ID alone pins** to a specific snapshot; for **earlier models**, the ID **plus a date suffix** is required. Verify the current convention at `platform.claude.com` at build time.

The full versioning discipline is three moves, in order:

1. **Pin the specific model version**, not the alias → an upstream model update becomes a **deliberate choice**, not a silent production change.
2. **Version the prompt and the asset alongside the code** — the model is only one of the three things that can shift the output.
3. **Keep the prior version available** so a regression can be **rolled back**.

⚠️ **An unpinned deployment makes every upstream model update an untracked change to your output.** That sentence is the whole lesson.

### Promote a version through the eval

**Gate promotion on the eval suite.** Send a new version to **a portion of traffic**, compare against the **pinned baseline**, and **promote or roll back on the result**.

This is where the [portable eval suite](#packaging-for-reuse--turning-a-working-build-into-an-accelerator) stops being a one-time test and becomes the **deployment gate** — the enforcement half of the pinning rule. (Same idea as lifecycle phase 5; see [Gates](#gates--where-a-regulated-engagement-keeps-control).)

### The deployment-platform decision table

| Platform | Identity and data model | When to choose it | How versioning is pinned |
|---|---|---|---|
| **First-party Claude API** | Anthropic identity and terms. | Customer has **no binding cloud or residency constraint** and wants the **newest capabilities**. | Pin the **full model ID**; keep the prior snapshot. |
| **Claude Platform on AWS** | Anthropic identity and terms, accessed **through the customer's AWS account**; inference **Anthropic-operated, outside the AWS boundary**. Lifecycle follows **Anthropic's** deprecation schedule. | Customer is **on AWS** but wants **Anthropic model IDs, lifecycle, and feature parity** with the first-party API. | Same model ID format as the Claude API (e.g. `claude-opus-4-8`). Lifecycle on Anthropic's schedule. _(Confirm at build time.)_ |
| **Claude in Amazon Bedrock** | **Messages API** at `/anthropic/v1/messages`; broad feature parity — confirm feature-specific requirements against Bedrock docs. Data stays in the **customer's configured AWS boundary**. | Customer is **on AWS**, wants broad parity with the 1P API, and holds a **compliance posture there**. | Pin the full model ID using the **`anthropic.` prefix** format. **Partner retirement dates differ from Anthropic's schedule.** |
| **Claude on Amazon Bedrock (legacy)** | AWS identity and billing; **`InvokeModel` / `Converse`** with **ARN-versioned** identifiers. | Customer is on an **existing Bedrock integration** that hasn't migrated to the Messages API. | Pin via **ARN-versioned model identifiers**, per Bedrock's versioning controls. |
| **Google Vertex AI** | Google Cloud identity, **IAM**, and billing; **regional or global endpoints** for residency. | Customer is **on Google Cloud** and holds a compliance posture there. | Pin the full model ID **before rollout**, in Vertex's model ID format. **Partner retirement dates differ from Anthropic's schedule.** |
| **Third-party platform** | The **wrapping product's** identity and billing. Foundry: **Hosted on Azure** (Opus 4.8 / Sonnet 5 / Haiku 4.5) vs. **Hosted on Anthropic** (everything else). | Customer **already runs the platform** that embeds Claude. | Pin per **that platform's** versioning controls. |

### Comparing platforms — latency, compliance, cost (class notes, 2026-07-19)

_Source: class module "Comparing Platforms" (Module 5, immediately after Deployment & Versioning). Sequel to the two screens above: you've **chosen a platform and pinned its version** — this is how you turn that placement into an argument **procurement and security will sign off on**. "Right for their cloud" is a starting point, not a defense._

**Latency — measure from the customer's region, not your laptop.**
Latency depends on **where the platform runs relative to the customer** and on **how access to new features is routed**. A platform running in the customer's own cloud region shortens the round trip versus a first-party endpoint sitting farther away. The trade-off is **timing of access**: the first-party API typically receives new capabilities **before** they reach other platforms.

- The number is only accurate when measured **from the customer's actual region against their actual payload**. A measurement from your laptop **hides the round-trip penalty** that appears once the workload runs where the customer is.
- **Bedrock specifically:** the choice between **global and regional endpoints** is the **primary residency control** *and* can **affect cost**. Measure from the customer's region **against both options** before committing.

**Compliance — usually the dimension that ends the debate.**
A customer who already holds a certification on one cloud is **unlikely to re-certify on another**. **Data residency** = a rule that the customer's data must be processed in a specific country or region. Available **certifications** and **who can audit access** differ by platform, and a regulated financial or healthcare customer treats these as **pass-or-fail, not tradeoffs to balance**.

- The **first-party Claude API may not offer EU data residency** — confirm current regional coverage at `platform.claude.com`. **EU-only residency typically requires Bedrock or Vertex AI.**
- On third-party platforms such as **Microsoft Foundry, hosting is per-model**: **Azure-hosted** Foundry models run inference end-to-end on Azure; **Anthropic-hosted** Foundry models **do not satisfy EU regional residency requirements**. Residency must be confirmed **per model and per deployment, with Microsoft**.
- **Raise the compliance constraint during scoping** — otherwise it surfaces at **contract review, after the work is done**.

**Cost — the per-token rate is not the total.**
Per-token rates are **broadly aligned across platforms**; total cost moves on **egress, platform fees, and integration effort**. A **lower token price can cost more in total** once data transfer and integration are factored in. **Instrument cost per call** for each platform and confirm the **current pricing pages at scoping**.

#### The cross-platform comparison reference

| Dimension | How it differs by platform | How to measure it | Where each platform wins |
|---|---|---|---|
| **Latency** | A platform in the customer's region shortens the round trip; the first-party API may reach **new features first**. | From the **customer's actual region** against their **actual payload**. | **In-region cloud platform** wins on round-trip latency; **first-party API** wins on earliest feature access. |
| **Compliance** | **Residency, certifications, and audit controls are determined by the deployment platform.** | Against the customer's **existing certification and residency requirements**, during **scoping**. | The cloud platform the customer has **already certified** — it needs **no re-certification**. |
| **Cost** | Token price, **data egress**, **platform fees**, and **integration effort** all vary. | **Total cost per call per platform**, including egress and integration — not token price alone. | The platform with the **lowest total cost for the actual workload** — **not always the cheapest token**. |

| | |
|---|---|
| **Handles well** | Measuring all three dimensions per platform turns a placement into one a **procurement team will sign off on**. |
| **Adds cost or complexity** | Instrumenting latency, compliance, and cost **across platforms requires real measurement work before any code ships**. |
| **Use a different approach** | When the customer's compliance requirement is **already pass-or-fail, skip the full comparison** — that constraint **determines the placement on its own**. |

**Exam angle:** the stem gives a platform already chosen "because it's their cloud" and asks what makes the choice defensible (→ measure all three dimensions from the customer's region), or gives an **EU-residency** requirement and asks which platform survives (→ Bedrock/Vertex; not the 1P API; Foundry only if the specific model is Azure-hosted), or offers **"the cheapest per-token rate"** as a distractor (→ egress + platform fees + integration decide the total). The inverse trap: when residency is already **pass-or-fail**, running the full three-dimension comparison is **wasted work** — the constraint has already decided.

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Matching the platform to the **customer's cloud** and pinning the version keeps a migration **reviewable** and a rollback **possible**. |
| **Adds cost or complexity** | Pinning, retaining prior versions, and gating promotion on the eval add **release-process overhead to every deployment**. |
| **Use a different approach** | For a **throwaway prototype that never touches production**, a **moving alias is fine** — pinning is for what ships. |

**Exam angle:** the stem gives a customer with an existing cloud/compliance posture and asks where to run, or gives a "the output changed and nobody deployed anything" symptom. Distractors are (a) *"pick the platform with the best benchmark/feature set"* — ignores that the customer's cloud and compliance agreement decide it; (b) *"use the alias so we always get the newest model"* — the untracked-change trap; (c) *"pin the model but leave prompt and asset unversioned"* — one of three; (d) *"promote after the eval passes in staging, no baseline comparison"* — misses **pinned baseline + partial traffic + rollback**; (e) *"Bedrock and Claude Platform on AWS are the same residency story"* — they are not.

---

## Multi-Component Applications — trust boundaries where components meet

_Source: class module "Trust Boundaries" (Module 5, final lesson; recorded 2026-07-19). Capstone of the Module 5 arc — [Packaging for Reuse](#packaging-for-reuse--turning-a-working-build-into-an-accelerator), [Contributing Back](#contributing-back--from-private-reuse-to-shared-infrastructure), [Deployment and Versioning](#deployment-and-versioning--where-the-workload-runs-and-what-ships), and [Comparing Platforms](#comparing-platforms--latency-compliance-cost-class-notes-2026-07-19) now come together in a single application. Skill: **Claude Application Design (8.6%)**, with the enforcement half in [D7 · Security and Safety](../domain-7-security/notes.md)._

### What a multi-component app is, and why it changes the security problem

A **multi-component app** coordinates more than one Claude capability into a single workflow. Canonical shape from the class: an **API request** triggers a **Claude Code task**, which reaches a **customer system through an MCP server**. Each component contributes a capability the others do not have.

What's different from a single deployment: **every connection between components creates a place where identity, secrets, and untrusted input can cross.** Connecting components doesn't add those places one at a time — it **multiplies** them.

> 🔑 The discipline in one line: **map which component does what *before* you connect anything.**

### The trust boundary is where data moves

**Definition:** a **trust boundary** is the point where data or instructions move **from one deployment environment to another**. It is exactly where the injection and access controls from [D7](../domain-7-security/notes.md) apply — the boundary isn't a new control, it's the *location* the existing controls attach to.

The concrete case: **content fetched by a Claude Code task is untrusted when it reaches the next component.** The receiving component treats it as **data, never as instructions** — the same principle used throughout the security material.

🚨 **The named trap: assuming a component is trusted because it worked correctly on its own.** Correct behavior in isolation says nothing about the seam. **Identify every seam as a boundary**, including the ones between components you built yourself.

### Least privilege applies to the whole application

Each component operates under **an identity**. You scope each component to the least privilege **its role in the workflow** requires — not the privilege the component *could* hold.

> 🔑 **The application is only as contained as its most privileged seam.** One component scoped too broadly becomes the weak point **even when every other component is properly scoped.**

This is the D7 blast-radius argument raised one level: least privilege is what keeps a **steered** component from reaching beyond its intended task, and at application scale the scope that matters is the widest one, not the average one.

### The multi-component integration map

| Component | What it contributes | The trust boundary at its seam | The control that enforces it |
|---|---|---|---|
| **First-party API** | Orchestrates the workflow; holds the entry point. | The **request entering the app from outside**. | **Input validation** + the **identity the call runs under**. |
| **Claude Code task** | Runs the agentic work; may **fetch external content**. | The **content it fetched**, which is untrusted downstream. | **Treat fetched content as data** at the next seam. |
| **MCP server** | Reaches a customer system to **read or act**. | The **system access it holds** on the app's behalf. | **Scope the server to least privilege** and **log the access**. |

Read the third column as the question to ask at each seam, and the fourth as the answer that must already exist in the design.

### Scoping for a regulated review — the module's synthesis

A regulated review requires justifying **audit logging, data-residency decisions, and permission controls across the full application** — not component by component. The reviewer's three questions from [D7](../domain-7-security/notes.md) are asked of the *whole* system.

- **Bedrock and Vertex AI** are typically the platforms that satisfy **regional residency** constraints (consistent with the platform comparison above).
- Confirm **ZDR** and **HIPAA BAA** eligibility **for each component** against the **Anthropic Trust Center** and **`platform.claude.com`** **before scoping** — eligibility varies by model and platform, so a multi-component app can fail on one component while passing on the others. _(Version-sensitive; verified 2026-07-19.)_

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Naming **every seam as a boundary** and scoping each component to **least privilege** is what makes a multi-component app **deployable under review**. |
| **Adds cost or complexity** | Mapping seams, enforcing a control at each, and **logging boundary crossings** adds **design and audit work to every integration**. |
| **Use a different approach** | 🚨 **When a seam cannot be secured, do not ship around it — escalate to a human owner.** (Same escalation shape as the licensing gate in [Contributing Back](#contributing-back--from-private-reuse-to-shared-infrastructure).) |

### Exam-style decision cues

| Cue in the stem | Answer |
|---|---|
| "each service was security-reviewed on its own, so the app is fine" | **Wrong** — a component being correct in isolation says nothing about the **seam**; every connection is a boundary |
| "where exactly is the trust boundary?" | Wherever **data or instructions move from one deployment environment to another** |
| "the Claude Code task fetched a page, then handed the result to the MCP server" | The fetched content is **untrusted at that seam** — the receiving component treats it as **data, not instructions** |
| "every component is least-privileged except one broad service account" | The app is **only as contained as its most privileged seam** — that one component is the exposure |
| "first step before wiring the components together" | **Map which component does what**, then name each seam, *then* connect |
| "regulated customer wants this multi-component app approved" | Justify **audit logging + data residency + permission controls across the full application** |
| "EU residency across a multi-component app" | Typically **Bedrock or Vertex AI**; confirm **ZDR / HIPAA BAA per component** at the **Trust Center** and `platform.claude.com` |
| "one seam can't be secured — ship with a compensating note?" | **No** — **escalate to a human owner** |

---

## Exam traps to remember
1. Batch discount is **50% off both input and output** — distractors will claim input-only or invented percentages.
2. Batch results are **unordered** — `custom_id` is the only safe join key.
3. Caching: **writes cost more than base** (1.25×/2×); only **reads** are 0.1× — "caching always saves money" is false for content used once.
4. Changing tool definitions invalidates the **entire** cache (top of the hierarchy).
5. `429` → backoff and retry; `400` → fix the request; retrying invalid requests is a distractor.
6. Vendor choice (Bedrock/Vertex/Foundry) is a procurement/infrastructure decision; features are **not** identical across vendors.
7. "Add a line telling the model to ignore malicious instructions" is never the right content-boundary answer — structure and separation are.
8. Streaming changes **perceived latency only** — not price, not the final output. And never act on a partial `tool_use` block: wait for `content_block_stop` to parse its JSON, and on a dropped stream **discard the partial turn** rather than committing it to history.
9. Image token cost scales with **pixels, not file size or file count** — `⌈w/28⌉ × ⌈h/28⌉`, one token per 28×28 patch; over-limit images are **downscaled first** (formula runs on scaled dimensions). "Compress the JPEG to save tokens" is a distractor — resize the pixel dimensions.
10. **User-facing + image ≠ batch.** Vision "works in batches," but an interactive upload where the user is waiting needs the **synchronous** API; batch (up to 24 h) is for offline, latency-tolerant volume only. Reaching for batch here is the classic latency-misread trap.
11. PDFs go in a **`document`** block (not `image`); `title`/`context` are **optional**, and there is **no required `name` field** — distractors invent a mandatory `name`.
12. **"The scripts run, so it's reusable" is false.** Loose scripts with customer-specific values scattered across files get **copied and diverged**, not configured. Reusability is a packaging decision (parameterize + document + bundle), not a property of working code.
13. **Packaging is not always right.** For a genuine one-off the customer will never reuse, the overhead loses — the exam does test the "ship it and move on" case. And never over-generalize a first build into a framework for hypothetical future customers.
14. A **portable eval suite ships dataset + rubric together**, and doubles as the **model-promotion gate** — a new model version runs against the **pinned baseline** before it goes live. Shipping the dataset without the rubric (or vice versa) is not a portable eval.
15. **Channel mismatch is the #1 reason a contribution never gets reviewed.** The Cookbook receives a **focused, self-contained example**; a full multi-component application sent there **stalls**. Tools and servers go to **their own repos**, under **those repos'** conventions.
16. **Rights and attribution gate *before* technical review, not after.** Any answer that reviews the code first and sorts out licensing later inverts the order. And when an engagement licensing constraint **cannot be cleared, the right move is escalate to the owner — not contribute anyway**.
17. **"The code is clean" is not the acceptance bar.** A maintainer needs to *verify*: one thing done, a **runnable example**, a **test that proves the behavior**, and a **short statement of assumptions**. A prose description of behavior does not substitute for the example + test pair.
18. **Platform choice is decided by the customer's existing cloud, identity, and compliance posture — not by technical merit or feature lead.** "Pick the platform with the newest features" is the distractor; matching an existing compliance agreement is what avoids a residency review from scratch.
19. **An alias is not a version.** `Opus`/`Sonnet`-style aliases **evolve** and can **resolve differently across platforms**; only a pinned full model ID is a fixed snapshot. Pin the **model, the prompt, *and* the asset**, and **keep the prior version** for rollback. Unpinned = every upstream update is an untracked change to your output. _(4.6+ pins by ID alone; earlier models need the date suffix — verify at build time.)_
20. **"Claude Platform on AWS" ≠ "Claude in Amazon Bedrock."** Platform-on-AWS runs through the customer's AWS account but inference is **Anthropic-operated outside the AWS boundary**, on **Anthropic's model IDs and deprecation schedule**. Bedrock keeps data in the **customer's AWS boundary** and has **partner retirement dates that differ from Anthropic's**. Legacy Bedrock = `InvokeModel`/`Converse` + ARN-versioned IDs.
21. **Promotion is partial traffic vs. a pinned baseline, then promote or roll back** — not "run the eval in staging and ship." And the exception is real: for a **throwaway prototype**, a moving alias is fine. Pinning is for what ships.
22. **Microsoft Foundry has two hosting forms** — *Hosted on Azure* (Opus 4.8 / Sonnet 5 / Haiku 4.5, inference end-to-end on Azure) and *Hosted on Anthropic* (all other Foundry Claude models). For a regulated customer, residency depends on **which form the specific model uses** — confirm with Microsoft at build time. **Anthropic-hosted Foundry models do not satisfy EU regional residency.**
23. **Latency measured from your laptop is not a latency measurement.** It hides the round-trip penalty that appears once the workload runs in the customer's region. Measure **from the customer's actual region against their actual payload** — and on Bedrock, against **both the global and the regional endpoint**, since that choice is the primary **residency** control *and* affects **cost**.
24. **The cheapest per-token rate is not the cheapest platform.** Per-token rates are broadly aligned; total cost moves on **egress, platform fees, and integration effort**. Instrument **cost per call**. "Platform X has the lowest token price" is a distractor.
25. **Compliance is pass-or-fail, not a tradeoff to balance** — and when it's already binding, the **full three-dimension comparison is wasted work**; the constraint decides the placement on its own. Corollary: **EU-only residency typically requires Bedrock or Vertex**, not the first-party API (verify current coverage at `platform.claude.com`).
26. **Raise the compliance constraint at scoping.** Surfaced late, it lands at **contract review — after the work is done.** Any option that defers residency/certification questions until after the build is the trap.
27. **A component that behaved correctly on its own is not a trusted component.** The exam offers "each service passed its own security review" as reassurance — the boundary is the **seam between** them, and it is unreviewed until someone names it.
28. **The application is only as contained as its most privileged seam.** Averaging doesn't apply: one over-scoped component defeats least privilege everywhere else. Scope each component to what **its role in the workflow** needs.
29. **Content fetched by one component is untrusted at the next component.** Data crossing from one deployment environment to another is where the D7 injection and access controls attach — the receiving component treats it as **data, not instructions**. And when a seam **cannot** be secured, **escalate to a human owner** rather than shipping around it.
