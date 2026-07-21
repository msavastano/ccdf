# Domain 4: Eval, Testing, and Debugging — Practice Questions

26 original items written to blueprint objectives (not from the live exam). Q1–Q8 are built around the four-layer cumulative debug task; Q9–Q14 cover evals and judges; Q15–Q20 cover testing levels, tracing, and retrieval routing; Q21–Q26 cover production failure handling (retriable vs. terminal, retries, tool errors, refusals). Answer key with per-option rationale at the end — don't scroll past the line until you've committed to answers.

---

**Q1 · D4 · Debugging and Error Handling** (select ONE)
An agent works in most sessions but throws an HTTP 400 on the request *immediately after* a tool call — but only occasionally, and always right after a user reports the app "hung for a second." Which layer should you investigate first?

A. The tool schema — the description is probably ambiguous.
B. The streaming layer — a dropped stream is committing a partial assistant turn to history.
C. The memory layer — prior sessions are overflowing the context window.
D. The model itself — switch to a larger tier to stabilize output.

**Q2 · D4 · Debugging and Error Handling** (select ONE)
A request that includes a `tool_result` block is rejected with HTTP 400 ("tool_result without matching tool_use"). The developer's retry logic re-sends the identical request three times; all three fail. What is the correct response?

A. Add exponential backoff so the retries eventually succeed.
B. Stop retrying — this is a structural error; fix how the `messages` array is built so the assistant `tool_use` turn is present before the `tool_result`.
C. Lower the temperature and retry once more.
D. Treat it as a rate limit and slow the request cadence.

**Q3 · D4 · Debugging and Error Handling** (select ONE)
An agent with three retrieval tools keeps calling the wrong one for a given user request. The tool-use loop executes correctly every time — the right tool just isn't the one Claude picks. Is this an integration-layer or a model-output problem, and where is the fix?

A. Integration-layer — add a `try/except` around tool execution.
B. Integration-layer — the pairing between `tool_use` and `tool_result` is broken.
C. Model-output — fix it upstream in the tool `description`s (state intent and an exclusion condition).
D. Model-output — raise `max_tokens` so Claude has room to reason.

**Q4 · D4 · Debugging and Error Handling** (select ONE)
An agent uses extended thinking with tools. To save tokens, a developer strips `thinking` blocks out of the assistant turn before appending it to history. The next request fails with a 400 about an invalid signature. What happened?

A. Thinking blocks must be passed back unmodified; each carries a signature, and removing them breaks the carry-back rule.
B. The thinking budget was exceeded, corrupting the block.
C. Streaming was required and was disabled.
D. The `tool_result` was malformed and the signature error is a red herring.

**Q5 · D4 · Debugging and Error Handling** (select ONE)
A support agent carries context across sessions. It's flawless in testing and in the first few days of production, then starts failing to respond by roughly the fourth or fifth session for a heavy user. `build_session_history` concatenates every message of every prior session. What's the fix?

A. Increase `max_tokens` so longer histories fit.
B. Store transcripts in external storage and inject only a summary of the last session at start.
C. Pin an older model version with a larger context window.
D. Retry the failing request with backoff.

**Q6 · D4 · Debugging and Error Handling** (select TWO)
In the four-layer debug task, the streaming layer commits the assistant turn before `message_stop` and strips the thinking block, and the context layer appends a `tool_result` with no complete preceding `tool_use` turn. Which TWO statements are correct?

A. The two are one root cause seen twice: fixing the streaming commit (keep all blocks, gate on `message_stop`) also resolves the pairing error.
B. Each requires an independent fix; correcting the streaming layer has no effect on the pairing error.
C. Gating the commit on `message_stop` and preserving the full block list restores both the thinking carry-back and the `tool_use`/`tool_result` pairing.
D. The pairing error is best fixed by appending an empty `tool_result` for any dangling `tool_use` block.
E. Both errors are transient and will clear on retry with backoff.

**Q7 · D4 · Debugging and Error Handling** (select ONE)
Two failures land in the logs: (1) `stop_reason: model_context_window_exceeded`, and (2) an HTTP 529. Which is safely retryable as-is, and which is not?

A. Both are retryable with backoff.
B. Neither is retryable.
C. The 529 is transient and retryable with backoff; the context-window failure is not — you must trim or summarize history first.
D. The context-window failure is retryable; the 529 requires a code change.

**Q8 · D4 · Debugging and Error Handling** (select ONE)
A teammate proposes debugging an agent that "sometimes does the wrong thing three tool calls in" by adding more unit tests around each tool function in isolation. Why is this unlikely to find the bug?

A. Unit tests can't run against Claude at all.
B. Agent failures emerge when components run together across turns; the bug lives in the transcript-level interaction, not in any single tool function.
C. The tools should be tested with a larger model.
D. Isolated tests are sufficient; the real problem is the temperature setting.

---

### Evals and Judges (blueprint-adjacent — supports D5 tier decisions and the D6 iteration loop)

**Q9 · D4 · Evals** (select ONE)
A feature must return a JSON object containing a `total` field with a number between 0 and 100. The team is grading eval cases with an exact string match against a reference output and sees many failures on outputs that are, on inspection, correct. What is the right change?

A. Switch to an LLM-as-judge with a quality rubric.
B. Switch to a code-graded check that parses the JSON and asserts `total` is present and in range.
C. Keep the exact match but add more reference strings to cover the variants.
D. Lower the temperature so the model produces byte-identical output every run.

**Q10 · D4 · Evals** (select ONE)
A team's judge returns only a score from 1 to 10. Reviewing a batch, nearly every output — good, mediocre, and bad — scores 6 or 7. What is the most likely cause?

A. The model tier is too small for grading; move the judge to Opus.
B. The judge prompt asks for a bare score with no reasoning, so the model drifts to a safe middle number.
C. The eval set is too large, which averages out the differences.
D. The temperature on the judge call is too low.

**Q11 · D4 · Evals** (select TWO)
Before relying on a judge's scores in a decision — such as whether a cheaper model is good enough — which steps are required? (Select TWO.)

A. Run the judge on a set of cases a human has already labeled and measure agreement.
B. Confirm the judge and the feature use the same model, so scoring is consistent.
C. If agreement is low, tighten the rubric (define each score, add a good and a bad example) and re-measure.
D. Raise all scores by a fixed offset to correct for the judge's known leniency.
E. Replace the judge with an exact-match grader to remove noise.

**Q12 · D4 · Evals** (select ONE)
An engineer rewrites the system prompt, adds two few-shot examples, and switches from Haiku to Sonnet, then re-runs the eval. The average score rises from 4.2 to 7.1. What is the problem with this result?

A. Nothing — a 2.9-point gain is a clear success.
B. The eval must be re-calibrated after any model change before scores are comparable.
C. Three levers moved at once, so the result doesn't identify what caused the gain — or whether one change hurt.
D. Average scores are never valid; only exact-match pass rates are.

**Q13 · D4 · Evals** (select ONE)
A team has 3 hand-graded eval cases with a carefully tuned rubric and is deciding whether to invest in expanding coverage. A regression keeps reaching production despite passing all 3. What is the highest-value move?

A. Refine the rubric further so the 3 cases grade more precisely.
B. Expand to ~20 cases including irregular and edge inputs, accepting slightly noisier automated grading — generating additional cases from the labeled seed set and spot-checking them.
C. Replace the code graders with a judge on all 3 cases.
D. Run the 3 cases more times per commit to reduce variance.

**Q14 · D4 · Evals** (select ONE)
A design document is being written for a summarization feature before implementation. Which entry is stated concretely enough to become an eval case?

A. "The summary should be high quality and useful to the reader."
B. "A two-sentence summary that lists every action item and its owner."
C. "The feature should summarize threads accurately and quickly."
D. "Users should be satisfied with the output."

---

### Testing and Tracing (class module, added 2026-07-19)

**Q15 · D4 · Testing and Tracing** (select ONE)
A RAG feature's eval passes at 8.5/10, but users report answers that cite the wrong document. Unit tests on the chunker pass and functional tests confirm the model call returns well-formed JSON every time. Which test level is most likely missing?

A. Unit — the chunker needs deeper coverage of edge-case documents.
B. Functional — the model call should be checked against more input shapes.
C. Integration — the seam where the retrieval result is handed to the model call is untested, and both sides can pass their own tests while the handoff is broken.
D. End-to-end — only a full user-path test can grade answer quality.

**Q16 · D4 · Testing and Tracing** (select ONE)
An end-to-end test fails on one case in a five-step workflow. The team wants to know which step produced the bad result. What gives them that?

A. Add more end-to-end cases until a pattern emerges.
B. A trace of the run recording each step's prompt, tool calls, intermediate outputs, and timing.
C. Standard operational logging — status codes and latencies per request.
D. Re-run the eval with a larger model to see if the failure disappears.

**Q17 · D4 · Testing and Tracing** (select TWO)
Which statements about the four test levels are correct? (Select TWO.)

A. A functional test validates that one Claude call returns the expected shape for a given input, but not the system around that call.
B. An end-to-end test is the fastest way to localize which component broke.
C. A unit test isolates one function, such as a parser or tool wrapper, and says nothing about how components fit together.
D. Integration tests are redundant once unit and end-to-end tests both pass.
E. A passing eval score guarantees no break exists inside the workflow.

**Q18 · D4 · Testing and Tracing** (select ONE)
A trace shows: step 1 `retrieve` ok (3 chunks), step 2 `build_prompt` ok (1,240 tok), step 3 `model.call` ok (answer returned), step 4 `parse` FAIL — `KeyError: amount`. What is the correct read?

A. Retrieval returned the wrong chunks; fix the index.
B. The model is underpowered for the task; move up a tier.
C. The failure is localized to the parser, which raised on a field the model did not return — fix the output contract (constrain/structure the response) and the parse handling, not the retrieval step.
D. The prompt is too long at 1,240 tokens; trim the context.

**Q19 · D4 · Testing and Tracing / D6 · Retrieval** (select ONE)
A support assistant handles a mix of single-fact policy lookups and multi-part investigative questions. All queries currently run through agentic search. What is the highest-value change?

A. Move every query to a pre-built retrieval index to cut latency.
B. Add a cheap classification call that routes lookups to fetch-once retrieval and multi-part questions to agentic search.
C. Increase the number of search rounds so the simple queries resolve faster.
D. Nothing — a single path is always preferable for maintainability.

**Q20 · D4 · Testing and Tracing / D6 · Retrieval** (select ONE)
A team adds a query router to a system where **every** incoming query is a single-fact lookup against a stable corpus. What is the effect?

A. Cost falls, because the classifier prevents unnecessary search rounds.
B. The router adds a classification call on every request while always choosing the same branch — pure overhead; hardcode the fetch-once path instead.
C. Answer quality improves, because classification sharpens the retrieval query.
D. The router is required regardless, since retrieval strategy must always be chosen at runtime.

---

### Production Failure Handling (class module, added 2026-07-19)

**Q21 · D4 · Debugging and Error Handling** (select ONE)
A production service is classifying API failures so its retry layer knows what to do. Which single question correctly sorts a failure into retriable vs. terminal?

A. Did the failure occur inside a tool call or inside the model call?
B. Would waiting and re-sending the *identical* request plausibly succeed?
C. Did the failure happen more than once in the last minute?
D. Is the error message user-facing or internal?

**Q22 · D4 · Debugging and Error Handling** (select TWO)
Your client wraps every Anthropic call in a custom retry loop with exponential backoff. During a traffic spike you see far more attempts against your rate limit than the cap you configured, and `429`s persist longer than expected. Which two statements identify real problems here?

A. The Anthropic SDK already retries transient failures automatically, so two loops multiply attempts rather than capping them.
B. Exponential backoff is the wrong strategy for a `429`; only fixed-interval retry is valid.
C. If the loop ignores the `retry-after` header on the `429` response, it is guessing at a wait the service already specified.
D. A `429` is terminal, so the loop should not be retrying it at all.
E. Retry logic belongs exclusively in the SDK; application-level fallbacks are never appropriate.

**Q23 · D4 · Debugging and Error Handling** (select ONE)
An agent's `run_tool` wrapper catches every exception and returns `{"type": "tool_result", "tool_use_id": ..., "content": ""}` so the loop never crashes. Users report the agent gives confident answers that are simply wrong. What is the defect?

A. The empty string violates the `tool_result` schema and should be `null`.
B. The wrapper should re-raise so the whole request fails and the user sees an error.
C. The error is silenced — the result must carry `is_error: true` and the error text so Claude can react instead of reasoning on an empty result as if it were valid data.
D. The `tool_use_id` is being reused across turns, corrupting the pairing.

**Q24 · D4 · Debugging and Error Handling** (select ONE)
A retry layer keys entirely off HTTP status codes. A subset of requests returns `200` but the output is unusable, and none of them are retried or flagged. The responses carry `stop_reason: "refusal"`. What is happening and what is the correct handling?

A. The refusal is a transient model fault; add `200`-with-empty-content to the retriable set.
B. A refusal is a content decision returned at HTTP `200`, so a status-code classifier never sees it — check `stop_reason` explicitly, then fail fast: raise and log, don't retry.
C. The responses were truncated by `max_tokens`; raise the limit and retry.
D. Refusals indicate an auth scope problem; treat them as `403` and fail fast.

**Q25 · D4 · Debugging and Error Handling** (select ONE)
During an incident, calls return `529`. An engineer proposes reducing the application's request rate and adding a longer fixed delay before each call. What is the most accurate assessment?

A. Correct — `529` is a rate-limit response, so lowering request rate is the fix.
B. Incorrect — `529` is terminal, so the calls should fail fast rather than be retried.
C. Partly right for the wrong reason — `529` signals Anthropic-side overload, not your rate limit. It is retriable: back off (honoring `retry-after` when present) and fail over to a fallback path or a graceful error if it persists.
D. Incorrect — `529` means a malformed request body and must be fixed in the request.

**Q26 · D4 · Debugging and Error Handling** (select ONE)
A team is unsure whether a newly-seen error code should be retried. Which default is correct, and why?

A. Retriable — retrying costs little and may recover the request.
B. Terminal — a failure wrongly marked terminal fails loudly and gets fixed, while one wrongly marked retriable hammers the service and hides the real problem behind repeated retries.
C. Retriable, but only for idempotent requests; otherwise skip error handling entirely.
D. Neither — suppress the error and return a cached response until the code is classified.

---

## Answer Key & Rationale

**Q1: B.**
- A — Schema bugs produce *systematic* wrong-tool selection, not intermittent 400s tied to network hiccups. ✗
- B — "Hung for a second" = a dropped/slow stream; committing a partial turn to history corrupts the *next* request. Intermittent + network-correlated + fails-after-a-tool-call is the streaming signature. ✓
- C — Memory overflow fails progressively by session count, not intermittently within a session. ✗
- D — Model tier doesn't change a structural history-corruption bug. ✗

**Q2: B.**
- A — Backoff is for transient errors; a structural 400 reproduces identically no matter the delay. ✗
- B — Unpaired `tool_result` is structural: the fix is in how the `messages` array is built (the assistant `tool_use` turn must be committed in full first). ✓
- C — Temperature affects sampling, not message structure. ✗
- D — It isn't a rate limit; slowing cadence changes nothing. ✗

**Q3: C.**
- A — The loop and pairing execute correctly every time; nothing in the integration layer is broken. ✗
- B — The loop and pairing execute correctly every time; nothing in the integration layer is broken. ✗
- C — Valid call, wrong *choice* = model-output, fixed upstream at the `description` (intent + "when NOT to use"). ✓
- D — More tokens doesn't fix selection driven by weak descriptions. ✗

**Q4: A.**
- A — With extended thinking + tools, thinking blocks (each signed) must be returned unmodified; stripping them breaks carry-back and the signature check → 400. ✓
- B — Budget overrun doesn't produce a signature error. ✗
- C — Streaming isn't required for carry-back. ✗
- D — The signature error is exactly the cause, not a distraction. ✗

**Q5: B.**
- A — `max_tokens` caps output length, not input history; it can't hold an unbounded transcript. ✗
- B — The classic memory-scope fix: external storage + a summary injected at session start keeps context flat across sessions. ✓
- C — A bigger window delays the ceiling; concatenation still grows without bound. ✗
- D — Retrying doesn't shrink the history that caused the failure. ✗

**Q6: A and C.**
- A — Bugs 2 and 3 share a root: the broken assemble-and-commit step. Fixing it resolves the pairing symptom. ✓
- B — False; they are coupled, not independent. ✗
- C — Preserving all blocks and gating on `message_stop` restores *both* invariants at once (carry-back and pairing). ✓
- D — Fabricating a `tool_result` for a tool that never ran injects invented data — wrong fix. ✗
- E — Both are deterministic structural/state bugs, not transient. ✗

**Q7: C.**
- A — The context-window failure won't clear on retry; the request is still too large. ✗
- B — The 529 (overloaded) is transient and retryable. ✗
- C — 529 → backoff + jitter; context-window exceeded → trim/summarize first, then resend. ✓
- D — Reversed. ✗

**Q8: B.**
- A — Unit tests against tool functions are fine and common. ✗
- B — Agent bugs surface across turns when components interact; isolated tests miss compounding routing/context/structure issues — you need transcript-level analysis. ✓
- C — Model size is unrelated to an integration-layer interaction bug. ✗
- D — Isolated tests are *not* sufficient here, and temperature isn't the cause. ✗

**Q9: B.**
- A — A judge is for open-ended quality; this output has a validatable structural rule, so a judge adds cost and variance for no gain. ✗
- B — Structured output with a checkable rule → code-graded check. It scores correct-but-differently-serialized outputs properly, which is exactly the failure described. ✓
- C — Enumerating string variants is unbounded and still brittle to key order and whitespace. ✗
- D — Temperature reduces variation but doesn't make a paraphrase-tolerant grader; the grading method is what's wrong. ✗

**Q10: B.**
- A — Middle-number drift isn't a capability limit; a bigger model asked for a bare score drifts too. ✗
- B — Judges asked only for a number gravitate to a safe middle (~6). Requiring strengths, weaknesses, and reasoning *before* the score anchors it to something specific. ✓
- C — Set size doesn't compress per-case scores; each case is graded independently. ✗
- D — Low temperature yields consistency, not a clustered-at-6 distribution across genuinely different outputs. ✗

**Q11: A and C.**
- A — Calibration *is* measuring agreement against human labels. Without it the score looks rigorous but is unvalidated. ✓
- B — Same-model is not a requirement, and using the feature's own model to grade itself is often worse, not better. ✗
- C — Low agreement is a rubric problem: define each score, add a good and a bad example, re-measure. ✓
- D — A blanket offset fabricates precision; it doesn't make disagreement go away. ✗
- E — Exact match can't evaluate the open-ended quality the judge exists for; that's trading a noisy signal for no signal. ✗

**Q12: C.**
- A — The gain is real but unattributable, and the eval's purpose is attribution. ✗
- B — There's no "re-calibration after a model change" requirement for the eval itself (calibration applies to a *judge* against human labels). ✗
- C — One lever at a time. With three changes, you don't know which helped, and an improvement in two could be masking a regression in the third. Per-case results would also need checking. ✓
- D — Averages are valid; they just conceal per-case movement, which is a separate caution. ✗

**Q13: B.**
- A — A sharper rubric on 3 cases doesn't add coverage; the regression is escaping through inputs the set never exercises. ✗
- B — Coverage catches edge cases and coverage comes from volume. A larger, slightly noisier set reveals more than a small perfect one; generating from a labeled seed plus spot-checking is the cheap way to scale. ✓
- C — Changes the grading method, not the coverage gap. ✗
- D — Repeating the same 3 inputs cannot surface behavior on inputs not in the set. ✗

**Q14: B.**
- A — "High quality and useful" cannot be graded; it's the vague goal the design doc exists to prevent. ✗
- B — States the output form and the required content, so a grader (code or judge) can check it and it becomes a real eval case. ✓
- C — "Accurately and quickly" has no threshold; latency belongs in the budget decision with a number. ✗
- D — Satisfaction is an outcome, not a checkable output specification. ✗

**Q15: C.**
- A — The chunker already passes in isolation; deeper unit coverage tests the same layer again. ✗
- B — The call returns a valid shape; the content handed *into* it is the problem. ✗
- C — Wrong-document citations with both sides passing their own tests is the signature of an untested seam. Integration is where silent failures live. ✓
- D — E2E would show the symptom (it already does, via user reports) but not the layer; and the eval is already grading final output. ✗

**Q16: B.**
- A — More E2E cases multiply the symptom without localizing it. ✗
- B — A trace records prompt, tool calls, intermediate outputs, and timing per step; the failing step is visible once the intermediate output is. ✓
- C — Status codes and latencies don't surface intermediate outputs, so they can't localize a workflow failure. ✗
- D — Swapping the model is a guess before localization, and may mask rather than identify the break. ✗

**Q17: A and C.**
- A — Exactly the functional level: one call, expected shape, nothing about the surrounding system. ✓
- B — Backwards. E2E is the *hardest* to localize since it sees only the final result. ✗
- C — Exactly the unit level. ✓
- D — Integration is precisely the level unit and E2E both miss: the handoff itself. ✗
- E — A passing eval grades final output only; a break inside can hide behind a good score. ✗

**Q18: C.**
- A — Retrieval returned 3 chunks and passed; the trace localizes elsewhere. ✗
- B — Nothing in the trace implicates model capability; the call succeeded. ✗
- C — Step 4 is the only FAIL, and the error names the cause: a field the model didn't return. Fix the output contract and the parse handling. ✓
- D — 1,240 tokens is unremarkable and step 2 passed. ✗

**Q19: B.**
- A — Forcing every query to a static index gives shallow answers on the multi-part questions that needed several passes. ✗
- B — Mixed traffic is exactly when a router earns its cost: one cheap classification call, iteration paid for only when the query needs it. ✓
- C — More rounds increases cost and latency on the queries that were already over-served. ✗
- D — A single path is only preferable when traffic is one shape; here it isn't. ✗

**Q20: B.**
- A — There are no unnecessary search rounds to prevent; the branch never varies. ✗
- B — Uniform traffic means the classifier pays a call per request to reach a foregone conclusion. Hardcode the path that fits. ✓
- C — Classification picks a path; it doesn't sharpen the retrieval query. ✗
- D — There is no requirement to choose at runtime; a fixed strategy is correct when the traffic is one shape. ✗

---

**Q21: B.**
- A — Location doesn't determine retriability; the *cause* does. A tool failure may be either. ✗
- B — Exactly the test: transient causes (capacity, network, per-minute limits) clear with time; causes inside the request do not. ✓
- C — Frequency helps localize a *layer*, not classify retriability. ✗
- D — Audience of the message is irrelevant to whether a retry can succeed. ✗

**Q22: A and C.**
- A — The SDKs auto-retry transient failures with progressive delays; a second loop wrapped around them multiplies attempts instead of capping them. ✓
- B — Exponential backoff with jitter is the correct strategy for a `429`. ✗
- C — `retry-after` on a `429`/`529` is authoritative; ignoring it means guessing at a wait the service already told you. ✓
- D — `429` is retriable. ✗
- E — Application-level fallbacks (cache, simpler path, graceful error) are exactly what your code should own once the SDK handles transient retries. ✗

**Q23: C.**
- A — The schema isn't the problem; the silencing is. ✗
- B — Crashing the whole request is the opposite over-correction — surfacing the error lets the model try another approach or stop cleanly. ✗
- C — A silenced tool error becomes a confident wrong answer because the model treats the empty result as valid data. `is_error: true` plus the error text lets it react. ✓
- D — Nothing in the scenario implicates pairing; the loop runs fine. ✗

**Q24: B.**
- A — A refusal isn't transient, and retrying a content decision changes nothing. ✗
- B — Refusals return `200`, so status-code classification misses them entirely; check `stop_reason`, then raise and log. ✓
- C — Truncation surfaces as a different `stop_reason`; `refusal` names the cause explicitly. ✗
- D — A refusal is not an auth problem, though the "fail fast" half is right for the wrong reason. ✗

**Q25: C.**
- A — Classic distractor: `529` looks like a limit but reflects Anthropic-side load, not your rate. ✗
- B — `529` is retriable, not terminal. ✗
- C — Right classification and right handling: back off honoring `retry-after`, then fall over or return a graceful error if it persists. ✓
- D — Malformed request bodies are `400`. ✗

**Q26: B.**
- A — This is the asymmetry backwards; cheap-looking retries are how a real bug gets buried. ✗
- B — Correct asymmetry: loud failures get diagnosed, silent retry loops hide the cause and burn retry budget other failures may need. ✓
- C — Idempotency matters for *whether a retry is safe*, but it doesn't make "retriable" the safe default, and skipping error handling is never right. ✗
- D — Serving stale data to mask an unclassified error hides the failure exactly the way silent retries do. ✗

---

**Scoring:** 30 correct decisions possible (22 single + 4×2 multi). Log misses to `weak-areas.md` with the skill tag (`D4 · Debugging and Error Handling` for Q1–Q8, `D4 · Evals and Judges` for Q9–Q14, `D4 · Testing and Tracing` for Q15–Q20, `D4 · Production Failure Handling` for Q21–Q26).
