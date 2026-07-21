# Domain 4: Eval, Testing, and Debugging — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Debugging and Error Handling

**Q:** What's the first move when debugging a Claude agent — before touching code?
**A:** Localize the failure to a layer (schema, streaming, context, or memory). The layer fixes the fix class; a wrong fix at the wrong layer is the classic trap.

**Q:** How does *frequency* of failure help you localize the layer?
**A:** Every time on the same input → structural/schema (deterministic). Only sometimes, tied to network events → streaming (dropped stream). Only after several sessions → memory (accumulation).

**Q:** Name the four error classes and whether each is retryable.
**A:** Structural (400 — no), model-output (valid call/wrong content — no), transient (429/5xx/529/timeouts — yes, backoff+jitter), capacity (context window — no, trim first).

**Q:** Why is retrying an HTTP 400 never the fix?
**A:** Structural errors reproduce identically on retry. Fix how the request is built (message structure, block preservation, schema) — backoff is only for transient errors.

**Q:** Integration-layer vs. model-output bug — what's the distinction?
**A:** Integration-layer = your code around the model (assembly, pairing, retries, context); deterministic, fixed in code. Model-output = the model produced something valid-but-wrong; probabilistic, fixed upstream (schema/description/prompt) then validated.

**Q:** Quick diagnostic to tell integration from model-output failures?
**A:** Does it fail the same way every time (integration/structural) or only on some inputs (model-output)?

**Q:** Why must you debug agents from the transcript, not from status codes alone?
**A:** Agents fail across turns when components run together; most structural bugs are visible as a malformed message array (unpaired tool_result, stripped thinking, half-built tool_use). You need transcript-level tooling.

**Q:** Schema-layer bug signature and fix?
**A:** Systematically wrong tool selection while the loop is fine. Fix the tool description: state intent and an exclusion ("use for X; do NOT use for Y").

**Q:** Streaming-layer bug signature and fix?
**A:** Intermittent 400s correlated with dropped connections; the next turn is corrupted. Gate the commit on message_stop, keep all blocks, and discard a partial turn instead of committing it.

**Q:** Context-layer bug signature and fix?
**A:** Deterministic 400 right after a tool call (unpaired tool_result / invalid signature). Preserve the full assistant content array and pair every tool_use with its tool_result.

**Q:** Memory-layer bug signature and fix?
**A:** Works early, fails by session N as the window fills. Move transcripts to external storage and inject only a summary at session start.

**Q:** In the four-layer debug task, why are the streaming and context bugs "one defect seen twice"?
**A:** The broken assemble-and-commit step is the root; the unpaired tool_result is the symptom. Fixing the commit (keep all blocks, gate on message_stop) resolves the pairing error with no separate change.

**Q:** Which two invariants both break at the assemble-and-commit step?
**A:** Thinking carry-back (signed thinking blocks must be returned unmodified) and tool_use/tool_result pairing (the full assistant tool_use turn must be committed before its tool_result).

**Q:** Why won't fabricating an empty tool_result for a dangling tool_use fix a pairing error?
**A:** It injects invented data for a tool that never ran, corrupting the run. Fix the upstream commit so the real, complete assistant turn is present instead.

**Q:** Do either of the two context-window failures silently drop your oldest content?
**A:** No. One rejects before generation (validation error); the other returns stop_reason: model_context_window_exceeded. Trimming/summarizing history is your job, not the API's.

**Q:** Why won't isolated unit tests catch an agent bug that appears "three tool calls in"?
**A:** The bug lives in the cross-turn interaction (routing, context, message structure), not in any single tool function; only transcript-level, multi-turn testing surfaces it.

## Evals and Judges

**Q:** What is an eval, in one sentence?
**A:** A fixed set of input cases plus the expected behavior for each, run through the feature and graded — turning "done" from a feeling into a score you can track.

**Q:** Why write the eval *before* the feature?
**A:** It forces you to define success before implementation, so you can't rationalize whatever output the model happens to produce later.

**Q:** What are the four decisions a design document must state?
**A:** (1) Success criteria, (2) failure handling with each error marked retriable or terminal, (3) cost and latency budget plus the reliability floor, (4) the trust boundary and least-privilege scope.

**Q:** What does each design-doc decision become downstream?
**A:** Criteria → eval cases; failures → error paths; budget → instrumentation and the architecture check; trust boundary → the input treated as data and the action gated by a hook.

**Q:** Why is "summarize the thread" a bad success criterion?
**A:** It can't be graded. "A two-sentence summary that lists every action item and its owner" can — specific enough to check is the bar.

**Q:** Name the three grading methods and the output shape each fits.
**A:** Exact/string match → one correct form. Code-graded check → structured output with a validatable rule. LLM-as-judge → open-ended quality.

**Q:** Feature returns three capital cities as a JSON array in a different order than your reference. How does each grader score it?
**A:** Exact match scores 0 (characters don't align) though the answer is correct; a code grader that parses and checks membership scores it full marks.

**Q:** Why not just use an LLM judge for everything?
**A:** It's one extra API call per case (1,000 cases = 1,000 extra calls per run) and it's noisy. Where a code check suffices, the judge adds cost and variance for no gain.

**Q:** What's the common split between code graders and judges in practice?
**A:** Grade format and structure with code on every commit; reserve the judge for a slower, scheduled quality pass.

**Q:** What must a judge return besides the score, and why?
**A:** Strengths, weaknesses, and reasoning. Without them models drift to a safe middle number (~6) regardless of quality; reasoning first anchors the score to something specific.

**Q:** What does calibrating a judge mean?
**A:** Run it on cases a human already labeled and measure how often it agrees. Until agreement is measured, the score looks rigorous but means nothing.

**Q:** Judge agreement with human labels is low. What do you fix?
**A:** The rubric — tighten what each score means, add a good and a bad example, then re-measure. Don't just accept the scores.

**Q:** Bigger eval set with noisier automated grading, or a small hand-graded set?
**A:** Bigger. Coverage catches edge cases and coverage comes from volume; 20 cases with irregular inputs beat 3 carefully chosen ones.

**Q:** How do you scale up an eval set cheaply?
**A:** Have Claude generate more cases from a small labeled seed set, then spot-check the generated ones so the set stays honest.

**Q:** Why change only one component per eval iteration?
**A:** If you rewrite the prompt, add examples, and swap the model at once, a score change tells you nothing about which lever caused it.

**Q:** Why read per-case results instead of just the average?
**A:** A steady average can hide a change that fixed three cases and broke three others.

**Q:** A case fails. What does the failure *type* tell you?
**A:** Formatting failure → the prompt's output instructions. Factual failure on retrieved content → the retrieval step. Failure only on long input → context handling. That's what makes the next fix targeted.

**Q:** Is a first eval score of 2/10 a problem?
**A:** No — that's normal. The signal is whether the number rises as you change one lever at a time, not the absolute value.

**Q:** When should you skip the judge entirely?
**A:** When the output has a single fixed format — a code check alone is enough.

---

## Testing and tracing _(class module "Testing & Tracing", added 2026-07-19)_

**Q:** What does an eval give you, and what does it *not* give you?
**A:** It gives you what good looks like as a number. It does not tell you *where* a failure happened, and it can pass while something inside the workflow is broken.

**Q:** What does a unit test isolate, and what is it blind to?
**A:** One function on its own — a parser, a tool wrapper. It says nothing about how components fit together.

**Q:** What does a functional test check?
**A:** That one Claude call returns the expected *shape* for a given input — right fields, right types, parseable. It validates the call, not the system around it.

**Q:** Which test level do most silent production failures hide at, and why?
**A:** Integration. Each side of a handoff (e.g. retrieval → model call) can pass its own tests while the seam between them is broken.

**Q:** What does an end-to-end test catch that the others can't — and what can't it do?
**A:** It catches breaks that only appear when everything runs together. It can't localize the break, since it only sees the final result.

**Q:** Four test levels, narrowest to widest?
**A:** Unit → functional → integration → end-to-end. Narrow = fast and precise but blind to composition; wide = catches emergent breaks but slow and hard to localize.

**Q:** What does a trace record?
**A:** Each step of a run — the prompt, the tool calls, the intermediate outputs, and the timing.

**Q:** Tests vs. traces — what does each tell you?
**A:** A test tells you a failure *exists*. A trace tells you *which step* produced the bad result.

**Q:** An eval case fails and you have no trace. What's the practical cost?
**A:** You know something is wrong but not where — the difference between a five-minute fix and a day spent hand-tracing the workflow.

**Q:** Why does tracing make a change reviewable?
**A:** You can show the *step that moved*, not just the score that dropped.

**Q:** When can you skip the tracing layer?
**A:** When the flow is one call with one fixed output shape — a functional test plus a code-graded eval covers it. Tracing and four test levels are infrastructure you build and maintain.

**Q:** What does a retrieval router do, and what does it cost?
**A:** A cheap classification call reads the query and sends lookups to fetch-once and multi-part questions to agentic search — one small model call, far less than running iterative search on a query one fetch would have answered.

**Q:** When is a retrieval router *not* worth it?
**A:** When every query is the same shape — then hardcode the path that fits. The router earns its cost only on mixed traffic.

**Q:** What does defaulting everything to iterative search cost? To a static index?
**A:** Iterative everywhere → inflated cost and latency on simple lookups. Static index everywhere → shallow answers on questions that needed several passes.

## Production failure handling _(class module "Failure Handling — tool errors", added 2026-07-19)_

**Q:** The single test that classifies any production failure?
**A:** Would waiting and re-sending the *identical* request plausibly work? Yes → retriable. No → terminal.

**Q:** Which Anthropic API status codes are retriable?
**A:** 429 (rate limit), 529 (overloaded), and 5xx server errors — 500, 502, 503, 504.

**Q:** Which status codes are terminal?
**A:** 400 (bad request), 401 (auth), 403 (permissions), 404 (missing). The cause is in the request; time changes nothing.

**Q:** What does `529` mean, and what does it *not* mean?
**A:** Anthropic-side overload — retriable with backoff. It is **not** a rate-limit signal, so "slow your request rate" is the wrong fix.

**Q:** Why is misclassifying a terminal error as retriable worse than the reverse?
**A:** A wrongly-terminal failure fails loudly and gets fixed. A wrongly-retriable failure hammers the service and buries the real problem under a wall of identical retries — while burning retry budget and adding latency.

**Q:** Is a timeout retriable?
**A:** Usually yes — the work may just have taken longer than the client would wait. But *repeated* timeouts on expensive requests mean fix the request, not retry it.

**Q:** Default classification when you're unsure?
**A:** Terminal. Raise it. A loud failure gets diagnosed; a silent retry loop hides the cause.

**Q:** What do the Anthropic SDKs do about transient failures on their own?
**A:** They automatically retry with progressive delays, up to a configurable max attempts.

**Q:** Why is wrapping your own retry loop around the SDK a bug?
**A:** Two loops around one call *multiply* attempts against a rate limit instead of capping them. Pick one owner: SDK for transient + your code for fallbacks, or SDK retries off and you own the path.

**Q:** Which wins — `retry-after` or your exponential backoff?
**A:** `retry-after`. The service is telling you exactly when capacity returns; backoff with jitter is the fallback for when the header is absent.

**Q:** When a tool call fails, what must go back to Claude?
**A:** A `tool_result` with `is_error: true` and the error text — never a silent empty result.

**Q:** What breaks if a failed tool returns an empty result instead of `is_error`?
**A:** The model treats the empty result as valid data and reasons on top of it — producing a confident, wrong answer downstream instead of a visible failure.

**Q:** With `is_error` set, what can the model actually do?
**A:** React — try a different approach, ask for clarification, or stop.

**Q:** Is a tool error retriable?
**A:** It depends on the underlying cause — retry only if that cause is transient. Surfacing the error flag to Claude is required either way.

**Q:** What HTTP status does a refusal return, and why does that matter?
**A:** `200`, with `stop_reason: "refusal"`. A status-code-based retriable classifier will never catch it — you have to check `stop_reason` explicitly.

**Q:** Correct handling for a refusal?
**A:** Fail fast — raise it to the caller and log it. It's a content decision, not a transient error; never silently retry or treat it as valid output.

**Q:** Fallback behavior after a `429` retry cap is exhausted?
**A:** Raise a clean error or route to a cached / simpler result — don't keep retrying past the cap.

**Q:** What does explicit per-type failure handling cost you?
**A:** Every failure path is code you write, test, and maintain on top of the happy path.
