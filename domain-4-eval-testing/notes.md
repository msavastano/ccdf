# Domain 4: Eval, Testing, and Debugging — Notes

**Exam weight: 2.6%** — small domain (~1–2 items), but it reuses machinery from D2 (streaming, message structure), D8 (tool schema, pairing), and D1 (memory). Version-sensitive facts verified against platform.claude.com docs **2026-07-18**.

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Debugging and Error Handling | 2.6% | Error type identification; recovery strategies; trace analysis; isolating integration-layer vs. model-output problems |

> **Note on scope.** "Debugging and Error Handling" is the *only* skill the blueprint names under Domain 4 — there is no separately weighted "Eval" skill. Evals still earn their keep because the **decision rules in the big domains cite them**: D5 says move model tiers only when *an eval set* justifies it (16.8%), and D6's prompt-iteration loop is scored *by* an eval (11.0%). Study evals as the instrument those decisions depend on, not as a 2.6% topic.

---

## Debugging and Error Handling (2.6%)

The exam tests **judgment, not stack-trace reading**: given a symptom, *which layer is broken and what class of fix applies.* The discipline that answers both — **localize before you touch code.** A wrong fix at the wrong layer (reword the prompt when the bug is structural) is the classic distractor.

### Localize first — which layer owns the bug?

A Claude agent has four places a bug tends to live. Each has a distinct signature, and the fix class is fixed by the layer — not by how loudly the error shouts.

| Layer | Typical symptom | Where the fix lives | Fix class |
|-------|-----------------|---------------------|-----------|
| **Schema** (tool definitions) | *Systematically* wrong tool selection; the loop code is provably fine | The tool `description` / `input_schema` | Reword the description: state **intent + an exclusion** ("use for X; do NOT use for Y") |
| **Streaming** (assemble & commit) | *Intermittent* 400s that correlate with dropped connections; the *next* turn is corrupted | The assemble-and-commit step | Gate the commit on `message_stop`; keep **all** blocks; discard a partial turn |
| **Context** (message structure) | *Deterministic* 400 on the request right after a tool call — "unpaired tool_result" / "invalid signature" | How you build the `messages` array | Preserve the full assistant content array; pair every `tool_use` ↔ `tool_result` |
| **Memory** (cross-session state) | Works early, fails by session N; the window fills before the current request is processed | `build_session_history` / what you carry forward | Move transcripts to external storage; inject a **summary** at session start |

> 🔑 **The localization tell:** *frequency* separates the layers. **Every time** on the same input → structural / schema (deterministic). **Only sometimes**, tied to network events → streaming (a dropped stream). **Only after several sessions** → memory (accumulation). Match the symptom's *pattern* to the layer before proposing a fix.

### Error-type identification → recovery strategy

The single most testable skill here: **name the error class, because the class dictates whether you retry and where you fix it.**

| Class | Tells | Retry? | Fix |
|-------|-------|--------|-----|
| **Structural** (malformed request) | HTTP `400`; unpaired `tool_result`; edited/stripped thinking-block signature; schema violation | **No** — an identical retry reproduces it | Fix how you *build* the request: message structure, block preservation, schema |
| **Model-output** (valid call, wrong content) | The API call is well-formed but the *content* is wrong — wrong tool, wrong format, hallucinated path | **No** | Upstream: description quality, output constraints / structured outputs, few-shot examples — then validate on receipt |
| **Transient** (server / network) | `429`, `500`, `529`, timeouts, a stream that drops mid-flight | **Yes** — exponential backoff + jitter | Retry; for a dropped stream, **discard the partial turn** and retry from the last complete turn |
| **Capacity** (context window) | Rejected *before* generation (validation error), or `stop_reason: model_context_window_exceeded` mid-generation | **No** — it won't fix itself | Trim or summarize history; the API **never drops your oldest content for you** |

> ➡️ **What the system *does* when one of these fires** — retriable vs. terminal, retry placement, `retry-after`, `is_error`, refusals — is in [Production failure handling](#production-failure-handling--retriable-vs-terminal) below.

> **Integration-layer vs. model-output — the distinction the blueprint names.**
> - **Integration-layer** bug = *your code around the model* (message assembly, pairing, retries, context budget). **Deterministic**; fixed in code.
> - **Model-output** bug = the model produced something **valid but wrong**. **Probabilistic**; fixed upstream with schema / description / prompt structure, then caught by validation.
> The quick diagnostic: does it fail **the same way every time** (integration / structural) or **only on some inputs** (model-output)? Reaching for a prompt tweak on a structural bug — or a schema change on a flaky network error — is the trap.

### Trace analysis

Agents fail **across turns, not in one call** — new failure modes appear only once components run together, so single-turn tests miss them. Debug from the **transcript**: the ordered sequence of assistant/user turns and the block *types* inside each. Most structural bugs are visible as a malformed message array — a `tool_result` with no matching `tool_use` turn, a stripped `thinking` block, a half-built `tool_use`. Standard operational logging (status codes, latencies) won't surface these; you need **transcript-level tooling.** (Ties to D1: agents require transcript-level observability that workflows don't.)

---

## Worked case study — the four-layer cumulative debug

A customer-service agent with extended thinking, one tool, the raw-Messages-API loop, and cross-session memory. **One planted bug per layer** — and two of them are the *same defect seen twice*.

| # | Layer | The bug | Runtime effect | Fix |
|---|-------|---------|----------------|-----|
| 1 | **Schema** | `"description": "Gets data."` — no intent, no exclusion | Claude can't distinguish this tool from any other retrieval tool; routes on surface words | Description that states intent + an explicit "do not use for…" exclusion |
| 2 | **Streaming** | Commits the turn before `message_stop` **and** strips the `thinking` block | A partial `tool_use` enters history; the stripped signed thinking breaks carry-back → next request `400` | Gate the commit on `stop_seen`; keep all blocks; `raise` on interruption |
| 3 | **Context** | A `tool_result` with no complete preceding assistant `tool_use` turn | API sees an unpaired `tool_result` → `400` | **Resolved by fixing Bug 2** — the full assistant turn is now appended first |
| 4 | **Memory** | Concatenates *all* prior session transcripts in-context | Window fills by session 4–5; the request is rejected before work starts | External store + inject a summary only |

> 🔑 **The coupling worth memorizing:** Bugs 2 and 3 are one defect. The broken streaming **commit** is the *root*; the pairing violation is the *symptom*. Fix the commit (preserve every block, gate on `message_stop`) and the context-layer error disappears with no separate change. On the exam, a "fix the tool_result pairing directly" option is a distractor when the real cause is the assemble-and-commit step upstream.

> **Two invariants both break at the commit step**, which is why one root causes two symptoms:
> - **Thinking carry-back** — thinking blocks carry a cryptographic `signature` and must be sent back **unmodified**; stripping or editing them → `400`.
> - **tool_use / tool_result pairing** — every `tool_use` block must be answered by a `tool_result` with a matching `tool_use_id` in the next user turn, and that assistant turn must be committed **in full** first.

**Interactive version:** step through all four with reveal-before-you-look self-tests in `four-layer-debug-walkthrough.html` (repo root).

---

## Production failure handling — retriable vs. terminal

Source: class module *"Failure Handling — surviving production failure: tool errors"* (added 2026-07-19). This continues the error-class table above: that table **names** the classes; this section decides **what the running system does the moment one fires.** Tests tell you a failure exists, the trace tells you where — this is the layer that decides what happens next in live traffic. Production produces failures a prototype never sees: rate limits, timeouts, malformed tool results, transient network errors. Resilient vs. fragile is whether you decided **in advance** how each kind is handled.

### The one question that starts every failure decision

> **Would waiting and re-sending the *identical* request plausibly work?**
> Yes → **retriable.** No → **terminal.**

Retriable causes are transient and sit *outside* the request: momentary over-capacity, a dropped connection, a per-minute limit briefly exceeded. Terminal causes sit *inside* the request: malformed body, expired key, a model name that doesn't exist. Time resolves the first and changes nothing about the second. Every later handling decision depends on which bucket the failure lands in.

On the Anthropic API the **status code tells you the bucket**:

| Status | Meaning | Bucket |
|--------|---------|--------|
| `429` | Rate limit | **Retriable** |
| `529` | Overloaded (Anthropic-side load, *not* a rate-limit signal) | **Retriable** |
| `500` / `502` / `503` / `504` | Server error / timeout — Anthropic-side faults that typically clear | **Retriable** |
| `400` | Bad request | **Terminal** |
| `401` | Auth failure | **Terminal** |
| `403` | Permissions — a retry cannot grant access | **Terminal** |
| `404` | Missing resource (e.g. nonexistent model) | **Terminal** |

```python
RETRIABLE = {429, 529, 500, 502, 503, 504}   # rate limit, overload, transient
TERMINAL  = {400, 401, 403, 404}             # bad request, auth, missing

def is_retriable(status):
    return status in RETRIABLE   # everything else fails fast
```

**Why the distinction carries so much weight:** retrying a terminal error wastes the retry budget and hides the actual problem behind a wall of identical failures. Each unnecessary retry also adds latency that a genuinely retriable failure elsewhere in the flow might have needed. Correct classification *preserves the retry budget for failures that need it.*

**Edge cases worth naming.** A **timeout** is usually retriable — the work may simply have run longer than the client would wait. But *repeated* timeouts on expensive requests is a signal to **fix the request**, not to keep retrying it. A `500` is retriable (server-side, often clears). A `403` is terminal (permissions).

> 🔑 **Default when unsure: treat it as terminal and raise.** The asymmetry is the whole argument — a failure wrongly marked terminal **fails loudly and gets fixed**; a failure wrongly marked retriable **hammers a service and buries the real problem under retries.**

### Know what the SDK already retries before you write your own loop

The Anthropic client libraries **automatically retry transient failures** with progressive retry delays, up to a configurable number of attempts. The point of knowing this is to avoid stacking your own retries on top: **two retry loops around the same call multiply attempts against a rate limit rather than capping them.**

Decide explicitly where the retry lives:

- **Option A** — let the SDK own transient cases; your code owns only application-specific *fallbacks* (cache, simpler path, graceful error).
- **Option B** — turn SDK retries down and own the full path yourself.
- **The anti-pattern** — both layers retrying the same failure, neither aware of the other.

### `retry-after` outranks your backoff

The API returns **rate-limit headers** on each response telling you how much of your limit remains and when it resets. The most useful is **`retry-after`**, included on a `429` or `529`, which states how long to wait. Honoring it is more precise than guessing with backoff, because the service is telling you exactly when capacity returns.

> **Order of precedence:** read `retry-after` first; fall back to exponential backoff **with jitter** only when the header is absent. ⚠️ *Version-sensitive:* specific header names and limit values are version-pinned — confirm against the reference docs at build time (noted 2026-07-19).

### Tool errors must come back to Claude explicitly

When a tool fails, return the result to Claude with **`is_error` explicitly set to `true`** — never a silent empty result.

```python
def run_tool(tool_use):
    try:
        result = execute(tool_use)
        return {"type": "tool_result", "tool_use_id": tool_use.id,
                "content": result}
    except Exception as e:
        # surface the error so Claude can react, do NOT return empty
        return {"type": "tool_result", "tool_use_id": tool_use.id,
                "is_error": True, "content": f"Tool failed: {e}"}
```

With the error surfaced, the model can **react** — try another approach, ask for clarification, or stop. A tool that swallows its own error and returns nothing produces a **confident wrong answer downstream**, because the model treats the empty result as valid data and keeps reasoning on top of it. A visible failure is far easier to catch than a plausible answer built on missing data.

Whether the tool error is *retriable* depends on the underlying cause: retry only if that cause is transient. Returning the flag to Claude is not optional either way.

### Refusal is a `200` — your status-code classifier will never see it

```python
# A refusal is a 200 at the HTTP layer; the retriable classifier will not catch it
if response.stop_reason == "refusal":
    raise ValueError("Model refused the request. Review input before retrying.")
```

A refusal is a **content decision, not a transient error.** Fail fast: raise it to the caller and log it. Do not silently retry it and do not treat it as valid output.

### The failure-handling decision table (keep this open while you build)

| Error type | Retriable or fail fast | Backoff strategy | Fallback behavior |
|------------|------------------------|------------------|-------------------|
| **Rate limit (`429`)** | Retriable | Exponential backoff with jitter, **honor `retry-after`**, capped attempts | After the cap, raise a clean error or route to a cached / simpler result |
| **Overloaded (`529`)** | Retriable | Backoff — reflects Anthropic-side load, *not* a rate-limit signal | Fail over to a fallback path, or return a graceful error if it persists |
| **Bad request (`400`)** | **Fail fast** | No retry — the identical request fails again | Fix or reject the input; surface the error to the caller |
| **Tool result error** | Depends on the tool | Retry only if the underlying cause is transient | Return `is_error: true` to Claude so the model can react — **never silence it** |
| **Refusal (`200`, `stop_reason: "refusal"`)** | **Fail fast** | No retry — a content decision, not a transient error | Raise to the caller and log; don't retry, don't treat as valid output |

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Keeps one bad response from cascading into an outage by handling each failure type *by name* |
| **Adds cost or complexity** | Every failure path is code you write, test, and maintain on top of the happy path |
| **Use a different approach** | Don't retry a terminal error — retrying a `400` only burns retry budget |

---

## Evals and Judges — defining "done" before you ship

Source: class module *"Evals & Judges — defining done before you ship."* Blueprint-adjacent: not its own weighted skill (see scope note above), but it is the mechanism behind the D5 tier-change rule and the D6 iteration loop.

### The design document comes first

Before any production code, write a **one-page design document** stating what you're building and how you'll know it's right. It exists so *you* define correct, instead of rationalizing whatever the model produces later. Four decisions, each concrete enough that someone could check the built system against it:

| # | Decision | What it must state | What it becomes downstream |
|---|----------|--------------------|----------------------------|
| 1 | **Success criteria** | The output for representative cases, specific enough to grade. "Summarize the thread" is uncheckable; "a two-sentence summary listing every action item and its owner" is gradeable | The **cases in your eval set** — writing these first is what makes the eval possible |
| 2 | **Failure handling** | Every error production will throw, each marked **retriable or terminal**, plus what the user gets when recovery fails | The **error paths** (D4 above) — decided on paper, not discovered at the first 429 |
| 3 | **Cost and latency budget** | Per-request budget, monthly cost ceiling, latency target, and the **minimum reliability you refuse to trade away** — set *before* architecture | The budget you **instrument against**; lets you check the architecture before writing code (D5 · Cost and Token Management) |
| 4 | **Trust boundary** | Which content the agent reads that *someone else can write*, and the smallest set of actions/access the feature needs | The **input you treat as data** and the action you gate with a hook (D7 · least privilege) |

> 🔑 **Why the document is first, not documentation.** Every production layer is *based on* it — criteria become eval cases, failures become error paths, budgets become instrumentation, the boundary becomes a hook. Writing the four once, up front, is what keeps the layers solving the same problem instead of four different ones. If you're building with an agentic coding tool, this document is also what you hand it **before** it writes anything: clear criteria + explicit constraints → fewer assumptions and code you can check against an agreement you already made.

### What an eval is

> An eval works like a thermometer: it doesn't make the patient healthier, it gives you a number you can trust.

Collect input cases → write the expected behavior for each → run the feature on every case → grade each output → average. That collection of cases, expectations, and grades **is** the eval. Before it, "done" is a feeling after a few manual tries; after it, "done" is a score on a fixed set.

The pipeline is the same small framework every time — load a dataset, run each case, grade, average:

```python
def run_test_case(test_case):
    """Run one case through the feature, then grade the result."""
    output = run_prompt(test_case)
    score = grade(test_case, output)
    return {"output": output, "test_case": test_case, "score": score}

def run_eval(dataset):
    """Run every case and report the average score."""
    results = [run_test_case(c) for c in dataset]
    average = sum(r["score"] for r in results) / len(results)
    print(f"Average score: {average}")
    return results
```

**The absolute score is not the signal.** A first attempt scoring 2–3 out of 10 is normal. What matters is whether the number *moves up* as you change the prompt, the tools, or the model — **one at a time.**

### Choosing the grading method — match it to the shape of the output

| Task type | Grading method | What it catches | Where it is unreliable | Cost per case |
|-----------|----------------|-----------------|------------------------|---------------|
| Single correct label or value | **Exact / string match** | A wrong answer when exactly one answer is correct, zero ambiguity | Fails every valid paraphrase or reordering — wrong for anything open-ended | ~0 (local) |
| Structured or code output | **Code-graded check** | Invalid JSON, unparseable code, out-of-range numbers, missing required fields | Says nothing about whether content is *good*, only that it's well-formed | ~0 (local) |
| Open-ended quality | **LLM-as-judge** | Faithfulness, instruction-following, completeness, tone — things no code rule expresses | Noisy and costly; produces a confident-looking number that **means nothing until calibrated** | 1 extra API call |

A code grader is often just a parse attempt — parses, score 10; throws, score 0:

```python
import json, ast

def validate_json(text):
    try:
        json.loads(text.strip()); return 10
    except json.JSONDecodeError:
        return 0

def validate_python(text):
    try:
        ast.parse(text.strip()); return 10
    except SyntaxError:
        return 0
```

**The worked comparison.** Feature returns three capital cities as a JSON array, in a different order than your reference string: exact match scores **0** (characters don't line up) though the answer is *correct*; a code grader that parses and checks membership scores it **10**. Now the feature returns a one-paragraph rationale: the code grader can only confirm it's a non-empty string (near-worthless), exact match is hopeless (no two good rationales are worded alike), and **only a judge** can say whether it's faithful and complete.

> 🔑 **The rule:** one correct form → match. A structural rule → code check. Open-ended quality → judge. **Using a judge where a code check suffices adds cost and variance for no gain.**

> **The cost dimension the table understates.** Match and code checks run locally at effectively zero cost, so you can run thousands on every change. A judge is one extra model call *per case* — a 1,000-case eval means 1,000 extra API calls every run. Reasonable as a periodic full pass; wasteful as a tight inner loop. Common practice: **grade format/structure with code on every commit; reserve the judge for a slower scheduled quality pass.**

### Building and calibrating the judge

A judge is a second model call guided by a rubric. What makes it usable: **ask for strengths, weaknesses, and reasoning alongside the score** — not the score alone. Without reasoning, models drift toward a safe middle number (usually ~6) regardless of actual quality. Reasoning first is what anchors the score to something specific.

```python
def grade_by_model(task, solution):
    eval_prompt = f"""
    You are an expert reviewer. Evaluate the solution for the task.
    Task: {task}
    Solution: {solution}
    Return JSON with:
      "strengths":  array of 1-3 points
      "weaknesses": array of 1-3 points
      "reasoning":  a one to two sentence explanation, 50 words maximum
      "score":      a number from 1 to 10
    """
    messages = [{"role": "user", "content": eval_prompt}]
    result = chat(messages)
    return json.loads(result)
```

**Calibration is the step most people skip — and it's what makes the judge trustworthy.** Start from cases a human has already labeled, run the judge on the same cases, and **measure agreement with the human labels**. A judge that disagrees half the time produces a rigorous-looking number with no value. If agreement is low, fix the *rubric*: tighten what each score means, add an example of a good and a bad answer, re-measure.

### Coverage beats perfection

A **larger** eval set with slightly noisier automated grading usually reveals more than a small hand-graded set. Twenty cases including irregular and edge inputs will catch a regression that three carefully chosen cases never exercise. When you need more cases, have Claude **generate additional ones from a small labeled seed set**, then spot-check the generated cases so the set stays honest. *Coverage catches edge cases, and coverage comes from volume.*

### The iteration loop

Set a goal → write an initial prompt → run the eval → read where it failed → apply **one** prompt-engineering change → re-run. Repeat the last two until the score holds.

- **Change one component at a time.** Rewrite the prompt, add two examples, and swap the model in one pass, and a score change teaches you nothing about which lever did it. Slower per iteration, far faster over the life of the feature.
- **Read the per-case breakdown, not just the average.** A steady average hides a change that fixed three cases and broke three others. The average conceals it; the per-case view shows it immediately.
- **A low score is information — ask *why*, not *whether*.** Formatting failure → the prompt's output instructions. Factual failure on retrieved content → the retrieval step. Failure only on long input → context handling. That categorization is what makes the next iteration a targeted fix rather than a guess.

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Turns "looks right" into a tracked score you can defend, and moves it one deliberate change at a time |
| **Adds cost/complexity** | Authoring cases and calibrating a judge is real up-front work before any feature ships |
| **Use a different approach** | For a single fixed-format output, a code check alone is enough — **skip the judge entirely** |

---

## Testing and tracing — the layer underneath the eval

Source: class module *"Testing & Tracing."* Added 2026-07-19.

An eval gives you **what good looks like as a number**. It does not tell you **where** a failure happened, and it does not stop a *passing* eval from hiding a break somewhere else in the workflow. A graded target needs two things underneath it: **tests that isolate each failure type**, and **traces that show which step produced the bad result.**

### The four test levels — each catches what the others miss

A test is only useful if you know **which failure it identifies**. Ordered narrowest → widest:

| Level | What it isolates | What it cannot catch |
|-------|------------------|----------------------|
| **Unit** | One function on its own — a parser, a tool wrapper | Anything about how components fit together |
| **Functional** | One Claude call returning the expected **shape** for a given input (right fields, right types, parseable) | Failures in the system *around* that single call |
| **Integration** | The **seam** where two components hand off — e.g. retrieval result → model call | Whole-flow behavior that only emerges end to end |
| **End-to-end** | The full flow as a user runs it, input → output | *Where* the break is — it sees only the final result |

> 🔑 **Where the silent production breaks live: the integration level.** Each side of a handoff can pass its own unit and functional tests while the **seam between them** is broken — retrieval returns fine, the model call is well-formed, and the thing passed between them is wrong. This is the level teams skip and the one the exam is most likely to make the correct answer.

> **The cost/localization tradeoff runs down the table.** Narrow tests are fast and localize precisely but see nothing about composition; end-to-end catches breaks that only appear when everything runs together, at the price of being the slowest to run and the hardest to localize. You want both ends, not one.

### Tracing — turning "it failed" into "step 4 failed"

Tests tell you a failure **exists**. They don't tell you **which step caused it**. That's what a trace adds.

A trace records each step of a run: **the prompt, the tool calls, the intermediate outputs, and the timing.** It reads like a timeline, and the failing step is usually obvious once the intermediate output is visible:

```
[trace run_id=8f21c]  case: "Where is my refund?"
  step 1  retrieve(query)        ok    42ms   -> 3 chunks
  step 2  build_prompt(chunks)   ok     1ms   -> prompt 1,240 tok
  step 3  model.call(prompt)     ok   980ms   -> answer "..."
  step 4  parse(answer)          FAIL   2ms   -> KeyError: amount
          final score: 0   (failure localized to step 4, the parser)
```

Without the trace, a failed eval says *something is wrong*. With it: *"step four — the parser raised a `KeyError` on a field the model did not return."* That is the difference between a five-minute fix and a day of hand-tracing the workflow.

> **Tracing is also what makes a change reviewable.** You can show **the step that moved**, not just the score that dropped. Ties directly to the D4 localization discipline above — a trace is the mechanical version of "localize before you touch code."

### Tradeoff summary

| | |
|---|---|
| **Handles well** | Localizes a failure to a **specific step**, and matches each test level to the break it can actually see |
| **Adds cost/complexity** | Tracing plus four test levels is **infrastructure you build and maintain** — not free instrumentation |
| **Use a different approach** | Where the flow is one call with one fixed output shape, a functional test plus a code-graded eval is enough; skip the tracing layer |

> **Routing between retrieval strategies** was taught in this same module but is a **retrieval-architecture** decision — the cheap classifier that sends single-fact lookups to fetch-once and multi-part questions to agentic search lives in [Domain 6 · Context Engineering → retrieval](../domain-6-prompt-context/notes.md). Its D4 connection: **the router is another step your trace has to record** — a wrong path choice looks like a bad answer unless the trace shows which branch ran.

---

## Cross-domain pointers

- **Eval sets as the precondition for a model-tier change (up to Opus / down to Haiku)** → [Domain 5 · Model Selection and Tradeoffs](../domain-5-model-selection/notes.md).
- **The prompt-iteration loop the eval scores; output constraints and structured outputs** → [Domain 6 · Prompt Engineering](../domain-6-prompt-context/notes.md).
- **Cost/latency budgets and instrumentation (design-doc decision 3)** → [Domain 5 · Cost and Token Management](../domain-5-model-selection/notes.md).
- **Trust boundary, least privilege, hooks as gates (design-doc decision 4)** → [Domain 7 · Security and Safety](../domain-7-security/notes.md).
- **SDK auto-retry behavior, rate-limit headers / `retry-after`, `stop_reason` values** → [Domain 2 · Claude API Mechanics](../domain-2-applications/notes.md).
- **Streaming events, partial-turn discard, `stop_reason` handling** → [Domain 2 · Claude API Mechanics](../domain-2-applications/notes.md).
- **Tool schema description quality, block-pairing invariant, thinking carry-back** → [Domain 8 · Tool Implementation](../domain-8-tools-mcps/notes.md).
- **Memory scope (in-context vs. external vs. summarized vs. stateless)** → [Domain 1 · Agent memory](../domain-1-agents/notes.md).
- **Context-window ceilings, pruning / compaction / clearing** → [Domain 6 · Context Engineering](../domain-6-prompt-context/notes.md).
- **Shipping an eval as a portable asset (dataset + rubric together), and using it as the model-promotion gate against a pinned baseline** → [Domain 2 · Packaging for Reuse](../domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator).

## Exam traps to remember

1. **Retrying a `400` is never the fix** — structural errors reproduce on retry. Backoff + jitter is for `429`/`5xx`/timeouts only.
2. **A prompt tweak can't fix a structural bug** (pairing, signature, schema) — those live in how you build the request.
3. **Localize by frequency:** every-time = deterministic/structural; sometimes = model-output or a dropped stream; only-after-N-sessions = memory accumulation.
4. **Fix the root, not the symptom:** the tool_result pairing error is usually caused *upstream* at the assemble-and-commit step — don't patch the `tool_result` append.
5. **Don't reach for a judge when a code check would do** — if the output has one correct form or a structural rule, a match or parse check is cheaper, deterministic, and runnable on every commit. The judge is for open-ended quality only.
6. **An uncalibrated judge is not evidence.** Agreement with human labels must be *measured* before its scores are used; a judge asked for a bare score drifts to ~6 regardless of quality.
7. **The average hides regressions** — always read per-case results. And change **one** lever per iteration or you learn nothing about what moved the number.
8. **Coverage > perfect rubric.** Twenty noisier cases including edge inputs beat three hand-graded ones.
9. **A passing eval is not a working system.** The eval scores the final output; a break at an internal seam can hide behind a score that still looks fine. Tests localize, the eval grades — they are not substitutes.
10. **Integration is the level teams skip and the one that hides silent failures** — both sides of a handoff can pass their own tests while the seam between them is broken.
11. **End-to-end tests prove a break exists but not where it is.** If an option says "add an E2E test to find which step failed," that's the wrong instrument — you want a **trace**.
12. **A trace records prompt, tool calls, intermediate outputs, and timing.** Status codes and latency logs alone (standard operational logging) won't localize a workflow failure.
14. **The retriable test is one question:** would waiting and re-sending the *identical* request plausibly work? `429`/`529`/`5xx`/timeouts → yes. `400`/`401`/`403`/`404` → no. When unsure, choose **terminal** — loud failures get fixed, silent retries hide the cause.
15. **`529` is not a rate limit.** It's Anthropic-side overload. Still retriable, but "reduce your request rate to fix a 529" is a distractor.
16. **Don't stack retry loops.** The SDK already retries transient failures; wrapping your own loop around it *multiplies* attempts against a rate limit. Pick one owner.
17. **`retry-after` outranks your backoff.** When the header is present it's authoritative; exponential backoff + jitter is the fallback for when it's absent.
18. **A failed tool must return `is_error: true`, never an empty result.** A silenced tool error becomes a confident wrong answer — the model treats the empty result as valid data.
19. **A refusal is HTTP `200` with `stop_reason: "refusal"`.** A status-code-based classifier will never see it. Fail fast and log; it's a content decision, not a transient fault.
20. Neither context-ceiling failure **silently drops** your oldest content — one rejects before generation, the other returns `stop_reason: model_context_window_exceeded`. Trimming is your job, not the API's.
