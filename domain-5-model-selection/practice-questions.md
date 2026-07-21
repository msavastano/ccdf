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
