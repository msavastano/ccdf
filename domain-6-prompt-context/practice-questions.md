# Domain 6: Prompt and Context Engineering — Practice Questions

Format per item: scenario stem · state how many responses to select · options A–D (or more for multiple-response) · tag (e.g., "D1 · Agent Architecture") · answer key + per-option rationale at the end of the file.

---

**Q1 · D6 · Prompt Engineering** (select ONE)
**Classifier output shape.** A support-ticket classifier returns the correct category, but the label varies run to run: `"Billing"`, then `"billing"`, occasionally a full sentence like *"This looks like a billing issue."* The downstream router expects one of a fixed label set and breaks on the inconsistency.
Which is the primary missing piece?

A. A more polite, clearer re-wording of "classify the ticket"
B. An output constraint (fixed label set, "return only the label")
C. A lower temperature setting
D. A longer system prompt describing good customer service

**Q2 · D6 · Prompt Engineering** (select ONE)
**Drift across a conversation.** A multi-turn assistant starts on-task but, as the conversation grows, widens its scope, shifts tone, and answers broader questions than asked.
Which technique addresses this failure?

A. Few-shot examples of the desired answer format
B. Wrapping each user message in XML tags
C. A system prompt (or a more specific one)
D. An output constraint specifying JSON

**Q3 · D6 · Prompt Engineering** (select ONE)
**Instructions mixed with data.** A prompt asks Claude to "debug this code using the provided documentation," pasting both inline. Claude sometimes treats the documentation as code to edit, or blends the two.
What is the best fix?

A. Add XML tags with descriptive names like `<my_code>` and `<docs>` to mark the boundary
B. Add the instruction "do not confuse the code and the docs"
C. Move the documentation into a separate follow-up message and hope Claude remembers
D. Use official, reserved XML tag names, since custom names are not recognized

**Q4 · D6 · Output Handling** (select TWO)
**What's true about structured outputs.** A team is deciding whether to enable structured outputs (`output_config.format`) and `strict: true` in a production pipeline.
Which statements are correct?

A. Constrained decoding allows only tokens that keep the output valid against the schema, so a schema-violating response can't be generated
B. A valid schema guarantees every response parses successfully
C. Enabling structured outputs reduces input token cost
D. `strict: true` constrains the arguments Claude passes to your tools, not the final message text
E. Message prefilling combines freely with JSON outputs

**Q5 · D6 · Output Handling** (select ONE)
**Incomplete JSON in production.** With JSON outputs enabled, a service occasionally receives JSON that is cut off mid-structure. The values present are valid, but the object is incomplete.
What is the most likely `stop_reason`, and the correct response?

A. `refusal` — log it and retry with the same parameters
B. `end_turn` — the JSON is complete; the parser has a bug
C. `max_tokens` — the response was truncated; raise `max_tokens` and retry
D. `tool_use` — switch to strict tool use instead

**Q6 · D6 · Prompt Engineering** (select ONE)
**Fifth re-prompt, still wrong.** A developer has re-prompted a task five times. Each version is longer than the last, yet the output is still wrong, and it's now hard to tell which change did what.
What is the best next step?

A. Add all four techniques (system prompt, XML, few-shot, output constraint) at once
B. Diagnose the failure type first, then add the single technique that matches it
C. Rephrase the existing instructions more emphatically
D. Raise `max_tokens` so the model has room to comply

**Q7 · D6 · Context Engineering** (select ONE)
**Passed in dev, stalled in prod.** An agent passes every test with the team's small fixtures. In production it runs fine for a few turns, then stalls mid-task; logs show `stop_reason: model_context_window_exceeded`. The code never trims history.
What best explains the failure and the right fix?

A. The API silently truncated the oldest turns and corrupted state; switch to a different model
B. Real tool outputs run several times larger than the fixtures and sessions run longer, so the window fills far earlier — add context management (compaction or subagents) and gate requests with token counting
C. Raising `max_tokens` will fix it, since that controls the context window
D. The context window is smaller in production than in development

**Q8 · D6 · Context Engineering** (select ONE)
**Agent forgets its edits after compaction.** A long-running coding agent uses manual compaction. After each compaction it loses track of which files it already modified and re-edits them, causing conflicts.
What is the most direct fix?

A. Increase the model's context window so compaction isn't needed
B. Rewrite the summarizer prompt to preserve all file paths modified, decisions made, and errors and their resolutions
C. Replace compaction with clearing so the context is always fresh
D. Prune back to the message before the edits started

**Q9 · D6 · Context Engineering** (select ONE)
**Choosing the strategy.** A developer finishes one task and the next request is on a completely unrelated topic; carrying the prior conversation forward would only bias the model.
Which budget strategy fits?

A. Compaction — summarize the prior task and continue
B. Pruning — rewind to an earlier message in the same thread
C. Clearing — start a new conversation with empty context
D. Subagent handoff — delegate the new task with prior context attached

**Q10 · D6 · Context Engineering** (select ONE)
**Retrieval that misses an exact identifier.** A support bot retrieves from an embedding index. A query for the exact error code `ERR_4032` returns passages about *general* connection errors but misses the one paragraph that names `ERR_4032`, because that paragraph is worded differently.
What is the best fix?

A. Make the chunks much larger so every chunk contains more text
B. Run a lexical (keyword) match alongside the semantic search so the exact term is found even when a more semantically similar chunk outranks it
C. Remove chunk overlap to sharpen the boundaries
D. Switch the model to a larger tier

**Q11 · D6 · Context Engineering** (select TWO)
**Index vs. agentic search.** Two teams need retrieval. Team A queries a **stable** internal policy manual with simple lookups and must be able to audit exactly which passages a query returned. Team B answers **multi-step** questions over a codebase that changes hourly.
Which choices are the better fit?

A. Team A: a retrieval index — inspectable, testable retrieval suits a stable corpus with simple lookups
B. Team A: agentic search, because it avoids all infrastructure
C. Team B: agentic search — it reads the current files at query time, avoiding index staleness on a fast-changing corpus
D. Team B: a nightly-rebuilt index, since multi-step questions always need an index
E. Both teams: paste the full corpus into the system prompt on every call

---

## Answer Key & Rationale

**Q1: B.**
- A — Rewording changes *how* you say something but adds no structural piece; the content is already correct, so clearer phrasing won't stabilize the *form*. ✗
- B — The symptom is a wrong output **shape** — the classic signal of a missing **output constraint** (fixed label set, "return only the label"). Few-shot pairs and XML tags typically accompany it to lock casing and separate examples, but the constraint is the primary missing piece. ✓
- C — Temperature affects variability at the margins but does not define an output contract; the label set and casing still aren't specified. ✗
- D — More system-prompt prose about service quality addresses content/tone, not the shape the parser needs. ✗

**Q2: C.**
- A — Few-shot examples fix *hallucinated structure*, not scope/tone drift across turns. ✗
- B — XML tags fix *instruction/data confusion*, not behavioral drift. ✗
- C — Drift that worsens deeper into a conversation signals an underspecified **system prompt** — the contract that holds role, scope, and format steady on every turn. ✓
- D — A JSON constraint governs form, not the widening scope/tone described. ✗

**Q3: A.**
- A — The failure is instructions mixed with input data; **XML tags with descriptive names** make the boundary unambiguous. ✓
- B — A plain instruction is exactly the phrasing-level fix that doesn't reliably enforce a boundary. ✗
- C — Splitting messages doesn't mark the boundary and adds fragility; the point is to delimit the content, not relocate it. ✗
- D — Descriptive, custom tag names work best; there is no requirement to use official/reserved names. ✗

**Q4: A and D.**
- A — That is the definition of constrained decoding — invalid tokens are disallowed at generation time. ✓
- B — `refusal` and `max_tokens` still return non-conforming output; a schema is not a guaranteed parse. Always check `stop_reason`. ✗
- C — Structured outputs **add** input tokens (an injected format-describing prompt); they don't reduce cost. ✗
- D — `strict: true` constrains **tool-call arguments**; `output_config.format` constrains the final response text. Different halves of the exchange. ✓
- E — Prefilling and JSON outputs are mutually exclusive on the same request. ✗

**Q5: C.**
- A — `refusal` carries refusal text that overrides the schema; it isn't "valid values, incomplete object," and retrying unchanged doesn't address truncation. ✗
- B — `end_turn` means a complete, schema-valid object — inconsistent with output cut off mid-structure. ✗
- C — Output truncated mid-structure with otherwise-valid values is the `max_tokens` signature; raise `max_tokens` and retry. ✓
- D — `tool_use` is unrelated to a truncated final message; strict tool use guards tool arguments, not this JSON payload. ✗

**Q6: B.**
- A — Stacking all four on an undiagnosed failure is over-engineering and makes it harder to isolate what actually fixed the issue. ✗
- B — A prompt that grows longer but not more precise is the tell to **diagnose the failure type first**, then add the single matching technique. ✓
- C — Emphasis is still phrasing; it adds no structural piece. ✗
- D — `max_tokens` addresses truncation, not a wrong-output-shape/content failure being described. ✗

**Q7: B.**
- A — Current models do **not** silently truncate old content — a request over the window is rejected before generation, and a request that hits the ceiling mid-generation returns what it produced with `model_context_window_exceeded`. Switching models doesn't address a budgeting problem. ✗
- B — The classic dev-to-prod trap: production tool outputs run ~3–5× larger than fixtures and sessions run longer, so the window fills at turn eight, not turn fifty. The fix is context management (compaction/subagents) plus token counting to gate requests before they error. ✓
- C — `max_tokens` caps **output**, not the context window; raising it doesn't create window headroom. ✗
- D — The window limit is the same; what changed is how fast real data fills it. ✗

**Q8: B.**
- A — You can't grow the window arbitrarily, and even a bigger window only delays the ceiling. The lost state is a summarizer problem, not a size problem. ✗
- B — What survives compaction is exactly what the summarizer prompt names. Preserving file paths modified, decisions, and errors + resolutions is the documented fix for task-critical state loss — the most common multi-session agent failure. ✓
- C — Clearing throws away *all* context, including the knowledge the agent still needs to finish the task. ✗
- D — Pruning to before the edits discards the completed work, forcing it to be redone. ✗

**Q9: C.**
- A — Compaction preserves prior context to keep working the **same** task — the opposite of what's wanted when the next task is unrelated. ✗
- B — Pruning stays in the same thread and keeps earlier context; it's for backing out of an unproductive path, not switching topics. ✗
- C — A completely different next task where prior context would only bias the model is the textbook case for clearing (new session / `/clear`). ✓
- D — Attaching the prior context is exactly the bias you want to avoid; a handoff is for decomposing a large task, not resetting topic. ✗

**Q10: B.**
- A — Larger chunks dilute the match with unrelated text and make retrieval *less* precise, not more — they won't reliably surface a specific identifier. ✗
- B — Semantic similarity can rank a differently-worded but related passage above the one containing the exact term. A parallel lexical/keyword match (hybrid retrieval) catches the exact identifier. ✓
- C — Overlap helps facts that cross chunk boundaries stay retrievable; removing it makes boundary losses *worse*. ✗
- D — The miss is in the retrieval step, not model capability; a bigger model can't answer from a chunk it never received. ✗

**Q11: A and C.**
- A — A stable corpus with simple lookups plus an audit requirement is the case where owning an index pays off — retrieval is inspectable and testable, and the sync/security cost is worth it. ✓
- B — Agentic search trades away inspectability, which is exactly what Team A needs; "avoids all infrastructure" ignores their audit requirement. ✗
- C — A fast-changing corpus and multi-step questions favor reading current files at query time — no index to keep in sync, no staleness — accepting higher tokens/time per query. ✓
- D — A nightly index is stale by construction on an hourly-changing corpus; multi-step questions don't *require* an index. ✗
- E — Pasting the full corpus every call wastes budget and can blow the window — the problem retrieval exists to avoid. ✗

---

## Supplement — Prompt Engineering, Context Engineering, and Output Handling

_Added 2026-07-27 to rebalance toward blueprint weight: D6 is 11.0% of the exam and had eleven items. Sourced from `notes.md` and `../domain-2-applications/structured-outputs-examples.md`._

**Q12 · D6 · Prompt Engineering** (select ONE)
**A label that is not a label.** A classifier prompt returns the right category but returns it as a full sentence on some runs, capitalized differently on others. The downstream router expects one value from a fixed set and breaks on anything else.
Which technique is missing?

A. An output constraint — the prompt never specified the form, the field names, or the stopping point, so the model returns plausible text the parser was not built to accept
B. A system prompt, since the content keeps changing
C. Few-shot examples, since the model has not understood the task
D. XML tags, since the ticket text is not delimited from the instructions

**Q13 · D6 · Prompt Engineering** (select ONE)
**The right answer in the wrong shape.** An extraction prompt reliably finds the correct values but invents its own nesting and field names, differently each run. The instructions describe the desired structure in prose.
Which technique is missing?

A. Few-shot examples — the model understood the task but cannot infer an exact structure from a description, and one correct input-to-output pair pins the shape down
B. A longer and more detailed prose description of the structure
C. A system prompt establishing the assistant's role
D. Lower model tier, since smaller models invent less

**Q14 · D6 · Prompt Engineering** (select ONE)
**Instructions and data in one blob.** A prompt says "debug this code using these docs" and then concatenates the code and the documentation with no separators. The model sometimes treats a comment in the code as an instruction and sometimes debugs the documentation.
Which technique is missing?

A. XML tags with descriptive names that mark where each input begins and ends, so the model can tell instructions, code, and documentation apart
B. A system prompt raising the priority of the debugging instruction
C. Few-shot examples showing correctly debugged code
D. An output constraint specifying the format of the debug report

**Q15 · D6 · Prompt Engineering** (select ONE)
**A prompt that keeps growing.** After six iterations a prompt has tripled in length and still fails on the same class of inputs. Each pass added more emphasis and more caveats.
What does this pattern indicate?

A. The diagnosis step is being skipped — rewording changes how something is said without supplying missing structure, so the fix is to name the failure type and add the one technique that matches it
B. The prompt is still too short and needs further elaboration
C. The task exceeds what prompting can achieve and requires fine-tuning
D. The model tier is too low and should be raised before any further prompt work

**Q16 · D6 · Prompt Engineering** (select ONE)
**Naming the tags.** An engineer delays adding XML tags to a prompt while searching the documentation for the official reserved tag names to use.
What is the correct guidance?

A. Use descriptive names that match the content, such as tags naming the code and the docs — there is no reserved set, and the descriptive name is what makes the boundary clear
B. Only a documented set of reserved tag names is recognized, so the search is necessary
C. Tag names are ignored entirely, so any single-letter name works equally well
D. XML tags should be avoided in favor of markdown headings, which are parsed natively

**Q17 · D6 · Prompt Engineering** (select ONE)
**Stacking on a simple task.** A prompt reads "Summarize this paragraph." An engineer proposes adding a system prompt, XML tags, three few-shot examples, and an output schema, on the grounds that all four techniques are best practice.
What is the correct assessment?

A. Do not add all four to a task that needs one — each technique answers a specific failure, and adding them without a failure to address costs context and adds nothing
B. Correct — stacking all four is the recommended baseline for every prompt
C. Correct for the examples and schema, but a system prompt is never needed for summarization
D. The task should be rewritten as a tool call instead

**Q18 · D6 · Context Engineering** (select ONE)
**Choosing among the four strategies.** A long agent session has accumulated a lengthy unproductive debugging detour. The team wants to continue the same task, keeping the knowledge that was actually useful and shedding the rest.
Which strategy fits, and what does it cost?

A. Compaction — summarize the history into a condensed version that keeps the key learnings, at the cost of any detail the summary did not capture
B. Clearing — start a fresh conversation, at the cost of nothing, since the useful knowledge can be re-derived
C. Pruning — rewind to before the detour, which preserves everything learned during it
D. Subagent handoff — delegate the remainder of the current task, which preserves full visibility into how it was completed

**Q19 · D6 · Context Engineering** (select ONE)
**A summarizer that lost the state.** A multi-session agent compacts with the instruction "summarize the conversation so far." After compaction it repeatedly re-explores files it already modified and re-encounters errors it had already resolved.
What is the fix?

A. Engineer the summarizer against the state the task cannot afford to lose — instruct it to preserve file paths modified, decisions made, and errors encountered with their resolutions
B. Compact less frequently, so more of the original history survives
C. Switch to clearing instead, since compaction always loses task state
D. Raise the model tier, since summarization quality is a capability limit

**Q20 · D6 · Context Engineering** (select ONE)
**Too big for one window.** A long-horizon task does not fit in a single context window. The team's proposal is to wait for a model with a larger window.
What is the correct approach?

A. Decompose the task — give each subagent a scoped task, the minimum relevant context, the tools it needs, and clear exit conditions, and have the parent collect results
B. Wait for the larger window, since decomposition adds implementation overhead for the same result
C. Raise `max_tokens`, which increases the space available for the task
D. Disable thinking, which frees the largest share of the window

**Q21 · D6 · Output Handling** (select ONE)
**Request versus guarantee.** A prompt instructs "return only JSON, no other text." It holds across every case the team tested and occasionally fails in production, returning a leading sentence that breaks the parser.
What is the correct characterization and fix?

A. A prompt is a request, so it holds on tested cases and slips on untested ones. Structured outputs constrain generation against a schema, so a schema-violating response cannot be produced in the first place
B. The instruction needs to be repeated in both the system prompt and the user turn
C. The parser should be made tolerant of leading prose, which is the standard approach
D. The failures indicate a model regression and should be addressed by pinning an older snapshot

**Q22 · D6 · Output Handling** (select ONE)
**A schema that still did not parse.** A service uses structured outputs with a JSON schema. Most responses parse. A small number arrive as incomplete JSON, and a few arrive as plain refusal text.
What does correct handling look like?

A. Check `stop_reason` before parsing — a truncated response ended at the token cap and needs a higher limit and a retry, while a refusal overrides the schema and must be handled as a refusal rather than parsed
B. Wrap every parse in a try-catch and retry on failure, which covers both cases
C. Remove the schema, since it is evidently not being enforced
D. Treat both as transient and retry the identical request until it parses

**Q23 · D6 · Output Handling** (select ONE)
**An enum that did not match.** A schema defines an enum with the values `high`, `medium`, and `low`. Downstream code compares the returned value with an exact string match and occasionally fails on a value that looks correct.
What is the defensive practice?

A. Compare case-insensitively, and never define two enum values that differ only in capitalization — returned casing is not guaranteed to match the schema exactly
B. Add every capitalization variant to the enum so all forms validate
C. Convert the enum to a free-text field and normalize in application code
D. Nothing is needed; enum values are returned exactly as defined

**Q24 · D6 · Output Handling** (select TWO)
**What structured outputs cost.** A team is deciding whether to adopt structured outputs across all endpoints and wants an accurate picture of the cost.
Which TWO statements are correct?

A. They add input tokens, because a format-describing prompt is injected into the request
B. The first request against a new schema pays a grammar-compile latency, after which the compiled schema is cached for a period
C. They reduce input tokens, since the schema replaces the formatting instructions in the prompt
D. They are always faster than an unconstrained request, because invalid tokens are never generated
E. They eliminate the need to check `stop_reason`, since the schema guarantees a parseable response

---

## Answer Key & Rationale — Prompt, Context, and Output Handling supplement

**Q12: A.**
- A — The content is right and the form varies, which is the signature of a missing output constraint: the prompt never named the form, the label set, or the stopping point. ✓
- B — Scope drift worsening across turns is what points at a system prompt; here the category is correct every time. ✗
- C — Examples help when the model invents a structure it was never given; here the problem is that no form was specified at all. ✗
- D — Delimiting inputs matters when instructions and data are mixed, which is not the failure described. ✗

**Q13: A.**
- A — Correct task, invented structure is the row that maps to few-shot examples: the model cannot infer an exact structure from a description, and one correct pair shows it. ✓
- B — More prose describing the structure is what has already failed. ✗
- C — Role and scope are steady; the shape is the problem. ✗
- D — A smaller model does not invent less, and capability is not the constraint here. ✗

**Q14: A.**
- A — Mixed inputs with no boundary is the case XML tags exist for. Descriptive names make each region's role unambiguous, so a comment inside the code is not read as an instruction. ✓
- B — A system prompt does not tell the model where the code ends and the docs begin. ✗
- C — Examples of debugged code do not resolve which of the two supplied inputs to debug. ✗
- D — The output shape is not what is failing. ✗

**Q15: A.**
- A — A prompt that gets longer rather than more precise with each pass is the tell that the diagnosis step is being skipped. Name the failure type, add the single technique that matches it, and re-run. ✓
- B — More text is the approach that produced six failed iterations. ✗
- C — Nothing indicates a capability limit; the failure is structural and repeatable. ✗
- D — Raising the tier to compensate for a missing structural piece pays more for the same gap. ✗

**Q16: A.**
- A — There is no reserved tag vocabulary. Descriptive names matching the content are what make the boundary clear, so the search is unnecessary and the work is blocked for no reason. ✓
- B — No such reserved set exists. ✗
- C — Names are not ignored — a descriptive name is what conveys what the region contains. ✗
- D — Tags are the Claude convention for this boundary; substituting headings weakens the delimiter. ✗

**Q17: A.**
- A — Each technique answers a specific failure. Applied to a task with no such failure they cost context and add nothing — the guidance is to simplify, not to stack by default. ✓
- B — Stacking is right when there is a defined output contract with edge cases to cover, not as a universal baseline. ✗
- C — The over-application is the problem, and singling out the system prompt misses it. ✗
- D — A summarization request is not a tool call. ✗

**Q18: A.**
- A — Same task, want the useful knowledge kept, want the bulk shed: that is compaction. What it costs is any detail the summary failed to capture, which is why the summarizer prompt matters. ✓
- B — Clearing discards all session context, and the cost is not nothing — anything needed later must have been persisted. ✗
- C — Pruning rewinds to an earlier point and drops everything after it, so anything learned during the detour is lost, not preserved. ✗
- D — Subagent handoff suits a self-contained subtask, and it costs visibility into how the answer was reached rather than preserving it. ✗

**Q19: A.**
- A — What survives compaction depends entirely on how the summarizer is written. Naming the state the task cannot lose — paths modified, decisions made, errors and their resolutions — is the fix, and under-specified summarizers are among the most common causes of multi-session agent failure. ✓
- B — Compacting less often postpones the loss without changing what the summary keeps. ✗
- C — Clearing discards everything, which is strictly worse when the task is continuing. ✗
- D — The instruction is under-specified; that is a prompting defect, not a capability ceiling. ✗

**Q20: A.**
- A — When a task is too big for one window, decomposition is the fix rather than a bigger window. Each subagent gets a scoped task, minimum context, its tools, and exit conditions, and the parent collects results. ✓
- B — Waiting blocks the work, and a larger window still fills and still degrades as it does. ✗
- C — `max_tokens` caps output for a single response; it does not enlarge the window. ✗
- D — Disabling thinking trades reasoning quality for space and does not make a task that exceeds the window fit. ✗

**Q21: A.**
- A — A prompt asks; it does not constrain. Structured outputs apply the schema during generation, so an invalid response cannot be produced — moving correctness from something verified afterward to something ruled out beforehand. ✓
- B — Repeating a request in two channels is still a request. ✗
- C — A tolerant parser accepts whatever arrives, which abandons the contract rather than enforcing it. ✗
- D — Occasional slippage on untested inputs is the expected behavior of a prompt-level instruction, not a regression. ✗

**Q22: A.**
- A — A guaranteed schema is not a guaranteed success. Check `stop_reason` first: a truncated structure means the token cap was reached and needs a higher limit plus a retry, while a refusal overrides the schema and must be handled as a refusal. ✓
- B — A blanket retry on parse failure re-sends an identical request that will truncate again, and retries a refusal that will refuse again. ✗
- C — The schema is being enforced; these two outcomes are the documented exceptions to it. ✗
- D — Neither is transient, so identical retries do not converge. ✗

**Q23: A.**
- A — Returned casing is not guaranteed to match the schema exactly, so compare case-insensitively — and never define two enum values that differ only in capitalization, since that makes the comparison ambiguous. ✓
- B — Enumerating variants makes the set ambiguous and does not scale. ✗
- C — Dropping to free text discards the constraint entirely. ✗
- D — Exact casing is precisely what is not guaranteed. ✗

**Q24: A and B.**
- A — A format-describing prompt is injected into the request, so structured outputs add input tokens rather than removing them. ✓
- B — A new schema pays a one-time grammar-compile latency on its first request, after which the compiled form is cached for a period. ✓
- C — Reversed: input tokens go up, not down. ✗
- D — "Always faster" is wrong; the first request on a new schema is slower, which is the cost in B. ✗
- E — Refusals and truncation both return non-conforming output, so `stop_reason` still has to be checked. ✗
