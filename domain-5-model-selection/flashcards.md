# Domain 5: Model Selection and Optimization — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Model Selection and Tradeoffs

**Q:** What's the default starting model, and why start there?
**A:** Sonnet — the balanced default for most production workloads. Model choice sets the price/speed floor every later decision moves within, so start balanced and move deliberately.

**Q:** The four Claude tiers, cheapest/fastest to most capable?
**A:** Haiku (speed/cost), Sonnet (balanced default), Opus (demanding work above Sonnet's envelope), Fable (most capable — maximum-intelligence tasks).

**Q:** When do you move up from Sonnet to Opus?
**A:** Only when an eval set shows Sonnet isn't meeting your quality bar — not preemptively "to be safe."

**Q:** When do you move down from Sonnet to Haiku?
**A:** Only when an eval set shows the quality regression is acceptable for your task — not merely to save costs.

**Q:** Is "switch to Haiku to save money" a sound reason on its own?
**A:** No — every model move, up or down, is a measured, eval-backed decision. Cost savings without an eval showing acceptable quality is the wrong answer.

**Q:** Is choosing a bigger model the same decision as enabling extended thinking?
**A:** No — tier selection and whether to reason are separate axes. A mechanical task on Sonnet with a tight prompt often beats a reflexive jump to Opus.

**Q:** Cost management vs. model selection — what's the difference?
**A:** Cost management optimizes spend *within* a model; model selection sets the *baseline* that optimization works from. Caching can't rescue a workload on the wrong tier.

**Q:** Can a higher-tier model ever be faster and cheaper than a lower one?
**A:** Yes — if it reaches a conclusion in fewer tokens. Per-token price isn't per-request price; compare cost per *completed task*.

**Q:** What belongs in the trade-off calculation besides token cost?
**A:** The cost of a mistake. Saving a few dollars a day isn't sound if the quality drop introduces errors with significant downstream cost.

**Q:** What's the most common and most expensive model-selection mistake in production?
**A:** Reaching for the most capable model by default instead of making the trade-off measurable.

**Q:** Describe the default-plus-override routing pattern.
**A:** Route the bulk of traffic to a balanced default model; send specific request types to a larger or smaller model based on a cheap signal read from the request — task type, input length, or a difficulty classification.

**Q:** What does routing cost you?
**A:** A classification step and a second model path to maintain.

**Q:** When should you skip the router?
**A:** When traffic is uniform at one quality bar — pin a single model. Routing is justified by variance in request difficulty, not adopted by default.

**Q:** What triggers a step *up* a tier, specifically?
**A:** An eval showing the current model fails on the hardest cases your traffic actually contains, *and* a high cost of a wrong answer.

**Q:** What triggers a step *down* a tier, specifically?
**A:** An eval showing a cheaper model holds the quality bar on the bulk of traffic — freeing budget and latency.

**Q:** Does changing models require rewriting the application?
**A:** No — the same prompt runs on any tier, so model choice is a per-workload lever you can change freely. That's what makes eval-driven switching practical.

## Cost and Token Management

**Q:** What does prompt caching store, and what should you cache?
**A:** The processing done on a stable request prefix. Cache the rarely-changing parts — a long system prompt, the tool-definition set, a reference doc queried repeatedly.

**Q:** How do you enable prompt caching, and how many breakpoints?
**A:** Mark a cache breakpoint with a `cache_control` field of `type: "ephemeral"` on the last block to cache; up to four breakpoints.

**Q:** First cache request vs. later ones — the cost difference?
**A:** The first request writes the prefix to cache (full cost); later requests sending identical content up to that point pay a fraction of the original.

**Q:** What does `count_tokens` do, and what does it cost to run?
**A:** Takes the same request body as a Messages call and returns the token count without running inference — measure context pressure before a request rather than after it fails.

**Q:** Why count tokens during development specifically?
**A:** To verify the context budget holds against real tool outputs (3–5× bigger than fixtures), not just the small test inputs — the gap that sinks sessions in production.

### Cost & Orchestration — observability, cache economics, the reliability floor _(added 2026-07-19)_

**Q:** Which three metrics do you instrument on every call?
**A:** Token usage (input and output separately), latency, and error rate — per call and per dependency. The API already returns usage; latency is wall-clock around the call.

**Q:** Why instrument from day one instead of when costs spike?
**A:** It's a thin wrapper around the call at build time and a retrofit under incident pressure later. Without it the invoice arrives before the explanation.

**Q:** What question does per-call logging let you answer that a monthly total doesn't?
**A:** Which step, on which request type, is responsible — a sortable row instead of a guess. Flows that look uniformly expensive usually have one step doing ~90% of the spend.

**Q:** Cache write vs. cache read vs. ordinary input — the price multipliers?
**A:** Write 1.25× base input at the 5-min TTL, 2× at the 1-hour TTL; read ~0.1×; ordinary input 1×. (Version-sensitive — re-verify.)

**Q:** What single condition decides whether caching saves money?
**A:** Reads must outnumber writes. A prefix written once and read once is a loss.

**Q:** Automatic vs. explicit cache breakpoints — which is the recommended starting point?
**A:** Automatic: one cache flag at the top level of the request, breakpoints managed as the conversation grows. Explicit `cache_control` on a specific block is the manual alternative. Either way, content after the last breakpoint is processed normally.

**Q:** What is the consistency tradeoff caching carries?
**A:** The cache holds the prefix as it was written. If the prefix must reflect data that can change, it may be stale for the life of the cache — a window your use case must tolerate. Fixed system prompts and stable tool schemas have nothing to go stale.

**Q:** Streaming vs. batching — do they ever compete for the same request?
**A:** No. Streaming optimizes perceived latency for a user in the loop; batching optimizes the bill when no user is waiting. A request is either user-facing or it isn't.

**Q:** Which two levers compound on a scheduled job with a long fixed system prompt?
**A:** Message Batches (lower cost per request) plus prompt caching (cheap reads on the repeated prefix inside each request).

**Q:** What is a "reliability floor," and when do you define it?
**A:** A stated baseline — e.g. complete within 4 s, up to 3 retries on a failed dependency — defined **before** cost tuning. Every cost change must then clear it.

**Q:** Why must the floor come first rather than second?
**A:** Cost pressure is loud and daily; reliability failures look like dismissible noise until they accumulate into an incident. Optimize cost first and the louder pressure wins — you find the floor after crossing it.

**Q:** What makes a reliability floor enforceable rather than aspirational?
**A:** A pinned eval baseline score. Any cost-saving change that drops the score below baseline fails the gate before it ships.
