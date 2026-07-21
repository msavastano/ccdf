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
