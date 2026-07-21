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
