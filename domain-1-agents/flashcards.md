# Domain 1: Agents and Workflows — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Agent Architecture

**Q:** In one sentence, what is an agent?
**A:** A multi-step tool-use loop with managed context and a defined goal.

**Q:** What is the most critical mistake in agent development, and when does it happen?
**A:** Choosing the wrong pattern (agent vs. workflow) — before the first line of code.

**Q:** Choose a workflow or an agent: you can enumerate the exact steps in code.
**A:** Workflow.

**Q:** Choose a workflow or an agent: you can specify the goal and tools but not the exact path.
**A:** Agent.

**Q:** Choose a workflow or an agent: inputs vary unpredictably in content and structure.
**A:** Agent.

**Q:** Choose a workflow or an agent: error cost is real and step-level guardrails matter.
**A:** Workflow.

**Q:** What's the cost of using an agent where a workflow would do?
**A:** You add behavioral complexity with no added capability.

**Q:** What's the cost of using a workflow where an agent is needed?
**A:** It breaks whenever user input deviates from the predetermined path.

**Q:** What's the recommended progression of patterns?
**A:** Single API call → workflow → agent. Move up only when the simpler pattern can't handle the variability.

**Q:** Why do new failure modes appear in agents that single-turn tests miss?
**A:** Components running together across turns compound: routing decisions stack, context fills faster than expected, and a step gets bad input from an earlier mis-structured tool call.

**Q:** What extra observability does an agent require vs. a workflow?
**A:** Transcript-level tooling, because the path emerges from the model's reasoning rather than explicit branches — standard operational logging isn't enough.

## Agent Construction with Claude

**Q:** Name the three wiring paths, ordered by how much infrastructure you hand off.
**A:** Raw Messages API loop (own everything) → Agent SDK (loop in your process) → Claude Managed Agents (Anthropic runs loop + sandbox).

**Q:** What should drive the choice of wiring path?
**A:** Deployment and compliance constraints — not whichever path is fastest to prototype.

**Q:** On the raw Messages API path, what do you own?
**A:** The full loop: tool execution, context management, retries, and exit conditions. Nothing is provided.

**Q:** With the Agent SDK, where does the loop run and who executes tools?
**A:** The loop runs inside your own process; the SDK provides the structure, but your code still executes the tools.

**Q:** With Claude Managed Agents, who runs the loop and how does your app interact with it?
**A:** Anthropic runs the loop and sandbox server-side; your app defines the agent once, refers to it by ID, sends user events, and streams results back over SSE.

**Q:** How is a Managed Agent defined, versus an Agent SDK agent?
**A:** Managed Agent = a versioned API resource. Agent SDK = code-level/filesystem config.

**Q:** Why are Managed Agent sessions not eligible for ZDR or a HIPAA BAA?
**A:** Sessions are stateful and stored server-side; that storage is what rules them out.

**Q:** Your workload carries PHI or is under a ZDR requirement. Which paths remain?
**A:** Agent SDK or a raw loop on a covered configuration. Managed Agents is ruled out regardless of operational fit.

**Q:** When is Managed Agents a strong default?
**A:** Long-running tasks (minutes/hours) and cases where you'd rather not build/secure a sandbox and loop yourself.

**Q:** Prototyping on the Agent SDK, then moving to Managed Agents — what should you expect?
**A:** A re-expression step, not a direct export. The definition carries over conceptually but the format changes (filesystem/code config → versioned API resource).

**Q:** What are the four steps of wiring the loop?
**A:** 1) Register tools, 2) set a scoped system prompt, 3) handle the tool-use loop (your code executes each call), 4) define exit conditions.

**Q:** Why scope the system prompt to the task?
**A:** A broad prompt produces broader, less reliable tool routing; naming the task and its tools produces more consistent behavior.

**Q:** What happens without explicit exit conditions?
**A:** The agent keeps requesting tool calls beyond what the task requires. Don't rely on Claude volunteering to stop.

**Q:** In the loop-wiring checklist, what must be true of tools referenced in the system prompt?
**A:** They must all be registered — no unregistered tool may be referenced (and don't omit scoping guidance for tools the agent does have).

**Q:** Before wiring prompts/tools/memory, what does a regulated-data constraint decide?
**A:** Which endpoint your code calls, which credentials it carries, the region, and where logs land.

**Q:** On direct Anthropic API traffic, is conversation content logged by default?
**A:** No. For an audited path (e.g., attorney-client privilege) the org must implement conversation logging in the application layer and route it to an approved destination.

**Q:** A partner needs EU data residency. Can they use the direct Anthropic API?
**A:** Not currently — the direct API doesn't provide EU data residency. Route through Bedrock or Vertex with the region pinned in client config.

**Q:** Does a HIPAA BAA cover Console, Workbench, beta features, or consumer plans?
**A:** No. BAA-covered access is direct API/SDK on a covered config or a cloud-mediated Bedrock/Vertex route; verify feature eligibility too.

**Q:** Which government routes are FedRAMP-authorized, and which is not?
**A:** Authorized: Claude for Government (via Palantir PFCS-SS), Bedrock GovCloud, Vertex AI Assured Workloads. Not authorized: Claude Enterprise on AWS Marketplace.

**Q:** Why is SOC 2 not in the endpoint-constraint table?
**A:** It governs how systems are built and operated, not which endpoint your code calls; it's a Domain 7 topic.

## Agent Patterns and Frameworks

**Q:** What does a human-in-the-loop checkpoint do?
**A:** Pauses agent execution and routes to a human review step before proceeding.

**Q:** What question determines where to place a HITL checkpoint?
**A:** What is the worst possible outcome if this step runs without a human check?

**Q:** Which HITL insertion point addresses the highest (irreversible) risk?
**A:** Before a destructive tool call — a write, delete, or send.

**Q:** Why insert a HITL check after a planning step?
**A:** A wrong plan produces the wrong outcome even if every step executes correctly (medium risk).

**Q:** What triggers an "on unexpected output" HITL check, and why not just retry?
**A:** An error flag, empty result, or out-of-bounds value; it catches failure modes retry logic alone won't resolve.

**Q:** Which is the more common production problem — over-tooling or under-tooling?
**A:** Over-tooling. Selection quality degrades as the tool surface grows.

**Q:** What does under-tooling cause?
**A:** The agent hallucinates a path or returns an incomplete result.

**Q:** What's the prescribed way to size an agent's toolset?
**A:** Start with the minimum set required, and add a tool only when a specific capability gap is confirmed.

**Q:** Which frameworks does the blueprint name under this skill?
**A:** Strands, LangGraph, and PydanticAI — alternative harnesses over the same loop pattern.

### Agent Patterns and Frameworks — Memory & Skills

**Q:** What is "memory scope"?
**A:** What the agent knows when the next session starts, and what it costs to carry that state forward.

**Q:** When should you choose an agent's memory scope — design time or refactor time?
**A:** Design time. Deciding then is cheap; refactoring memory under production pressure is expensive.

**Q:** What are the two opposite failure modes of a bad memory-scope choice?
**A:** Too much state in-context inflates every API call (full context re-sent each turn); too little in persistent storage strips cross-session memory (anything unwritten is gone at session end).

**Q:** Name the four memory approaches.
**A:** In-context, external storage, summarized, and stateless (no persistent memory).

**Q:** In-context memory — what persists and what's the cost?
**A:** State survives turns within one session only; zero retrieval overhead but token cost climbs as the conversation grows. A restart/new session wipes it.

**Q:** External storage — what does it buy and what does it cost?
**A:** State survives across sessions/users/agent instances; cost is retrieval latency per call plus the read/write logic you build and own.

**Q:** Summarized memory — when is it right, and what's the risk?
**A:** For long-running conversational agents whose full history would outgrow the context budget; the risk is that the summarizer drops any detail its prompt didn't preserve.

**Q:** When is stateless (no persistent memory) the right choice?
**A:** Task-execution agents that finish and close out, or pipelines where every session is independent by design.

**Q:** Same user across multiple days vs. one-job-and-close — which memory scope each?
**A:** Multi-day same user → carry state between sessions (external/summarized storage). One-job-and-close → stateless.

**Q:** Why is "just hold all state in-context, the window is big enough" the wrong default?
**A:** Token cost grows every turn; without caching/compaction, long sessions accumulate cost fast and eventually hit the hard limit and stop responding. Measure session token usage vs. the window limit first.

**Q:** What problem do Skills solve that memory scope does not?
**A:** Carrying repeatable *instructions* across tasks without injecting them into every session (memory scope is about *state* across sessions).

**Q:** What is a Skill, and what are its two parts?
**A:** A reusable `SKILL.md` file that teaches one kind of task once; a frontmatter block (`name` + `description`) plus the instructions below it.

**Q:** What determines whether a Skill loads on a given request?
**A:** The description. Claude matches every Skill's name+description against your message and loads the full instructions only on a match — otherwise they never enter context.

**Q:** Does `CLAUDE.md` always load into every session?
**A:** In the Claude Code CLI, yes, unconditionally. In the Agent SDK it depends on the `settingSources` configuration — set it explicitly rather than relying on a default.

**Q:** Skill vs. CLAUDE.md vs. in-context instructions — one-line best-fit for each.
**A:** Skill = task-specific expertise loaded on demand; CLAUDE.md = always-on project standards; in-context = short one-off sessions that don't need to persist.

**Q:** What two beta headers are required to use Skills on the Messages API (as of 2026-07-18)?
**A:** `code-execution-2025-08-25` and `skills-2025-10-02` — verify against current docs, as beta headers change toward GA.

**Q:** Where do Messages-API Skills run, and why does it matter?
**A:** Inside the code-execution container, not the calling app's environment — which limits the filesystem access and tools the Skill can rely on.

**Q:** Do subagents inherit Skills from the parent session?
**A:** No — a subagent starts with a clean context; Skills and conversation history don't carry over. List any Skill it needs in the subagent's own configuration.

**Q:** What *does* a subagent inherit from the parent, even though Skills and history don't?
**A:** The permission context — permission scope is not reset at delegation. "Clean context" is not "clean permissions."

### Agent Patterns — orchestrator-worker _(added 2026-07-19)_

**Q:** What are the three phases of an orchestrator-worker design?
**A:** Plan (lead decomposes the task) → parallel fan-out (subagents run concurrently, each with its own context window) → synthesis (lead compiles the returns).

**Q:** What did Anthropic report for the token cost of its multi-agent research system?
**A:** Roughly 15× a normal chat interaction — each subagent spends its own tokens against its own context, so the multiplier hits input and output alike. Quality improved substantially on the internal research eval (Opus 4 lead + Sonnet 4 subagents vs. a single-agent Opus 4 baseline).

**Q:** What explains most of the performance variance in that multi-agent result?
**A:** Token usage. The architecture works largely because it buys more parallel computation — which is why it only pays when the task genuinely parallelizes.

**Q:** Which task shape is orchestrator-worker *wrong* for?
**A:** Tightly coupled work such as coding, where each step depends on the previous one and nothing can be explored in parallel. A single agent with good context handles it at a fraction of the cost.

**Q:** Is 15× a ceiling?
**A:** No — a baseline. A runaway subagent or an oversized tool result can push well past it before the request completes.

**Q:** What model split blunts the cost multiplier?
**A:** More capable model as the lead, cheaper models as the subagents — coordination quality where it matters, without top-tier rates across every parallel context.

**Q:** Does fan-out reduce or increase your failure-handling work?
**A:** Increases it. Each subagent needs its own retriable-vs-terminal classification, backoff, and fallback. One subagent that hits a rate limit with no backoff stalls the entire synthesis step while the lead waits.

**Q:** The hiring analogy for multi-agent orchestration?
**A:** Five researchers finish a broad survey faster than one — and you pay five salaries. Hire a team only when the work splits into parts nobody has to wait on.
