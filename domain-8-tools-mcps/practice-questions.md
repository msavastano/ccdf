# Domain 8: Tools and MCPs — Practice Questions

13 original items written to blueprint objectives (not from the live exam). Answer key with per-option rationale at the end — don't scroll past the line until you've committed to answers.

Q1–Q6 cover the tool-use loop, schema design, and MCP-vs-manual. **Q7–Q13** cover the class module on **building and configuring an MCP server** (resources/prompts, transport, scope, permission rules, auth).

---

**Q1 · D8 · Tool Implementation** (select ONE)
A tool-use integration works in local testing but in production the conversation stalls right after Claude returns its first `tool_use` block — the tool's effect never appears and Claude never continues. What is the most likely cause?

A. Claude executed the tool but discarded the result.
B. The application isn't executing the tool and returning a `tool_result`, so the loop never completes.
C. The tool descriptions are too long for Claude to parse.
D. Parallel tool use is disabled.

**Q2 · D8 · Tool Implementation** (select ONE)
Intermittent HTTP 400 validation errors occur on the request immediately after Claude returns a turn containing both a `text` block and a `tool_use` block. The app stores only the `tool_use` block in history and sends the matching `tool_result` two turns later. Which change fixes the errors?

A. Lower `temperature` to make outputs deterministic.
B. Preserve the full content array (text + tool_use) and place the matching `tool_result` in the immediately following user turn.
C. Enable extended thinking so Claude repairs the history.
D. Mark every `input_schema` field as required.

**Q3 · D8 · Tool Implementation** (select ONE)
Claude keeps choosing `get_cached_result` when it should call `search_knowledge_base`. Both descriptions begin "Use this to find information." What is the best *first* fix?

A. Rename both tools so the names are more distinct.
B. Add an exclusion condition to each description stating when NOT to use it.
C. Move more parameters into the `required` array.
D. Immediately merge the two tools into one.

**Q4 · D8 · Tool Implementation** (select ONE)
An agent must look up a customer's account ID from their email address, then fetch that account's balance using the ID. How should the tools be modeled?

A. As independent tools, so Claude emits both `tool_use` blocks in one turn for parallel execution.
B. As separate sequential turns, because the balance call can't be built until the ID is returned.
C. In one turn with `disable_parallel_tool_use` set and both fields optional.
D. As a single MCP call, which removes the dependency.

**Q5 · D8 · MCP Server Development** (select TWO)
A team connects five MCP servers to one session and sees high token usage before any user message is sent. Which TWO statements are correct?

A. MCP tool definitions consume context even when their tools aren't used in the current turn.
B. Connecting more servers carries no context cost until a tool is actually called.
C. Using `defer_loading` / `enabled` via `mcp_toolset`, and registering only servers in active use, reduces upfront cost.
D. Switching to the deprecated SSE-only transport lowers tool-definition context cost.
E. Tool definitions load only after the first `tool_use` block is issued.

**Q6 · D8 · Agentic Customization** (select ONE)
A team wants to integrate a remote service that already has a well-maintained MCP server covering every operation they need, but they also want to expose only three of its tools to keep routing tight. Using the Anthropic API MCP Connector, what is the best approach?

A. Hand-author custom schemas for all operations to control scope.
B. Connect the MCP server, allowlist the three tools via `MCPToolset`, then tune those descriptions.
C. Connect the server over its stdio transport through the connector.
D. Avoid MCP entirely, because connectors can't limit which tools Claude sees.

**Q7 · D8 · MCP Server Development** (select ONE)
An internal MCP server hosts a policy handbook. Every session needs the handbook's table of contents in context from the very first turn, and it takes no parameters. Which primitive should the server expose it as?

A. A tool, so the model can call it whenever it decides the handbook is relevant.
B. A direct resource — read-only data at a fixed address the client fetches into context.
C. A templated resource, so the address can carry a section identifier.
D. A prompt, since the handbook contains instructions.

**Q8 · D8 · MCP Server Development** (select ONE)
A team writes an MCP server for an internal tool and wants every teammate to get it automatically on clone, with no per-person setup steps. The server is a Node package launched via `npx` on the developer's machine. Which statement about this plan is correct?

A. Project scope with a committed `.mcp.json` works, but the stdio server still spawns locally per clone — each teammate needs Node installed.
B. Committing a stdio server to `.mcp.json` makes it run centrally, so teammates need no local runtime.
C. stdio servers cannot be referenced in `.mcp.json` at all; they must be user-scoped.
D. Enterprise scope is the only scope that survives a clone.

**Q9 · D8 · MCP Server Development** (select TWO)
A developer connects the GitHub MCP server and wants the agent to open issues without prompting, but never to merge pull requests, while other GitHub tools keep prompting normally. Which TWO actions accomplish this?

A. Add an allow rule for `mcp__github__create_issue`.
B. Add a deny rule for the merge-pull-request tool on the same server.
C. Add an allow rule for the entire `github` server and rely on Claude's judgment for merges.
D. Set `bypassPermissions` so only the explicitly listed tools run.
E. Disconnect and reconnect the server with a narrower URL.

**Q10 · D8 · MCP Server Development** (select ONE)
During review, a teammate finds a GitHub Personal Access Token written inline in a `.mcp.json` that was committed three weeks ago. They propose overwriting the file with an environment-variable reference in a new commit. Is that sufficient?

A. Yes — the current file no longer contains the token, so the exposure is closed.
B. No — the token is in repository history and must be **revoked and rotated**; the config should reference an environment variable going forward.
C. Yes, provided the repository is private.
D. No — the token should instead be moved to a user-scoped config, still inline.

**Q11 · D8 · MCP Server Development** (select ONE)
A team compares the GitHub MCP server with the Linear MCP server. Both are remote and hosted by their respective vendors. What is the substantive difference between connecting to them?

A. GitHub uses HTTP transport while Linear uses stdio.
B. GitHub must be project-scoped while Linear must be user-scoped.
C. Authentication — GitHub uses a PAT you generate and store in an env var; Linear uses an OAuth browser sign-in that issues and stores the token automatically.
D. Linear exposes resources while GitHub exposes only tools.

**Q12 · D8 · MCP Server Development** (select ONE)
A team registers a server through the API MCP connector. They want the model to never see a particular destructive tool at all — not to be prompted about it, not to reason about it, not to spend context on its definition. Which control fits?

A. A deny permission rule on `mcp__server__destructive_tool`.
B. The `enabled` flag set to false for that tool in `mcp_toolset`.
C. Setting `defer_loading` to true for that tool.
D. Plan mode.

**Q13 · D8 · Agentic Customization** (select ONE)
A single developer needs a one-off integration with an internal endpoint used only inside one project, by them, for one workflow. No other application will use it. What is the best approach?

A. Build an MCP server and deploy it at enterprise scope for future reuse.
B. Wire the tool directly into the application's API call — a server adds a process to maintain for no reuse benefit.
C. Build an MCP server with stdio transport and project scope so teammates get it too.
D. Expose it as an MCP prompt.

---

## Answer Key & Rationale

**Q1: B.**
- A — Claude never executes tools at all; it only emits `tool_use` blocks. ✗
- B — The app owns steps 4–5 (execute + return `tool_result`). Skip them and the loop never completes — the exact failure described. ✓
- C — Description length affects *selection*, not whether the loop completes. ✗
- D — Disabling parallel changes concurrency, not whether results are returned. ✗

**Q2: B.**
- A — Temperature is unrelated to a block-pairing validation error. ✗
- B — Structural invariant: every `tool_use` must be answered by a `tool_result` with a matching id in the *immediately following* user turn, and the accompanying `text` block must be preserved in history. ✓
- C — Extended thinking doesn't repair history; you'd also then owe unchanged `thinking` blocks. ✗
- D — Marking all fields required is unrelated and causes fabricated inputs. ✗

**Q3: B.**
- A — Names help, but routing weights descriptions heavily; identical descriptions still collide. ✗
- B — Exclusion conditions give Claude a decision rule instead of two identical-looking options. ✓
- C — Required fields don't affect routing. ✗
- D — Merging is the fallback *only* when two near-duplicate tools need ever-longer descriptions to stay apart; try disambiguation first. ✗

**Q4: B.**
- A — Parallel calls work only when subtasks are independent; here step 2's input depends on step 1's result. ✗
- B — A real data dependency must be modeled as separate turns so the first result is available before the second call is built. ✓
- C — Disabling parallel forces one call per turn, but the reason is the dependency; making fields optional is irrelevant/harmful. ✗
- D — Wrapping in MCP doesn't remove a data dependency. ✗

**Q5: A and C.**
- A — MCP tool definitions load into the context window up front, used or not. ✓
- B — False; that upfront cost is exactly the problem. ✗
- C — `defer_loading`/`enabled` via `mcp_toolset`, plus registering only active servers, is the intended mitigation. ✓
- D — Transport choice doesn't change tool-definition context cost, and SSE-only is deprecated. ✗
- E — False; definitions are present before the first `tool_use`. ✗

**Q6: B.**
- A — Re-authoring every schema adds overhead for no new capability when a maintained server already covers the operations. ✗
- B — Server exists and is maintained → use MCP; scope is handled by allow/denylisting via `MCPToolset`, then description tuning for precision (the "use both" pattern). ✓
- C — The API MCP Connector supports remote HTTP servers only; stdio isn't connectable through it. ✗
- D — False; the connector can limit exposed tools via `MCPToolset` allow/denylisting. ✗

**Q7: B.**
- A — A tool makes the handbook available *if the model chooses to call it*; the requirement is that it be in context **from the start of the turn**. ✗
- B — A resource is read-only data the client fetches **by address** into context directly; **no parameter → direct** resource. ✓
- C — Templated resources put a **parameter in the address**; this data takes none. ✗
- D — A prompt is a pre-written **instruction template** invoked by name, not a data payload. ✗

**Q8: A.**
- A — Project scope + committed `.mcp.json` does distribute the config, but a stdio server runs as a **local subprocess per clone**; the config stores only the launch command, so each teammate needs the **runtime** (Node) installed. ✓
- B — False; stdio never runs centrally — that's the defining property of the transport. ✗
- C — False; stdio servers can be project-scoped, with the local-runtime caveat above. ✗
- D — False; project scope travels with the repo. Enterprise scope is admin-pushed, a different mechanism. ✗

**Q9: A and B.**
- A — An allow rule on `mcp__github__create_issue` exempts that single tool while every other tool on the server still prompts. ✓
- B — A deny rule on the merge tool blocks it; **deny beats an allow on the server**, and read/other tools stay available. ✓
- C — A server-wide allow removes the gate from **every** tool, including merge — the opposite of the requirement. ✗
- D — `bypassPermissions` removes safety prompts wholesale; it does not act as an allowlist. (Deny rules would still block, but the mode is the wrong instrument.) ✗
- E — The server URL doesn't scope the tool list; permission rules and the `enabled` flag do. ✗

**Q10: B.**
- A — Overwriting the file does **not** remove the token from repository **history**; anyone with clone access can recover it. ✗
- B — Once committed, the credential must be treated as **compromised — revoke and rotate** — and the config should reference an **environment variable** thereafter. ✓
- C — Private repos still expose the token to everyone with access, plus forks, mirrors, and CI logs. ✗
- D — Changing scope doesn't help; the problem is the **inline secret**, not where the file sits. ✗

**Q11: C.**
- A — Both are remote **HTTP** servers; neither uses stdio. ✗
- B — Scope is a choice about who loads the server, not a property either service imposes. ✗
- C — Same transport, same scope logic; **authentication is the only substantive difference** — PAT you manage vs. OAuth sign-in that manages the token for you. ✓
- D — Not the distinction being drawn; both expose tools, and resource support is a client-side concern. ✗

**Q12: B.**
- A — A deny rule governs whether an **exposed** tool may **run**; the definition is still loaded and the model still sees it. ✗
- B — The `enabled` flag controls **visibility** — the model never sees the tool, so it costs no context and can't be selected. ✓
- C — `defer_loading` delays loading until needed; the tool remains available to be loaded. ✗
- D — Plan mode is a Claude Code permission mode, unrelated to what a connector exposes. ✗

**Q13: B.**
- A — Enterprise scope pushes to the whole org for a tool exactly one person uses in one project. ✗
- B — For a one-off, single-project, single-person integration with no cross-application reuse, wiring the tool directly is simpler than maintaining a **separate process**. ✓
- C — Project scope shares it with teammates who don't need it, and adds a server to maintain for no reuse benefit. ✗
- D — A prompt is an instruction template, not an integration with an endpoint. ✗

---

**Scoring:** 16 correct decisions possible (12 single + 2×2 multi). Log misses to `weak-areas.md` with the skill tag.
