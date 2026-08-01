# Domain 8: Tools and MCPs — Notes

**Exam weight: 10.6%**

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Tool Implementation | 4.4% | Function calling; tool description writing; error handling; agentic harness dispatch; client-side vs. server-side; approval patterns |
| MCP Server Development | 2.1% | Server authoring, deployment, integration; MCP resources/tools/prompts; stdio vs. sockets; client vs. server |
| Agentic Customization | 4.1% | Tradeoffs among built-in Tools, custom Tools, Skills, and MCPs for a given use case |

> **Central idea:** With most prompting techniques you steer *language* toward a good answer. With tool-use you hand Claude a set of *actions* and trust it to pick the right one — and that pick is driven almost entirely by what you wrote in the **schema**. Get the schema right and selection is reliable; leave it vague and Claude produces calls that look syntactically correct but pick the wrong tool, pass malformed inputs, or loop.

---

## Tool Implementation (4.4%)

### The tool-use loop — who owns what

The most common misconception is that **Claude runs the tools**. It does not. Claude reads your tool definitions, decides which one fits, and tells *your application* what to call and with which inputs. Your code executes the tool, gets the result, and sends it back; Claude then continues.

| Step | Action | Owner |
|------|--------|:-----:|
| 1 | Define schema (name, description, input_schema) | You |
| 2 | Send message to Claude | You |
| 3 | Claude returns a `tool_use` block (which tool + inputs) | **Claude** |
| 4 | Execute the tool | **You** |
| 5 | Return the result as a `tool_result` block | **You** |
| 6 | Claude continues — another `tool_use` block or a final end-turn response | **Claude** |

Key exam points:

- **The loop is not automatic.** If your app doesn't complete step 4 (execute) and step 5 (return), Claude never gets the data it asked for and the loop breaks.
- **The Claude-owns / code-owns boundary is where most tool-use bugs live.** Claude owns *selection*; your code owns *execution and returning results*.
- If the miss is **systematic** (Claude keeps picking wrong), the fix is upstream at **step 1 — the schema definition**, not in the runtime code.

### Message block structure

A tool-use conversation is built from **structured blocks**, not plain text. Each assistant and user turn is a *list* of blocks. Four block types do the work:

| Block type | Role | Contains | Critical rule |
|------------|------|----------|---------------|
| `text` | Assistant | Claude's prose output | Claude may return a `text` block *alongside* a `tool_use` block in the same turn. Your code must **preserve the full content array** (including the text block) when appending the turn to history. Dropping the text block corrupts the context Claude relies on for follow-ups. |
| `tool_use` | Assistant | Tool name, a unique **ID**, and the input arguments | Every `tool_use` block must be answered by a `tool_result` block in the **immediately following** user turn, carrying the **same ID**. Without that pairing the API rejects the next request. |
| `tool_result` | User | Matching `tool_use_id`, the result content, optional `is_error: true` when the call failed | `tool_use_id` must match the original **exactly**. Claude uses it to connect each result to the call that produced it — matters when one turn issues **multiple** calls and results arrive out of order. |
| `thinking` | Assistant (extended thinking only) | Claude's internal reasoning | Must be passed back **unchanged**. A **signature** verifies the reasoning wasn't modified; any edit or summary breaks it and the API rejects the message. **Redacted** thinking blocks follow the same rule — pass them back as received even though the content is encrypted. |

> **Related (already written):** the `thinking` / `redacted_thinking` carry-back rule is covered from the model-behavior side in [Domain 5 · LLM Fundamentals → Extended thinking](../domain-5-model-selection/notes.md). Same rule, two lenses: here it's a block-pairing invariant, there it's how extended thinking behaves in the loop.

**The critical invariant:** every `tool_use` block from an assistant turn must have a corresponding `tool_result` block in the **immediately following** user turn. Missing results, mismatched IDs, or results that appear in a *later* turn all cause an API **validation error**.

> This is **structural, not a prompting problem.** You cannot fix a block-pairing error by rewording the prompt — your code has to produce the correct sequence on every request.

### Schema anatomy — what Claude reads to select a tool

A schema has three parts. The **description** is what determines correct selection.

- **`name`** — a short, *specific* identifier. `get_account_balance` beats `get_data`.
- **`description`** — the critical part. Write it in **two halves: when to use *and* when NOT to use** the tool.
  - Too vague ("use this to find information") → Claude can't distinguish it from any other retrieval tool → wrong selections.
  - Good ("retrieve the current balance for a specific account ID; **do not** use this for transaction history") → gives Claude an **exclusion condition** to route on.
- **`input_schema`** — the parameters, in JSON Schema.
  - Mark a field **required** only when the call doesn't make sense without it.
  - Mark fields **optional** when the tool can operate without them (defaults / absence carries meaning).
  - **Overlapping parameter types between tools is the most common source of wrong-tool calls.**

Routing priority: Claude routes on **name + description**, with **parameter types as a secondary signal**. When signatures are identical, routing collapses to the description alone.

### Schema design decision table

| Decision | How to handle it | Why it matters |
|----------|------------------|----------------|
| **Subtask dependency** | If one tool's output feeds the next → **sequential** (separate turns), because the second call can't be built until the first result returns. If subtasks are independent → let Claude issue **multiple `tool_use` blocks in one turn** and run them concurrently. | The one decision that changes schema design. Current Claude models **default to parallel** when calls are independent. Model real dependencies as separate turns. Use **`disable_parallel_tool_use`** to force one call per turn. |
| **Required fields** | Put in the `required` array only fields the call can't work without. | Marking everything required forces Claude to **fabricate** values for fields it has no basis to fill. |
| **Optional fields** | Leave out of `required`; give defaults in the function signature. | Lets Claude **omit** info it doesn't have instead of guessing. An optional-but-required field forces every call to invent a value. |
| **Description length** | ~**3–4 sentences**: what it does, when to reach for it, what it returns. Add input examples where format matters. | Too short → Claude guesses (not enough signal to distinguish tools). Too long → trigger conditions get buried under detail Claude won't reference at decision time. |
| **Overlapping parameter types** | When two tools share a parameter shape, add **disambiguating language** naming the domain/trigger each is for. | With identical signatures, routing collapses to description alone; similar-sounding descriptions become indistinguishable. |

### Worked example — wrong-tool selection and the fix

*(Illustrative pattern, not a real production system.)* Two tools registered: `search_knowledge_base` and `get_cached_result`. Names are distinct, but **both descriptions start "use this to find information."** On ambiguous inputs Claude frequently picks the wrong one — because at the decision point the two look identical.

**Fix — add an exclusion sentence to each:**

- `search_knowledge_base`: "Use this to search the knowledge base when the user asks a question that requires looking up current information. **Do not use this if the result of a prior search in this session already covers the question.**"
- `get_cached_result`: "Use this to retrieve a result already fetched during this session. **Only use this if `search_knowledge_base` was called earlier in this conversation for the same query.**"

Exclusion conditions give Claude a **decision rule** instead of two identical-looking options.

- **Dependency on history:** these exclusion conditions rely on the **complete conversation history** being passed each request. If prior turns are truncated or dropped, Claude can't evaluate them and the exclusion logic **silently fails**.
- **Know when to stop disambiguating:** every extra tool increases the surface area Claude reasons over. If two tools do similar things and need *ever-longer* descriptions to keep apart → **merge them into one tool with a `type` parameter** instead.

| Handles well | Poor fit |
|--------------|----------|
| Routing to the right tool reliably when descriptions are specific and exclusion conditions are stated. | Two near-duplicate tools that need ever-longer descriptions to stay distinct → merge into one tool with a `type` parameter. |

---

## MCP Server Development (2.1%)

### What MCP is, and when to reach for it

Everything above assumes **you** author the schemas (name, description, input_schema, execution function). Often you don't need to. **MCP (Model Context Protocol)** is a standardized communication layer that moves tool **definitions and execution** out of your app and into dedicated **servers**. When a server already exists for the service you want, you connect to it instead of building the integration.

*Example:* a full GitHub integration (repos, PRs, issues, projects) would mean writing and maintaining a schema + execution function for every operation as GitHub's API evolves. An MCP server for GitHub has already done that — your app connects, receives the tool list, and Claude selects among them using **the same description-based routing**. What changes is *who wrote and owns the definitions*, not the mechanism.

### How MCP fits the loop

The loop **does not change**. Claude still issues a `tool_use` block, your app still executes and returns a `tool_result`, and all block-pairing rules still apply. Only **setup** differs: instead of registering schemas you wrote, your MCP client sends a **`ListToolsRequest`** to the server, receives the tool list, and passes those definitions to Claude. From Claude's view, MCP tools are **indistinguishable** from hand-authored ones.

> **Context-cost gotcha:** MCP servers add their tool definitions to the **context window even when the tools aren't used** in the current turn. Connect several servers and the definitions spend budget *before the first message*. Register only the servers you're actively using; check context cost against your window limit when connecting multiple.

### API MCP Connector configuration (context control)

If you use the API MCP Connector, you control loading cost through an **`mcp_toolset`** object in the `tools` array. It carries a **`default_config`** block applied to every tool on the server, with per-tool overrides via **`configs`** keyed by tool name. Two settings matter for context cost:

- **`defer_loading`** (boolean, in `default_config` or a per-tool `configs` entry): delays loading a tool definition until the model needs it → less upfront context when a server exposes a large tool list.
- **`enabled`** (boolean): turns individual tools on/off, so you can register a server but expose only the tools you want Claude to see.

> ⚠️ **Version-sensitive (as taught in class; verify against current docs — noted 2026-07-18):** the MCP Connector `mcp_toolset` behavior above requires the **`mcp-client-2025-11-20`** beta header on the request. Without it, `mcp_toolset` config won't apply as described.

### Transports — where the server lives decides which one

| Transport | Where | How it works |
|-----------|-------|--------------|
| **stdio** | Local servers | Your app spawns the server as a **subprocess** and communicates over standard input/output. |
| **Streamable HTTP** | Remote servers | Connect over the network via HTTP — **POST** for client→server messages, optional **GET-based SSE** stream for server-initiated messages. |

- An older **SSE-only** transport exists but is **deprecated** — new integrations should use Streamable HTTP.
- **Anthropic API MCP Connector supports remote (HTTP) servers only.** **stdio** servers require you to manage the MCP client connection yourself via the SDK (e.g., with **Claude Desktop or Claude Code** as the client).
- Once the connection is established and definitions received, your code treats **both transports identically**.

---

## Agentic Customization (4.1%)

> This skill is broader than MCP-vs-manual. The **selection tradeoff across all mechanisms** is immediately below; the **MCP vs. manual schema** axis follows it. The **Skills loading-mechanics** angle — Skill vs. `CLAUDE.md` vs. in-context instructions — is covered in [Domain 1 · Agents → Skills — on-demand instruction loading](../domain-1-agents/notes.md).

### Built-in vs. custom Tools vs. Skills vs. MCPs — the selection tradeoff

_Verified against platform.claude.com 2026-07-31. The tool inventory and beta surfaces are version-sensitive — re-check at build time._

Two questions sort every mechanism, and neither is "how hard is this to build":

1. **Who writes the schema?** You · Anthropic · a third party.
2. **Who executes the call?** Your code · Anthropic's infrastructure.

A third question comes *before* both: **is the thing you're adding a capability at all?** If Claude is missing *access*, you need a tool. If Claude is missing *knowledge of how you want the job done*, you need a Skill — and no tool will help.

| Mechanism | Schema by | Executed by | Reach for it when |
|---|---|---|---|
| **Server tools**<br>`web_search`, `web_fetch`, `code_execution`, `advisor`, `tool_search` | Anthropic | **Anthropic** | The capability is generic infrastructure you'd otherwise build and secure. No handler code in your app — results come back directly. |
| **Anthropic-schema client tools**<br>`memory`, `bash`, `text_editor`, `computer_use` | Anthropic | **You** | The tool touches *your* machine (filesystem, shell, desktop), so execution can't live anywhere else — but the schema is already published and Claude is trained on it. |
| **Custom tools** | You | You | The capability is yours (your database, your business rules), or routing precision matters more than saved effort. |
| **MCP servers** | A third party | Your client / the connector | A maintained server already covers the service. Coverage over precision — then allowlist and tune. |
| **Skills** | — *not a tool* — | — *not a tool* — | The gap is *how you want it done*, not access. Loads only on a description match. |

🚨 **"Built-in" is not one category, and this is where items are set.** `web_search` runs on Anthropic's infrastructure and returns results directly. `bash` and `text_editor` are *also* Anthropic-defined — Anthropic publishes the schema and trains Claude on it — but **your application still executes them** and returns a `tool_result`. Same "built-in" label, opposite execution model. A stem that treats every Anthropic-provided tool as server-executed is wrong.

> ⚠️ One exception to "server tools need no handler code": if Claude calls a server tool in the **same group of parallel tool calls** as one of your client tools, you are back in the handling path. See the Messages API's stop-reason/fallback behavior.

**The declaration form is the tell:**

```python
# Server tool / Anthropic-schema client tool — a versioned `type`, no schema from you
{"type": "web_search_20260209", "name": "web_search"}

# Custom tool — you supply all three parts
{"name": "lookup_order",
 "description": "Retrieve the current status of one order by ID. Do not use for…",
 "input_schema": {"type": "object", "properties": {...}, "required": ["order_id"]}}
```

🔑 **If you wrote an `input_schema`, you own the routing wording *and* the execution. If you passed a `type` string instead, Anthropic wrote both.**

**A Skill is not a tool.** It grants no capability, emits no `tool_use` block, executes nothing, and returns nothing. It changes *how* Claude does something it could already do. The one-line test: **missing access → a tool; missing knowledge of your conventions → a Skill.** A scenario describing "the output is correct but not in our format" is never solved by registering a tool. (Loading mechanics — Skill vs. `CLAUDE.md` vs. in-context, and the subagent-inheritance rules — are in [D1 · Skills](../domain-1-agents/notes.md).)

**Cost — each mechanism spends differently, and some of it before the first message:**

| Cost | Where it lands |
|---|---|
| **Tool definitions occupy context** | Every registered definition, whether or not it's called. **MCP servers add their whole tool list even when unused** — connect several and the definitions spend budget before you say anything. |
| **The tool-use system prompt** | Supplying *any* tools makes the API insert a system prompt enabling tool use. On **Opus 5** that's **286 tokens** for `tool_choice: auto`/`none` and **406** for `any`/`tool`; counts differ per model *(verified 2026-07-31)*. |
| **Server-tool usage charges** | Client-side tools price like any other request. **Server tools may add usage-based charges on top of tokens** — web search bills per search performed. |
| **Maintenance** | Custom schemas are yours forever, including every time the underlying service changes. MCP moves that burden to the server's maintainer. |

**Reducing the context cost** — on the API MCP Connector, `defer_loading` delays loading a definition until the model needs it, and `enabled` exposes only selected tools (see the MCP Connector section above). When the tool list is genuinely large, the **`tool_search` server tool** lets Claude discover and load tools on demand instead of holding every definition in context.

**Exam-style decision cues:**

| Stem says | Answer is |
|---|---|
| "Search the web / run Python on a file / fetch a page" | **Server tool** — don't build and secure a sandbox that exists |
| "Edit files in our repo / run shell commands / control a desktop" | **Anthropic-schema client tool** — schema provided, *your* code executes |
| "Query our internal database / apply our pricing rules" | **Custom tool** — nobody else can write that schema |
| "Integrate all of GitHub/Slack/Jira, maintained as their API changes" | **MCP server** — coverage, then allowlist down |
| "Output is correct but not in our house format / follow our checklist" | **Skill** — instructions, not capability |
| "We need scope control over which tools Claude sees" | **Not automatically hand-authoring** — the connector allowlists per server. Description quality is still a valid reason |

### MCP vs. manual schema authoring — decision framework

| Choose | When |
|--------|------|
| **Use MCP** | A **well-maintained MCP server already exists** for the service — *and* it covers the specific operations you need and is actively maintained against the service's current API. Re-authoring those schemas yourself adds overhead for no new capability. (Reminder: the API MCP Connector supports **remote servers only**; local stdio servers need Claude Desktop / Claude Code as client, not the API connector directly.) |
| **Write schemas manually** | **No server covers your use case**, *or* you need **description-quality / scope control** a general-purpose server won't give. Note: for scope alone, the API MCP Connector supports **allowlisting / denylisting** tools per server via `MCPToolset` — so scope control isn't automatically a reason to hand-author. Description quality still can be. |
| **Use both** | Connect an MCP server for **breadth**, then apply the **description-tuning discipline** to the specific tools you actually route to. Narrowing the tool set (allowlist via `MCPToolset`) and sharpening descriptions are **two separate levers** — use both: allowlist to shrink the surface Claude reasons over, then tune descriptions for routing precision. |

**Recurring tradeoff to remember for the exam:** MCP gives you **coverage** (someone else wrote and maintains the schemas); manual authoring gives you **precision** (you own description quality and scope). They are not mutually exclusive.

---

## Building and Configuring an MCP Server — resources, prompts, transport, scope, auth

_Source: class module "MCP Servers" (recorded 2026-07-19). Extends the MCP Server Development section above; follows the plugins/packaging module in [Domain 3 · Packaging Workflows](../domain-3-claude-code/notes.md), which covers plugins as the layer that bundles skills, hooks, subagents, **and MCP servers** into one installable unit._

### Why a server, not a wired-in tool

Wire a tool directly into an app and you own both the schema and the execution **inside that app**. Three apps needing the same external service means three integrations to maintain. MCP separates tool definitions from any individual application and turns them into a **process** — build the capability once, and **every MCP client that connects gets it** without re-implementing.

Claude Code has a **built-in MCP client**: connect a server and Claude Code discovers its tools and can invoke them during a session.

### Three things a server exposes — tools, resources, prompts

Tools are only one of three primitives. The other two cover cases where a tool call isn't the right shape.

| Primitive | What it is | Reach for it when |
|-----------|-----------|-------------------|
| **Tool** | An action the model can call | The model needs to *do* something or fetch something it decides it needs |
| **Resource** | **Read-only data** the server exposes for the **client to fetch and place into context directly** — no model tool call involved. Requested **by address**. | You want known data in context **from the start of a turn**, and pulling it in directly is cheaper and more predictable than a tool call to go get it |
| **Prompt** | A **pre-written instruction template** the server exposes so a client can invoke a **vetted** prompt by name | Specific wording materially beats whatever a user would type, and you want **every client to get the same quality**, maintained in one place |

**Two resource forms:**

- **Direct resource** — a **fixed address** for data that takes no parameters (e.g., a list of available documents).
- **Templated resource** — a **parameter in the address** (e.g., a document address that takes a document identifier).

> ⚠️ **Resource support varies across MCP clients.** Verify your client has a mechanism to inject resources into context **before** designing around this pattern.

🔑 Exam cue: "read-only data the client pulls into context by address, not something the model calls" = **resource**. "Vetted, reusable instruction invoked by name" = **prompt**. "Action the model chooses" = **tool**.

### Transport — where the server runs decides the channel

Transport is the **communication channel** between MCP client and server.

| Transport | How it works | Use when | Does not work for |
|-----------|--------------|----------|-------------------|
| **stdio** | Client **launches the server as a local subprocess** on the same machine and talks over standard input/output | A local tool, a personal script, a dev server on your own machine | A server you want to **share across a team** or host remotely |
| **HTTP** | Client connects over the network to a **remotely hosted** server | Shared team servers, third-party hosted servers (GitHub, Linear), org-wide deployments | Anything that must run only on the local machine |
| **SSE** | Older server-push transport | — | **Deprecated** — use Streamable HTTP for new integrations |

### Context cost — and the Claude Code default that differs from the API connector

Every connected server contributes tool definitions that **would** occupy the context window if loaded upfront. Two different behaviors, and the exam can test either:

| Surface | Default behavior |
|---------|------------------|
| **Claude Code** | **Defers** tool definitions by default and uses a **search step** to discover and load only the tools a task calls for. An **opt-in mode** loads definitions **upfront when they fit within roughly 10% of the context window**, deferring only past that limit. |
| **API MCP Connector** | Loading is **explicit** — you control it with `defer_loading` / `enabled` in `mcp_toolset` (see the section above). |

> ⚠️ **Reconciles with the earlier note.** The "MCP servers add their definitions to context even when unused" warning above describes the **API connector / upfront-load** case. In **Claude Code**, deferral is the default. Either way the principle holds: **connect only the servers you need**, because every connected server enlarges the pool of definitions the model must account for.

This deferred-discovery behavior **is agentic search** applied to tools — same pattern as retrieval over documents. See [D6 · Context Engineering → RAG](../domain-6-prompt-context/notes.md).

### Configuration scope — who loads the server

Scope determines **which users and projects** load the server. Each scope maps to a different config location.

| Scope | Config location | Who gets it | Right for |
|-------|----------------|-------------|-----------|
| **Local** | `~/.claude.json`, under the **current project's path** | Only you, only this project | A server tied to one project's context that you aren't ready to commit; tooling that only makes sense in one repo |
| **User** | Your **personal Claude settings** | Only you, **all** your projects | A personal utility you use everywhere — a local DB tool, a script you rely on regardless of codebase |
| **Project** | **`.mcp.json` at the repo root**, committed to version control | **Everyone who clones the repo**, automatically | A server the whole team needs — the config travels with the code |
| **Enterprise** | **Managed settings**, admin-controlled | Everyone in the org, pushed centrally | Shared internal services, security tooling, anything that must be present org-wide and can't be left to individuals |

⚠️ **Project scope + stdio gotcha:** a project-scoped server still **runs from each teammate's machine**. For a stdio server the committed config stores the **launch command**, so every clone spawns its **own local subprocess** — and each teammate needs the **runtime installed locally** (e.g., Node for an `npx`-launched server).

🔑 **Transport and scope are independent decisions that interact.** A stdio server **cannot be project-scoped for sharing in the hosted sense** — it only ever runs on one machine at a time. **Match transport to where the server runs, then choose scope.**

### Permission rules that target a single MCP tool

Connecting a server exposes its **full** tool list — but you rarely want the agent reaching every one unchecked. The permission layer from [D3 · Permission modes](../domain-3-claude-code/notes.md) extends to MCP tools, and rules can name **an individual tool**.

- **Rule identifier format:** `mcp__server__tool` (double underscores).
- An **allow** rule on `mcp__github__create_issue` lets that one tool run without a prompt while **every other tool on the GitHub server still prompts**.
- A **deny** rule on a write-capable tool blocks it while **read-only tools on the same server stay available**.
- **A deny on one tool overrides an allow on the server.** (Same precedence as everywhere else in the permission system.)

This is how you connect a **broad** server but keep the agent inside a **narrow slice** of what it can do.

**Two different controls — don't conflate them:**

| Control | Question it answers | Type of control |
|---------|--------------------|-----------------|
| **Permission rule** (`mcp__server__tool`) | May this exposed tool **run**? | **Governance** |
| **`enabled` flag** (`mcp_toolset`, API MCP connector) | Does the model **see** this tool at all? | **Context-cost and scope** |

They're often used together. ⚠️ Verify exact rule syntax and the connector beta header against current docs before publishing.

### Worked example — the GitHub MCP server

A **remote server maintained by GitHub** exposing repo-management tools (review PRs, open issues, search code). It shows transport + scope + auth working together on a server someone else owns.

| Dimension | GitHub MCP |
|-----------|-----------|
| **Transport** | **HTTP** — it's hosted remotely by GitHub. You register it by providing the **server URL**. |
| **Scope** | **Project** when the whole team needs the same repo tooling; **Local** when only you need it. |
| **Auth** | **Personal Access Token (PAT)** — generate in GitHub, pass as a **Bearer token in the request header** of your MCP config. |

🚨 **The token must be supplied through an environment variable and referenced in the config file — never written inline into `.mcp.json`.** A token committed into a file enters **repository history** and **cannot be removed by overwriting the file in a later commit**.

### Two authentication patterns — PAT vs. OAuth

| | **Service credential (PAT)** — e.g. GitHub | **OAuth** — e.g. Linear |
|---|---|---|
| **How you get it** | You generate the token yourself in the service | Client redirects to the service's **browser sign-in** page on first connect |
| **Who manages it** | **You** store and rotate it | Token is **issued and stored automatically** after you approve access |
| **Handling** | Must live in an **env var**, referenced by config | **No credential copied or managed by hand** |
| **Right for** | Service-level credentials you control | Any integration where authorization is **tied to user identity** |

Both are **remote HTTP servers** and both follow the **same transport and scope logic**. **The authentication step is the only thing that differs** — a likely distractor axis on the exam.

### The MCP setup reference

| Context | Transport | Scope | Config location | Secrets handling |
|---------|-----------|-------|-----------------|------------------|
| **Personal local tool** (your machine only) | stdio | Local | `~/.claude.json` (per-project entry) | Env variables only. **Never** in the config file. |
| **Shared team server** (all teammates → same service) | HTTP | **Project** (`.mcp.json`) | `.mcp.json` committed to repo root | OAuth or env variables. **API keys must never be committed to `.mcp.json`.** |
| **Personal experiment** (not ready to share) | stdio or HTTP | Local | Personal Claude settings | Env variables only. |
| **Org-wide deployment** (admin-managed) | HTTP | Enterprise | Managed settings (admin-controlled) | Secrets managed by administrator; config **locked to prevent override**. |

### Cost · Complexity · Risk

- **Cost:** each connected server adds tool definitions to the pool. More servers → larger requests. **Load only the servers a given task needs.**
- **Complexity:** transport and scope are independent but interacting decisions. **Match transport to where the server runs before choosing scope.**
- **Risk:** 🚨 **committing an API key inside `.mcp.json` is the most common mistake in this material.** The key travels into repo history, where **rotating later is not sufficient to remove the exposure**. Secrets go in **environment variables**; the config file holds only the **server address**.

| | |
|---|---|
| **Handles well** | A **reusable** integration used across multiple sessions and shared with the team, where the capability is **stable enough to maintain as a separate process**. GitHub MCP is the model case. |
| **Adds cost or complexity** | Teams **not already managing environment secrets carefully** — each added server increases the number of places a secret can be mishandled, and the risk concentrates on the **committed `.mcp.json`**. |
| **Use a different approach** | A **one-off** task where the tool logic can live in the codebase and needs no reuse across sessions or applications. For a **single-project integration used by one person**, wiring the tool directly into the API call is simpler than maintaining a server. |

### Exam-style decision cues

| Cue in the stem | Answer |
|-----------------|--------|
| "read-only data we want in context from the start of the turn, fetched by address" | **Resource** (direct if no parameter, **templated** if the address takes one) |
| "we want every client to run the same carefully worded instruction, by name" | **Prompt** |
| "server runs as a local subprocess on my machine" | **stdio** transport |
| "the whole team should get this server automatically when they clone" | **Project scope** → `.mcp.json` committed to repo root |
| "a personal utility I want in every one of my projects, but not my teammates'" | **User scope** |
| "admin must push this to everyone and users can't override it" | **Enterprise scope** (managed settings) |
| "let one tool run unprompted but keep the rest of the server gated" | **Allow rule on `mcp__server__tool`** |
| "block the write tool but keep read tools usable on the same server" | **Deny rule on that one tool** — deny beats an allow on the server |
| "we don't want the model to even see this tool" | **`enabled: false`** in `mcp_toolset` — visibility, not permission |
| "we rotated the key after committing it to `.mcp.json`" | **Insufficient** — it's in repo history; the exposure isn't removed by a later commit |
| "committed config, stdio server, teammate gets 'command not found'" | Project-scoped stdio spawns **locally per clone** — teammate lacks the **runtime** |
| "browser sign-in on first connect, no token copied by hand" | **OAuth** (Linear pattern), not a PAT |

**Related:** the deny-beats-allow precedence here is the same rule as in [D3 · Permission modes](../domain-3-claude-code/notes.md); secrets-in-config is the [D7 · Identity, Secrets, and Key Management](../domain-7-security/notes.md) angle on the same fact; the deferred tool-loading behavior is the tool-side instance of agentic search in [D6 · Context Engineering](../domain-6-prompt-context/notes.md).

---

## Enterprise Integration — authenticating and deploying a server in a regulated environment

_Source: class module "MCP Servers" → Enterprise Integration (recorded 2026-07-19). Continues the section above: that one covered **building** a server and choosing transport + scope; this one covers what changes when the integration must survive a **security review**._

### Prototype vs. production — the questions that get added

A prototype answers one question: **does the connection work?** A production enterprise integration must also answer four:

| Question | What answers it |
|----------|-----------------|
| **Who is the model acting as, and is that identity auditable?** | The auth pattern — OAuth ties access to a **user identity**; a service credential ties it to a **service identity** |
| **What data can it access, and where does that data leave the org?** | Credential scope + **data residency** (regional endpoint + region-pinned platform deployment) |
| **Can an admin lock the configuration so no individual developer can change the auth setup?** | **Enterprise scope / managed settings** — admin-deployed, not user-overridable |
| **Can access be logged well enough to satisfy a compliance audit?** | A **`PostToolUse` hook** writing every tool call and its parameters to an audit store |

> These are not new problems — they're the same identity, access, and compliance requirements that apply to **any external system touching regulated data**. Treating them as part of integration *design* is what separates a demo from something deployment-ready.

### Authentication pattern by service type

| Service type | Auth method | Why |
|--------------|-------------|-----|
| **Remote, user identity** (SaaS, cloud tools) | **OAuth** | The server returns **401 Unauthorized** to signal auth is required; the client opens a **browser sign-in**; after approval a token is issued and stored. **No secret is copied by hand.** Expected pattern whenever the *user's* identity is part of the authorization model. **Linear MCP** is the example. |
| **Remote, service identity** (internal API) | **API key / PAT in an environment variable** | The credential belongs to the *service*, not a person. Passed as a header, sourced from an env var referenced by config — **never inline**. **GitHub MCP** is the example. |
| **Local, file-system access** | **File-system permissions** | **No credential exists to leak.** Access is bounded by **deny rules** on paths instead. |

🔑 The **401 → browser sign-in → token issued and stored** sequence is the exam's signature for OAuth. "Generate the token yourself and paste it into a header" is the service-credential path.

### The enterprise integration checklist

| Service type | Auth method | Where secrets live | What gets logged | Who can lock the config |
|--------------|-------------|--------------------|------------------|-------------------------|
| **Remote — user identity** (SaaS, cloud) | OAuth | Token issued by the OAuth provider, stored by the client | `PostToolUse` hook → audit log | Administrator via **enterprise managed settings** |
| **Remote — service identity** (internal API) | API key in an **environment variable** | Environment only. **Never** in committed config. | `PostToolUse` hook → audit log | Administrator via **enterprise managed settings** |
| **Local** (file system, local DB) | File-system permissions | **No credential needed** — deny rules enforce path access | `PostToolUse` hook → audit log | **Deny rules** in enterprise managed settings |

> Note the constant: the **audit hook is the same in all three rows.** What varies is the credential and where it lives.

### What regulated industries add on top of working authentication

A financial-services or healthcare customer asks three questions a prototype never faced, and each maps to a specific mechanism already in this material:

| Their question | Mechanism that answers it | Why it's a checkable answer |
|----------------|---------------------------|-----------------------------|
| "Can a developer change the auth setup mid-audit?" | **Enterprise managed configuration** — admin-deployed server config that **individual users cannot override** | Auth is consistent org-wide and doesn't depend on each developer's settings file being correct |
| "How is access logged?" | **`PostToolUse` hook** logging every tool call + parameters to an audit store | The hook fires **deterministically for every call, regardless of what the model decides** — the log is not something the model can skip |
| "Where is data processed?" | **Data residency** — server configured with an HTTP endpoint **in a specific region**, plus a platform deployment that **pins processing to that region** | Gives a reviewer a verifiable answer to where data goes |

🔑 This is why the **infrastructure requirement and platform choice matter at audit time, not just at build time.** The residency decision is the same one framed from the endpoint side in [D1 · Regulated data sets the endpoint, credentials, and logging](../domain-1-agents/notes.md) and [D7 · Identity, Secrets, and Key Management](../domain-7-security/notes.md).

### Cost · Complexity · Risk

- **Cost:** OAuth adds a **one-time setup step per user per service**. API keys require a **rotation process**. Audit logging via `PostToolUse` adds **small overhead to every tool call**.
- **Complexity:** Regulated environments add requirements that never appear in a prototype. **Identifying them during scoping** is the discipline that keeps the integration on schedule.
- **Risk:** 🚨 Risk **concentrates at the prototype→production transition.** A system with **hardcoded credentials, no audit log, and no central lock will not pass a regulated customer's security review.** The fixes aren't hard — they just have to happen *before* the review.

| | |
|---|---|
| **Handles well** | Any integration touching data a regulated customer cares about, where the tooling **already supports enterprise managed settings and audit hooks**. Scoping security up front costs little and prevents the integration stalling at final review. |
| **Adds cost or complexity** | Teams unfamiliar with **OAuth flows or enterprise secrets management**. These patterns require **coordination with security/IT** in most regulated orgs — the timeline must account for that. |
| **Use a different approach** | A **prototype or PoC that will never see production data.** The full checklist isn't warranted for a demo — but **apply the environment-variable habit anyway**: it costs nothing and is good practice. |

### Exam-style decision cues — enterprise integration

| Cue in the stem | Answer |
|-----------------|--------|
| "server returns 401, client opens a browser sign-in, token stored automatically" | **OAuth** — remote service with user identity |
| "internal API, credential belongs to the service not a person" | **API key in an environment variable**, passed as a header |
| "local file-system server — what's the credential story?" | **No credential.** File-system permissions + **deny rules** on paths |
| "compliance needs a record of every tool call and its parameters" | **`PostToolUse` hook** to an audit store — fires deterministically, model can't skip it |
| "a developer must not be able to change the auth config during an audit window" | **Enterprise managed settings** — admin-deployed, non-overridable |
| "reviewer asks where the data is processed" | **Data residency** — regional HTTP endpoint + region-pinned platform deployment |
| "prototype has hardcoded creds, no audit log, no central lock — is it ready?" | **No** — those three gaps are exactly what fails a regulated security review |
| "demo-only integration, no production data — do we need the full checklist?" | **No**, but still use **environment variables** for secrets |

---

## Packaging a server for another team — pointer

Distributing a working server as a reusable asset (an **MCP server package**) is covered as one of three asset types in [Domain 2 · Packaging for Reuse](../domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator). The server-specific rule: **document each tool's expected inputs and let the installing team set the scope**, with credentials passed **by reference**, so the server installs into a new environment **without code edits**. Bundle the audit log (data touched · identity acted under · what it did) — the same three questions the enterprise-integration checklist above answers, now shipped as part of the package rather than configured per deployment.
