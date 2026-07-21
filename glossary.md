# Glossary — CCDV-F

Key terms from the class modules, mapped to the exam blueprint. Alphabetical. Each entry is tagged with its home **domain · skill** and links to where the concept is developed in depth in the domain notes. Terms here are cross-domain by nature — the glossary is the single place they all live; the notes are where the tradeoffs and decision criteria sit.

**Modules folded in so far:** *Production-Grade Prompting, Agents & Tool-use* (→ review sheet [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md)) · *Claude Code, MCP & Integration* (→ review sheet [`capstone-claude-code-mcp-integration.md`](capstone-claude-code-mcp-integration.md)) · *Evals & Judges* and *Testing & Tracing* (→ [Domain 4 notes](domain-4-eval-testing/notes.md)) · *Cost & Orchestration* (→ [Domain 5 notes](domain-5-model-selection/notes.md#observability--instrument-before-you-optimize) and [Domain 1 · Orchestrator-worker](domain-1-agents/notes.md#orchestrator-worker--parallel-exploration-at-a-15-token-multiplier)) · *Production Engineering, Evals & Security* (→ [Domain 7 notes](domain-7-security/notes.md) and [Domain 2 · Errors, retries, and rate-limit headers](domain-2-applications/notes.md)) · *Packaging for Reuse* — Module 5, lesson 1 (→ [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator)) · *Contributing Back* — Module 5, lesson 2 (→ [Domain 2 · Contributing Back](domain-2-applications/notes.md#contributing-back--from-private-reuse-to-shared-infrastructure)) · *Trust Boundaries* — Module 5, final lesson (→ [Domain 2 · Multi-Component Applications](domain-2-applications/notes.md#multi-component-applications--trust-boundaries-where-components-meet)) · *Accelerators & IP Contribution* — Module 5 recap (→ review sheet [`capstone-accelerators-ip-contribution.md`](capstone-accelerators-ip-contribution.md)).

> How to use this: skim the index to place a term, click through to the notes for the reasoning the exam actually tests. Definitions are tightened from the class modules; exam-angle and version flags added per project standards.

## Quick index

| Term | Domain · Skill | One-liner |
|------|----------------|-----------|
| [Accelerator](#accelerator) | D2 · Systems Life Cycle (D1/D8/D4 · asset types) | A build packaged so the next engagement **configures** it instead of rewriting it |
| [Agent template](#agent-template) | D1 · Agent Construction (D2 · packaging) | Prompt + tool schemas + loop, with domain values pulled into documented config |
| [Agentic search](#agentic-search) | D6 · Context Engineering (D8 · Tools) | Model issues its own queries across rounds — no index, no staleness, more tokens |
| [Claude Agent SDK](#claude-agent-sdk) | D1 · Agent Construction | Managed runtime for the Claude Code agent loop, embeddable in your product |
| [CLAUDE.md](#claudemd) | D3 · Claude Code Operation | Project file prepended to context every session; dilutes with size |
| [Context window](#context-window) | D6 · Context Engineering | All tokens a model processes in one request |
| [Contribution readiness](#contribution-readiness) | D2 · Systems Life Cycle (D8 · channels) | The five things a maintainer needs to **verify** a contribution — quality is not one of them |
| [Data residency](#data-residency) | D2 · Application Design (D7 · Compliance, D1 · routes) | A rule that data must be **processed in a specific country or region** — **pass-or-fail**, not a tradeoff |
| [Deployment platform](#deployment-platform) | D2 · Configuration Management (D7 · residency) | Where the workload runs — decided by the customer's **existing cloud and compliance posture** |
| [Design document](#design-document) | D4 · Eval/Debugging (D2 · Application Design) | One page fixing success criteria, failure handling, budget, trust boundary — *before* code |
| [Eval](#eval) | D4 · Eval, Testing, Debugging | Fixed case set + expected behavior + grading; turns "looks right" into a trackable score |
| [Exponential backoff](#exponential-backoff) | D2 · Claude API Mechanics (D4 · failure handling) | Growing retry interval + jitter, capped — and `retry-after` beats your math |
| [Function signature](#function-signature) | D8 · Tool Implementation | A function's name + parameters; the shape a tool schema declares |
| [HITL](#hitl-human-in-the-loop) | D1 · Agent Patterns | A human approval step before a consequential action |
| [Hook](#hook) | D3 · Claude Code Operation (D7 · Claude Hooks) | A command bound to a lifecycle event — **deterministic**, unlike an instruction |
| [Hook-based guardrail](#hook) → *see* Hook | D7 · Guardrails and Safe Deployment | The same mechanism used as an **enforced control**: `PreToolUse` blocks and logs |
| [Integration test](#integration-test) | D4 · Eval, Testing, Debugging | Tests the **seam** between two components — where silent failures hide |
| [LLM-as-judge](#llm-as-judge) | D4 · Eval, Testing, Debugging | A second model scoring open-ended output against a rubric — **worthless until calibrated** |
| [Model version pinning](#model-version-pinning) | D2 · Configuration Management (D5 · model selection) | A dated/full model ID fixes the snapshot; an **alias moves under you** |
| [Model alias vs. pinned ID](#model-version-pinning) → *see* Model version pinning | D2 · Configuration Management | An alias is *the current edition of a book*; a pin **cites a fixed edition** |
| [MCP](#mcp-model-context-protocol) | D8 · MCP Server Development | Open protocol: a client attaches to a server exposing tools, resources, prompts |
| [MCP transport](#mcp-transport) | D8 · MCP Server Development | stdio (local subprocess) vs. HTTP (remote); decides who can connect |
| [Observability](#observability) | D5 · Cost and Token Management | Three metrics on every call — tokens, latency, error rate — so cost traces to a step |
| [Orchestrator-worker](#orchestrator-worker) | D1 · Agent Patterns | Lead agent fans subtasks out to parallel subagents — **~15× tokens** |
| [Permission mode](#permission-mode) | D3 · Claude Code Operation | How often the agent stops to confirm; **deny rules override every mode** |
| [Pinned baseline](#pinned-baseline) | D2 · Configuration Management (D4 · evals) | The score a new model version must meet **before** it goes live |
| [Portable eval suite](#portable-eval-suite) | D4 · Eval, Testing, Debugging (D2 · packaging) | Dataset **and** rubric shipped together, runnable in the next team's context |
| [Plugin](#plugin) | D3 · Claude Code Operation | Versioned bundle of skills/hooks/subagents/MCP servers, installed in one step |
| [Prompt injection](#prompt-injection) | D7 · AI Application Security | Instructions hidden in fetched content, obeyed because context is **one undifferentiated stream** |
| [Query router](#query-router) | D6 · Context Engineering (D4 · tracing) | Cheap classification call picking the retrieval path per query — worth it only on mixed traffic |
| [Refactor](#refactor) | D2 · Software Engineering Foundations | Change code's structure without changing its behavior |
| [Reliability floor](#reliability-floor) | D5 · Cost and Token Management (D4 · evals) | Stated latency/retry baseline set **before** cost tuning; cost is optimized above it |
| [Retriable vs. terminal error](#retriable-vs-terminal-error) | D4 · Eval, Testing, Debugging (D2 · API Mechanics) | **The first question on any production failure** — back off, or fail fast |
| [Rules instruction file](#rules-instruction-file) | D3 · Claude Code Operation | Guidance scoped to a path — loads only where it applies |
| [SOC 2](#soc-2) | D7 · Security and Safety | AICPA audit framework for how a vendor handles customer data |
| [State](#state) | D1 · Agent Patterns | What an agent carries between turns |
| [stop_reason](#stop_reason) | D2 · Claude API Mechanics | API field: why the model stopped (`end_turn` / `tool_use`) |
| [Subagent](#subagent) | D1 · Agent Architecture | A clean-context agent spun up by an orchestrator for a subtask |
| [Token](#token) | D5 · Cost and Token Management | The unit Claude measures and prices text in |
| [Trace](#trace) | D4 · Eval, Testing, Debugging | Step-by-step record of a run — prompt, tool calls, intermediate outputs, timing |
| [Trust boundary](#trust-boundary) | D7 · Security and Safety (D4 · design doc) | The line between content someone else can write and actions the system may take |
| [tool_use block](#tool_use-block) | D8 · Tool Implementation | Assistant block requesting a function call; needs a matching `tool_result` |

---

## Definitions

### Accelerator
`D2 · Systems Life Cycle` (asset types in `D1`, `D8`, `D4`)

A solution **packaged so future engagements start from a working foundation rather than a blank repository**. You take a build that works, separate the parts that are customer-specific, and expose them as **parameters with documented defaults** — the asset then gets *configured* rather than rewritten.

**Packaging for reuse** is the operation: separate engagement-specific code from the reusable core, parameterize the rest. It produces one of three asset types — an [agent template](#agent-template), an **MCP server package**, or a [portable eval suite](#portable-eval-suite) — and each parameterizes differently.

🔑 **"The scripts run, so it's reusable" is the trap.** Loose scripts with customer-specific values scattered across files get **copied and diverged**, not configured. ⚠️ And packaging isn't free: for a **one-off the customer will never reuse**, the separation and documentation overhead loses — ship the build and move on. Package **while the build is fresh**; reconstructing intent months later costs more.

→ Developed in: [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator) (three asset types, the packaging checklist, the audit bundle).

### Agent template
`D1 · Agent Construction with Claude` (packaging in `D2 · Systems Life Cycle`)

An [accelerator](#accelerator) built from a working agent: the **system prompt, the tool schemas, and the loop structure**, with every domain-specific value pulled into **configuration with documented defaults**. The test of correct packaging is that a new team **sets values rather than editing the loop**.

What must be parameterized: prompts, paths, scopes, **credentials by reference** (the parameter names the secret; it never carries the value), and thresholds. What must be documented: environment assumptions, expected inputs, handled failure modes, and the eval that defines "working."

→ Developed in: [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator); loop and construction mechanics in [Domain 1 · Agent Construction](domain-1-agents/notes.md).

### Agentic search
`D6 · Context Engineering` (mechanics in `D8 · Tools and MCPs`)

Retrieval in which the **model issues its own queries, reads the results, and refines across several rounds**, instead of fetching a fixed set of context once. It is tool-driven reading at the moment of need rather than matching against an index built in advance.

**The tradeoff, in one line:** you gain multi-step question handling and **no index to build, sync, secure, or let go stale**; you pay **more tokens and more latency per query**, over a **less inspectable** process (you can't point at the chunks a query returned).

🔑 **The distinction the exam tests is timing, not accuracy.** Classical RAG and agentic search both find a relevant slice and generate from it — RAG matches against a **pre-built** index, agentic search finds the slice **at query time**. That's why the corpus decides: a **stable** reference corpus with **simple lookups** favors the index; a **changing** corpus or **multi-step** questions favor search. ⚠️ Any "agentic search beats the index by X%" headline is version-pinned — don't quote a number.

→ Developed in: [Domain 6 · The RAG path and its three break points](domain-6-prompt-context/notes.md); routing between the two paths under [Query router](#query-router); tool-call mechanics and the context cost of tool definitions in [Domain 8](domain-8-tools-mcps/notes.md).

### Claude Agent SDK
`D1 · Agent Construction with Claude`

A managed agent runtime distributed as `@anthropic-ai/claude-agent-sdk` (TypeScript) / `claude-agent-sdk` (Python). It gives you programmatic access to the same agent loop that powers Claude Code — iterate, execute tools, observe, terminate — so you can embed an agent **inside your own product** instead of running Claude Code in a terminal. Distinct from the **Anthropic SDK**, which is a thin convenience wrapper over the API and does **not** run an agent loop.

It exposes the **same agent loop Claude Code runs in the terminal** — so it can be invoked from code, with the permission mode and available tools set programmatically and no interactive session required. 🔑 **The same permission model and deny rules that apply in the terminal apply in the SDK** — headless is not unpermissioned. Loading `.claude` sources (skills, settings) into an SDK run requires **`settingSources`** to be configured.

→ Developed in: [Domain 1 · Agent Construction — the three wiring paths](domain-1-agents/notes.md) (raw Messages API loop vs. Agent SDK vs. Managed Agents); skill-loading mechanics per runtime in [Domain 3 · Skills](domain-3-claude-code/notes.md). The Anthropic SDK contrast belongs to [Domain 2 · Claude API Mechanics](domain-2-applications/notes.md).

### CLAUDE.md
`D3 · Claude Code Operation`

A Markdown file at the root of a Claude Code project whose contents are **prepended to the context window at the start of every session**. It holds the universal project constraints, conventions, and commands that should apply **unconditionally** across all sessions — most usefully, the conventions an agent would otherwise infer from surrounding legacy code.

⚠️ **It dilutes with size.** Files past roughly **200–300 lines** risk burying critical rules under content weight. Path-specific guidance belongs in a [rules instruction file](#rules-instruction-file); anything that must happen *every time regardless of what the model decides* belongs in a [hook](#hook), not here.

→ Developed in: [Domain 3 · Durable Project Context](domain-3-claude-code/notes.md) (the four-mechanism map) and the settings hierarchy in the same file. Cross-interface framing in [Domain 2 · Instruction interpretation across interfaces](domain-2-applications/notes.md).

### Contributing back
`D2 · Systems Life Cycle` (also `D2 · Configuration Management`)

Moving an asset from **private reuse into shared infrastructure** through a **documented channel** — one that carries the **version, installation steps, and components as a single unit**, so a team that never spoke to you installs it and gets the same working setup. A packaged [accelerator](#accelerator) is already most of the way there: its parameters prove it can be *configured*, its documented assumptions name the environment it expects, and its bundled [eval](#portable-eval-suite) gives the maintainer a way to confirm it still works.

**Match the contribution to the channel.** The **Claude Cookbook** is a GitHub repo of **focused reference implementations** — self-contained single- or multi-pattern examples working end to end. **MCP servers and tools** each live in **their own repository with their own conventions**.

**The maintainer's bar is verifiability, not cleverness:** the code **does one thing**, an **example shows it running**, a **test proves it works**, and a **short statement names the assumptions** (otherwise the first failure becomes the maintainer's problem).

🔑 **Channel mismatch is the top stall cause** — a full multi-component application sent to the Cookbook doesn't fit what reviewers look for and never gets reviewed. ⚠️ **Rights and attribution gate *before* technical review**: confirm the right to contribute engagement code and attribute prior work, or it becomes a problem legal must unwind later. When an engagement licensing constraint **can't be cleared, escalate to the owner — don't contribute**.

→ Developed in: [Domain 2 · Contributing Back](domain-2-applications/notes.md#contributing-back--from-private-reuse-to-shared-infrastructure); the packaging that precedes it in [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator).

### Contribution readiness
`D2 · Systems Life Cycle` (channels in `D8`)

**What a maintainer needs in order to verify a contribution** — the review bar, stated as five items: **focused code** that does one thing, a **runnable example**, a **test that proves the behavior**, a **statement of environment assumptions**, and **confirmed rights** to contribute the code.

🔑 **The bar is verifiability, not quality.** Well-written code a reviewer cannot verify **sits at the back of the queue**; the five items exist so a stranger can confirm the asset works without talking to the author. ⚠️ **Rights clear *before* technical review**, not in parallel — and an engagement licensing constraint that **can't** be cleared means **escalate to the owner, don't contribute**. The other stall cause isn't readiness at all but [channel mismatch](#contributing-back): the right asset in the wrong channel never gets reviewed either.

→ Developed in: [Domain 2 · The contribution-readiness reference](domain-2-applications/notes.md#the-contribution-readiness-reference); the packaging that produces most of it in [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator); routed in [`capstone-accelerators-ip-contribution.md`](capstone-accelerators-ip-contribution.md).

### Context window
`D6 · Context Engineering` (also `D5 · Cost and Token Management`)

The total number of **tokens** a model can process in a single request — system prompt, conversation history, tool definitions, tool results, **and the model's own output**. When the running total reaches the limit, earlier content must be removed or summarized before new content can be added.

→ Developed in: [Domain 6 · Context Engineering](domain-6-prompt-context/notes.md); budgeting/cost angle in [Domain 5 · Cost and Token Management](domain-5-model-selection/notes.md). Ties directly to agent [memory scope](domain-1-agents/notes.md) — in-context memory grows the window every turn.

### Data residency
`D2 · Claude Application Design` (compliance in `D7`, regulation routes in `D1`)

A rule that a customer's data must be **processed in a specific country or region**. It sits alongside **available compliance certifications** and **who can audit access** — all three are determined by the **deployment platform**, not by application code.

🔑 **For a regulated customer these are pass-or-fail, not tradeoffs to balance** — no latency or cost advantage offsets a residency gap, and a customer already certified on one cloud is unlikely to re-certify on another. **Raise it during scoping**; surfaced late it lands at **contract review, after the work is done**. ⚠️ As stated 2026-07-19: the **first-party Claude API may not offer EU data residency** (EU-only typically requires **Bedrock or Vertex AI**); on **Microsoft Foundry** residency is **per model** — Anthropic-hosted Foundry models **do not** satisfy EU regional residency. On **Bedrock**, the **global-vs-regional endpoint** choice is the primary residency control and can affect cost. Verify at `platform.claude.com` and with the partner.

→ Developed in: [Domain 2 · Comparing platforms](domain-2-applications/notes.md#comparing-platforms--latency-compliance-cost-class-notes-2026-07-19); regulation-by-regulation routes in [Domain 1 · notes](domain-1-agents/notes.md).

### Deployment platform
`D2 · Configuration Management` (residency in `D7`, model IDs in `D5`)

The environment where the Claude workload runs: the **first-party Claude API**, **Claude Platform on AWS**, **Claude in Amazon Bedrock** (and legacy Bedrock), **Google Vertex AI**, or a **third-party platform** such as Microsoft Foundry. Identity and data location are answered **by the platform, not by your code**.

🔑 **The choice is rarely about technical merit.** It follows the customer's **existing cloud infrastructure, identity management, and compliance agreements** — matching those avoids a data-residency review from scratch. ⚠️ Two traps: **Claude Platform on AWS** goes through the customer's AWS account but runs **Anthropic-operated inference outside the AWS boundary**; **Microsoft Foundry** has **two hosting forms** (*Hosted on Azure* vs. *Hosted on Anthropic*), so residency depends on the specific model. _(Class-stated 2026-07-19 — verify at build time.)_

→ Developed in: [Domain 2 · Deployment and Versioning](domain-2-applications/notes.md#deployment-and-versioning--where-the-workload-runs-and-what-ships).

### Design document
`D4 · Eval, Testing, and Debugging` (also `D2 · Claude Application Design`)

A short written record — usually a single Markdown page — produced **before implementation**, fixing four decisions: **success criteria** (the output for representative cases, stated specifically enough to grade), **failure handling** (each production error marked retriable or terminal, plus what the user gets on unrecoverable failure), **cost and latency budget** (per-request, monthly ceiling, latency target, and the reliability floor you won't trade away), and the **trust boundary** (which inputs are untrusted; the least privilege the feature needs).

🔑 Its point is that **each decision becomes a downstream artifact**: criteria → eval cases, failures → error paths, budget → instrumentation, boundary → the hook that gates the action. Writing them once up front keeps the production layers consistent with each other. When building with an agentic coding tool, this is the artifact you hand over *before* it writes anything.

→ Developed in: [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md).

### Eval
`D4 · Eval, Testing, and Debugging`

A fixed set of input cases, each with the behavior you expect, run through the feature and graded — the collection of cases, expectations, and grades. It converts "I tried it a few times and it looked right" into a **number you can track** as the prompt, tools, or model change. Written **before** the feature, so success is defined instead of rationalized afterward.

The absolute score isn't the signal — a first run at 2–3/10 is normal. What matters is the score **moving up as you change one lever at a time**, and the **per-case** breakdown, which reveals fixes that broke other cases where the average hides them. Grading method follows output shape: exact match (one correct form) → code check (structural rule) → [judge](#llm-as-judge) (open-ended quality).

⚠️ **Exam angle:** D5's rule for changing model tier — up to Opus, or down to Haiku — is *"only when an eval set shows…"*. An eval is the evidence those decisions require.

→ Developed in: [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md); the tier-change rule in [Domain 5 · Model Selection](domain-5-model-selection/notes.md).

### Exponential backoff
`D2 · Claude API Mechanics` (also `D4 · Production failure handling`)

A retry strategy that **waits a growing interval between attempts** — up to a **cap** and a **fixed maximum number of tries** — usually with **random jitter** so concurrent clients don't retry in lockstep. Immediate retries against a [retriable error](#retriable-vs-terminal-error) deepen the very rate limit you're waiting out; a growing interval lets the limit clear.

🔑 **`retry-after` is authoritative.** When a `429`/`529` response carries the header, honor it — your own curve is the fallback for when it's absent. And the **Anthropic SDKs already auto-retry** transient failures with progressive delays up to a configurable max: wrapping your own loop around them multiplies attempts against the limit instead of capping them.

⚠️ Backoff is for retriable failures only. Applied to a terminal `400`, it just burns the retry budget on a request that will fail identically every time. Note also that fan-out multiplies this concern — in an [orchestrator-worker](#orchestrator-worker) run, **each subagent needs its own backoff and fallback**.

→ Developed in: [Domain 2 · Errors, retries, and rate-limit headers](domain-2-applications/notes.md); decision table and fallback behavior in [Domain 4 · Production failure handling](domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal).

### Function signature
`D8 · Tool Implementation`

A programming term for the **declaration** of a function: its name plus the list of parameters it accepts, including their names, types, and any default values. In tool use, the tool's **JSON input schema is effectively the signature Claude fills in** when it issues a call.

→ Developed in: [Domain 8 · Tool Implementation / Schema design](domain-8-tools-mcps/notes.md).

### HITL (human-in-the-loop)
`D1 · Agent Patterns`

Inserting a human review or approval step into an automated process **before a consequential action is taken**. The question that places one: *what's the worst outcome if this step runs without a human check?*

→ Developed in: [Domain 1 · Agent Patterns — HITL insertion points](domain-1-agents/notes.md) (before a destructive tool call / after a planning step / on unexpected output). Also a [Domain 7 · Security and Safety](domain-7-security/notes.md) concern for high-risk actions.

### Hook
`D3 · Claude Code Operation` (home skill: `D7 · Claude Hooks`)

A **command bound to a lifecycle event** in Claude Code's execution — `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`.

🔑 **The distinguishing property is determinism.** Unlike an instruction in [CLAUDE.md](#claudemd), which asks the model and may be ignored, a hook **runs at the configured event regardless of what the model decides**. A `PreToolUse` hook can **exit with code 2 to block a tool call before it runs**; a `PostToolUse` hook is the standard mechanism for a compliance audit trail (every tool call + parameters written to an audit store).

**Used as a guardrail** (the D7 framing), a hook is a check that **runs at a fixed point in the agent lifecycle and can block an action and log it**. The distinction a **regulated review** cares about: a prompt instruction is a *request*, a hook is an **enforced control that runs before the protected action** — one is auditable, the other isn't.

→ Exam angle: **"must / every time / regardless / for audit" is hook language**, and an instruction-file option is the reliable distractor. Developed in: [Domain 3 · Hooks](domain-3-claude-code/notes.md); enforcement framing in [Domain 7 · Hook-based guardrails](domain-7-security/notes.md) and audit-logging use in [Domain 7 · `PostToolUse` as the compliance audit trail](domain-7-security/notes.md).

### Integration test
`D4 · Eval, Testing, and Debugging`

A test that exercises the **handoff between two components** — for example, where a retrieval result is passed into a model call. It sits between the *functional* test (one Claude call returns the expected shape for an input) and the *end-to-end* test (the whole flow as a user runs it), and above the *unit* test (one function, such as a parser or tool wrapper, on its own).

🔑 **This is where most silent production failures live**, because each side of the seam can pass its own tests while the thing passed between them is wrong. Narrow levels localize precisely but see nothing about composition; end-to-end catches emergent breaks but can't tell you *where* the break is — for that you need a [trace](#trace).

⚠️ **Exam angle:** given "both components' own tests pass but the output is wrong," the answer is the untested seam — not more unit coverage and not a bigger model.

→ Developed in: [Domain 4 · Testing and tracing](domain-4-eval-testing/notes.md).

### LLM-as-judge
`D4 · Eval, Testing, and Debugging`

A grading method in which a **second model call** scores an output against a rubric. It is the only method that scales questions like *"is this summary faithful?"* or *"did this follow the instructions?"* — no code rule expresses them. It is also the most expensive (one extra API call **per case**) and the noisiest.

Two requirements make it usable:
- **Ask for reasoning, not a bare score.** Return strengths, weaknesses, and a short explanation *alongside* the score; asked for a number alone, models drift to a safe middle (~6) regardless of quality.
- **Calibrate before you trust it.** Run the judge on cases a human already labeled and **measure agreement**. Low agreement is a *rubric* problem — define each score, add a good and a bad example, re-measure.

⚠️ **The trap:** reaching for a judge where a code check would do. If the output has one correct form or a validatable structural rule, use match or a parse check — cheap, deterministic, and runnable on every commit. Common split: code-grade format on every commit, judge quality on a scheduled pass.

→ Developed in: [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md).

### Model version pinning
`D2 · Configuration Management` (enforced by the [pinned baseline](#pinned-baseline) in `D4`)

Configuring a **specific model snapshot** rather than a moving convenience alias. Aliases (`Opus`, `Sonnet`, or an undated `claude-haiku-4-5`) **evolve over time** and may **resolve to different versions across deployment platforms**; a pinned full model ID resolves to a fixed snapshot until you change the line.

🔑 **It's three moves, not one:** pin the **model**, version the **prompt and asset** alongside the code, and **keep the prior version** available for rollback. An unpinned deployment makes **every upstream model update an untracked change to your output**. Pinning format is platform-specific — `anthropic.`-prefixed IDs on Bedrock, Vertex's format on Vertex, **ARN-versioned** identifiers on legacy Bedrock, and **partner retirement dates differ from Anthropic's schedule**. ⚠️ Convention split as stated **2026-07-19**: Claude **4.6 and later** pin by model ID alone; earlier models need the **date suffix**. Exception: a throwaway prototype that never ships may use a moving alias.

→ Developed in: [Domain 2 · Deployment and Versioning](domain-2-applications/notes.md#deployment-and-versioning--where-the-workload-runs-and-what-ships).

### MCP (Model Context Protocol)
`D8 · MCP Server Development`

An **open communication layer** letting an MCP **client** (such as Claude Code) connect to an MCP **server** that exposes **tools, resources, and prompts**. The protocol defines how the client discovers and calls the server's tools.

The point of it: **tool definition and maintenance move out of individual application code and into a reusable server** that any MCP client can attach to. The cost: connecting a server adds its **tool definitions to context whether or not the tools are used** — connect deliberately.

→ Developed in: [Domain 8 · MCP Server Development + Building and Configuring an MCP Server](domain-8-tools-mcps/notes.md); the MCP-vs-manual-schema decision sits under Agentic Customization in the same file. Governance of individual server tools uses the `mcp__server__tool` permission-rule format.

### MCP transport
`D8 · MCP Server Development`

The **communication channel** between an MCP client and server. **stdio** runs the server as a **local subprocess on the same machine** as the client; **HTTP** connects to a **remotely hosted** server over a network. Transport determines **where the server can run and who can connect to it**.

🔑 **Transport and [configuration scope](domain-8-tools-mcps/notes.md) are independent decisions with dependent consequences.** A shared team server needs **HTTP** plus project or enterprise scope. ⚠️ A **stdio server committed to `.mcp.json` looks shareable and isn't** — every clone spawns its own subprocess and needs the runtime installed locally.

→ Developed in: [Domain 8 · Transports + Configuration scope + the MCP setup reference](domain-8-tools-mcps/notes.md).

### Observability
`D5 · Cost and Token Management`

Instrumenting **three metrics on every model call** — **token usage** (input and output separately), **latency**, and **error rate** (per call and per dependency) — so a cost or latency problem attributes to a named step and request type rather than appearing as a monthly total. The usage figures come back on the API response already; the work is logging them.

**Why it's a design-time decision, not a later step:** in development the volume is too low for cost or latency to show. In production the same calls become the constraint, and retrofitting instrumentation happens under incident pressure. A common finding once the data exists: one step accounts for ~90% of spend, and the slowest step is rarely the expected one.

→ Developed in: [Domain 5 · Observability](domain-5-model-selection/notes.md#observability--instrument-before-you-optimize). Distinct from a [trace](#trace), which records the *sequence* of a single run; observability aggregates the *metrics* across runs. The two are complementary — the trace names the step, the metrics say what it costs.

### Orchestrator-worker
`D1 · Agent Patterns`

A multi-agent pattern in which a **lead agent** decomposes a task, delegates the subtasks to **subagents running in parallel** (each with its own context window), and then **synthesizes** their returns. Three phases: plan → fan-out → synthesis.

**The tradeoff the exam tests:** Anthropic reported a substantial quality gain on an internal research eval (Opus 4 lead, Sonnet 4 subagents) at roughly **15× the tokens** of a normal chat interaction, with **token usage explaining most of the performance variance** — the pattern works because it buys parallel computation. So it pays only when the task has **genuinely independent** parts. For **tightly coupled work such as coding**, a single agent with good context is better and far cheaper. 15× is a baseline, not a ceiling: a runaway subagent pushes past it. Fan-out also **multiplies the failure surface** — each subagent needs its own backoff and fallback.

→ Developed in: [Domain 1 · Orchestrator-worker](domain-1-agents/notes.md#orchestrator-worker--parallel-exploration-at-a-15-token-multiplier). See also [Subagent](#subagent) for what a delegated agent does and doesn't inherit.

### Permission mode
`D3 · Claude Code Operation`

A Claude Code setting controlling **how often the agent stops to request confirmation before executing tool calls** — from `default` (prompts before nearly every action) through `plan`, `acceptEdits`, `auto`, and `dontAsk`, to `bypassPermissions` (no prompts at all).

🔑 **Two rules hold across every mode:** a **deny rule always beats an allow rule**, and **a deny rule still applies under `bypassPermissions`**. A deny rule set at the **enterprise settings level cannot be bypassed by any individual configuration** — which makes it the most durable governance control in the system.

→ Exam angle: mode choice is a **risk decision, not a speed decision**; a stem describing someone easing prompts for convenience is usually answered by restoring the checkpoint at a level the individual can't undo. Developed in: [Domain 3 · Permission modes + the four settings levels](domain-3-claude-code/notes.md); extension to MCP tools in [Domain 8](domain-8-tools-mcps/notes.md).

### Plugin
`D3 · Claude Code Operation`

A **versioned bundle** of Claude Code components — skills, hooks, subagents, and MCP server configurations — distributed through a **marketplace**. Installing one gives the recipient the same setup as the author **in a single step**, replacing a page of manual configuration with a versioned, auditable install. Enterprise administrators can deploy plugins organization-wide through **managed settings**, which sit above user and project settings and cannot be overridden.

⚠️ **Two portability failures to know:** an **absolute path** into the author's home directory (installs for the author, fails everywhere else), and an **undocumented environment-variable dependency**. And a plugin **carries only what it bundles** — a deny rule or hook the author relied on locally does not travel unless listed. Test the install from a clean machine.

→ Developed in: [Domain 3 · Plugins + the packaging decision table](domain-3-claude-code/notes.md) (skill vs. custom command vs. plugin).

### Pinned baseline
`D2 · Configuration Management` (evidence from `D4 · Eval, Testing, and Debugging`)

The **score a packaged [eval suite](#portable-eval-suite) recorded for the currently deployed configuration**, held as the bar a change must clear. When you promote a new model version to production, you run it against the pinned baseline **before the version goes live**.

🔑 **It's the enforcement half of [model version pinning](domain-2-applications/notes.md#configuration-management-41).** Pinning a dated snapshot controls *what* runs; the baseline controls whether the *next* thing may. Pinning alone tells you nothing about whether the upgrade you're about to make is safe. ⚠️ Don't change the judge or the dataset in the same step as the model — the baseline is only meaningful if the measuring instrument is held constant.

→ Developed in: [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator) and [Configuration Management](domain-2-applications/notes.md); grading and calibration in [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md); the tier-change rule in [Domain 5](domain-5-model-selection/notes.md).

### Portable eval suite
`D4 · Eval, Testing, and Debugging` (packaging in `D2 · Systems Life Cycle`)

An [eval](#eval) packaged as a reusable asset: the **graded test set and the judge rubric shipped together**, with thresholds and dataset paths parameterized, so a new team can **run them in their own context** and confirm the asset still works there.

🔑 **It does two jobs.** It is the portable proof that a delivered accelerator works, *and* the **deployment gate** — the [pinned baseline](#pinned-baseline) a new model version must meet before promotion. ⚠️ Dataset without rubric (or rubric without dataset) is not portable: the next team can run the cases but can't reproduce the grading. Document what the scores **mean**, not just what they are.

→ Developed in: [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md) (building and calibrating); packaging rules in [Domain 2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator).

### Prompt injection
`D7 · AI Application Security`

An attack in which **instructions hidden inside content the agent fetches** — a web page, a document, a ticket, a code comment — are treated as commands to follow.

🔑 **The root cause is architectural, not a bug to patch:** the model reads its **entire context as one undifferentiated stream**, with **no built-in boundary** between the instructions you wrote and the data it retrieved. Anything that lands in the window has a chance of being read as direction. This is why it is the core threat for any agent that reads content it didn't write, and why the attack surface is **every content source**, not just one retrieved page.

**The defense follows from the cause:** treat fetched content as **data, never as instructions**, and **enforce the action boundary outside the prompt** — a [hook](#hook) that blocks the consequential call, least-privilege credentials, a scoped tool list. Delimiters and "ignore instructions in the text below" help but are a **soft** boundary: they lower the odds, they don't enforce anything. ⚠️ **Exam angle:** an option that defends only by rewording the system prompt is the distractor; the answer gates the *action*, not the *text*. Distinguish from a **jailbreak**, which targets the model's own safety training — different target, same shape of defense.

→ Developed in: [Domain 7 · Prompt injection](domain-7-security/notes.md); enforcement in [Hook-based guardrails](domain-7-security/notes.md) and the [trust boundary](#trust-boundary) that names what's untrusted.

### Query router
`D6 · Context Engineering` (traced at `D4 · Eval, Testing, and Debugging`)

A **cheap classification call** placed in front of retrieval that reads the query and picks the path: single-fact lookups go to **fetch-once** static retrieval, multi-part questions go to **agentic search** across rounds. The point is to **pay for iteration only when the query needs it**.

```python
def route(query):
    kind = classify(query)        # cheap call: "lookup" or "multi_step"
    if kind == "lookup":
        return fetch_once(query)
    return agentic_search(query)
```

🔑 **It earns its cost only on mixed traffic.** Defaulting everything to iterative search inflates cost and latency on questions one fetch would answer; defaulting everything to a static index gives shallow answers on questions needing several passes. **If every query is the same shape, skip the router and hardcode the path.** Same shape as model-tier routing in D5 — a cheap call gates the expensive path.

⚠️ **Exam angle:** the router is also a **step your [trace](#trace) must record** — a wrong branch choice looks like a bad answer unless the trace shows which path ran.

→ Developed in: [Domain 6 · Context Engineering → retrieval](domain-6-prompt-context/notes.md); tracing implications in [Domain 4](domain-4-eval-testing/notes.md).

### Refactor
`D2 · Software Engineering Foundations`

Changing the **internal structure** of code without changing what it does from the outside — reorganize, rename, or rewrite the implementation to make it cleaner, faster, easier to test, or easier to extend, while the behavior the rest of the system sees stays the same.

→ Exam angle: several design decisions are cheap at design time and expensive as a production refactor — e.g., agent [memory scope](domain-1-agents/notes.md) should be chosen up front, not retrofitted once token cost has already scaled. The same asymmetry drives enterprise integration: identity, residency, audit logging, and config lock are each cheap **before** deployment and expensive **after** a failed security review ([Domain 8 · Enterprise Integration](domain-8-tools-mcps/notes.md)).

### Reliability floor
`D5 · Cost and Token Management` (enforced via `D4 · Evals`)

A **stated baseline the system may not be optimized below** — typically a latency ceiling plus a retry budget, e.g. *"a user-facing request completes within 4 seconds and may retry a failed dependency up to 3 times."* Defined **first**; cost optimization then happens above it, and every cost-saving change must show it didn't cross the line.

**Why order matters:** a high bill appears on a dashboard daily and applies constant pressure; a reliability problem appears as occasional failures that look like noise until they accumulate into an incident. Optimize cost first and the louder pressure wins — you locate the floor only after crossing it. A **pinned eval baseline score** is what makes the floor checkable rather than asserted: a change that drops the score fails the gate before shipping.

→ Developed in: [Domain 5 · Reliability floor](domain-5-model-selection/notes.md#reliability-has-a-floor-you-tune-cost-within-it); the gate mechanism is in [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md#evals-and-judges--defining-done-before-you-ship).

### Retriable vs. terminal error
`D4 · Eval, Testing, and Debugging` (also `D2 · Claude API Mechanics`)

**The first distinction to make about any production failure**, because it decides the entire handling path.

| | Retriable | Terminal |
|---|---|---|
| **What it means** | Likely to succeed on a later attempt — the failure is about *timing*, not the request | Will fail again identically — the cause is *in the request* |
| **Examples** | `429` rate limit, `529` overload, `5xx` | `400`, `401`, `403`, `404` |
| **What you do** | [Exponential backoff](#exponential-backoff) + jitter, capped attempts; honor `retry-after` | **Fail fast** — surface it; don't spend retries |

🔑 **Getting this backwards fails in both directions:** retrying a terminal error burns the budget and delays the real error reaching someone who can fix it; failing fast on a rate limit throws away a request that would have succeeded a second later.

⚠️ **Two failures a status-code classifier misses entirely:** a **refusal is HTTP `200`** with `stop_reason: "refusal"` — check `stop_reason`, then fail fast. And a failed tool execution comes back as a `tool_result` with **`is_error: true`**, never an empty result. Marking each expected error retriable or terminal is one of the four decisions fixed in the [design document](#design-document), *before* the code exists.

→ Developed in: [Domain 4 · Production failure handling](domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal); status codes and headers in [Domain 2 · Errors, retries, and rate-limit headers](domain-2-applications/notes.md).

### Rules instruction file
`D3 · Claude Code Operation`

A file that **scopes guidance to a specific path or condition**. Unlike [CLAUDE.md](#claudemd), which loads unconditionally for every session, a rules file **activates only when Claude Code is working in the directory it supervises** — which is how you keep path-specific guidance out of the main project memory file and stop it diluting the universal rules.

→ Exam angle: "this guidance applies only inside `<directory>`" → rules file, **not** CLAUDE.md. A 400-line CLAUDE.md whose top rules are being ignored is usually half path-specific content that belongs here. Developed in: [Domain 3 · Rules instruction files + the mechanism map](domain-3-claude-code/notes.md).

### SOC 2
`D7 · Security and Safety`

**Service Organization Control 2** — an audit framework from the American Institute of CPAs (AICPA) for evaluating how a service organization handles customer data. It's the standard most commonly cited when a SaaS vendor or cloud provider is asked to show their security practices meet a recognized bar.

→ Exam angle: SOC 2 governs **how your systems are built and operated**, *not* which endpoint your code calls — so it does **not** belong in the endpoint/credential/region/logging decision (contrast the note in [Domain 1 · Regulated data](domain-1-agents/notes.md)). Home domain: [Domain 7 · Security and Safety](domain-7-security/notes.md).

### State
`D1 · Agent Patterns`

The information an agent carries between turns: the conversation so far, what the user asked for, and results from earlier tool calls.

→ Developed in: [Domain 1 · Agent memory](domain-1-agents/notes.md) — the design-time choice of what state survives a session (in-context / external storage / summarized / stateless) and what each costs.

### stop_reason
`D2 · Claude API Mechanics`

A field in the API response that tells your code **why the model stopped generating**. The two values most relevant to agentic loops:
- `end_turn` — Claude has finished and is **not** requesting further action.
- `tool_use` — Claude issued one or more [tool_use blocks](#tool_use-block) and is **waiting for results** before continuing.

→ Developed in: [Domain 2 · Claude API Mechanics](domain-2-applications/notes.md). It's the signal your loop reads to decide continue-vs-exit (see [Domain 1 · exit conditions](domain-1-agents/notes.md)).

### Subagent
`D1 · Agent Architecture`

A separate agent instance spun up by an orchestrating agent to handle a discrete subtask. Subagents do **not** inherit conversation history, Skills, or context from the parent session — each starts clean and must be configured explicitly with the instructions and tools it needs. Results return to the orchestrator, which folds them into the broader task.

In Claude Code specifically, a subagent is a **separate execution context launched to handle a delegated task**: it does not inherit the main conversation's context or accumulated files, performs the task, and **returns only a summary**. That makes it the right mechanism for **exploratory or investigative work** whose intermediate output would otherwise fill the main session with content that will never be reused.

→ Developed in: [Domain 1 · Agent Architecture & Patterns](domain-1-agents/notes.md); as one of the four durable-context mechanisms in [Domain 3](domain-3-claude-code/notes.md). **Watch two exceptions:** a subagent starts with clean *context* but **inherits the parent's permission context** — "clean context" is not "clean permissions" — and **subagents do not automatically preload skills, in any runtime**; anything the subagent needs must be listed for it explicitly.

### Token
`D5 · Cost and Token Management`

The unit Claude uses to measure and process text. The characters-per-token average depends on the model's **tokenizer** and differs between model generations — treat any chars-per-token rule of thumb as **model-dependent** and confirm current tokenizer behavior at build time. Everything in the [context window](#context-window) consumes tokens (prompts, responses, tool schemas, tool results); tokens are the basis for **both pricing and context-budget** calculations.

→ Developed in: [Domain 5 · Cost and Token Management](domain-5-model-selection/notes.md). *Version-sensitive (per class, 2026-07-18): tokenizer behavior is model-specific — verify against current docs.*

### tool_use block
`D8 · Tool Implementation` (surfaced in `D2 · Claude API Mechanics`)

A content block returned by the assistant when Claude wants to call a function. It contains the **tool name, a unique ID, and the input arguments** Claude wants passed to your code. Every `tool_use` block must be answered by a matching **`tool_result` block in the immediately following user turn, with the same ID preserved exactly** — and all `tool_use` blocks from one assistant turn are resolved together before the next assistant turn.

→ Developed in: [Domain 8 · Tool Implementation](domain-8-tools-mcps/notes.md); message-structure mechanics in [Domain 2 · Claude API Mechanics](domain-2-applications/notes.md). This is the block your loop reads after a `tool_use` [stop_reason](#stop_reason).

### Trace
`D4 · Eval, Testing, and Debugging`

A **step-by-step record of one run**: the prompt, the tool calls, the intermediate outputs, and the timing. It reads like a timeline, and the failing step is usually obvious once the intermediate output is visible.

```
step 3  model.call(prompt)   ok   980ms  -> answer "..."
step 4  parse(answer)        FAIL   2ms  -> KeyError: amount
```

🔑 **Tests tell you a failure exists; a trace tells you which step caused it.** Without one, a failed [eval](#eval) says only "something is wrong" — the difference between a five-minute fix and a day of hand-tracing. It's also what makes a change reviewable: you can show **the step that moved**, not just the score that dropped. Standard operational logging (status codes, latencies) does **not** substitute — it never surfaces intermediate outputs.

⚠️ **Exam angle:** if an option proposes "add an end-to-end test to find which step failed," that's the wrong instrument. E2E proves a break exists; a trace localizes it.

→ Developed in: [Domain 4 · Testing and tracing](domain-4-eval-testing/notes.md); the layer-localization discipline it mechanizes in the same file.

### Trust boundary
`D7 · Security and Safety` (named as design-doc decision 4 in `D4`)

The line between content the agent reads that **someone else can write** (untrusted input) and the actions the agent is permitted to take. Naming it explicitly is what turns least privilege into an enforceable **design decision** — the untrusted content gets treated as *data*, and the consequential action gets gated by a [hook](#hook) — rather than a setting someone remembers to add later.

**In a multi-component application** the definition sharpens to a location: the point where **data or instructions move from one deployment environment to another** (API → Claude Code task → MCP server). Every such **seam** is a boundary, and the app is **only as contained as its most privileged seam**.

→ Developed in: [Domain 7 · Security and Safety](domain-7-security/notes.md); as one of the four written decisions in [Domain 4 · Evals and Judges](domain-4-eval-testing/notes.md); at application scale in [Domain 2 · Multi-Component Applications](domain-2-applications/notes.md#multi-component-applications--trust-boundaries-where-components-meet).

---

*Sources: class module "Production-Grade Prompting, Agents & Tool-use" (Glossary screen, 2026-07-18), class module "Claude Code, MCP & Integration" (Key Terms screen, 2026-07-19), class module "Evals & Judges" (2026-07-19), class module "Testing & Tracing" (2026-07-19), and class module "Production Engineering, Evals & Security" (Glossary screen, 2026-07-19), class module "Trust Boundaries" (2026-07-19). Definitions cross-checked against existing domain notes; version-sensitive items flagged with the class date.*

*Module "Production Engineering, Evals & Security" (2026-07-19) contributed four new terms — [Agentic search](#agentic-search), [Exponential backoff](#exponential-backoff), [Prompt injection](#prompt-injection), [Retriable vs. terminal error](#retriable-vs-terminal-error) — and sharpened four already here: [Eval](#eval), [Integration test](#integration-test), [LLM-as-judge](#llm-as-judge), [Orchestrator-worker](#orchestrator-worker). Its "hook-based guardrail" is the D7 enforcement framing of [Hook](#hook) and is folded into that entry rather than duplicated. ⚠️ Status codes, header names, and the 15× orchestrator multiplier are version-pinned to **2026-07-19**.*

*⚠️ Version-sensitive across the second module: permission mode names, settings file locations, hook event names, skill loading mechanics (beta header / `settingSources`), and MCP permission-rule syntax were current as of **2026-07-19** — confirm exact strings against docs.claude.com before relying on them.*

*Module 5 lesson "Comparing Platforms" (2026-07-19) contributed [Data residency](#data-residency) and sharpens [Deployment platform](#deployment-platform) with the three comparison dimensions — **latency** (measured from the customer's region, not your laptop), **compliance** (pass-or-fail; usually ends the debate), and **cost** (egress + platform fees + integration, not the token rate).*

*Module 5 recap, "Accelerators & IP Contribution" (2026-07-19), contributed one new term — [Contribution readiness](#contribution-readiness), previously folded into [Contributing back](#contributing-back) — and adds the module's five glossary framings to entries already here: [Accelerator](#accelerator) (packaging bundles the eval **and** the audit log), [Deployment platform](#deployment-platform) (the module names **six**: first-party Claude API, Claude Platform on AWS, Claude in Amazon Bedrock, legacy Bedrock, Google Vertex AI, third-party platforms), [Model version pinning](#model-version-pinning) (the book-edition metaphor — an alias is the *current* edition, a pin *cites a fixed* one), and [Trust boundary](#trust-boundary) (**trust does not carry over from the component that sent the data**). Routed in [`capstone-accelerators-ip-contribution.md`](capstone-accelerators-ip-contribution.md).*

*Module 5 lesson "Deployment & Versioning" (2026-07-19) contributed two new terms — [Deployment platform](#deployment-platform) and [Model version pinning](#model-version-pinning) — and sharpens [Pinned baseline](#pinned-baseline), which is the promotion gate those two feed. ⚠️ **Most version-sensitive entries in this glossary:** model names, Foundry hosting forms, platform API surfaces, and the 4.6+ pinning convention are all as stated on **2026-07-19** — re-verify at `platform.claude.com` and the partner's docs before relying on them.*
