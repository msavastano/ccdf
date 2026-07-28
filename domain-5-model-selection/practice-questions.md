# Domain 5: Model Selection and Optimization — Practice Questions

Format per item: scenario stem · state how many responses to select · options A–D (or more for multiple-response) · tag (e.g., "D1 · Agent Architecture") · answer key + per-option rationale at the end of the file.

---

**Q1 · D5 · Model Selection and Tradeoffs** (select ONE)
**Where to start.** A team is building a new general-purpose production workload. They have no evaluation set yet and no measured quality or latency requirements beyond "good enough for users."
Which model should they start on, and why?

A. Opus, to guarantee the highest quality from day one
B. Sonnet — the balanced default for most production workloads; move off it only when an eval justifies the move
C. Haiku, because it's the cheapest and fastest
D. Fable, since the most capable model removes all quality risk

**Q2 · D5 · Model Selection and Tradeoffs** (select ONE)
**Justifying a downgrade.** To cut costs, a team wants to move a ticket-classification workload from Sonnet down to Haiku.
What must justify the move?

A. The projected cost savings alone
B. An eval set showing the quality regression on this specific task is acceptable
C. Haiku being the fastest model in the family
D. Nothing — smaller models are always adequate for classification

**Q3 · D5 · Cost and Token Management** (select TWO)
**Prompt caching for a multi-turn agent.** An agent sends a large, stable system prompt and a fixed set of tool definitions on every turn, followed by a short changing user message.
Which statements are correct?

A. Caching the system prompt and tool definitions once and reusing them across turns is the highest-leverage cost cut here
B. The first request writes the prefix to cache at full cost; later requests with an identical prefix pay a fraction
C. Prompt caching works by reducing the number of output tokens generated
D. You should place the cache breakpoint on the short user message, since that's what changes
E. You can set an unlimited number of cache breakpoints

**Q4 · D5 · Cost and Token Management** (select ONE)
**Preventing window-overflow errors.** A production service occasionally sends requests that exceed the context window and error out mid-run. The team wants to catch these before the request is sent.
What is the right approach?

A. Lower `max_tokens` so responses are shorter
B. Call `count_tokens` with the same request body first and gate any request that would exceed the window
C. Rely on the API to silently drop the oldest turns
D. Enable structured outputs so responses are constrained

**Q5 · D5 · Model Selection and Tradeoffs** (select ONE)
**Mixed-difficulty traffic.** A document-processing service handles two kinds of requests on one endpoint: short, formulaic field extractions (roughly 80% of volume) and long multi-document synthesis requests that currently fail quality review on the team's default model. Request type is trivially detectable from the payload. The team wants to hold the quality bar without paying top-tier prices on every request.
What is the best approach?

A. Move the entire endpoint to the most capable model so the hard requests always pass
B. Route on request type — keep the default model for the bulk of traffic and override to a more capable model for the synthesis requests
C. Move the entire endpoint to the cheapest model and add prompt caching to offset the quality drop
D. Keep the current model and increase `max_tokens` on the synthesis requests

**Q6 · D5 · Model Selection and Tradeoffs** (select ONE)
**When routing is the wrong answer.** An internal service classifies support tickets. Every request has the same shape, the same length, and the same quality bar, and an eval shows one mid-tier model clears that bar on the full test set. An engineer proposes adding a difficulty classifier that routes hard tickets to a larger model.
What is the strongest objection?

A. Routing is never appropriate for classification workloads
B. The traffic is uniform at one quality bar, so the router adds a classification step and a second model path that buy nothing
C. Difficulty classification can only be done by the same model that answers the request
D. Routing would invalidate the existing prompt cache on every request

**Q7 · D5 · Model Selection and Tradeoffs** (select TWO)
**Reading the trade-off correctly.** A team is debating a downgrade to a cheaper tier for an agentic workflow that writes results into a system of record.
Which statements about the cost/latency/quality trade-off are correct?

A. A higher-tier model can be faster and cheaper on a request if it reaches a conclusion in fewer tokens than a lower tier would
B. The cost of a mistake belongs in the trade-off calculation alongside token spend
C. Lower per-token price reliably means lower cost per completed task
D. Upgrading a tier always increases latency
E. Because there is a globally correct model tier, the trade-off only has to be evaluated once per organization

**Q8 · D5 · Model Selection and Tradeoffs** (select ONE)
**What gates a model change.** A team wants to promote a model change from their default tier to a more capable one for a production workload.
What should the change be promoted on?

A. A measured score on an eval set built from their own cases, showing the current model failing the hardest cases their traffic contains
B. Vendor benchmark results published for the newer model
C. A week of production traffic on the new model with subjective spot-checks by the team
D. The observation that the more capable model is the safer default

**Q9 · D5 · Cost and Token Management** (select ONE)
**The bill arrived without an explanation.** A team's monthly Claude spend tripled. Their application runs a six-step flow, and they log only the total request duration and a success/failure flag per request.
What is the most useful change to make first?

A. Switch the whole flow to a cheaper model tier and watch whether the bill drops
B. Instrument every call with input tokens, output tokens, latency, and error rate, so the spend attributes to a specific step and request type
C. Enable prompt caching on all six steps
D. Move the flow to the Message Batches API

**Q10 · D5 · Cost and Token Management** (select TWO)
**Caching that costs more than it saves.** A support tool builds a 3,000-token prefix containing a system prompt plus **the current ticket's status line**, then marks a cache breakpoint after it. Requests for a given ticket arrive roughly once an hour. The team reports that caching increased their bill.
Which explanations are correct?

A. The prefix includes per-request data, so it never matches exactly and every request pays the write premium instead of a read
B. Under the 5-minute default TTL, an hourly request arrives after expiry, so writes are repeated with no read benefit
C. The prefix is below the minimum cacheable length, so no caching occurred at all
D. Cache reads cost more than ordinary input tokens, so a high hit rate raises the bill
E. Caching cannot be combined with a system prompt

**Q11 · D5 · Cost and Token Management** (select ONE)
**Choosing the lever by workload shape.** Two workloads run on the same application. **(1)** A chat feature streams answers to a user waiting on screen. **(2)** A nightly job re-classifies 400,000 archived documents against a fixed taxonomy using an identical 8,000-token system prompt on every request.
Which assignment of levers is correct?

A. Streaming for (1); Message Batches **plus** prompt caching for (2), since the batch discount and the cache read price compound on a repeated prefix
B. Message Batches for both, since batching always lowers cost
C. Streaming for both, since streaming reduces cost per request
D. Prompt caching for (1) and streaming for (2)

**Q12 · D5 · Cost and Token Management** (select ONE)
**Optimizing below the floor.** A user-facing endpoint has a stated requirement: complete within 4 seconds, with up to 3 retries on a failed dependency. To cut costs, an engineer proposes reducing retries from 3 to 2 on a slow dependency, noting the savings are real and no user has complained.
What is the correct evaluation?

A. Accept it — the savings are measured and no complaints have been filed
B. Reject it if it pushes the failure rate past what the stated floor allows; the floor is the fixed constraint, and cost is optimized underneath it
C. Accept it, then raise the latency ceiling to 6 seconds to compensate
D. Reject all cost optimizations on user-facing paths, since reliability always outranks cost

**Q13 · D5 · Cost and Token Management** (select ONE)
**Why the floor is set first.** Why does the order — reliability floor first, cost optimization second — matter in production?

A. Because reliability changes are harder to deploy than cost changes
B. Because a high bill is visible daily and generates constant pressure, while reliability problems appear as dismissible noise until they accumulate into an incident — so optimizing cost first lets the louder pressure win
C. Because cost cannot be measured until reliability is instrumented
D. Because the cheapest configuration is usually also the most reliable, so the floor is satisfied automatically

---

## Answer Key & Rationale

**Q1: B.**
- A — Jumping to Opus "to be safe" spends more without evidence Sonnet falls short; the move up should be eval-driven. ✗
- B — Sonnet is the balanced default; you start there and change tier only on evidence — an eval showing Sonnet misses the bar (move up) or that a regression is acceptable (move down). ✓
- C — Moving to Haiku requires an eval showing the quality regression is acceptable for the task; "cheapest and fastest" alone isn't a basis. ✗
- D — "Most capable" doesn't remove quality risk and over-spends on latency and cost with no evidence it's needed. ✗

**Q2: B.**
- A — Cost savings are the *motivation*, not the *justification* — a downgrade still has to clear a quality check. ✗
- B — Move down only when an eval set shows the quality regression on that specific task is acceptable. The decision is measured, not assumed. ✓
- C — Speed is a property of Haiku, not evidence that quality holds on this workload. ✗
- D — "Always adequate" is exactly the untested assumption the eval exists to check. ✗

**Q3: A and B.**
- A — The stable system prompt and tool schemas are the ideal cache prefix; caching them once and reusing across turns is the biggest available cost reduction for this shape of session. ✓
- B — The first request pays to write the prefix to cache; subsequent requests with identical content up to the breakpoint pay a fraction. ✓
- C — Caching reuses processing on a stable input **prefix**; it doesn't change how many output tokens are generated. ✗
- D — You cache the **stable** prefix and place the breakpoint on the last stable block — not on the part that changes every turn. ✗
- E — You can place up to **four** cache breakpoints, not unlimited. ✗

**Q4: B.**
- A — `max_tokens` caps output length; it doesn't stop an oversized **input**/context from exceeding the window. ✗
- B — `count_tokens` takes the same request body and returns a token count without running inference, so you can gate a request before it errors with `model_context_window_exceeded`. ✓
- C — The API does not silently drop old turns; managing history is the application's job. ✗
- D — Structured outputs constrain response shape, not context size. ✗

**Q5: B.**
- A — Upgrading the whole endpoint pays top-tier prices on the 80% of traffic that doesn't need it — the "reach for the most capable model by default" mistake, applied wholesale. ✗
- B — This is the default-plus-override pattern: a cheap signal (request type, already trivially detectable) routes the minority of hard requests to a more capable model, so you pay for capability only where it's needed. ✓
- C — Caching reduces the cost of tokens already in the window; it does nothing for a quality drop on the synthesis requests, which are already failing review. ✗
- D — `max_tokens` caps output length. It doesn't add the capability the synthesis requests are missing. ✗

**Q6: B.**
- A — Too broad. Routing is fine for classification workloads *with* difficulty variance; the objection here is about this traffic, not the task type. ✗
- B — Routing is justified by variance in request difficulty. With uniform traffic at one quality bar and an eval showing one model clears it, the router adds a classification step and a second path to maintain for no benefit — pin the single model. ✓
- C — Routing signals are deliberately cheap — task type, input length, or a small classifier. There's no requirement that the answering model do the classification. ✗
- D — Routing doesn't inherently invalidate caching; caches are per-model prefixes and a router changes which model a request reaches, not whether its prefix is stable. ✗

**Q7: A and B.**
- A — Per-token price isn't per-request price. A higher tier that concludes in fewer tokens can finish faster and cheaper; compare cost per *completed task*. ✓
- B — Saving a few dollars a day isn't a sound trade if the quality drop introduces errors with significant downstream cost — especially acute here, where results are written to a system of record. ✓
- C — This is exactly the assumption A refutes: a cheap model that flails, retries, or over-explains can cost more end-to-end. ✗
- D — Upgrading *usually* increases latency, not always — see A. ✗
- E — There is no globally correct choice, only the right choice for a task at a quality standard. The trade-off is evaluated per workload. ✗

**Q8: A.**
- A — The eval is the instrument in both directions: a model change is promoted on a measured score against your own cases, and a step up specifically requires evidence the current model fails the hardest cases your traffic actually contains. ✓
- B — Vendor benchmarks aren't your traffic and don't measure your quality bar; they can motivate a test but can't gate the change. ✗
- C — Subjective spot-checks in production aren't a measured score, and testing in production risks the very errors the gate exists to prevent. ✗
- D — "More capable is safer" is the default-to-the-biggest-model reflex — the most common and most expensive model-selection mistake in production. ✗

**Q9: B.**
- A — Changing the model before you know which step spends the money is guesswork, and it risks a quality regression to fix a cost problem you haven't localized. Identify the lever *before* pulling it. ✗
- B — Per-call instrumentation of token usage, latency, and error rate turns "why is the bill high?" into "which step, on which request type, is responsible" — a row you can sort. Flows that look uniformly expensive usually have one step doing ~90% of the spend. ✓
- C — Caching helps only where a long, stable prefix recurs inside the TTL. Applied blindly to all six steps it can add write premiums with no reads. ✗
- D — Batches suit non-urgent scheduled work. Nothing in the stem says the flow is offline, and batching a user-facing path breaks it. ✗

**Q10: A and B.**
- A — The cache is matched on an exact prefix. A per-ticket status line inside the cached region means no request ever matches a prior one, so every request pays the write premium (1.25× base input at the 5-min TTL) and never earns a read at 0.1×. ✓
- B — Reads must outnumber writes for caching to pay. At hourly arrivals under the 5-minute default, the window expires before the next request — the write cost repeats with no read benefit, strictly worse than not caching. (A 1-hour TTL exists but writes at 2×, so it must be justified by the same arithmetic.) ✓
- C — 3,000 tokens clears the 1,024-token minimum for most current models. (Note this failure mode is real and *silent* — just not what's happening here.) ✗
- D — Cache reads are ~0.1× base input — far cheaper. Hits are the saving; the problem is that this design never gets one. ✗
- E — A long system prompt is one of the two canonical caching targets, alongside a large tool schema. ✗

**Q11: A.**
- A — A request is either user-facing or it isn't, and that decides the lever. Streaming improves perceived latency for (1); (2) is scheduled, high-volume, and reuses an identical long prefix, so the batch discount lowers each request and the cache read price lowers the repeated prefix inside it. The two compound. ✓
- B — Batches return within an asynchronous completion window — wrong for anyone waiting on screen. ✗
- C — Streaming changes perceived latency only. It does not change cost or output content. ✗
- D — Reversed on both counts, and caching offers little to a short interactive turn with no stable long prefix. ✗

**Q12: B.**
- A — "No complaints yet" is not a measurement. Reliability problems surface as occasional failures that look like noise — exactly the pressure asymmetry the floor exists to resist. ✗
- B — The floor is defined first and treated as fixed; every cost change must demonstrate it did not trade reliability away. Trading retries for savings when it raises the failure rate past the floor is exchanging a visible expense for silent failures. ✓
- C — Moving the ceiling to accommodate a saving is redefining the floor to pass the test — the discipline the floor exists to prevent. ✗
- D — Overcorrection. Cost optimization above the floor is expected — e.g. a cheaper tier that still fits the latency ceiling without burning the retry budget is fine. ✗

**Q13: B.**
- A — Deployment difficulty isn't the reason; the asymmetry in how the two problems *present* is. ✗
- B — Cost pressure is loud and daily; reliability failure is quiet and cumulative. Set the floor first and reliability becomes the fixed constraint with cost optimized underneath — otherwise you discover the floor only after crossing it. A pinned eval baseline is what makes the floor checkable rather than asserted. ✓
- C — Both are instrumented from the same per-call metrics; neither blocks the other. ✗
- D — The opposite — the cheapest configuration is rarely the most reliable, which is why the floor has to be stated rather than assumed. ✗

---

## Supplement A — Technical Fundamentals (6.1%) and LLM Fundamentals (5.2%)

_Added 2026-07-27 to close blueprint coverage: these two skills together are 11.3% of the exam and had no items. Sourced from `notes.md` and docs.claude.com (verified 2026-07-27). Model IDs, pricing, and beta flags are version-sensitive._

**Q14 · D5 · Technical Fundamentals** (select ONE)
**What the SDK actually is.** A team is scoping a Claude integration in Python. An engineer argues they should call the REST endpoint directly with `requests`, because "the SDK is a limited convenience layer and won't expose newer features like batch processing or prompt caching."
What is the correct response?

A. The SDK wraps the same REST API, and features like batching and caching are parameters or endpoints available through it — the concern is unfounded, and the SDK adds auth resolution, retries, timeouts, streaming accumulation, and typed errors for free
B. The engineer is right — the SDKs lag the REST API by a full release cycle, so raw HTTP is the correct default for production
C. Both approaches should be used in the same codebase, calling the SDK for simple requests and raw HTTP for anything newer
D. Raw HTTP is required because the SDK cannot set custom headers

**Q15 · D5 · Technical Fundamentals** (select ONE)
**A retry loop on top of a retry loop.** A service using the official SDK wraps every call in a custom loop that retries up to 5 times on any exception. Under load, the team sees far more requests reaching the API during rate-limit periods than they expected.
What is the most likely explanation?

A. The SDK already retries transient failures automatically, so the two loops multiply — the custom loop's attempts each expand into the SDK's own attempts
B. The SDK disables its own retries whenever an outer exception handler is present
C. Rate-limit errors are not retried by the SDK, so the custom loop is the only retry path
D. Exponential backoff increases total request volume by design

**Q16 · D5 · Technical Fundamentals** (select ONE)
**Which failures are worth retrying.** A service logs a burst of `400 invalid_request_error` responses after a deploy. The on-call engineer adds them to the retry policy alongside `429` and `529` "so transient issues self-heal."
What is wrong with this?

A. A `400` means the request itself is invalid, so an identical retry reproduces it exactly — retrying burns quota and delays discovery of the real defect
B. Nothing — retrying `400`s is standard practice as long as backoff is applied
C. `400`s should be retried, but only without backoff
D. `400`s are transient on the Claude API and usually succeed on the second attempt

**Q17 · D5 · Technical Fundamentals** (select ONE)
**Choosing a transport for streamed responses.** An architect is designing a chat feature and proposes a websocket connection to the Claude API "so tokens can stream and the client can send interrupts on the same channel."
What is the correct assessment?

A. The Messages API streams over server-sent events on the same HTTP request and does not offer a websocket transport — SSE fits because a request produces one streamed response, with nothing needing to travel client-to-server mid-response
B. Websockets are supported and are the recommended transport for any streaming workload
C. Websockets are supported, but only for the Batch API
D. Streaming requires a websocket; SSE is used only for non-streaming responses

**Q18 · D5 · Technical Fundamentals** (select ONE)
**A long generation that never returns.** A job requests a very large `max_tokens` value without streaming, and the SDK refuses the request rather than sending it.
What is the reason, and the correct fix?

A. Large non-streaming generations risk exceeding HTTP timeouts and dropping the connection; stream the request and use the SDK's final-message helper to still receive one complete message object
B. Large `max_tokens` values are rejected by the API itself; lower it below the model's output ceiling
C. The SDK requires streaming for every request over 1,000 tokens, and there is no way to opt out
D. The request needs the Batch API, which is the only path for large outputs

**Q19 · D5 · Technical Fundamentals** (select TWO)
**Reading a stream correctly.** A team is writing a direct SSE integration rather than using an SDK helper, and wants to report token usage and assemble tool calls.
Which TWO statements are correct?

A. Token counts reported in `message_delta` events are cumulative, so summing them across events double-counts usage
B. Tool-use input arrives as partial JSON string deltas that must be accumulated and parsed once the content block stops — the final `input` is an object, never the partial text
C. Each `content_block_delta` reports the tokens consumed by that delta alone, so the total is their sum
D. Tool-use input arrives as a single complete JSON object in one delta event
E. Errors never appear inside a stream; any failure surfaces as a non-200 HTTP status before streaming begins

**Q20 · D5 · Technical Fundamentals** (select ONE)
**Matching on tool input.** A harness decides what to execute by checking whether the raw serialized tool-call input contains the substring `"mode": "write"`. It works in testing but occasionally misroutes in production after a model upgrade.
What is the defect?

A. Serialized JSON escaping can differ between models, so raw string matching is unreliable — parse the input into an object and read the field
B. Tool inputs are encrypted in production and cannot be inspected
C. The tool input is only available after the tool executes
D. Substring matching is correct; the real problem is that `tool_choice` was not set

**Q21 · D5 · Technical Fundamentals** (select TWO)
**Timeout behavior.** A team ports a working Python integration to TypeScript. They copy the client configuration, including a timeout value of `60`, and set `max_retries` to 3. In production the TypeScript service fails almost every request instantly, and an unrelated service occasionally blocks far longer than its configured timeout.
Which TWO statements explain what they are seeing?

A. Timeout units differ by SDK — Python takes seconds while TypeScript takes milliseconds, so `60` became 60 milliseconds
B. Timeouts are themselves retried, so worst-case wall-clock is roughly the timeout multiplied by the number of attempts, not the timeout alone
C. TypeScript clients ignore the timeout setting entirely and use a fixed 10-minute value
D. Setting `max_retries` above 2 disables the timeout
E. A timeout is terminal and never retried, so wall-clock can never exceed the configured value

**Q22 · D5 · Technical Fundamentals** (select ONE)
**Where conversation state lives.** A developer building a multi-turn assistant assumes the API retains conversation history between requests and sends only the newest user message each turn. Users report the assistant has no memory of anything said earlier.
What is the correct explanation?

A. The Messages API is stateless — there is no server-side conversation, so the full `messages` array must be resent every turn, and session state is the application's responsibility
B. Conversation history is retained but expires after five minutes, so the requests arrived too late
C. History is retained only when prompt caching is enabled
D. History is retained only on the Batch API

**Q23 · D5 · Technical Fundamentals** (select ONE)
**Why jitter.** A fleet of workers all implement plain exponential backoff with no randomization. After a rate-limit event, the team observes repeated synchronized bursts of `429`s rather than a smooth recovery.
What is the fix?

A. Add randomized jitter to the backoff so retrying clients spread out instead of colliding on the same schedule
B. Shorten the base delay so retries clear the queue faster
C. Remove backoff entirely and retry immediately
D. Increase the retry count so more attempts land inside the rate-limit window

**Q24 · D5 · Technical Fundamentals** (select ONE)
**A failure a status-code classifier misses.** A service classifies outcomes purely by HTTP status: `2xx` means success, everything else routes to error handling. Occasionally a request returns `200` but the application stores an empty result, and no alert fires.
What is the most likely cause?

A. The response carried a non-standard `stop_reason` such as a refusal — the request succeeded at the HTTP layer while producing no usable content, so the classifier must inspect `stop_reason`, not just the status
B. The API returns `200` with an empty body whenever it is overloaded
C. The client library strips content from responses over a size threshold
D. A `200` always indicates usable content, so the bug must be in the storage layer

**Q25 · D5 · Technical Fundamentals** (select ONE)
**Volume without a waiting user.** A nightly job must process 200,000 documents before morning. An engineer proposes issuing them as 200,000 concurrent realtime requests using an async client and a large connection pool, "since concurrency is how you get throughput."
What is the strongest objection?

A. Nothing is waiting on these results, so the Batch API fits the workload — it is priced substantially lower and tolerates the available turnaround, while mass concurrency still pays realtime rates and will collide with rate limits
B. Async clients cannot issue more than a few hundred concurrent requests
C. Concurrency and batching are the same mechanism, so the choice does not matter
D. Realtime requests cannot be used for document processing

**Q26 · D5 · Technical Fundamentals** (select ONE)
**Surviving an API update.** A stream handler uses a `switch` over event types with no default branch, and a separate `switch` over `stop_reason` values that raises on anything unrecognized. After a model release, the service starts crashing on a fraction of requests.
What practice would have prevented this?

A. Handle unknown event types and stop reasons gracefully — new values are added under the API's versioning policy, so an exhaustive match with no fallback is a latent failure
B. Pin the `anthropic-version` header, which prevents any new event types from ever being sent
C. Disable streaming, which removes event-type variability entirely
D. Retry the request, since unknown event types are transient

**Q27 · D5 · LLM Fundamentals** (select ONE)
**Estimating tokens before sending.** A team needs to know whether a prompt will fit before issuing the request. An engineer adds `tiktoken` to the project, noting it is fast, local, and free.
What is wrong with this?

A. `tiktoken` is OpenAI's tokenizer and materially undercounts Claude tokens — worse on code and non-English text; the correct instrument is the `count_tokens` endpoint, called with the same model ID used for inference
B. `tiktoken` is accurate for Claude but too slow for production use
C. Nothing is wrong — token counts are standardized across model providers
D. Token counts cannot be estimated in advance by any means; you must send the request and read `usage`

**Q28 · D5 · LLM Fundamentals** (select ONE)
**Migrating to a newer model.** A service pins a model version and has carefully tuned `max_tokens`, compaction triggers, and cost dashboards against measured token counts. The team upgrades to a newer model in the same tier and begins seeing responses truncated mid-answer.
What is the most likely cause?

A. Tokenization is model-specific, so the same text can produce a materially different token count on the new model — budgets calibrated on the old one must be re-measured, not scaled by a guessed multiplier
B. Newer models always require the Batch API for long outputs
C. Truncation indicates a rate-limit problem, not a token-count problem
D. `max_tokens` was deprecated in the newer model and is now ignored

**Q29 · D5 · LLM Fundamentals** (select TWO)
**What fills the window.** A team is auditing why an agent hits context limits far earlier than their arithmetic predicted. They had counted only the user and assistant messages.
Which TWO statements are correct about what consumes the context window?

A. Tool definitions consume window space from the first request, before any tool is ever called
B. The model's own output for the turn counts toward the window, including its thinking tokens
C. Tool definitions are stored server-side and do not consume context
D. Thinking tokens are billed but do not occupy the context window
E. Images and documents are processed out-of-band and do not count toward the window

**Q30 · D5 · LLM Fundamentals** (select ONE)
**A caching misconception.** An agent is approaching its context limit. An engineer proposes enabling prompt caching on the large system prompt and tool schemas, arguing this will "free up window space since cached content no longer takes up context."
What is the correct assessment?

A. Caching changes what you pay for those tokens, not whether they occupy the window — the cached prefix still counts, so this does not address the limit; compaction or context editing does
B. Correct — cached prefixes are excluded from the context window
C. Correct, but only when the one-hour TTL is used
D. Caching increases context consumption, so the proposal makes the problem worse

**Q31 · D5 · LLM Fundamentals** (select ONE)
**More context, worse answers.** A retrieval-backed assistant is upgraded to a model with a much larger context window. The team responds by raising the retrieval limit from 5 passages to 60, reasoning that more context can only help. Answer accuracy measurably drops.
What best explains this?

A. Accuracy and recall degrade as the window fills — curating what goes into context matters as much as how much room remains, so the fix is tighter retrieval rather than more of it
B. Larger context windows are slower but never less accurate, so the regression must come from the model change alone
C. Retrieval passages are not counted toward context, so the change had no effect on the model
D. The assistant exceeded the window and silently dropped the oldest passages

**Q32 · D5 · LLM Fundamentals** (select ONE)
**Three ways a long request can end.** An engineer is writing error handling and needs to distinguish between an input that is too long to send, an output that ran out of window mid-generation, and an output that hit the requested cap.
Which mapping is correct?

A. Input alone over the window returns a `400` before anything runs; generation reaching the window limit ends with `stop_reason: "model_context_window_exceeded"`; generation reaching the requested cap ends with `stop_reason: "max_tokens"`
B. All three produce `stop_reason: "max_tokens"` and are indistinguishable
C. All three return `400` errors and none produce a `stop_reason`
D. Input over the window is silently truncated from the oldest message forward, so no error is raised

**Q33 · D5 · LLM Fundamentals** (select ONE)
**A test that fails intermittently.** A CI suite asserts that a summarization call returns an exact expected string. It passes locally and fails roughly one run in four. An engineer proposes setting `temperature` to 0 to make the output deterministic.
What is the correct assessment?

A. Sampling makes identical requests capable of producing different outputs, and `temperature` at 0 reduces variance without guaranteeing identical results — the fix is to grade against criteria in an eval rather than assert exact equality
B. Setting `temperature` to 0 guarantees byte-identical output and fully resolves the flakiness
C. The flakiness indicates a network fault, and retries will resolve it
D. Exact-match assertions are correct; pinning the model to a dated snapshot will make the test pass consistently

**Q34 · D5 · LLM Fundamentals** (select ONE)
**A parameter that stopped working.** After migrating a workload to a current-generation model, every request begins failing with a `400`. The request body is unchanged and includes `temperature` and `top_p` values the team tuned months ago.
What is the most likely cause and the correct fix?

A. Sampling parameters are removed on the newest models and are rejected — remove them from the request and steer the behavior they were tuning through prompting instead
B. The parameters are still supported but must now be nested inside `output_config`
C. The values fell outside the valid range after the migration, so clamping them to 0 through 1 will fix it
D. Both parameters may be sent, but only one at a time — sending either alone resolves the error

**Q35 · D5 · LLM Fundamentals** (select TWO)
**Evaluating fast mode.** A team with a latency-sensitive endpoint is considering fast mode and wants to understand what they would be buying.
Which TWO statements are correct?

A. Fast mode runs the same model at a higher output token rate — it is a latency lever, not a quality or capability lever
B. Fast mode carries premium pricing and has its own rate limit, separate from the standard pool for that model
C. Fast mode upgrades the request to a more capable model tier, which is where the speed gain comes from
D. Fast mode is available on every current model and on every platform Claude is offered through
E. Fast mode is the recommended default for all production traffic, since latency always matters

**Q36 · D5 · LLM Fundamentals** (select ONE)
**Choosing how many examples.** An extraction prompt keeps producing output that is almost the right shape — correct fields, inconsistent formatting, and unpredictable handling when a field is absent from the source. The instructions already describe the format in detail.
What is the most effective next step?

A. Add a small number of worked examples, including at least one showing the missing-field case — examples demonstrate what instructions can only describe, and edge cases are exactly what they encode best
B. Rewrite the instructions at greater length, since the format is already described and only needs to be clearer
C. Move to a more capable model tier, since formatting consistency is a capability limit
D. Add fifty examples covering every case the team can enumerate

**Q37 · D5 · LLM Fundamentals** (select ONE)
**When examples are not enough.** A downstream service will reject any response that is not valid JSON matching a fixed schema, and a rejection triggers a costly manual review. The current prompt uses six few-shot examples and is right the vast majority of the time.
What is the correct approach?

A. Use structured outputs to constrain the response to the schema — examples make the correct shape likely, while a schema constraint is what makes it guaranteed
B. Add more few-shot examples until the failure rate reaches zero
C. Raise the model tier, which removes the need for schema enforcement
D. Keep the examples and retry any malformed response, since retries are cheaper than schema work

---

## Answer Key & Rationale — Supplement A

**Q14: A.**
- A — The SDK wraps the same REST surface, so anything the API supports is reachable through it, plus credential resolution, automatic retries, timeout defaults, stream accumulation, typed exceptions, and auto-pagination. ✓
- B — The SDKs are generated against the same API specification and are the documented default; there is no release-cycle lag that justifies raw HTTP as a general policy. ✗
- C — Mixing both in one codebase is explicitly discouraged: you lose the SDK's retry, timeout, and error semantics on half the calls and double the surface to maintain. ✗
- D — Custom headers are supported through the client, so this is not a limitation that forces raw HTTP. ✗

**Q15: A.**
- A — The SDKs retry connection errors and transient status codes with exponential backoff by default. An outer loop of 5 wrapping an inner policy of 2 does not cap attempts, it multiplies them. Configure `max_retries` instead of adding a second loop. ✓
- B — Nothing about an outer exception handler disables the SDK's internal retry policy. ✗
- C — Rate-limit responses are squarely in the class the SDK retries automatically. ✗
- D — Backoff spaces attempts out; it does not create additional ones. ✗

**Q16: A.**
- A — A `400` reports a defect in the request. The identical retry produces the identical failure, consuming quota and hiding the real bug behind retry noise. Fix the request. ✓
- B — Backoff changes timing, not the outcome of a deterministically invalid request. ✗
- C — Removing backoff makes it worse, not correct. ✗
- D — `400` is a terminal class on this API, not a transient one. ✗

**Q17: A.**
- A — Streaming uses server-sent events over the same HTTP request. The interaction is one request producing one streamed response, so a full-duplex channel would add infrastructure complexity for no capability. ✓
- B — There is no websocket transport for the Messages API to recommend. ✗
- C — The Batch API is asynchronous job submission and polling; it has no websocket transport either. ✗
- D — Reversed: SSE is the streaming mechanism. ✗

**Q18: A.**
- A — Idle connections on long non-streaming generations risk HTTP timeouts, so the SDKs refuse requests they estimate will exceed them. Streaming keeps the connection active, and the final-message helper accumulates events into the same complete message object a non-streaming call would return. ✓
- B — The value is within the model's supported output ceiling; the constraint is the HTTP connection, not the API's limit. ✗
- C — The guard is tied to estimated duration, not a fixed small token count, and it can be overridden with an explicit timeout. ✗
- D — Batching addresses latency tolerance and cost, not the HTTP timeout on a single long generation. ✗

**Q19: A and B.**
- A — Usage figures on `message_delta` are cumulative; treating them as per-event increments and summing them produces inflated totals. ✓
- B — Tool input streams as partial JSON string fragments. Accumulate them and parse once the block closes; the assembled `input` is always an object. ✓
- C — Per-delta token attribution is not what these events report, which is the source of the double-counting bug described in option A. ✗
- D — Input arrives incrementally across multiple delta events, not as one complete object. ✗
- E — Errors can and do arrive as events inside an already-successful stream, which is why stream handling needs its own error path. ✗

**Q20: A.**
- A — JSON string escaping in tool-call input can differ across models, so a substring match on the serialized form is not stable. Parse into an object and read the field. ✓
- B — Tool inputs are returned in the response content and are directly inspectable. ✗
- C — The input arrives in the `tool_use` block precisely so the harness can decide what to execute before executing it. ✗
- D — `tool_choice` controls whether and which tool is selected; it does nothing about how the harness inspects the input. ✗

**Q21: A and B.**
- A — Timeout units are not uniform across SDKs: Python and Ruby take seconds, TypeScript takes milliseconds. A copied `60` becomes 60 milliseconds and fails nearly everything instantly. ✓
- B — A timed-out request is retried like other transient failures, so worst-case wall-clock is roughly the timeout times the number of attempts. Upstream deadlines must be sized against that product. ✓
- C — TypeScript clients honor a configured timeout; what differs is the default, not whether the setting applies. ✗
- D — Retry count and timeout are independent settings, and neither disables the other. ✗
- E — The opposite of B, and it is the assumption that makes the second symptom surprising. ✗

**Q22: A.**
- A — The API holds no conversation state. Every turn resends the full `messages` array, which is also why context growth and session storage are application concerns. ✓
- B — There is no server-side history to expire; the five-minute figure belongs to the default prompt-cache TTL, which caches processing, not conversation. ✗
- C — Caching reduces the cost of reprocessing a stable prefix you resend; it does not store the conversation for you. ✗
- D — The Batch API is equally stateless per request. ✗

**Q23: A.**
- A — Without randomization every client computes the same delays from the same event and retries in lockstep, colliding again. Jitter spreads the attempts across the window. ✓
- B — A shorter base delay increases collision frequency rather than removing the synchronization. ✗
- C — Immediate retry is the worst case of the same problem. ✗
- D — More attempts on a synchronized schedule amplifies the bursts. ✗

**Q24: A.**
- A — A refusal returns a successful HTTP status with `stop_reason: "refusal"` and no usable content, so a status-only classifier records it as a success. Inspect `stop_reason` before reading content. ✓
- B — Overload surfaces as `529`, or as an error event inside a stream — not as an empty successful body. ✗
- C — No client library silently strips content by size; oversized requests are rejected with `413` on the way in. ✗
- D — This is precisely the assumption the scenario disproves. ✗

**Q25: A.**
- A — No user is waiting and the deadline is overnight, which is the defining shape for batch: substantially lower cost with an asynchronous completion window. Mass concurrency pays full realtime rates and runs straight into rate limits. ✓
- B — Async clients can sustain high concurrency; the objection is economic and rate-limit-driven, not a client capability limit. ✗
- C — They are different mechanisms with different pricing and latency guarantees, which is the whole point of the choice. ✗
- D — Realtime requests are perfectly capable of processing documents; they are just the wrong economics here. ✗

**Q26: A.**
- A — New event types and stop reasons are added under the API's versioning policy, so exhaustive matching without a fallback branch is a latent break that fires on the next release. Handle unknown values gracefully. ✓
- B — The version header pins the wire contract but is explicitly not a guarantee that no new event types appear; the documented guidance is to tolerate them. ✗
- C — Disabling streaming removes one source of new values and leaves `stop_reason`, and it gives up streaming for an unrelated reason. ✗
- D — An unrecognized event type is a deterministic parsing gap, not a transient failure. ✗

**Q27: A.**
- A — `tiktoken` is OpenAI's tokenizer and undercounts Claude tokens substantially, with the error worst on code and non-English text. The `count_tokens` endpoint takes the same request body and returns a count without running inference — and must be called with the model you will actually use. ✓
- B — The problem is accuracy, not speed. ✗
- C — Tokenization differs by provider and even between model generations from one provider. ✗
- D — Pre-flight counting is exactly what `count_tokens` exists for. ✗

**Q28: A.**
- A — Tokenizers differ across model generations, so identical text can consume materially more tokens on the new model, pushing output past a `max_tokens` value that used to fit. Re-measure with `count_tokens` against the new model rather than applying a guessed scaling factor. ✓
- B — Nothing about a model upgrade forces the Batch API; batch is a latency and cost decision. ✗
- C — Rate limiting produces `429` responses, not truncated content. ✗
- D — `max_tokens` remains the enforced output cap; it is the calibration that went stale. ✗

**Q29: A and B.**
- A — Tool schemas are part of the request and consume window space from the first call, which is why large tool sets are a real context cost and why deferring or trimming them is a lever. ✓
- B — The turn's generated output counts toward the window, and thinking tokens are part of that output — a common source of the "my arithmetic said it would fit" surprise. ✓
- C — Tool definitions are sent with each stateless request, not held server-side. ✗
- D — Thinking tokens are billed as output and also occupy the window. ✗
- E — Images and documents are converted to tokens and counted; a request can even hit size limits before the token limit. ✗

**Q30: A.**
- A — Prompt caching changes the price of the cached prefix, not its occupancy. The tokens still count, so a context-limit problem needs compaction or context editing, not caching. ✓
- B — Cached prefixes are not excluded from the window; this is the specific misconception the item tests. ✗
- C — TTL affects how long the cache entry lives and what the write costs, never whether the tokens occupy the window. ✗
- D — Caching does not increase consumption either; occupancy is unchanged in both directions. ✗

**Q31: A.**
- A — Accuracy and recall degrade as the window fills, so filling a larger window indiscriminately can lower answer quality. What goes into context matters as much as how much room remains, which makes tighter retrieval the fix. ✓
- B — A larger window does not immunize a model against degradation from excess context. ✗
- C — Retrieved passages are ordinary message content and count fully. ✗
- D — Silent truncation of the oldest content is not this API's overflow behavior; overflow produces an error or a distinct stop reason. ✗

**Q32: A.**
- A — Three distinct outcomes with three distinct signals: an over-long input is rejected up front with a `400`; running out of window during generation ends the turn with `model_context_window_exceeded`; hitting your requested cap ends it with `max_tokens`. The remedies differ, which is why the distinction matters. ✓
- B — Collapsing them loses the information needed to choose between compacting the conversation and raising the cap. ✗
- C — Only the first case is an HTTP error; the other two complete successfully with a stop reason. ✗
- D — The API does not silently drop history on this surface. ✗

**Q33: A.**
- A — The model samples from a probability distribution, so identical requests can differ. Lowering temperature narrows the distribution without guaranteeing identical output, and on current models the parameter may not be accepted at all. Grade against criteria in an eval instead of asserting exact strings. ✓
- B — Determinism was never guaranteed at temperature 0 on any model. ✗
- C — Intermittent content variation is a property of sampling, not a network fault; retrying returns another sample. ✗
- D — Pinning removes model drift as a variable but does nothing about per-request sampling variation. ✗

**Q34: A.**
- A — Sampling parameters are removed on the newest models and rejected outright, which is exactly the shape of this failure: unchanged body, new model, immediate `400`. Delete them and steer through prompting. ✓
- B — They were not relocated into `output_config`; `effort` lives there, and it is a different control. ✗
- C — The failure is that the parameters are not accepted at all, not that the values are out of range. ✗
- D — The one-of-two restriction applies to older Claude 4 models; on the newest models neither is accepted. ✗

**Q35: A and B.**
- A — Fast mode runs the same model at a higher output token rate. Quality and capability are unchanged, which is why it belongs in the latency conversation alongside model tier and effort rather than in the quality one. ✓
- B — It is priced at a premium and draws on a dedicated rate-limit pool, so a `429` there does not mean the standard pool is exhausted. ✓
- C — No tier upgrade occurs; the speed comes from serving the same model faster. ✗
- D — Availability is narrow: a limited set of models, and the first-party API surface only. ✗
- E — It is a research-preview option with premium pricing and restricted availability, not a universal default; it also interacts badly with prompt caching if toggled per request. ✗

**Q36: A.**
- A — When instructions already describe the format and output is still almost-right, examples are the higher-leverage move: they demonstrate what prose can only describe, and the missing-field case is precisely the kind of edge condition examples encode well. ✓
- B — More prose describing a format that is already described is the approach that has already failed. ✗
- C — Formatting consistency at this level is a prompting problem, not a capability ceiling; a tier change costs more and probably does not fix it. ✗
- D — Examples occupy the window on every request and stop earning past a point, competing for attention with the actual request. A small set targeted at the failure mode beats fifty. ✗

**Q37: A.**
- A — When a malformed response carries real downstream cost, likely is not good enough. Structured outputs constrain the response to the schema, converting a probabilistic property into an enforced one. ✓
- B — Examples raise the probability but cannot drive it to a guarantee, and each one costs window space on every request. ✗
- C — A more capable model still samples, and still offers no schema guarantee. ✗
- D — Retrying is a fallback, not a control. It leaves the guarantee absent and adds latency and cost on every malformed response. ✗
