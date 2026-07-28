# Domain 1: Agents and Workflows — Practice Questions

Format per item: scenario stem · state how many responses to select · options A–D (or more for multiple-response) · tag (e.g., "D1 · Agent Architecture") · answer key + per-option rationale at the end of the file.

12 original items written to blueprint objectives (not from the live exam). Answer key with per-option rationale at the end — don't scroll past the line until you've committed to answers.

---

**Q1 · D1 · Agent Architecture** (select ONE)
A team is automating a nightly job: read a fixed CSV, validate each row against a known schema, write valid rows to a database, and email a fixed summary. The steps never vary and the inputs are well-constrained. They're debating whether to build it as an agent "to be future-proof." What's the best guidance?

A. Build an agent — agents are more capable, so they're the safer default.
B. Build a workflow — the steps are enumerable in code, so an agent adds behavioral complexity without adding capability.
C. Build a multi-agent system with a planner and an executor for observability.
D. Build an agent but disable tool use so it behaves deterministically.

**Q2 · D1 · Agent Architecture** (select ONE)
Which situation most clearly *requires* an agent rather than a workflow?

A. A pipeline whose every execution follows the same sequence of five steps.
B. A task where you can specify the goal and the available tools but cannot enumerate the path in advance, and user inputs vary unpredictably.
C. A task with a real error cost where step-level guardrails and standard-tooling observability are required.
D. A batch process over inputs constrained to a known set.

**Q3 · D1 · Agent Construction with Claude** (select ONE)
A healthcare application processes Protected Health Information and must operate under a HIPAA BAA. The team likes Claude Managed Agents because the tasks run long and they'd rather not build a sandbox. What's the correct call?

A. Use Managed Agents; long-running sandboxed execution is exactly its strength.
B. Use Managed Agents but enable Zero Data Retention on the session to satisfy HIPAA.
C. Rule out Managed Agents and route to the Agent SDK or a raw loop on a covered configuration, because Managed Agent sessions are stateful/stored server-side and aren't eligible for a BAA or ZDR.
D. Use Managed Agents in production and the Agent SDK only for local prototyping.

**Q4 · D1 · Agent Construction with Claude** (select ONE)
A developer's single-agent loop keeps issuing tool calls well past the point the task is actually complete, never returning a final answer. Which part of the four-step wiring is most likely missing or wrong?

A. Tool registration — a tool the agent needs isn't registered.
B. The system prompt is too narrowly scoped to the task.
C. Exit conditions — there's no explicit stop criterion, so the loop depends on Claude volunteering to stop.
D. The tool-use loop isn't returning `tool_result` blocks.

**Q5 · D1 · Agent Construction with Claude** (select ONE)
A team prototyped an agent on the Agent SDK locally and now wants it in production as a Claude Managed Agent. What should they expect when moving the agent definition over?

A. A direct export — the SDK can serialize the agent straight into a Managed Agent.
B. A re-expression step: the definition carries over conceptually, but the format changes from code/filesystem config to a versioned API resource.
C. No change is needed; Managed Agents read Agent SDK config files directly.
D. A full rewrite of the loop logic, since the loop pattern differs between the two.

**Q6 · D1 · Agent Construction with Claude** (select ONE)
A partner has a firm internal data-residency policy: all model traffic must run on the cloud vendor their CIO has approved, and only that vendor. Another route is technically easier and would ship sooner. What should the code target?

A. The easier route — technical capability is what matters; procurement can be reconciled later.
B. The direct Anthropic API, since it's simplest to configure.
C. The delivery route on the partner's approved cloud vendor — procurement-level constraints rule the path out before engineering preference applies.
D. Whichever route the developer has the most experience with.

**Q7 · D1 · Agent Patterns and Frameworks** (select ONE)
An agent can call a `delete_records` tool and a `send_invoice` tool. Where should a human-in-the-loop checkpoint go, and why?

A. On unexpected output only, since retries handle everything else.
B. After the planning step, because a wrong plan is the highest risk here.
C. Before the destructive tool calls (delete/send), because they're irreversible and a wrong call can't be undone.
D. No checkpoint is needed if the tools are well-described.

**Q8 · D1 · Agent Patterns and Frameworks** (select TWO)
A production agent's tool selection has become erratic after the team registered every tool they "might need." Which TWO statements reflect correct orchestration guidance?

A. Over-tooling is a common production problem; selection quality degrades as the tool surface grows.
B. More registered tools always improve routing because Claude has more options.
C. Start with the minimum set required and add a tool only when a specific capability gap is confirmed.
D. Under-tooling has no downside, so err toward the smallest possible set regardless of the task.
E. Erratic routing from too many overlapping tools is fixed only by switching frameworks.

**Q9 · D1 · Agent Patterns and Frameworks** (select ONE)
A team stores the full conversation in the `messages` array and sends it on every call. The prototype works fine. What is the most likely failure as real sessions get long, and when should the fix have been chosen?

A. Latency and token cost stay flat because Claude caches the context automatically; no fix is needed.
B. Token cost and latency climb with every turn until a long session hits the context limit and the agent stops responding — and the memory scope should have been chosen at design time.
C. The agent silently forgets the current session's earlier turns; fix it by adding a summarizer at refactor time.
D. Nothing breaks — in-context memory scales indefinitely as long as the window is large.

**Q10 · D1 · Agent Patterns and Frameworks** (select ONE)
A customer-support agent must remember a user's prior tickets across sessions spanning days, and the same context must be visible to other agent instances serving that user. Which memory approach fits, and what cost do you accept?

A. In-context memory — zero retrieval overhead, and it survives restarts.
B. Stateless — each ticket is independent, so no memory is needed.
C. External storage — state survives across sessions and instances; you accept retrieval latency per call plus read/write logic you own.
D. Summarized memory alone — inject a summary at session start and never persist full state.

**Q11 · D1 · Agent Patterns and Frameworks** (select ONE)
Your project has an output-format checklist that applies to only about one task type in five. You want it available when relevant but don't want to pay context cost on every session. Where does it belong?

A. In `CLAUDE.md`, so it's always loaded and never missed.
B. In a `SKILL.md` whose description matches that task type, so its full body loads only on a match.
C. Pasted into the system prompt of every session as in-context instructions.
D. In an external database read at the start of every session.

**Q12 · D1 · Agent Patterns and Frameworks** (select TWO)
A parent agent uses a Skill, then delegates a subtask to a subagent, expecting it to behave the same way. Which TWO statements are correct?

A. The subagent automatically inherits the parent's Skills, so no extra configuration is needed.
B. The subagent starts with a clean context — Skills and conversation history don't carry over — so any Skill it needs must be listed in its own configuration.
C. The subagent inherits the parent's permission context; permission scope is not reset at delegation.
D. Delegating resets permissions to a safe default, so the subagent can't act until re-granted.
E. Conversation history carries into the subagent even though Skills do not.

**Q13 · D1 · Agent Patterns and Frameworks** (select ONE)
A team is building a coding agent that refactors a module: each edit depends on the result of the previous one. Someone proposes an orchestrator-worker design — a lead agent that fans the refactor out to four subagents in parallel — citing Anthropic's reported quality gain on its research system. What is the best response?

A. Adopt it — the reported quality gain generalizes across agent workloads.
B. Adopt it, but use the cheapest model for all five agents to offset the token multiplier.
C. Decline — fan-out buys parallel exploration, and tightly coupled work like coding has no independent parts to explore in parallel; a single agent with good context is the better fit.
D. Adopt it only if the team first adds retry logic to the lead agent.

**Q14 · D1 · Agent Patterns and Frameworks** (select TWO)
A research task is genuinely parallelizable and the team has decided an orchestrator-worker design is justified. Which TWO statements about the cost and risk profile are correct?

A. Anthropic reported roughly a 15× token cost versus a normal chat interaction, because each subagent spends its own tokens against its own context.
B. Running the more capable model as the lead and cheaper models as the subagents reduces the multiplier while preserving coordination quality.
C. The 15× figure is a ceiling — a misbehaving subagent or oversized tool result cannot push cost above it.
D. Fan-out replaces per-agent failure handling, since the lead's retry logic covers the subagents it dispatched.
E. Parallel subagents eliminate coordination latency because the planning and synthesis passes run concurrently with the workers.

**Q15 · D1 · Agent Patterns and Frameworks** (select ONE)
In a production orchestrator-worker system, one subagent hits a rate limit and has no backoff configured. What is the most likely observed failure?

A. The lead agent silently drops that subtask and synthesizes from the remaining returns.
B. The whole synthesis step stalls while the lead waits on a return that never arrives.
C. The request fails fast with a terminal error, since rate limits are non-retriable.
D. The other subagents inherit the rate limit and fail in sequence.

---

## Answer Key & Rationale

**Q1: B.**
- A — "More capable, so safer default" is the exact over-tooling-of-pattern mistake; agents add complexity, not free safety. ✗
- B — Steps are enumerable and inputs constrained → workflow; an agent would add behavioral complexity with no added capability. ✓
- C — Multi-agent adds even more overhead for a fixed, deterministic job. ✗
- D — An agent with tools disabled is just a workflow with extra machinery. ✗

**Q2: B.**
- A — Fixed, repeating sequence is the workflow signature. ✗
- B — Goal-and-tools-known but path-unknown, plus unpredictable inputs, is precisely when an agent is required. ✓
- C — Real error cost + step guardrails + standard-tooling observability all point to a workflow. ✗
- D — Known, constrained inputs → workflow. ✗

**Q3: C.**
- A — Operational fit doesn't matter; the compliance constraint decides first. ✗
- B — Managed Agent sessions aren't ZDR-eligible; you can't toggle that on to satisfy HIPAA. ✗
- C — Stateful, server-side session storage is why Managed Agents aren't BAA/ZDR-eligible; PHI/ZDR workloads route to the Agent SDK or a raw loop on a covered configuration. ✓
- D — Backwards: the constraint rules Managed Agents out of production for PHI, not just prototyping. ✗

**Q4: C.**
- A — A missing tool causes wrong/blocked actions, not endless looping past completion. ✗
- B — A narrowly scoped prompt improves routing; it isn't what makes the loop run forever. ✗
- C — Without explicit exit conditions the agent keeps requesting tool calls beyond the task; you must define when done means done. ✓
- D — Missing `tool_result` blocks stall the loop (Claude never gets data), the opposite of running too long. ✗

**Q5: B.**
- A — There's no direct serialize/export between the two formats. ✗
- B — Expect a re-expression step: conceptually the same agent, but code/filesystem config becomes a versioned API resource. ✓
- C — Managed Agents don't consume Agent SDK config files directly. ✗
- D — The loop *pattern* is constant across paths; you're not rewriting loop logic. ✗

**Q6: C.**
- A — Procurement/data-residency constraints rule the path out before engineering preference; "reconcile later" is how the wrong client config ships. ✗
- B — "Simplest" ignores the binding approved-vendor constraint. ✗
- C — Build against the CIO-approved vendor's route; the constraint decides the endpoint/credentials before convenience does. ✓
- D — Developer familiarity doesn't override an approved-vendor policy. ✗

**Q7: C.**
- A — Unexpected-output checks are for error flags/empty/out-of-bounds results; they don't cover irreversible writes/sends. ✗
- B — After-plan checks address wrong *plans* (medium risk); the sharpest risk here is the irreversible actions themselves. ✗
- C — Destructive tool calls (write/delete/send) are the high-risk, irreversible case → checkpoint before them. ✓
- D — Good descriptions don't make a delete/send reversible; a checkpoint is still warranted. ✗

**Q8: A and C.**
- A — Over-tooling is the common production failure; selection quality degrades as the tool surface grows. ✓
- B — False; more tools with overlapping descriptions produce erratic, not better, routing. ✗
- C — Correct discipline: minimum viable toolset, add only on a confirmed capability gap. ✓
- D — False; under-tooling forces the agent to hallucinate a path or return incomplete results — it has a real downside. ✗
- E — The fix is trimming/sharpening the toolset, not switching frameworks. ✗

**Q9: B.**
- A — Nothing is cached by default here; cost and latency grow with session length. ✗
- B — Full context is re-sent every turn, so cost/latency climb until the hard limit stops the agent; the cheap moment to pick a scope was design time. ✓
- C — In-context memory doesn't drop earlier turns mid-session; the failure is hitting the window limit, and the lesson is design-time choice, not a refactor-time patch. ✗
- D — In-context memory does not scale indefinitely; the window is a hard ceiling. ✗

**Q10: C.**
- A — In-context memory is wiped at session end; it can't survive a restart or reach other instances. ✗
- B — The requirement is explicitly to remember across sessions, so stateless can't satisfy it. ✗
- C — External storage is the approach for state that must survive across sessions, move between users, and be shared across instances; the tradeoff is per-call retrieval latency plus the read/write logic you own. ✓
- D — Summaries help with long single conversations, but "never persist full state" doesn't guarantee cross-instance shared state and summarization drops detail — not the fit here. ✗

**Q11: B.**
- A — `CLAUDE.md` loads every session (CLI) and pays fixed overhead even on the 4-in-5 tasks it doesn't apply to. ✗
- B — A Skill loads its full body only when the request matches its description, so unrelated sessions pay nothing beyond name+description — exactly the on-demand case. ✓
- C — In-context instructions sit in every turn of the session and grow cost; wrong for task-specific, occasional guidance. ✗
- D — External storage is for state, not conditionally loaded instructions, and reading it every session reintroduces the overhead you're trying to avoid. ✗

**Q12: B and C.**
- A — Skills do not carry over; the subagent starts clean. ✗
- B — Correct: clean context means Skills and history don't transfer; register the Skill against the subagent. ✓
- C — Correct: the permission context is inherited — "clean context" is not "clean permissions." ✓
- D — Permissions are not reset at delegation; this is the opposite of the rule. ✗
- E — Conversation history does not carry into the subagent either. ✗

**Q13: C.**
- A — The gain was measured on a broad *research* eval whose subtasks are independent; Anthropic's own analysis notes the pattern is less effective for tightly coupled tasks such as coding. ✗
- B — Downgrading every agent doesn't fix the structural mismatch, and it degrades the lead's coordination quality on top of it. ✗
- C — Correct. Fan-out buys parallel computation. Sequential, dependent steps have nothing to parallelize, so you pay ~15× tokens for no gain. ✓
- D — Retry logic is necessary in any design but doesn't make an unsuited architecture suited. ✗

**Q14: A and B.**
- A — Correct. Each subagent carries its own context and generates its own output, so the multiplier applies to input *and* output tokens. ✓
- B — Correct. The capable-lead / cheap-subagent split is the standard way to blunt the multiplier without losing coordination quality. ✓
- C — 15× is a reported baseline, not a ceiling; a runaway subagent or oversized tool result pushes well past it. ✗
- D — Fan-out *multiplies* the failure surface. Each subagent needs its own retriable-vs-terminal handling, backoff, and fallback. ✗
- E — Fan-out reduces wall-clock time on the independent work but *adds* coordination latency for the plan and synthesis passes, which are sequential bookends. ✗

**Q15: B.**
- A — Silent drop-and-continue is not the default; the lead is waiting on that return. ✗
- B — Correct. A stalled subagent blocks the compilation step — the concrete reason each subagent needs independent backoff. ✓
- C — Rate limits (429) are the canonical *retriable* error; with backoff this recovers. ✗
- D — Rate limits apply at the account/key level, not by inheritance from a sibling agent, and this isn't the described failure. ✗

---

**Scoring:** 18 correct decisions possible (12 single + 3×2 multi). Log misses to `weak-areas.md` with the skill tag.

---

## Supplement — Agent Architecture and Agent Construction

_Added 2026-07-27 to rebalance toward blueprint weight. Agent Architecture (4.5%) had two items and Agent Construction with Claude (5.3%) had four, against nine for Agent Patterns. Sourced from `notes.md`; deployment-path and compliance facts are version-sensitive — re-verify before relying on them._

**Q16 · D1 · Agent Architecture** (select ONE)
**Enumerable steps.** A finance team needs a monthly process: pull three named reports from a reporting system, reconcile them against a fixed rule set, and file an exception ticket for each mismatch. The steps, their order, and the rules never vary.
Which pattern fits, and why?

A. A workflow — the exact steps can be enumerated in code, so explicit branching gives step-level guardrails and observability with standard tooling
B. An agent, because the reconciliation involves judgment and agents handle judgment better
C. An agent, because the process touches multiple systems and only agents can call multiple tools
D. A multi-agent system with a planner and an executor, since the process has distinct phases

**Q17 · D1 · Agent Architecture** (select ONE)
**Complexity with no added capability.** A team builds an agent for a task whose steps they can already write out in order. In production it usually works, occasionally takes a different route through the same tools, and is hard to explain when it does.
What is the correct diagnosis?

A. Using an agent where a workflow was sufficient adds behavioral complexity with no added capability — the non-determinism is the cost, and there is nothing being bought with it
B. The agent needs a more capable model so its routing becomes consistent
C. The agent needs more tools so it has better options at each step
D. This is expected agent behavior and should be documented rather than changed

**Q18 · D1 · Agent Architecture** (select ONE)
**When the path cannot be enumerated.** A support assistant handles inbound requests that vary widely in content and structure. The team implemented it as a fixed sequence of steps. It handles the common cases well and fails outright whenever a request does not match the anticipated shape.
What does this indicate?

A. A workflow was chosen where an agent is needed — the system breaks whenever input deviates from the predetermined path, which is the defining failure mode of that mistake
B. The workflow needs more branches until every observed request shape is covered
C. The model is underpowered for the task and should be upgraded
D. The inputs should be constrained by rejecting requests that do not match a known shape

**Q19 · D1 · Agent Architecture** (select ONE)
**Where to start.** A team is scoping a new capability and debating whether to begin with an agent "so we don't have to rebuild later."
What is the correct progression?

A. Single API call, then workflow, then agent — start with the simplest pattern that solves the problem and move up only when the simpler one cannot handle the variability
B. Start with an agent, since starting simpler means rebuilding when requirements grow
C. Start with a workflow in every case, since workflows are always safer
D. Build the agent and the workflow in parallel and pick whichever performs better

**Q20 · D1 · Agent Architecture** (select TWO)
**What choosing an agent costs.** A team has correctly concluded that their task needs an agent.
Which TWO consequences should they plan for?

A. The path through the work emerges from the model's reasoning over accumulated context rather than from explicit branching in code
B. Observability requires transcript-level tooling — standard operational logging of status codes and latencies will not surface the structural failures
C. Coordination overhead and context cost drop relative to a workflow, since the agent decides its own path
D. Failure surface narrows, because the agent handles error cases the workflow's branches would have missed
E. Non-determinism is eliminated once the toolset is registered, since the tools constrain the possible actions

**Q21 · D1 · Agent Architecture** (select ONE)
**Tests that passed anyway.** Each component of an agent passes its own tests. Assembled, the system fills context faster than expected, and one step receives the wrong input because an earlier tool call was structured incorrectly.
What does this illustrate?

A. New failure modes appear only when components run together across turns, so isolated component testing cannot catch them — the system needs end-to-end testing against the assembled loop
B. The components were tested incorrectly and each unit test should be rewritten
C. Context filling faster than expected is unrelated to the integration and indicates a model change
D. This is a model capability limit and should be addressed by upgrading the tier

**Q22 · D1 · Agent Architecture** (select ONE)
**When a second agent earns its place.** A team proposes splitting a working single agent into a planner, an executor, and an evaluator running as separate agents that hand off through structured artifacts.
What is the right basis for the decision?

A. Multi-agent adds design decisions beyond the loop itself — handoff contracts, artifact formats, and failure handling between agents — so it needs a reason such as genuinely independent tracks or a separate evaluation context, not a preference for structure
B. Splitting is always an improvement, since separation of concerns applies to agents as it does to services
C. The split is required once an agent uses more than five tools
D. Multi-agent is only ever appropriate when the agents run on different models

**Q23 · D1 · Agent Architecture** (select ONE)
**Isolating context.** An agent's main loop is accumulating large volumes of intermediate search output that it needs only to answer one narrow sub-question.
What is the argument for delegating that sub-question to a subagent?

A. The subagent works in its own context and returns only the answer, keeping the bulk of the intermediate output out of the main loop's accumulated context
B. Subagents are faster because they run in parallel by default
C. Subagents reduce cost because their token usage is not billed to the parent
D. Subagents remove the need for exit conditions in the main loop

**Q24 · D1 · Agent Construction with Claude** (select ONE)
**Choosing among the wiring paths.** A team is deciding between a raw Messages API loop, the Agent SDK, and Claude Managed Agents. An engineer proposes picking whichever gets a prototype working fastest.
What is the correct basis for the decision?

A. Deployment and compliance constraints — they determine which endpoint, credentials, and data-handling model are permissible, and they rule paths out before convenience is considered
B. Prototyping speed, because the path can always be changed later at low cost
C. Which path the team has used before, since familiarity reduces defects
D. Model tier, since the wiring path is determined by which model is selected

**Q25 · D1 · Agent Construction with Claude** (select ONE)
**A constraint that decides the path.** An organization operates under a Zero Data Retention requirement. Managed Agents fits their operational needs well: long-running sessions and a managed sandbox they would otherwise have to build and secure.
What is the correct decision?

A. Managed Agents is ruled out — its sessions are stateful and stored server-side, and that storage is why the path is not eligible under a Zero Data Retention requirement; route to the Agent SDK or a raw loop on a covered configuration
B. Use Managed Agents and delete each session immediately after it completes, which satisfies the requirement
C. Use Managed Agents but disable the sandbox, which removes the stored state
D. The requirement applies to training data rather than session state, so Managed Agents is acceptable

**Q26 · D1 · Agent Construction with Claude** (select TWO)
**The Managed Agents trade.** A team is evaluating what changes if they move their agent to Claude Managed Agents.
Which TWO statements are correct?

A. They stop owning the iteration loop, the execution sandbox, in-loop retries, and the tool-execution runtime
B. They take on an agent defined as a versioned API resource plus an application layer that sends events and consumes streamed results
C. They stop owning the agent definition, since the configuration is inferred from usage
D. They gain the ability to run sessions under any compliance configuration, since the infrastructure is managed
E. They stop needing an application layer entirely, since the service handles the client side as well

**Q27 · D1 · Agent Construction with Claude** (select ONE)
**Prototype to production.** A team prototypes on the Agent SDK locally and plans to move to Managed Agents for production. They budget the migration as an export of their existing agent definition.
What should they expect instead?

A. A re-expression step — the agent definition carries over conceptually, but the format changes from code-level and filesystem configuration to a versioned API resource
B. A direct export, since both paths use the same definition format
C. A complete rewrite, because no part of the agent design carries over
D. No migration at all, since the Agent SDK deploys to Managed Agents automatically

**Q28 · D1 · Agent Construction with Claude** (select ONE)
**An agent that will not stop.** An agent completes the substantive work of a task and then continues issuing tool calls — re-reading files it has already read and re-running checks that already passed.
What is the most likely cause?

A. No explicit exit condition was defined, so the loop depends on the model volunteering to stop rather than on a stated stopping criterion
B. The tool descriptions are too short, so the agent re-reads to compensate
C. The context window is too small, so earlier results were dropped and must be re-fetched
D. The model tier is too low to recognize task completion

**Q29 · D1 · Agent Construction with Claude** (select ONE)
**A system prompt that is too broad.** An agent has six registered tools. Its system prompt says only "You are a helpful assistant. Use the available tools when appropriate." Tool routing is inconsistent across similar requests.
What is the highest-leverage fix?

A. Scope the system prompt to the agent's specific task and its actual tools — a broad prompt produces broader, less reliable routing, while one that names the task and the tools produces more consistent behavior
B. Register additional tools so the agent has a better option for each request
C. Remove the system prompt entirely and rely on tool descriptions alone
D. Increase the model tier, since routing consistency is a capability limit

**Q30 · D1 · Agent Construction with Claude** (select ONE)
**An EU residency requirement.** A team must guarantee that model execution happens within an approved EU jurisdiction. Their current client calls the direct Anthropic API against a global endpoint with no region specified.
What is the correct configuration change?

A. Route through a cloud-mediated path such as Bedrock or Vertex with the region pinned in client configuration to a covered jurisdiction, because the direct API does not currently provide EU data residency
B. Keep the direct API and add a region parameter to the existing global endpoint
C. Keep the direct API and pin a dated model snapshot, which fixes execution to one region
D. Keep the direct API and add application-layer logging of the region each request was served from

**Q31 · D1 · Agent Patterns and Frameworks** (select ONE)
**Where the checkpoint goes.** An agent drafts an outbound customer email, then sends it through an email tool. The team can add one human-in-the-loop checkpoint.
Where does it belong, and why?

A. Immediately before the send — the question that decides placement is what the worst outcome is if the step runs unchecked, and a sent email is irreversible
B. Immediately after the draft is generated, since reviewing the text is what matters
C. At the start of the run, so a human approves that the agent should proceed at all
D. After the send, so the human can review what went out and correct it in a follow-up

**Q32 · D1 · Agent Patterns and Frameworks** (select ONE)
**Erratic routing.** An agent has twelve registered tools, several with overlapping descriptions covering similar operations. It selects inconsistently among them for equivalent requests.
What is the most likely cause and fix?

A. Over-tooling with overlapping descriptions produces erratic routing — consolidate the overlapping tools and rewrite each description to state its distinct purpose and an explicit exclusion
B. Under-tooling — add more specific tools so each request has an exact match
C. The loop is executing tools in the wrong order and needs sequencing logic
D. Tool count does not affect routing, so the cause must be the model version

---

## Answer Key & Rationale — Agent Architecture and Construction supplement

**Q16: A.**
- A — The steps, order, and rules are fixed and enumerable, which is the defining condition for a workflow. Explicit branching gives step-level guardrails and observability with standard tooling. ✓
- B — Applying a fixed rule set is not open-ended judgment; nothing about the task requires the model to choose a path. ✗
- C — Workflows call tools too. Tool count is not what separates the two patterns. ✗
- D — Multi-agent adds coordination design on top of an agent that was not needed in the first place. ✗

**Q17: A.**
- A — When the path is already enumerable, an agent contributes non-determinism and a harder-to-explain execution trace without adding capability. That is the textbook cost of choosing an agent where a workflow was sufficient. ✓
- B — A more capable model still chooses its own path; the variability is inherent to the pattern. ✗
- C — More tools widen the space the model routes over, which makes inconsistency more likely. ✗
- D — Documenting a cost that buys nothing is not a substitute for removing it. ✗

**Q18: A.**
- A — Inputs varying unpredictably in content and structure is exactly the condition that calls for an agent, and breaking whenever input deviates from the predetermined path is the signature failure of choosing a workflow instead. ✓
- B — Chasing observed shapes with more branches never converges when the input space is genuinely open. ✗
- C — Common cases already work, so capability is not the limit. ✗
- D — Rejecting unanticipated requests refuses the requirement rather than meeting it. ✗

**Q19: A.**
- A — Start with the simplest pattern that solves the problem and move up only when the simpler one cannot absorb the variability. Each step up adds coordination overhead, context cost, and failure surface. ✓
- B — Starting at the most complex pattern pays those costs immediately for capability that may never be needed. ✗
- C — A workflow is not always safest; when the path cannot be enumerated it is the pattern that breaks. ✗
- D — Building both doubles the work to answer a question the requirements already answer. ✗

**Q20: A and B.**
- A — In an agent the path emerges from the model's reasoning over accumulated context rather than from branching in code, which is both the capability and the cost. ✓
- B — Structural failures — an unpaired tool result, a malformed message array, a stripped block — are invisible to status-code and latency logging, so agents need transcript-level observability. ✓
- C — Reversed: agents carry more coordination overhead and higher context cost than simpler patterns. ✗
- D — Reversed: agents have more failure surface, not less. ✗
- E — The toolset constrains which actions are possible, not which sequence gets chosen; non-determinism remains. ✗

**Q21: A.**
- A — New failure modes appear only once components run together across turns. Compounding routing errors, faster-than-expected context growth, and a step receiving badly structured input from an earlier call are all integration-level, so end-to-end testing against the assembled loop is required. ✓
- B — The unit tests were not wrong; they simply cannot observe cross-component behavior. ✗
- C — Context growth here comes from accumulated tool output across turns, which is squarely an integration effect. ✗
- D — Nothing described points at a capability ceiling. ✗

**Q22: A.**
- A — A multi-agent split introduces handoff contracts, artifact formats, and inter-agent failure handling on top of the loop. It needs a specific justification such as genuinely independent tracks or an evaluation that benefits from a separate context. ✓
- B — Service-style separation of concerns does not transfer for free; each boundary is a new place for information to be lost. ✗
- C — No tool count triggers a split; tool sprawl is addressed by consolidating descriptions. ✗
- D — Running on different models is one possible reason among several, not a requirement. ✗

**Q23: A.**
- A — A subagent runs in its own context and returns only its conclusion, so bulky intermediate output never enters the parent's accumulated context. That context isolation is the argument. ✓
- B — Parallelism is a separate property and is not automatic. ✗
- C — Subagent tokens are billed; the saving is in what the parent then carries forward, not in the delegation being free. ✗
- D — The main loop still needs a stopping criterion regardless of delegation. ✗

**Q24: A.**
- A — Deployment and compliance constraints determine which endpoint may be called, which credentials it carries, where logs land, and what data handling is permissible. They eliminate options before convenience is weighed. ✓
- B — Changing paths later means re-expressing the agent and re-validating the compliance posture; it is not low-cost. ✗
- C — Familiarity is a tiebreaker among permissible paths, not a basis for choosing one. ✗
- D — The same model runs on every path; tier and wiring are independent decisions. ✗

**Q25: A.**
- A — Managed Agent sessions are stateful and stored server-side, and that storage is precisely why the path is not eligible under a Zero Data Retention requirement. The operational fit does not override the governing constraint. ✓
- B — Deleting after the fact does not change that the data was retained during the session. ✗
- C — Session state is not a function of the sandbox, so disabling it does not address the constraint. ✗
- D — The requirement governs retention of the organization's data, which is exactly what session storage is. ✗

**Q26: A and B.**
- A — Anthropic runs the loop, the sandbox, in-loop retries, and the tool-execution runtime server-side, which is the whole point of the path. ✓
- B — What replaces it is an agent defined as a versioned API resource plus an application layer that sends events and consumes streamed results. ✓
- C — The agent definition is what the team continues to own; it is not inferred. ✗
- D — Managed infrastructure narrows the eligible compliance configurations rather than widening them. ✗
- E — The client side remains the team's, which is what consumes the streamed results. ✗

**Q27: A.**
- A — The agent design carries over conceptually while the format changes: code-level and filesystem configuration on the Agent SDK becomes a versioned API resource under Managed Agents. Budget a re-expression, not an export. ✓
- B — The two paths do not share a definition format. ✗
- C — The design is reusable; it is the encoding that changes. ✗
- D — There is no automatic deployment from one to the other. ✗

**Q28: A.**
- A — Without a stated stopping criterion the loop continues as long as the model keeps proposing tool calls. Defining when done means done is one of the four wiring steps precisely because the model does not reliably volunteer to stop. ✓
- B — Short descriptions cause routing problems, not failure to terminate. ✗
- C — Re-fetching due to lost context would also lose the earlier reasoning; the described behavior is redundant work after completion, not recovery. ✗
- D — Termination is a loop-design property, not a capability the tier supplies. ✗

**Q29: A.**
- A — A broad system prompt produces broad, less reliable tool routing. Naming the specific task and the tools actually available narrows the space the model routes over and makes behavior consistent. ✓
- B — More tools widen the routing space and make inconsistency worse. ✗
- C — Tool descriptions alone leave the task unscoped, which is the underlying problem. ✗
- D — The prompt is under-specified; that is a construction defect rather than a capability ceiling. ✗

**Q30: A.**
- A — The direct Anthropic API does not currently provide EU data residency, so residency-bound workloads route through a cloud-mediated path with the region pinned in client configuration. A global endpoint with no region is the common break. ✓
- B — Adding a region parameter does not create a residency guarantee the endpoint does not offer. ✗
- C — Snapshot pinning fixes model behavior, not where execution happens. ✗
- D — Logging records where a request was served; it does not constrain it. ✗

**Q31: A.**
- A — The placement question is what the worst outcome is if the step runs without a check. A sent email is irreversible, so the checkpoint belongs immediately before the destructive action. ✓
- B — Reviewing the draft is reasonable but leaves the irreversible step unguarded if anything changes between draft and send. ✗
- C — An upfront approval addresses whether to start, not the specific action that cannot be undone. ✗
- D — Review after an irreversible action is not a checkpoint. ✗

**Q32: A.**
- A — Too many tools with overlapping descriptions produce erratic routing. The fix is consolidation plus descriptions that state each tool's distinct purpose and an explicit exclusion for what it is not for. ✓
- B — Adding more tools to a set that already overlaps compounds the ambiguity. ✗
- C — The symptom is inconsistent selection among equivalent options, not execution order. ✗
- D — Tool count and description quality are the primary drivers of routing behavior. ✗
