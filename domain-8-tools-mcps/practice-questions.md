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

---

## Supplement — Agentic Customization and Tool Implementation

_Added 2026-07-27 to rebalance toward blueprint weight. Agentic Customization (4.1%) had two items and Tool Implementation (4.4%) had four, against seven for MCP Server Development (2.1%). Sourced from `notes.md`._

**Q14 · D8 · Agentic Customization** (select ONE)
**Four options, one requirement.** A team needs their assistant to answer questions about events after the model's training cutoff. Anthropic already offers a server-side tool for exactly this, running on Anthropic's infrastructure with no execution loop on the team's side.
What should they reach for?

A. The built-in server-side tool — declaring it requires no client-side execution, no schema authoring, and no infrastructure, so writing a custom equivalent buys nothing
B. A custom tool wrapping a search provider, so the team controls the result format
C. An MCP server, since any external data access should go through MCP
D. A Skill containing current information, refreshed on a schedule

**Q15 · D8 · Agentic Customization** (select ONE)
**A server already exists.** A team needs their agent to work with a third-party service. A well-maintained MCP server exists for it, covers the operations they need, and is actively maintained against the service's current API. An engineer proposes hand-authoring the tool schemas anyway "so we understand them."
What is the correct assessment?

A. Use the existing server — re-authoring schemas someone else already maintains adds ongoing overhead for no new capability, and maintenance against the service's API changes becomes the team's problem
B. Hand-author, because understanding the schemas is worth the ongoing maintenance cost
C. Hand-author, because MCP servers cannot be scoped to a subset of their tools
D. Use neither; call the service's REST API directly from application code and skip tools entirely

**Q16 · D8 · Agentic Customization** (select ONE)
**No server covers it.** A team needs tools against an internal service with no public MCP server, and the operations are specific to their own data model.
What follows?

A. Author the schemas manually — when no server covers the use case, hand-authoring is the path, and it also gives full control over description quality
B. Build and publish an MCP server first, since custom tools are deprecated in favor of MCP
C. Use a general-purpose MCP server and constrain it with prompting
D. Wait for a server to become available, since manually authored schemas cannot be maintained

**Q17 · D8 · Agentic Customization** (select TWO)
**Coverage and precision together.** A team connects a broad MCP server that exposes forty tools. The agent needs six of them and routes inconsistently among several with similar descriptions.
Which TWO actions address this?

A. Allowlist the tools the agent actually needs, which shrinks the surface the model reasons over
B. Sharpen the descriptions of the tools it does route to, which improves routing precision among the remaining set
C. Replace the MCP server with hand-authored schemas, since scope control requires manual authoring
D. Register additional tools so each request has a more exact match
E. Move all forty tools into a Skill, which loads them only when relevant

**Q18 · D8 · Agentic Customization** (select ONE)
**A common reason that is not a reason.** An engineer argues the team must hand-author schemas because they need to limit which of a server's tools the agent can reach.
What is the correct correction?

A. Scope alone does not require hand-authoring — tools can be allowlisted or denylisted per server. Description quality is a legitimate reason to hand-author; scope by itself is not
B. Correct — the only way to limit a server's exposed tools is to author the schemas yourself
C. Correct, and additionally the connector cannot restrict tools at all
D. Scope is irrelevant, because exposing extra tools has no effect on routing

**Q19 · D8 · Agentic Customization** (select ONE)
**Procedure versus access.** A team wants two things: their agent should follow a specific internal review procedure whenever it writes a design document, and it should be able to read and update records in an external ticketing system.
Which assignment fits?

A. A Skill for the review procedure — packaged instructions loaded when relevant — and an MCP server or tools for the ticketing system, because reaching an external system requires an execution path, not instructions
B. A Skill for both, since a Skill can contain both instructions and system access
C. An MCP server for both, since MCP is the general integration mechanism
D. Custom tools for both, with the review procedure expressed as a tool the agent calls

**Q20 · D8 · Agentic Customization** (select ONE)
**The recurring axis.** A team is weighing an existing MCP server against writing their own schemas for the same service.
Which statement best captures the tradeoff?

A. MCP gives coverage — someone else wrote and maintains the schemas; manual authoring gives precision — you own description quality and scope. They are not mutually exclusive, and using both is often correct
B. MCP is always preferable, because maintained schemas are more accurate than hand-written ones
C. Manual authoring is always preferable, because it gives control
D. The choice is determined by tool count: use MCP above ten tools and manual authoring below

**Q21 · D8 · Tool Implementation** (select ONE)
**Who runs the tool.** A developer's agent hangs after the model requests a tool. Their code logs the request and waits, expecting the API to execute the tool and return the result on the next response.
What is the misconception?

A. Claude selects a tool and reports what to call with which inputs; the application executes it and returns a result block. The loop does not advance until the application completes execution and returns the result
B. The API executes registered tools automatically, so the hang indicates a network problem
C. Tools execute only when `tool_choice` forces them, which was not set
D. The result arrives asynchronously through a separate endpoint the application should poll

**Q22 · D8 · Tool Implementation** (select ONE)
**A validation error on the next request.** A harness executes two of the three tool calls in a turn, returns those two results, and defers the third to the following turn. The next request is rejected.
What rule was violated?

A. Every tool-use block from an assistant turn needs a matching result in the immediately following user turn — results deferred to a later turn, missing results, and mismatched identifiers all produce a validation error
B. Tool results must be returned one per turn, so returning two at once caused the rejection
C. Tools must be executed in the order the model requested them
D. Nothing structural — the deferred result simply arrives late and the model handles it

**Q23 · D8 · Tool Implementation** (select ONE)
**A dropped block.** An assistant turn contains a text block explaining what it is about to do, followed by a tool-use block. The harness appends only the tool-use block to history, discarding the text.
What is the consequence?

A. Preserving the full content array is required — dropping the text block corrupts the context the model relies on for follow-ups, because that turn no longer reflects what was actually said
B. No consequence — text blocks alongside tool use are decorative and safe to discard
C. The tool will execute twice, since the model re-issues the call it cannot see
D. The text block must be discarded, since only tool blocks belong in history

**Q24 · D8 · Tool Implementation** (select ONE)
**Systematic versus intermittent.** Two agents misbehave. Agent A picks the wrong tool for one whole category of requests, every time, and the loop code is provably correct. Agent B intermittently fails with unpaired tool results after network interruptions.
Where does each fix belong?

A. Agent A is a schema problem — fix the tool description and its exclusion condition. Agent B is a harness problem — gate the commit of an assistant turn so a partial turn is discarded rather than appended
B. Both are schema problems and both are fixed in the tool descriptions
C. Both are harness problems and both are fixed in the loop code
D. Agent A is a model capability limit and Agent B is a schema problem

**Q25 · D8 · Tool Implementation** (select ONE)
**Reasoning blocks in a tool loop.** A harness filters response content by block type before appending it to history, keeping only blocks whose type equals `thinking`. Requests begin failing after tool calls when reasoning is enabled.
What is wrong?

A. Reasoning blocks must be returned exactly as received, and the filter drops the redacted variant while also breaking the signature that verifies the block was unmodified — the fix is to preserve the content array intact rather than filter it
B. Reasoning blocks should never be sent back, so the filter should exclude them entirely
C. Reasoning blocks can be summarized to save context, and the failure is caused by their size
D. This is a prompting problem and can be resolved by instructing the model to reason more briefly

**Q26 · D8 · Tool Implementation** (select ONE)
**Two tools with the same signature.** An agent has `lookup_customer` and `lookup_order`, both taking a single optional string parameter named `id`, with descriptions that both begin "Retrieve information about a record."
What is the primary cause of the misrouting, and the fix?

A. Routing runs on name and description with parameter types as a secondary signal; identical signatures collapse routing onto the description alone, so each description must state its distinct purpose and an explicit exclusion
B. The parameters should be marked required, which is what determines routing
C. The tools should be merged into one, since two tools can never have compatible signatures
D. Parameter names must be unique across all tools, and renaming one resolves it

---

## Answer Key & Rationale — Agentic Customization and Tool Implementation supplement

**Q14: A.**
- A — A server-side built-in runs on Anthropic's infrastructure: declare it and results arrive as content blocks in the same response. No schema to author, no execution loop, no infrastructure to secure. Rebuilding that as a custom tool is pure cost. ✓
- B — Controlling result format is a real consideration, but it does not outweigh building and operating an execution path that already exists. ✗
- C — MCP is for integrating services that need a server; it is not a requirement for all external data. ✗
- D — A Skill carries instructions, not live data, and a scheduled refresh cannot keep pace with arbitrary current-events questions. ✗

**Q15: A.**
- A — When a maintained server already covers the operations you need, re-authoring the schemas adds no capability and transfers ongoing maintenance against the service's API changes onto your team. ✓
- B — Understanding is a training goal, not a production architecture; reading the server's schemas achieves it without owning them. ✗
- C — Scope is controllable through allowlisting and denylisting, so this is not a reason to hand-author. ✗
- D — Skipping tools removes the model's ability to decide when the service should be called, which is the point of registering them. ✗

**Q16: A.**
- A — No coverage means nothing to reuse, so hand-authoring is the path. It also carries the upside of full control over description quality, which is the main lever on routing accuracy. ✓
- B — Custom tools are not deprecated, and building a server to serve one consumer adds a component for no benefit. ✗
- C — Prompting cannot substitute for tools that do not exist against your internal data model. ✗
- D — Manually authored schemas are ordinary maintained artifacts. ✗

**Q17: A and B.**
- A — Allowlisting shrinks the surface the model reasons over, which directly reduces the space in which similar tools compete. ✓
- B — Sharpening descriptions raises routing precision among whatever tools remain. Narrowing the set and tuning descriptions are two separate levers and both apply. ✓
- C — Scope control does not require hand-authoring, so replacing the server discards its coverage for nothing. ✗
- D — Adding tools to a set that already overlaps compounds the ambiguity. ✗
- E — A Skill packages instructions, not tool registrations, so this does not describe an available mechanism. ✗

**Q18: A.**
- A — Tools can be allowlisted or denylisted per server, so scope alone is satisfied without hand-authoring. Description quality remains a legitimate reason; scope by itself is not. ✓
- B — Limiting exposure does not require owning the schemas. ✗
- C — Restriction is supported, so this compounds the error. ✗
- D — Extra tools do affect routing, which is why narrowing the set is one of the two levers. ✗

**Q19: A.**
- A — A Skill packages procedure and loads when its description matches the task, which fits the review procedure. Reaching an external ticketing system requires an execution path, which is what an MCP server or tools provide. ✓
- B — A Skill carries instructions, not an execution path to an external system. ✗
- C — Putting a purely instructional procedure behind a server adds an integration for something that needs no execution. ✗
- D — Expressing a procedure as a callable tool inverts the mechanism: the procedure shapes how the agent works, it is not an action it invokes. ✗

**Q20: A.**
- A — MCP supplies coverage through schemas someone else maintains; manual authoring supplies precision through description quality and scope you own. They compose — connect for breadth, then narrow and tune the tools you actually route to. ✓
- B — Maintained does not mean tuned for your routing needs; a general-purpose description can be the source of misrouting. ✗
- C — Control at the cost of maintaining every schema is rarely worth it when coverage already exists. ✗
- D — No tool-count threshold governs the choice. ✗

**Q21: A.**
- A — Claude owns selection; the application owns execution and returning the result. Nothing advances until the harness executes the call and returns a matching result block. ✓
- B — Custom tools are never executed by the API; that is the defining property of a client-side tool. ✗
- C — `tool_choice` influences whether and which tool is selected, not who executes it. ✗
- D — There is no separate result endpoint to poll for custom tool execution. ✗

**Q22: A.**
- A — The invariant is that every tool-use block is answered in the immediately following user turn, with the identifier matching exactly. Deferring one to a later turn leaves an unpaired call and the API rejects the request. ✓
- B — Multiple results in one turn is the correct arrangement, not the error. ✗
- C — Execution order does not matter; identifiers connect each result to its call. ✗
- D — This is a structural validation failure, not a latency effect. ✗

**Q23: A.**
- A — The full content array must be preserved. Dropping the text block leaves history that does not reflect what the assistant actually said, degrading the context the model uses on follow-up turns. ✓
- B — The text is part of the turn and part of the reasoning trail the model continues from. ✗
- C — Discarding a text block does not cause re-execution of the tool. ✗
- D — Assistant turns are lists of blocks, and all of them belong in history. ✗

**Q24: A.**
- A — A consistent, category-wide wrong selection with correct loop code points upstream to the schema: reword the description with an explicit exclusion. An intermittent unpaired-result failure correlated with dropped connections points at the assemble-and-commit step: gate the commit so a partial turn is discarded rather than appended. ✓
- B — The intermittent, network-correlated failure has nothing to do with descriptions. ✗
- C — Systematic misrouting with provably correct loop code is not a harness defect. ✗
- D — Neither is a capability limit, and the assignment is reversed. ✗

**Q25: A.**
- A — Reasoning blocks carry a signature verifying they were not modified, and must be returned exactly as received. Filtering on the exact type string silently drops the redacted variant, which is the classic version of this bug. Preserve the content array intact instead of filtering it. ✓
- B — Omitting them entirely is what breaks the turn when tools are in the loop. ✗
- C — Summarizing them breaks the signature; size is not the issue. ✗
- D — This is a structural invariant in the message array, and rewording the prompt cannot fix it. ✗

**Q26: A.**
- A — Routing runs on name and description, with parameter types as a secondary signal. When two tools share a signature, that secondary signal disappears and routing rests entirely on the description — so each needs a distinct statement of purpose plus an explicit exclusion. ✓
- B — Marking parameters required changes validation, not which tool is chosen. ✗
- C — Two tools can share a signature; the descriptions then have to do all the work. ✗
- D — Parameter names need not be globally unique; the overlap matters only because it removes a routing signal. ✗
