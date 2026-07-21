# Domain 6: Prompt and Context Engineering — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Prompt Engineering

**Q:** A prompt works in interactive testing but breaks in production. What's the fix?
**A:** Identify the missing **structural piece** and add that one technique — not more words. Rewording changes how you say something; it doesn't supply missing structure.

**Q:** What are the four structural techniques for a reliable output shape?
**A:** System prompt, XML tags, few-shot examples, output constraint.

**Q:** Output comes back in the wrong **shape** (a sentence where you wanted a label). What's missing?
**A:** An **output constraint** — the prompt never specified form, field names, or stopping point.

**Q:** Content drifts / scope widens and it gets worse deeper into the conversation. What's missing?
**A:** A **system prompt** (or a more specific one) — nothing is holding role, scope, and format steady across turns.

**Q:** Claude does the right task but **invents a structure** you never asked for. What's missing?
**A:** **Few-shot examples** — Claude can't infer an exact structure from a description alone; one correct pair shows it.

**Q:** Output is clean on tested inputs but breaks on an edge-case variant. What's missing?
**A:** A **constraint covering the variant** — name it in the constraint or add an example for it. The prompt only handled the happy path.

**Q:** When do XML tags solve the problem, and must you use official tag names?
**A:** When the prompt **mixes inputs with instructions** (e.g., code + docs). Use **descriptive** names (`<my_code>`, `<docs>`) — official/reserved names are not required.

**Q:** In the classifier before/after, what distinct job does each of the three techniques do?
**A:** System prompt = output contract (one label from a fixed set, nothing else); XML tags = separate examples from the instruction; few-shot pairs = show exact casing/format.

**Q:** What's the tell that you're skipping diagnosis and just padding the prompt?
**A:** The prompt keeps getting **longer** each iteration instead of **more precise**. Stop and diagnose the failure type first.

**Q:** When should you NOT stack all four techniques?
**A:** On a simple task that needs one (e.g., "summarize this paragraph" needs no few-shot examples or output schema). Stack all four only against a clearly defined output contract.

## Output Handling

**Q:** Why is a prompt instruction like "respond only in JSON" unreliable in production?
**A:** The prompt is a **request** — it holds on tested cases and slips on an untested edge case (stray sentence, wrong field name, malformed JSON).

**Q:** What is constrained decoding?
**A:** The API only allows tokens that keep the output valid against your JSON schema as Claude generates, so a schema-violating response can't be produced in the first place.

**Q:** JSON outputs vs. strict tool use — what does each constrain?
**A:** `output_config.format` (JSON outputs) constrains Claude's **final response text**; `strict: true` constrains the **arguments Claude passes to your tools**.

**Q:** With structured outputs on, does a schema guarantee a successful parse?
**A:** No. `stop_reason: refusal` (safety; text overrides schema) and `stop_reason: max_tokens` (truncated mid-structure) still return non-conforming output. Always check `stop_reason`.

**Q:** Two "gotchas" beyond stop_reason when handling structured output?
**A:** Enum **casing isn't guaranteed** (compare case-insensitively; never define values differing only by case); structured outputs **add** input tokens and pay a first-call grammar-compile latency (cached 24 h).

**Q:** A malformed tool argument would crash your function in an agentic loop. Prompt instruction or API constraint?
**A:** API constraint — `strict: true` on the tool, validated before your code runs. Don't trust a prompt instruction for this.

**Q:** What does "skepticism toward confident output" mean in practice?
**A:** Confident-sounding ≠ validated. Constrain what you can at the API, still check `stop_reason`, and validate values a schema can't enforce (ranges, referential integrity, business rules).

## Context Engineering

**Q:** What is context engineering, in one line?
**A:** Deciding *in advance* what enters the context window, what comes back out as a summary, and what never enters at all.

**Q:** What happens to every tool result in an agent session?
**A:** It's appended to the context window and stays there for the rest of the session — invisible in a single turn, decisive across ten to twenty tool calls.

**Q:** The two ways a request hits the context ceiling — and does either silently truncate?
**A:** Larger-than-window → rejected before generation with a validation error; fits but generation hits the ceiling → returns output so far with `stop_reason: model_context_window_exceeded`. Neither drops your oldest content.

**Q:** To run a session past the window limit, whose job is trimming/summarizing history?
**A:** Your application's — the API won't drop old content for you. Trim or summarize before the next request goes out.

**Q:** Why does a workload pass every dev test and then fail in production on context?
**A:** Prod tool outputs run 3–5× longer than test fixtures and sessions run more turns, so a window that held 20 turns in testing fills at turn 8.

**Q:** Name the four budget strategies.
**A:** Pruning, compaction, clearing, subagent handoffs.

**Q:** Pruning vs. clearing — the difference?
**A:** Pruning rewinds to an earlier message and drops what came after (same task, continue on); clearing starts a brand-new empty context (the next task is completely different).

**Q:** When compaction is manual, what decides what the agent remembers next turn?
**A:** The summarizer prompt you write. "Summarize the conversation so far" loses task-critical state; specify file paths modified, decisions made, and errors + resolutions.

**Q:** `/compact` and `/clear` are Claude Code commands — what are the API equivalents?
**A:** Clearing = a new session; compaction = server-side compaction (beta) the platform runs, or manual client-side summarization.

**Q:** A task is too big for one context window. Is the fix a bigger window?
**A:** No — decompose and hand off to a subagent with a scoped task, minimum relevant context, the tools it needs, and clear exit conditions; the parent collects the summary.

**Q:** What do you give up with a subagent handoff?
**A:** Visibility into *how* it reached its answer — the intermediate steps are discarded with the subagent's context.

**Q:** The three break points of a RAG path?
**A:** Chunking (unit size + overlap), embedding match (semantic similarity vs. exact term), assembly (chunks must reach the model in the structure the prompt expects).

**Q:** Why run a lexical match alongside the semantic one in retrieval?
**A:** Similarity search returns semantically close content, not the exact term; a query for a specific identifier can miss its chunk if a more semantically similar one outranks it.

**Q:** Retrieval index vs. agentic search — when is each better?
**A:** Index for a stable corpus with simple lookups (inspectable, but you build/store/sync/secure it); agentic search for a changing corpus or multi-step questions (no staleness, but more tokens and time per query).
