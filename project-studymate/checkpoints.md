# StudyMate Checkpoints — 16 items, 2 per level

Answer these after finishing each level's script and its printed CHECKPOINT prompt —
don't skip straight here. Same format as the domain `practice-questions.md` files:
scenario-based, answer key with per-option rationale at the end. Original items,
not from the live exam.

---

**L1-Q1 · D5 · Model Selection & Tradeoffs** (select ONE)
While running Level 1, you saw Haiku answer in under a second, Sonnet take noticeably
longer, and Opus longer still, with output_tokens rising each tier. You're building a
real-time chat widget where users expect a reply in under two seconds, and separately,
an overnight job that rewrites 5,000 flashcards for clarity with no one watching.
Which pairing best fits what you measured?

A. Opus for the chat widget (best quality matters most when a user is watching), Haiku for the overnight job (speed doesn't matter, so use the cheapest).
B. Haiku (or Sonnet, if quality demands it) for the chat widget, where the latency budget is small and hard; a larger tier for the overnight job, where quality compounds across 5,000 items and latency per item doesn't matter.
C. Sonnet for both — it's the "balanced" tier, so it's always the safe default regardless of constraint.
D. Whichever tier is cheapest per token for both jobs, since cost is the only axis that matters once a model clears a quality bar.

**L1-Q2 · D2 · Claude API Mechanics** (select ONE)
In `ask()`, you built `messages=[{"role": "user", "content": question}]` and passed
a separate `system=` parameter in Level 2. A teammate suggests simplifying Level 2 by
just adding `{"role": "system", "content": SYSTEM_PROMPT}` as the first entry in the
`messages` list instead, to "keep everything in one place." What's wrong with that?

A. Nothing — `"system"` is a valid role in the messages list and this is an equivalent, just less conventional, way to set it.
B. The Messages API has no `"system"` role inside `messages`; system-level instructions are a separate top-level `system` parameter, not a turn in the conversation.
C. It would work, but it doubles token cost because system content would be billed twice.
D. It would work for Haiku and Sonnet but is rejected by Opus specifically.

---

**L2-Q1 · D2 · Structured Outputs** (select ONE)
A teammate says Level 2 is over-engineered: "just tell it in the prompt — 'respond
ONLY with JSON matching this exact shape' — and skip `output_config`." Why is
`output_config.format` still the better design choice?

A. `output_config.format` is faster on every call, with no exceptions, so it's a pure performance win.
B. A prompt instruction is a request the model can slip on under an untested input; `output_config.format` constrains the output per-token at generation time, so a schema-violating response can't be produced in the first place.
C. Prompt-only JSON requests are deprecated and will stop working in a future API version.
D. `output_config.format` is required any time `max_tokens` is set above 300.

**L2-Q2 · D2 · Claude API Mechanics** (select ONE)
Your Level 2 `generate_question()` gets a response with a valid `output_config`
schema attached, but `response.stop_reason` comes back as `"max_tokens"`. What should
`generate_question()` do?

A. Call `json.loads()` anyway — the schema guarantees valid JSON regardless of `stop_reason`.
B. Treat it as truncated output, not a completed structured answer — raise or retry with a higher `max_tokens` rather than parsing.
C. Retry the exact same request immediately in a tight loop until `stop_reason` is `"end_turn"`.
D. Ignore `stop_reason` entirely; it only matters when tools are involved.

---

**L3-Q1 · D2 · Streaming** (select ONE)
In `stream_answer()`, you accumulated text on `content_block_delta` events but only
finalized the return value after a specific event. Which one, and why?

A. `content_block_stop` — it fires once per content block, which is enough to know that block's text is complete and safe to store.
B. `message_delta` — it carries the final `stop_reason`, which is what actually ends a turn.
C. `message_stop` — a single assistant turn can contain more than one content block (as you saw directly in `ask_with_thinking`, where a thinking block and a text block share one turn); only `message_stop` confirms the entire turn, every block, is done.
D. It doesn't matter which event you use, as long as you eventually see `content_block_delta` at least once.

**L3-Q2 · D5 · Extended Thinking** (select ONE)
Your `ask_with_thinking()` result for the refund-vs-escalate scenario returned both a
`thinking` block and a `text` block in `response.content`. If this were turn 1 of a
longer conversation and you wanted to ask a follow-up in turn 2, what must you do with
that first assistant turn's content before sending turn 2?

A. Strip the `thinking` block before appending the turn to `messages` — the model already used it and it's just extra tokens on future requests.
B. Summarize the thinking block into a shorter string to save tokens, then append that summary instead of the raw block.
C. Append the assistant turn's content back exactly as returned, thinking block included and unmodified — editing or removing it is a documented way to break the next request.
D. Only append the `text` block; thinking blocks are never valid as conversation history.

---

**L4-Q1 · D8 · Tool Implementation** (select ONE)
Level 4 gave Claude two tools: `search_notes` (read-only lookup) and `log_weak_area`
(a real write to `weak-areas.md`). Early in writing your tool descriptions, a student
just asks the user "What's a workflow?" without calling any tool, but on a different
run, the *same question* triggers an unwanted `log_weak_area` call. What's the most
likely root cause, and the fix?

A. The model is malfunctioning; retry the request and it will self-correct.
B. `log_weak_area`'s description didn't state an exclusion condition (e.g., "only after the student explicitly says they answered incorrectly") — Claude routes tool selection on the description text, so an under-scoped description gets called on questions it shouldn't touch.
C. Both tools should be merged into one tool to remove the ambiguity entirely.
D. `max_tokens` was set too low, causing the model to default to a tool call instead of a text answer.

**L4-Q2 · D8 · Tool Implementation** (select ONE)
Inside your `run_with_tools()` loop, `search_notes_impl()` raises an exception because
a domain folder doesn't exist. What should the corresponding `tool_result` block look
like?

A. `{"type": "tool_result", "tool_use_id": ..., "content": ""}` — an empty result is the safest way to signal nothing was found.
B. `{"type": "tool_result", "tool_use_id": ..., "content": str(exception), "is_error": True}` — the error text is returned, explicitly flagged so Claude treats it as a failure, not as data.
C. Skip appending a `tool_result` for that block entirely and continue the loop.
D. Raise the exception out of `run_with_tools()` and let the whole request fail.

---

**L5-Q1 · D1 · Agent Architecture & Patterns** (select ONE)
In Level 5, `plan_domain_budget()` is fixed deterministic code, while
`recommend_weak_area()` hands the decision to a model call. A reviewer suggests
swapping them — hardcode which topics get logged, and let the model freely decide the
domain question-budget each run "for variety." What's the problem?

A. There's no problem; both are equally valid places to put either kind of logic.
B. `plan_domain_budget` is exactly-specifiable in code (proportional allocation by a fixed weight table) — a workflow is the simpler, more predictable pattern for it. Whether a wrong answer reflects a real gap worth logging is a judgment call that varies by context — that's what an agent step is for. Swapping them adds model-call cost and nondeterminism to the part that didn't need it, while removing judgment from the part that did.
C. Hardcoding which topics to log is strictly better because it's cheaper — the swap is a pure improvement.
D. Only agent-decided logic can be tested; workflow logic like proportional budgeting can't be verified at all.

**L5-Q2 · D1 · Agent Architecture & Patterns** (select ONE)
Your `confirm_and_log()` asks the real user "Log this to weak-areas.md? [y/N]" —
*before* calling `l4.log_weak_area_impl`. A teammate suggests moving the confirmation
to happen *after* the write, as an "undo" option instead, to make the flow feel
faster. Why is the current placement correct?

A. It isn't — moving confirmation after the write and offering undo is equivalent and would feel more responsive.
B. The write is a persistent, hard-to-fully-reverse change to a real file the moment it happens; the human checkpoint belongs in front of an action like that, not as a cleanup step after it already landed.
C. Confirmation prompts must always come before any tool call, regardless of what the tool does, per API requirements.
D. `input()` cannot be called after a file write in Python, so the current order is a technical necessity, not a design choice.

---

**L6-Q1 · D7 · AI Application Security** (select TWO)
In Run A (undefended) of your injection drill, the fabricated `malicious_note.md`
content was handed to the model as a raw tool result and included an embedded
instruction to reveal the system prompt and call `log_weak_area` with junk arguments.
Which TWO changes in Run B are the actual defenses against this, as opposed to
incidental differences?

A. `wrap_untrusted()` frames the tool result as clearly-delimited data, with an explicit instruction that imperative-sounding text inside it should be treated as a suspected injection, not obeyed.
B. `guarded_log_weak_area()` enforces least privilege at the tool boundary itself — a call with an out-of-scope `domain_skill` is rejected before the real file write, independent of whether the model complied with the injected instruction.
C. Run B used a different, more "trustworthy" model tier than Run A.
D. Run B's system prompt was longer than Run A's.
E. Run B ran the request through the streaming API instead of a single `create()` call.

**L6-Q2 · D7 · Identity, Secrets, and Key Management** (select ONE)
`check_no_hardcoded_secrets()` scans this project's `.py` files for a pattern shaped
like a real Anthropic API key. Every level script instead reads the key via
`os.environ.get("ANTHROPIC_API_KEY")` (through `common.require_api_key()`). Why does
this matter even in a solo study project with no other collaborators?

A. It doesn't — hardcoding is only a risk in multi-developer or open-source repos.
B. A hardcoded key ends up in git history the moment the file is committed, is exposed to anyone who later reads or forks the repo, and can't be rotated without editing and redistributing code — an environment variable keeps the secret out of committed config entirely.
C. Environment variables are required by the Anthropic SDK and hardcoded keys are simply rejected at request time.
D. `.gitignore` alone (without the env-var pattern) is fully sufficient protection, so the scan is redundant.

---

**L7-Q1 · D4 · Evals and Judges** (select ONE)
Level 7 grades four cases with `code_check()` and one with `judge_check()`. Why isn't
`code_check()` used for all five?

A. Code checks are always more reliable, but `judge_check()` is included only to demonstrate the API for exam purposes.
B. Grading mechanism should match what "correct" means for the case: structural properties (right number of choices, no duplicates, valid index) are exactly specifiable in code, but "does the correct choice's wording give away the answer" is an open-ended quality judgment code can't directly check — that's what an LLM judge is for.
C. `judge_check()` is required whenever `output_config` is used anywhere in the pipeline.
D. Code checks can't run inside a `for` loop over multiple cases, so at least one case must use a model call.

**L7-Q2 · D4 · Testing and Tracing** (select ONE)
One eval case fails. Instead of re-reading the full console output, you open
`trace_log.jsonl` and filter to that `case_id`'s line. What does the trace give you
that the pass/fail summary alone doesn't?

A. Nothing extra — the printed PASS/FAIL line already contains everything the trace does.
B. The per-case elapsed time and the specific recorded reason for that step, letting you localize the failure (e.g., "this call took 4x normal latency and returned an empty rationale array") instead of re-inspecting the entire run to find where things went wrong.
C. The trace only matters for security auditing, not for debugging failed eval cases.
D. Traces are only useful once a system has more than 100 eval cases; at 5 cases the summary is sufficient and the trace is overhead.

---

**L8-Q1 · D8 · Tool Implementation** (select ONE)
You've wired `mcp_server.py` into `.mcp.json` using a **stdio** transport so Claude
Code on your machine can call `search_notes`/`log_weak_area`. Your study group of 6
people now wants to share one always-on StudyMate server so everyone's `log_weak_area`
calls land in one shared tracking sheet. Does stdio still fit?

A. Yes — stdio scales to any number of users automatically since each client just connects to the same running process.
B. No — stdio spawns a local subprocess per client, so it runs on whichever single machine launches it and each teammate would get their own independent process (and their own separate `weak-areas.md`, not a shared one); a shared, always-on server needs an HTTP transport instead.
C. Yes, as long as `.mcp.json` is committed to the shared repo — committing the config file is what makes a server shared, regardless of transport.
D. No — MCP servers can only ever be used by the single developer who wrote them, regardless of transport.

**L8-Q2 · D1 · Orchestrator-Worker** (select ONE)
`run_orchestrator()` fans out one `generate_question()` call per domain concurrently,
then makes one more call to merge the results into a briefing. Which of these is the
better candidate for this same fan-out pattern?

A. Generating 8 independent practice questions, one per blueprint domain, in parallel — the same shape as what you built.
B. Having one worker draft a paragraph of a flashcard's explanation and a second worker "improve" that exact same paragraph afterward — the second call depends entirely on the first call's output, so it isn't independent work and fanning it out wouldn't save anything; it would just add a second full model call's worth of tokens to a task one call could do alone.
C. Any task at all, since orchestrator-worker always reduces total latency regardless of how the subtasks relate to each other.
D. Only tasks that don't call the API at all, since orchestrator-worker is a cost-saving pattern rather than a parallelism pattern.

---

## Answer Key & Rationale

**L1-Q1: B.**
- A — Backwards: it optimizes quality where latency is the binding constraint, and cost/speed where quality is actually free to relax. ✗
- B — Match the tier to the constraint that actually binds: hard latency ceiling → fast tier; no latency pressure but quality compounds at volume → larger tier. ✓
- C — "Balanced" isn't "always correct" — that's exactly the equal-effort-everywhere mistake the exam penalizes. ✗
- D — Ignores that quality still has to clear a bar for each use case; cost-only optimization can pick a tier too weak for the job. ✗

**L1-Q2: B.**
- A — There is no `"system"` role for messages; the API's roles inside `messages` are `"user"` and `"assistant"` only. ✗
- B — System-level instruction is `system=`, a separate top-level parameter — that's the actual API shape you used correctly in Level 2. ✓
- C — Fabricated mechanism; not how the API prices or structures requests. ✗
- D — Fabricated; behavior doesn't vary by tier here. ✗

**L2-Q1: B.**
- A — Overstates it: `output_config.format` does add first-request latency to compile the grammar (cached 24h) — "faster on every call, no exceptions" is false. ✗
- B — This is the actual mechanism: constrained decoding restricts which tokens can be generated so a schema-violating response can't be produced, versus a prompt instruction the model can simply fail to follow. ✓
- C — Fabricated; prompt-only JSON requests aren't deprecated, just less reliable. ✗
- D — Fabricated constraint; no such `max_tokens` threshold exists. ✗

**L2-Q2: B.**
- A — Wrong: `max_tokens` truncation means the JSON is incomplete; `json.loads()` would raise or silently parse something wrong. ✗
- B — Correct handling: `max_tokens` cut the output short mid-structure; the fix is raising `max_tokens` and retrying, not parsing what's there. ✓
- C — An immediate tight-loop retry doesn't address the root cause (too low a `max_tokens`) and wastes calls. ✗
- D — `stop_reason` matters for tool-only requests too, but it's equally relevant here — this option describes the opposite of what Level 2 needs. ✗

**L3-Q1: C.**
- A — `content_block_stop` only confirms ONE block is done; a turn can have more than one (thinking + text). ✗
- B — `message_delta` carries `stop_reason` but isn't itself the final "turn is over" signal you commit on. ✗
- C — Correct: only `message_stop` confirms every content block in the turn is complete — the exact behavior `ask_with_thinking` demonstrated with two blocks in one turn. ✓
- D — Event ordering and type both matter; this understates the requirement. ✗

**L3-Q2: C.**
- A — Stripping the thinking block before continuing the conversation is a documented way to break the next request — the opposite of correct. ✗
- B — Summarizing/editing the thinking block is equally unsupported; it must be passed back unmodified. ✗
- C — Correct: continuing a thinking-enabled conversation requires appending the prior assistant turn's content exactly as received. ✓
- D — Thinking blocks are a normal, expected part of conversation history in a thinking-enabled multi-turn exchange. ✗

**L4-Q1: B.**
- A — Not a model malfunction; it's a routing decision made from the description text, and it's reproducible, not random. ✗
- B — Correct: Claude selects tools based on their descriptions; without an explicit "only when X" exclusion clause, a tool can get called on inputs its author never intended. ✓
- C — Merging removes the ambiguity between the two tools but doesn't fix the root cause (an under-scoped description) and creates a different problem (one tool now serving two unrelated purposes). ✗
- D — `max_tokens` doesn't influence tool-selection behavior this way. ✗

**L4-Q2: B.**
- A — An empty-string result reads to the model as "the tool ran and found nothing" (data), not "the tool failed" — exactly the failure mode to avoid. ✗
- B — Correct: return the error text as the result content and set `is_error: True` so Claude knows to treat it as a failure signal, not as data to reason over. ✓
- C — Skipping the `tool_result` entirely breaks the required one-tool_result-per-tool_use_id contract and will error on the next request. ✗
- D — Letting the whole loop crash on one tool's failure defeats the purpose of having a recoverable agentic loop. ✗

**L5-Q1: B.**
- A — There is a real difference: one is exactly-specifiable in code, the other requires contextual judgment; treating them as interchangeable misses the point of the level. ✗
- B — Correct: match the pattern to whether the step is exactly-specifiable (workflow) or requires judgment that varies by case (agent) — swapping them adds cost/nondeterminism where none was needed and removes judgment where it mattered. ✓
- C — Cost isn't the deciding factor here — correctness of the pattern match is. ✗
- D — Workflow logic is, if anything, easier to test (deterministic output for a given input) than model-decided logic. ✗

**L5-Q2: B.**
- A — Moving confirmation after the write is a different design with a different risk profile (relying on someone noticing and undoing), not an equivalent one. ✗
- B — Correct: a checkpoint in front of a persistent action is what makes it a real gate; after-the-fact "undo" depends on the write being cleanly reversible and on someone actually catching it. ✓
- C — Fabricated; there's no such API-level ordering requirement for tool calls generally. ✗
- D — Fabricated technical constraint — `input()` can be called at any point in a Python script. ✗

**L6-Q1: A and B.**
- A — This is the framing defense: label fetched content as data and instruct the model not to treat imperative text inside it as a command. ✓
- B — This is the enforcement defense: the tool itself rejects an out-of-scope call regardless of whether the model was talked into attempting it — defense in depth if the first layer fails. ✓
- C — Both runs use the same model in this drill; tier isn't the variable being tested. ✗
- D — System prompt length isn't the defense mechanism here; the delimiter/framing content is. ✗
- E — Streaming vs. non-streaming doesn't change whether embedded instructions get obeyed. ✗

**L6-Q2: B.**
- A — Wrong: git history, forks, and future collaborators all make a "solo" repo less solo than it looks, and habits formed here carry into shared work. ✗
- B — Correct: a hardcoded secret persists in history, is visible to anyone with repo access (present or future), and can't be rotated without a code change and redistribution — the exact reasons secrets belong in environment/config, not source. ✓
- C — Fabricated; the SDK doesn't detect or reject hardcoded key strings. ✗
- D — `.gitignore` only prevents a *new* secret file from being committed; it doesn't help once a key is already pasted into a tracked `.py` file — which is exactly what the regex scan catches. ✗

**L7-Q1: B.**
- A — Understates code checks' real limits — some criteria genuinely aren't structurally checkable, which is the actual reason for the split. ✗
- B — Correct: match the grading mechanism to what "correct" means for that case — exact/structural properties get a code check; open-ended quality judgments get an LLM judge. ✓
- C — Fabricated dependency; `judge_check` isn't required by `output_config` usage elsewhere in the pipeline. ✗
- D — Fabricated constraint; loops and model calls aren't mutually exclusive. ✗

**L7-Q2: B.**
- A — The whole point of a trace is that it carries more than the summary line — per-case timing and the specific reason recorded at that step. ✗
- B — Correct: the trace lets you localize a failure to the specific step and its recorded detail, rather than re-reading an entire run to guess where it went wrong. ✓
- C — Tracing serves debugging as much as (or more than, in this level) security auditing. ✗
- D — Tracing is useful at small scale too — it's what let you name the exact case and reason here, not just "something failed." ✗

**L8-Q1: B.**
- A — Backwards: stdio does NOT scale to multiple users automatically; it's a per-client local subprocess model, not a shared server. ✗
- B — Correct: stdio ties the server to whichever machine spawns it, one process per client — a shared, always-on team resource needs an HTTP transport, not stdio. ✓
- C — Committing `.mcp.json` shares the *configuration*, not a running shared server — with stdio, every clone still spawns its own separate local process. ✗
- D — Overstated; MCP servers over HTTP are routinely used by multiple clients — the limitation is specific to stdio's process model, not MCP itself. ✗

**L8-Q2: A.**
- A — Correct: independent, parallel, non-dependent subtasks (one question per domain) are exactly the shape that justifies fan-out. ✓
- B — This describes tightly coupled sequential work — the second step needs the first step's output, so it doesn't parallelize and fanning it out just adds cost without benefit. ✗
- C — Overstated; the pattern's benefit is conditional on the subtasks being independent, not universal. ✗
- D — Backwards: orchestrator-worker fan-out typically multiplies token cost (more calls, more input context repeated per worker) in exchange for parallel wall-clock time — it is not a cost-saving pattern by default. ✗
