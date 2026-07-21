# Domain 1: Agents and Workflows — Notes

**Exam weight: 14.7%**

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Agent Architecture | 4.5% | Workflow vs. agent decision criteria; manager/supervisor hierarchies; subagents for task execution |
| Agent Construction with Claude | 5.3% | Claude Agent SDK; custom agent loops/harnesses; self-hosted vs. Anthropic-hosted deployment; hooks for deterministic actions |
| Agent Patterns and Frameworks | 4.9% | Tool-use loops, sub-agents, memory, context-window management; frameworks (Strands, LangGraph, PydanticAI) |

> **Central idea:** An agent is a **multi-step tool-use loop with managed context and a defined goal**. The exam tests *judgment*, not trivia: does this problem even need an agent, who runs the loop once you've decided it does, and where do the human checks and constraints go. The loop itself is constant across every way you can build it — what changes is how much of it you own.

---

## Agent Architecture (4.5%)

### The first decision: workflow or agent?

The most critical mistake in agent development is choosing the wrong pattern **before writing the first line**. Workflows and agents solve different problems:

- Use an **agent** when a workflow is sufficient → you add behavioral complexity with no added capability.
- Use a **workflow** when an agent is needed → the system breaks whenever user input deviates from the predetermined path.

| Choose a **workflow** when… | Choose an **agent** when… |
|---|---|
| You can enumerate the exact steps in code. | You can specify the goal and the tools but **not** the exact path. |
| Error cost is real and step-level guardrails matter. | The path through the work cannot be enumerated in advance. |
| Observability with standard tooling is required. | Non-determinism is acceptable; possible actions are constrained by the registered toolset. |
| Inputs are well-constrained to a known set. | User inputs vary unpredictably in content and structure. |
| Every execution follows the same sequence. | The task requires creative sequencing of available tools. |

### Start simple; move up only when forced

Agents are the **last step in a progression**, not the default. Start with the simplest pattern that solves the problem and move up only when the simpler one can't handle the variability:

**single API call → workflow → agent**

Agents carry coordination overhead, expanded context cost, and more failure surface than simpler patterns. What you take on when you choose an agent: the path emerges from the model's reasoning over accumulated context rather than from explicit branching in your code, and **observability requires transcript-level tooling** rather than standard operational logging.

> **New failure modes appear only when components run together** across turns — routing that passed single-turn tests starts to compound, context fills faster than expected, and a step gets the wrong input because an earlier tool call was structured incorrectly. Isolated testing does not catch these.

> **Multi-agent** architectures (a planner, executor, and evaluator running as separate agents that hand off through structured artifacts) add design decisions beyond the loop itself. For a *single*-agent system the loop pattern is constant across all wiring paths.

---

## Agent Construction with Claude (5.3%)

### The three wiring paths — who runs the loop

Once you've decided the task needs an agent, you've decided on the **pattern**: a loop that calls tools, manages context, and runs until a goal is met. The pattern doesn't change based on how you build it. What changes is **how much of the loop you write yourself vs. hand to a library or a hosted service.** The three paths sit on a spectrum of how much infrastructure you own (ordered below by how much you hand off).

> ⚠️ **Decision rule:** choose based on **deployment and compliance constraints** — *not* whichever path is fastest to prototype.

| Path | Who runs the loop | What you own | Choose it when |
|------|-------------------|--------------|----------------|
| **Raw Messages API loop** | Your code runs every iteration — send request, read `tool_use` blocks, execute tools, append results yourself. | The **full** loop: tool execution, context management, retries, exit conditions. Nothing is provided. | You need full control over each step, have constraints a library can't accommodate, or you're learning the loop before adding abstraction. Maintenance cost is yours — everything the SDK gives free becomes code you write and test. |
| **Agent SDK** | The same loop runs **inside your own process**; the SDK provides tool-execution structure, context management, and the iteration structure. | The agent definition (code-level + filesystem config) and tool execution — your code still executes tools. | You want the loop's structure built for you but still want it running **in-process** on your own infrastructure/credentials. |
| **Claude Managed Agents** *(public beta)* | **Anthropic runs the loop and the sandbox** server-side. Your app defines the agent once, refers to it by ID, sends user events, and streams results back over server-sent events (SSE). | An agent **defined as a versioned API resource**, plus an application layer that sends events and consumes streamed results. | Long-running tasks; you'd rather not build/secure a sandbox and loop. See constraint below. |

> ⚠️ **Version-sensitive (recorded from class 2026-07-18 — verify against current docs):** Managed Agents is in **public beta**; a beta surface can change between releases.

### Claude Managed Agents — what you stop owning vs. take on

| Category | What you **stop** owning | What you **take on** instead |
|----------|--------------------------|------------------------------|
| Execution & infrastructure | The iteration loop, execution sandbox, in-loop retries, tool-execution runtime — Anthropic runs all of it server-side. | An agent definition managed as a **versioned API resource**, plus an app layer that sends events and consumes streamed results. |
| Session duration & state | Long-running execution management — sessions run for **minutes or hours** without your process holding the loop open. | **Server-side session state.** Sessions are stateful and stored by Anthropic, subject to its data-handling policies (see the constraint below). |
| Sandbox lifecycle | Sandbox provisioning and teardown for tool execution. | A dependency on the managed sandbox's available tools and execution model, rather than your own environment. |

**Choose Managed Agents when:** the task runs **long** (minutes/hours are awkward to hold open in your own process); you want a **managed sandbox** rather than building/securing an execution environment for tool calls; or you'd simply rather not build the loop, sandbox, and tool-execution layer at all and will define the agent as an API resource.

> 🔑 **The constraint that decides it for regulated work:** Managed Agent sessions are **stateful and stored server-side.** That storage is *why* these sessions are **not currently eligible for Zero Data Retention (ZDR) or a HIPAA Business Associate Agreement (BAA).** If your workload carries **PHI or falls under a ZDR requirement, this path is ruled out** no matter how well it fits operationally → route to the **Agent SDK or a raw loop on a covered configuration.** The governing constraint picks the path before convenience gets a say.

**Prototype → production progression:** a common pattern is to prototype on the **Agent SDK locally**, then move to **Managed Agents** for production. The core agent definition carries over *conceptually*, but the **format changes** — Agent SDK uses code-level/filesystem config; Managed Agents defines the agent as a versioned API resource. Expect a **re-expression step, not a direct export.**

### Wiring the loop — the four steps that hold across every path

These four steps define a working loop no matter the path. On the **raw Messages API** you implement all four yourself; with the **Agent SDK** it provides the structure for steps 1–2 and iterates the loop, and **your code still executes tools** in step 3.

1. **Register tools.** Every tool follows the same schema structure; registration tells Claude what's available.
2. **Set the system prompt.** Scope it to the agent's task. A **broad** system prompt produces broader, less reliable tool routing; one that **names the specific task and its tools** produces more consistent behavior.
3. **Handle the tool-use loop.** Whether you or the SDK iterates, **your code executes every tool call** Claude issues and returns each in a `tool_result` block. *(Loop ownership — Claude selects, your code executes and returns — is detailed in [Domain 8 · Tool Implementation](../domain-8-tools-mcps/notes.md). Same mechanism, here viewed as an agent-construction step.)*
4. **Define exit conditions.** The loop runs until a stop condition. **Without explicit exit conditions the agent keeps requesting tool calls beyond what the task requires.** Define when *done* means done — don't depend on Claude volunteering to stop.

#### Loop wiring checklist — verify regardless of path

| # | Item | What to verify |
|---|------|----------------|
| 1 | Tools registered | Every tool the agent may need is registered. No **unregistered** tool is referenced in the system prompt. |
| 2 | System prompt scoped | Names the task and available tools. Doesn't describe tools the agent lacks; doesn't omit scoping guidance for tools it has. |
| 3 | Tool-use loop implemented | Your code handles every `tool_use` block and returns a `tool_result` for each **before the next assistant turn**. All `tool_use` blocks from one assistant turn are resolved **together**. |
| 4 | HITL insertion point defined | At least one point in the loop has a human-in-the-loop check (see Agent Patterns below). |
| 5 | Exit conditions defined | A clear stopping criterion that **doesn't depend on Claude volunteering to stop.** |

### Regulated data sets the endpoint, credentials, and logging *before* you wire anything

If data carries specific constraints (attorney-client privilege, HIPAA, GDPR, FedRAMP, internal data-residency), that constraint decides **which endpoint your code calls, which credentials it carries, and where logs land** — *before* any choice about prompts, tools, or memory. As a developer you usually don't pick the surface, but you write the code that targets an endpoint, attaches credentials, configures the region, and emits logs. **Get the governing constraint named at the start** — the wrong client configuration is far more expensive to undo after the agent is wired.

| Constraint | What it tends to rule out in code | What usually survives review |
|-----------|-----------------------------------|------------------------------|
| **Attorney-client privilege** | Calls from a consumer **Claude.ai** surface the firm can't audit end-to-end; sending privileged content to any endpoint not approved for privileged material. | Direct API/SDK calls from the firm's own app, SSO-authenticated, routed through a firm-approved **LLM gateway with full request/response logging.** Note: on **direct API traffic Anthropic does not capture conversation content by default**, so the org must implement conversation logging in the **application layer** and route it to an approved destination. Confirm the logging design with your Anthropic account team. |
| **HIPAA (PHI)** | Sending PHI to any endpoint/route **not covered by a BAA** for the exact configuration in use — including any logging/retention path not scoped under the same BAA. | Direct API/SDK on a **BAA-covered configuration** (Anthropic provisions a dedicated HIPAA-enabled org), **or** a cloud-mediated route via **AWS Bedrock / GCP Vertex** on a HIPAA-eligible cloud account. **BAA does not cover Console, Workbench, beta features, or consumer plans.** Not all API features are covered — verify the current eligibility list in Anthropic's Implementation Guide. |
| **GDPR / data residency** | Routes where the region of model execution **can't be pinned in code**, or a request can be served outside the approved boundary. Defaulting to a **global endpoint without a region** is the common break. | A cloud-mediated route (**Bedrock / Vertex**) with the **region pinned** in client config to a covered jurisdiction. The **direct Anthropic API does not currently provide EU data residency** → EU-residency partners route through Bedrock/Vertex instead of calling the API directly. |
| **FedRAMP / government** | Any endpoint **not on an authorized cloud environment** at the required impact level — including dev/test paths hitting the commercial endpoint while prod hits the authorized one (credentials/patterns leak between them). | Three authorized routes (as of publish time): **Claude for Government (C4G)** — FedRAMP High via Palantir **PFCS-SS**; **Claude via Amazon Bedrock GovCloud** — FedRAMP High + DoD IL4/5; **Claude via Vertex AI Assured Workloads** — FedRAMP authorized. **Claude Enterprise on AWS Marketplace is *not* FedRAMP authorized.** |
| **Internal data-residency policy** | Any SDK client configured against a cloud vendor **outside the partner's approved list**, regardless of technical capability. Procurement rules the path out before engineering preference enters. | The delivery route on the partner's **approved** cloud vendor — whichever SDK client/endpoint their CIO has already cleared. Build against that one; don't switch mid-project because another route looks easier. |

> **SOC 2 is not in this table.** It governs how your systems are **built and operated**, not which endpoint your code calls → covered in Domain 7, not here. This table is only about constraints that directly determine **endpoint + credential + region + logging** selection.

> ⚠️ **Version-sensitive (recorded from class 2026-07-18 — verify at trust.anthropic.com and Anthropic's Implementation Guide before configuring):** covered configurations, feature eligibility under the BAA, and FedRAMP authorization status all change.

> **Forward pointer → [Domain 7 · Security and Safety](../domain-7-security/notes.md):** secure-by-design IAM/privacy, prompt-injection defenses for untrusted input, runtime guardrails, and agent hardening live there. This section's narrower job: surface the constraint at the point in the build where it actually rules options out — endpoint, client config, and credentials.

---

## Agent Patterns and Frameworks (4.9%)

### Human-in-the-loop (HITL) — insertion points

A HITL checkpoint **pauses agent execution and routes to a human** before proceeding. The question that decides where to insert one: **what is the worst possible outcome if this step runs without a human check?**

| Insertion point | What triggers the check | Risk level it addresses |
|-----------------|-------------------------|-------------------------|
| **Before a destructive tool call** | The agent is about to execute a **write, delete, or send**. | **High** — irreversible actions a wrong call can't undo. |
| **After a planning step** | The agent has generated a plan and is about to execute it. | **Medium** — an incorrect plan produces the wrong outcome *even if every step executes correctly.* |
| **On unexpected output** | A tool result carries an **error flag, empty result, or out-of-bounds value.** | **Variable** — catches failure modes that **retry logic alone won't resolve.** |

### Tool orchestration — over-tooling vs. under-tooling

Routing behavior is shaped by **how tools are described** and **how many are registered.**

- **Too many** tools with overlapping descriptions → **erratic routing.**
- **Too few** tools → the agent **hallucinates a path or returns an incomplete result.**

> 🔑 **Over-tooling is the more common production problem.** Teams register every tool "just in case" and find Claude's **selection quality degrades as the tool surface grows.** Fix: **start with the minimum set** required for the task and **add a tool only when a specific capability gap is confirmed.**

*(Description-quality mechanics — writing "when to use / when NOT to use," exclusion conditions, merging near-duplicates behind a `type` param — are in [Domain 8 · Tool Implementation](../domain-8-tools-mcps/notes.md). Here the point is the count/quantity lever; there it's the wording lever.)*

### Agent design patterns grouped under this skill

The blueprint files several patterns you've already met under this one objective. They aren't separate machinery — each is a view of the same loop, plus the decision about what outlives it.

| Pattern | What it is | Where it lives |
|---------|-----------|----------------|
| **Tool-use loop** | Model calls a tool, reads the result, continues — the core agent pattern. | *Wiring the loop* (Construction, above); mechanics in [Domain 8 · Tool Implementation](../domain-8-tools-mcps/notes.md). |
| **Multi-step task decomposition** | Break one goal into ordered subtasks. | Loop steps above; subtask-dependency modeling in [Domain 8 · Schema design](../domain-8-tools-mcps/notes.md). |
| **Planning-and-execution** | Separate *deciding* the plan from *carrying it out* — the split the HITL "after a planning step" check guards. | HITL insertion points, above. |
| **Orchestrator-worker** | A lead agent decomposes a task and fans it out to parallel subagents, then synthesizes their returns. | Next section. |
| **Memory scope** | What state survives once the loop ends. | Below. |

### Orchestrator-worker — parallel exploration at a ~15× token multiplier

_Source: class module "Cost & Orchestration" (added 2026-07-19). The cost-and-latency instrumentation this section assumes lives in [D5 · Observability](../domain-5-model-selection/notes.md#observability--instrument-before-you-optimize)._

A **lead agent** decomposes a task into subtasks and delegates them to several **subagents running in parallel, each with its own context window**. When the subagents finish, the lead compiles their results. Three phases: **plan → parallel fan-out → synthesis.**

```python
async def orchestrate(task):
    plan = await lead.plan(task)              # lead agent decomposes
    results = await gather(*[                 # subagents run in parallel
        worker.run(subtask) for subtask in plan.subtasks
    ])                                        # each spends its own tokens
    return await lead.synthesize(results)     # lead compiles the answer
```

**The right mental model is a hiring decision.** Five researchers finish a broad survey faster than one — and you pay five salaries. You hire a team only when the work genuinely splits into parts nobody has to wait on.

**What Anthropic reported** _(internal research eval; treat the figures as directional and version-sensitive)_:

| Finding | Number |
|---|---|
| Multi-agent (Opus 4 lead + Sonnet 4 subagents) vs. single-agent Opus 4 baseline | Substantial improvement on the internal research eval |
| Token cost vs. a normal chat interaction | **~15×** |
| What explains most of the performance variance | **Token usage** — the architecture works largely because it buys more parallel computation |

**Rough cost arithmetic, made concrete.** A single agent answers a research question in ~10k tokens. The orchestrator version spins up a lead plus four subagents, each reading its own slice of sources in its own context, then a synthesis pass — five contexts plus synthesis, ~15× the tokens, so **~150k tokens for the same question.** The number is neither large nor small on its own. Its value depends entirely on whether the task **required** the extra agents. If the "research question" was a single lookup in costume, you paid the multiplier for nothing.

🚨 **When it fits and when it doesn't:**

- ✅ **Fits:** large tasks that split into **independent** parts — research across many separate sources, where subagents can explore simultaneously instead of sequentially.
- ❌ **Doesn't fit: tightly coupled work such as coding**, where each step depends on the previous one and cannot be explored in parallel. A single agent with good context handles most work at a fraction of the cost.

⚠️ **The multiplier compounds when something misbehaves.** A runaway subagent or an oversized tool result can push well past the 15× baseline before the request even completes.

**Fan-out multiplies the failure surface, it does not replace failure handling.** Every subagent needs the *same* retriable-vs-terminal classification, backoff, and fallback discipline as a single agent, applied **independently** — see [D4 · Production failure handling](../domain-4-eval-testing/notes.md#production-failure-handling--retriable-vs-terminal). One subagent that hits a rate limit with no backoff can **stall the whole synthesis step** while the lead waits on a return that never comes.

💡 **Model split that blunts the multiplier:** run the **more capable model as the lead** and **cheaper models as the subagents**. You keep coordination quality where it matters without paying top-tier rates across every parallel context. (Tier framing → [D5 · Model Selection and Tradeoffs](../domain-5-model-selection/notes.md#model-selection-and-tradeoffs-27).)

| | |
|---|---|
| **Handles well** | Broad tasks with **genuinely independent** parts — parallel exploration reduces wall-clock time on work that would otherwise run sequentially |
| **Adds cost or complexity** | **~15× tokens** before improving any answer, plus coordination latency to plan and compile, plus one failure surface per subagent |
| **Use a different approach** | **Tightly coupled work (coding), or a task one agent handles with good context → single agent.** Fan-out buys parallel computation; if the task has nothing to parallelize, you bought nothing |

### Agent memory — choosing what state survives a session

Memory scope is the decision of **what the agent knows when the next session starts, and what it costs to carry that forward.** It belongs in the **design phase, not a production refactor.** Get it wrong and you pay in one of two opposite directions:

- **Too much state held in-context** inflates every API call — the model re-reads the full conversation on every turn, so the bill scales with session length.
- **Too little state in persistent storage** strips the agent of cross-session memory — anything not written down is gone the moment the conversation ends.

| Approach | What persists | Cost | Use when | What you lose |
|----------|---------------|------|----------|---------------|
| **In-context memory** | State lives in the active conversation; survives turns *within* one session. | Zero retrieval overhead; token cost climbs as the conversation grows (full context re-sent each turn). | Short sessions where all needed state fits the window and nothing must survive a restart. | Everything at session end — a new session or a clear command wipes it. |
| **External storage** | State written to a database, read back at session start or on demand. | Retrieval latency on each call **+** the read/write logic you build and own. | State that must survive across sessions, move between users, or be shared across agent instances. | Nothing on the persistence side; the cost shows up as latency and ongoing implementation complexity. |
| **Summarized memory** | A condensed version of prior conversation, generated and injected at the next session's start. | Lower token cost than replaying full history, but the summarization step drops detail. | Long-running conversational agents whose full history would outgrow the context budget before they're done. | Any detail the summarizer didn't keep — the agent sees only what the summarization prompt chose to preserve. |
| **Stateless (no persistent memory)** | Nothing; each session is independent. | No overhead — nothing to store or retrieve. | Task-execution agents that finish and close out, or pipelines where every session is independent by design. | All prior context; a follow-up that depends on an earlier session has no way to reach it. |

> **Decide at design time.** An agent that helps the *same user across days* needs state carried between sessions → store summaries or full history outside the model's context window so the next session reads it back. An agent that takes *one job, finishes, and closes it out* has no prior session to recall → run it stateless.

**Handles well** — the scope matches the task at design time: external storage when the agent continues a thread across sessions; stateless when each job is self-contained; in-context when the session is short and doesn't need to survive a restart.

**Adds cost or complexity** — external storage adds retrieval latency and the read/write logic that goes with it; summarized memory depends on a **well-specified summarizer prompt** — without one, task-critical state gets dropped on every compression. Neither is free.

**Use a different approach** — holding all state in-context on the assumption the window will be big enough. Token cost grows with every turn (full context re-sent each call); without caching or compaction, long sessions accumulate cost faster than teams expect when they only measure early turns. **Measure actual session token usage against the window limit before committing.**

> 🔑 **Why design-time is cheap and refactor-time is dear.** The default path — store full history in the `messages` array and send it on every call — works in the prototype and keeps working for a while. Then token cost scales with every added turn, latency climbs as the window fills, and a long session eventually hits the hard limit and the agent stops responding. The fix (pull conversation state into external storage; add back only what each turn needs) is **mechanical** — a few hundred lines and a database the team already has. What it costs is **timing**: the work lands under a deadline already in motion, and every hour restructuring memory is an hour not spent on what the agent is supposed to do next.

### Skills — on-demand instruction loading

Memory scope (above) covers how an agent carries **state** across sessions. Skills solve a **different** problem: how to carry **repeatable instructions** across *tasks* without paying to inject them into every session.

A **Skill** is a reusable markdown file — **`SKILL.md`** in an identified directory — that teaches Claude how to handle one kind of task once. It has two parts: a **frontmatter block** (`name` + `description`) and the **instructions** below it. The **description is the matching criterion**: on each request Claude reads the name and description of every available Skill, compares them against your message, and **loads the full instructions only on a match.** Instructions not relevant to the current request never enter the context window.

That's the key contrast with the memory patterns above — in-context memory is **always present and grows every turn**; a Skill sits on disk until a task calls for it.

> **`CLAUDE.md` is environment-dependent — don't assume it always loads.** In the **Claude Code CLI**, `CLAUDE.md` loads into *every* session regardless of the task. In the **Agent SDK**, whether filesystem settings (including `CLAUDE.md`) load is controlled by the **`settingSources`** configuration — don't rely on a default; set it explicitly to the sources you intend, and confirm current default behavior against the Agent SDK reference at build time. A Skill, by contrast, loads only when the task matches — in **both** environments.

| Pattern | When it loads | Context cost | Best for |
|---------|---------------|--------------|----------|
| **Skill (`SKILL.md`)** | On demand, when a request matches the Skill's description. | **Low** — only name + description load at startup; the full body loads only on a match. | Task-specific expertise that shouldn't inflate sessions where it's unused: domain-specific output formats, specialized review checklists, workflows that apply to a subset of tasks. |
| **`CLAUDE.md`** | Every session, unconditionally (CLI) / per `settingSources` (SDK). | Fixed overhead per session regardless of task. | Always-on project standards that apply to everything: coding conventions, required output-format rules, constraints that hold across all tasks. |
| **In-context instructions** | Present for every turn within that session. | Grows with session length; doesn't survive session end. | Short sessions where the full history fits the window and nothing needs to persist — one-off exploratory work. |

> ⚠️ **Version-sensitive (as taught in class; verify against current docs — noted 2026-07-18):** Skills are available on the **Messages API** today, but the integration is **beta** and its configuration differs from the Claude Code / Agent SDK paths. Two beta headers are required on the request: **`code-execution-2025-08-25`** and **`skills-2025-10-02`**. Skills invoked this way run **inside the code-execution container**, not the calling application's environment — which constrains what filesystem access and tools the Skill can rely on. Beta headers are versioned and change as features move toward GA; confirm the header values, whether the feature has reached GA, and whether the code-execution container is still the runtime path before building against this in production.

**Subagents don't inherit Skills.** When you delegate a task to a subagent it starts with a **clean context** — Skills *and* conversation history do **not** carry over. If the subagent needs a Skill, you must **list it explicitly in the subagent's configuration.** Design-time implication: register the instructions *against the subagent*, don't assume they flow down from the parent.

> **One thing that *does* carry down:** subagents **inherit the permission context** from the parent session — permission scope is **not** reset at delegation, even though Skills and history are. Don't read "clean context" as "clean permissions."

> **Cross-domain pointer → [Domain 8 · Agentic Customization](../domain-8-tools-mcps/notes.md):** choosing among **built-in Tools vs. custom Tools vs. Skills vs. MCPs** for a given use case is the Domain 8 decision. This section's narrower job is the **loading mechanics** — Skill vs. `CLAUDE.md` vs. in-context — as a context-management pattern alongside memory scope.

### Frameworks (blueprint pointer)

The blueprint names **Strands, LangGraph, and PydanticAI** under this skill. They are alternative harnesses for the same loop pattern — the register/prompt/execute/exit steps above don't change; the framework supplies more or less of the scaffolding. _Framework-specific detail to be added as class covers it._
