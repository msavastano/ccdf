# Domain 8: Tools and MCPs — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Tool Implementation

**Q:** In the tool-use loop, does Claude execute the tool?
**A:** No. Claude emits a `tool_use` block (tool name + inputs); your application executes it and returns a `tool_result`. Claude then continues.

**Q:** Which steps of the tool-use loop does your application own?
**A:** Executing the tool and returning the result (steps 4–5). The loop is not automatic — skip those and it breaks.

**Q:** If tool selection is systematically wrong, where is the fix?
**A:** Upstream at step 1 — the schema definition (usually the description), not the runtime code.

**Q:** What is the core block-pairing invariant in tool-use?
**A:** Every `tool_use` block in an assistant turn must be answered by a `tool_result` block with a matching `tool_use_id` in the immediately following user turn.

**Q:** What happens if a `tool_result` is missing, mis-ID'd, or lands in a later turn?
**A:** An API validation error. It's structural — you can't fix it by rewording the prompt.

**Q:** Why must you keep the `text` block that arrives alongside a `tool_use` block?
**A:** Dropping it corrupts the conversation context Claude relies on for follow-up turns; preserve the full content array in history.

**Q:** What does `is_error: true` on a `tool_result` signal?
**A:** That the tool call failed, so Claude can react or retry.

**Q:** Why does exact `tool_use_id` matching matter with parallel calls?
**A:** Multiple results can arrive out of order; the ID connects each result back to the call that produced it.

**Q:** How must `thinking` (and `redacted_thinking`) blocks be handled across turns?
**A:** Passed back unchanged — a signature verifies they weren't modified; any edit/summary breaks it and the API rejects the message.

**Q:** What are the three parts of a tool schema?
**A:** `name`, `description`, and `input_schema`.

**Q:** Which part of the schema most drives correct tool selection?
**A:** The `description` (Claude routes on name + description; parameter types are only a secondary signal).

**Q:** What two things should every tool description state?
**A:** When to use the tool and when NOT to use it (an exclusion condition).

**Q:** What is the most common source of wrong-tool calls?
**A:** Overlapping parameter types / look-alike descriptions between tools.

**Q:** When should a parameter go in the `required` array?
**A:** Only when the call makes no sense without it. Marking everything required forces Claude to fabricate values.

**Q:** How do current Claude models call tools by default, and how do you force one per turn?
**A:** Parallel when the calls are independent; use `disable_parallel_tool_use` to force one call per turn. Model true dependencies as separate turns.

**Q:** Recommended tool description length?
**A:** ~3–4 sentences: what it does, when to reach for it, what it returns — plus input examples where format matters.

**Q:** Two tools need ever-longer descriptions to stay distinct — what's the fix?
**A:** Merge them into a single tool with a `type` parameter.

**Q:** What silently breaks exclusion-condition disambiguation?
**A:** Truncating or dropping prior turns — Claude can't evaluate "was X called earlier?" without the complete conversation history.

## MCP Server Development

**Q:** What is MCP (Model Context Protocol)?
**A:** A standardized layer that moves tool definitions and execution out of your app into dedicated servers you connect to.

**Q:** Does the tool-use loop change when you use MCP?
**A:** No — Claude still emits `tool_use`, you return `tool_result`, pairing rules still apply. Only setup differs: the client sends a `ListToolsRequest` to get the tool list.

**Q:** What is the context-window cost of connecting MCP servers?
**A:** Tool definitions consume context even when unused; connecting many servers spends budget before the first message. Register only servers you're actively using.

**Q:** Name the two MCP transports and where each is used.
**A:** stdio (local — app spawns the server as a subprocess over stdin/stdout) and Streamable HTTP (remote — POST plus optional GET/SSE). SSE-only is deprecated.

**Q:** Which transport does the Anthropic API MCP Connector support?
**A:** Remote HTTP servers only. stdio servers require you to manage the client yourself (e.g., Claude Desktop or Claude Code).

**Q:** In the API MCP Connector, what do `defer_loading` and `enabled` do?
**A:** `defer_loading` delays loading a tool definition until needed (cuts upfront context); `enabled` turns individual tools on/off. Set via `mcp_toolset` `default_config` / per-tool `configs`. (Beta header `mcp-client-2025-11-20` required — version-sensitive.)

## Agentic Customization

**Q:** When should you use an existing MCP server instead of authoring schemas?
**A:** When a well-maintained server already covers the operations you need and is actively maintained against the service's current API.

**Q:** When is manual schema authoring justified over MCP?
**A:** When no server covers the use case, or you need description-quality control a general server won't give. (Scope alone isn't enough — the connector allow/denylists tools via `MCPToolset`.)

**Q:** What is the "use both" pattern for MCP + manual?
**A:** Connect a server for breadth, allowlist to shrink the tool surface, then apply description tuning for routing precision — two separate levers.

**Q:** In one line, what does MCP trade against manual authoring?
**A:** MCP gives coverage (someone else owns/maintains the schemas); manual gives precision (you own description quality and scope).

## MCP Server Development — building & configuring (class module, 2026-07-19)

**Q:** What three primitives does an MCP server expose?
**A:** Tools (actions the model calls), resources (read-only data the client fetches by address into context), and prompts (pre-written instruction templates invoked by name).

**Q:** What is an MCP *resource*, and when do you reach for one?
**A:** Read-only data the client fetches **by address** and places into context directly — no model tool call. Use it when you want known data in context from the **start of a turn** and pulling it in is cheaper/more predictable than a tool call.

**Q:** Direct vs. templated resource?
**A:** Direct = fixed address, no parameters (e.g. a list of documents). Templated = a **parameter in the address** (e.g. a document address taking a document ID).

**Q:** What's the caveat before designing around MCP resources?
**A:** Resource support **varies across MCP clients** — verify your client can inject resources into context first.

**Q:** What is an MCP *prompt* for, given users can just type their own request?
**A:** Cases where specific wording materially beats what a user would type, and you want **every client to get the same vetted quality**, maintained in one place on the server.

**Q:** Which transport for a local personal script, and how does it work?
**A:** **stdio** — the client launches the server as a **local subprocess** and communicates over standard input/output. Doesn't work for team-shared or remote servers.

**Q:** How does Claude Code handle MCP tool-definition context cost **by default**?
**A:** It **defers** definitions and uses a **search step** to load only the tools a task needs. An opt-in mode loads upfront when definitions fit within roughly **10% of the context window**.

**Q:** Name the four MCP configuration scopes and who gets each.
**A:** **Local** (`~/.claude.json`, this project only, just you) · **User** (personal settings, all your projects, just you) · **Project** (`.mcp.json` in repo root, everyone who clones) · **Enterprise** (managed settings, admin-pushed org-wide).

**Q:** Which scope shares a server with the whole team, and where does the config live?
**A:** **Project scope** — a `.mcp.json` file at the repo root, committed to version control.

**Q:** What's the gotcha with a project-scoped **stdio** server?
**A:** It runs from **each teammate's machine** — the committed config stores the launch command, every clone spawns its own subprocess, and each teammate needs the **runtime installed locally** (e.g. Node for `npx`).

**Q:** How is a single MCP tool named in a permission rule?
**A:** `mcp__server__tool` (double underscores) — e.g. an allow rule on `mcp__github__create_issue` lets just that tool run unprompted while the rest of the server still prompts.

**Q:** Deny on one MCP tool vs. allow on the server — which wins?
**A:** **Deny wins.** A deny on one tool overrides an allow on the server.

**Q:** Permission rule vs. the `enabled` flag — what's the difference?
**A:** A permission rule decides whether an **exposed** tool may **run** (governance). The `enabled` flag decides whether the model **sees** the tool at all (context-cost and scope). Often used together.

**Q:** Transport, scope, and auth for the GitHub MCP server?
**A:** **HTTP** (remotely hosted by GitHub, registered by URL) · **Project** scope for a team, **Local** for yourself · **Personal Access Token** passed as a **Bearer token** in the request header.

**Q:** Why is rotating an API key insufficient after committing it inline in `.mcp.json`?
**A:** The key is already in **repository history** — overwriting the file in a later commit does **not** remove the exposure. Secrets belong in **environment variables**; the config holds only the server address.

**Q:** GitHub MCP vs. Linear MCP — what actually differs?
**A:** Only **authentication**. Both are remote HTTP servers with the same transport/scope logic. GitHub uses a **PAT you generate and store**; Linear uses **OAuth** — a browser sign-in flow that issues and stores the token automatically.

**Q:** When is OAuth the right MCP auth pattern?
**A:** When the service's authorization model is **tied to user identity**, so each user signs in as themselves rather than sharing a service credential.

**Q:** When is an MCP server the *wrong* answer?
**A:** A **one-off** task where the tool logic can live in the codebase and needs no reuse across sessions or applications — for a single-project integration used by one person, wiring the tool directly is simpler.

## Enterprise Integration

**Q:** What four questions does a production enterprise integration have to answer that a prototype doesn't?
**A:** Who is the model acting as (auditable identity)? What data can it access and where does it leave the org? Can an admin lock the config? Can access be logged for a compliance audit?

**Q:** Which auth pattern fits a remote service where authorization is tied to the user's identity?
**A:** OAuth — server returns 401, client opens a browser sign-in, token is issued and stored automatically. No secret copied by hand. (Linear MCP.)

**Q:** Which auth pattern fits a remote internal API with a service identity?
**A:** An API key/PAT passed as a header, sourced from an environment variable referenced in config — never inline. (GitHub MCP.)

**Q:** What is the credential story for a local file-system MCP server?
**A:** There isn't one — no credential exists to leak. Access is bounded by file-system permissions and deny rules on paths.

**Q:** What HTTP status signals that an MCP server requires authentication?
**A:** 401 Unauthorized — it triggers the client's OAuth sign-in flow.

**Q:** What gets logged for audit, and by what mechanism?
**A:** Every tool call and its parameters, via a `PostToolUse` hook writing to an audit store.

**Q:** Why is a `PostToolUse` hook acceptable as a compliance control when a prompt instruction isn't?
**A:** The hook fires deterministically for every call regardless of what the model decides — the model can't skip it. A prompt is an instruction it may not follow.

**Q:** Which row of the enterprise checklist is identical across all three service types?
**A:** "What gets logged" — a `PostToolUse` hook to an audit log, regardless of OAuth, API key, or local file access.

**Q:** What answers "a developer must not be able to change the auth setup during an audit window"?
**A:** Enterprise managed configuration — an admin-deployed server config individual users cannot override.

**Q:** What gives a compliance reviewer a checkable answer to "where is data processed?"
**A:** Data residency — an HTTP endpoint in a specific region plus a platform deployment that pins processing to that region.

**Q:** Name the three gaps that will fail a regulated customer's security review.
**A:** Hardcoded credentials, no audit log, and no way to centrally lock the configuration.

**Q:** Where does enterprise-integration risk concentrate?
**A:** At the prototype→production transition — the security requirements have to be named during scoping, not discovered at the review.

**Q:** Does a demo-only PoC need the full enterprise checklist?
**A:** No — but use environment variables for secrets anyway. It costs nothing, and prototypes get promoted.

**Q:** What makes enterprise integration *more* expensive for some teams?
**A:** Unfamiliarity with OAuth flows or enterprise secrets management — these require coordination with security/IT, which the timeline must absorb.
