# Domain 7: Security and Safety — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## AI Application Security

**Q:** Why is prompt injection possible at all — what's the mechanism?
**A:** The model processes its whole context as one stream of tokens with no built-in structural boundary between trusted instructions and untrusted data. Instructions hidden in fetched content sit in the same context as your prompt, so the model treats them as commands.

**Q:** State the defense that follows directly from that mechanism.
**A:** Treat fetched and user-supplied content as data to be examined, never as instructions to be followed.

**Q:** Why doesn't trusting your users solve prompt injection?
**A:** The hostile instruction usually arrives in the content the agent *retrieves*, not in the user's prompt.

**Q:** What two things does Anthropic do about injection, and what limitation does it state?
**A:** Trains the model to recognize and refuse injected instructions, and runs classifiers over untrusted content entering the context. The stated limit: no agent that reads untrusted content is fully immune.

**Q:** Do delimiters around untrusted content solve the problem?
**A:** No — they help, but it's a soft boundary. The content can mimic your delimiters or argue persuasively for being an exception. The reliable boundary is what the agent is *allowed to do*, not the wording.

**Q:** Name the injection vectors beyond a fetched web page.
**A:** Any content someone else can write that the agent reads: shared-drive documents, database records, email bodies, output from a tool that itself fetched elsewhere.

**Q:** Indirect vs. hidden injection?
**A:** Indirect = planted in content the agent will read later, not in the current interaction. Hidden = white text, inside an image, or in a part of a page a human wouldn't scroll to.

**Q:** Jailbreak vs. prompt injection — what's the difference in target?
**A:** A jailbreak targets the model's own safety constraints; an injection targets your application's instructions. Different targets, same layered defense shape: constrain what reaches the model and limit what it's allowed to do as a result.

## Guardrails and Safe Deployment

**Q:** Why is least privilege called a design principle rather than a configuration setting?
**A:** It's the control that holds when every other layer fails. Assume the injection lands and the agent acts — the damage is bounded entirely by what that identity is allowed to do.

**Q:** Same injection, two identities — what's the difference in outcome?
**A:** Broad identity (write anywhere, read every secret) → an incident. Narrow identity (one output dir, read-only input) → a denied action and a log entry.

**Q:** Why must the agent's auth configuration be protected as tightly as the secret?
**A:** Anything that can modify the auth config can effectively act with that identity — and can remove the very control that bounds the blast radius. Editing the role is a privileged action.

**Q:** What makes a hook a security control where a prompt instruction isn't?
**A:** A prompt rule is not enforced. A hook is code that runs before the tool executes — it can block the call and log it, deterministically.

**Q:** What does a single `PreToolUse` hook give you beyond the block?
**A:** The evidence — it logs both the blocked action and every permitted privileged action, so the control and its audit record exist before a reviewer asks.

**Q:** Precedence when multiple hooks or rules apply to one action?
**A:** `deny` > `ask` > `allow`. One deny blocks regardless of how many allows are present.

**Q:** What gap does OS-level sandboxing close that hooks and roles can't?
**A:** Hooks and roles only cover the path or endpoint they explicitly name — a hook checking `write_file` won't block a call to an unreviewed endpoint. Sandboxing isolates at the process level, so it holds even when a hook is missing, misconfigured, or bypassed.

**Q:** The two forms of OS-level sandboxing?
**A:** Filesystem isolation (agent confined to its working directory) and network isolation (outbound limited to named endpoints). Configured via Claude Code settings; documented at code.claude.com.

**Q:** Which control do enterprise security reviewers ask about first?
**A:** OS-level sandboxing — it's what closes the gap between "we have hooks" and "we have a defensible boundary."

**Q:** Why is layering the point, rather than picking the best single control?
**A:** A defense depending on one control failing closed is one bug away from an incident. A layered defense degrades instead of collapsing when any single layer is bypassed.

**Q:** The one-line rule to carry out of this material?
**A:** No prompt instruction is a security control. If it must hold, enforce it with a hook, not a prompt.

## Identity, Secrets, and Key Management

**Q:** State the core rule for MCP credentials in one sentence.
**A:** The config file holds the address (and a variable reference); the environment or a secret store holds the value.

**Q:** Name the three secret-handling practices and the exposure each closes.
**A:** Separation (value never travels with the config that references it — closes committed/cloned copies); storage (env var or secret store — closes scattered per-service copies); rotation (scheduled and on suspected exposure — the only fix for an already-leaked key).

**Q:** Why is a committed credential worse than a shared one?
**A:** It enters repository history, and overwriting the file in a later commit does not remove it — forks, mirrors, clones, and CI logs still expose it.

**Q:** When is an environment variable enough, and when do you need a secret store?
**A:** Env var when the secret is local and short-lived (one machine, one pipeline run). Secret store when it's shared across services/people or must be audited.

**Q:** What three things does a secret store give you that an env var doesn't?
**A:** Runtime delivery to authorized callers, a record of who read what, and one rotation that updates every consumer at once.

**Q:** Why can't you cleanly rotate a hardcoded credential?
**A:** The old value stays in history, and every consumer hardcoded to it breaks when the value changes.

**Q:** Why does referencing a secret by name make rotation cheap?
**A:** The name doesn't change when the value behind it does, so no code has to be touched.

**Q:** Two habits that make rotation cheaper?
**A:** Scope each credential to the narrowest access its task needs, and keep a record of which services use it so a rotation doesn't have to discover its consumers mid-incident.

**Q:** Is rotation sufficient on its own?
**A:** No — rotation is a workable recovery only if separation and proper storage already hold.

**Q:** What three questions does a regulated (financial/healthcare) reviewer ask early?
**A:** Where is the data processed (data residency)? How is access logged (audit trail)? Can an administrator control the configuration centrally (managed configuration)?

**Q:** Why name those three during scoping rather than at review time?
**A:** They're expected questions — their absence reads as a risk. Raising them up front turns the security review from a blocker into a checklist you pass by showing what you already have.

**Q:** What does "managed configuration" actually prevent?
**A:** An individual developer quietly widening permissions on their own machine — it's the organizational version of locking the auth configuration.

**Q:** What's the catch with zero data retention (ZDR)?
**A:** Eligibility varies by model *and* by platform and is not guaranteed for every model even under an existing ZDR agreement — not all current models are ZDR-eligible, and newer/higher-capability ones may not have confirmed status.

**Q:** How do you resolve a ZDR requirement at scoping?
**A:** Confirm each model's current eligibility against the Anthropic Trust Center, and on Bedrock / Vertex AI / Microsoft Foundry confirm retention under that platform too. Treat it as a constraint on model and platform selection. _(Verified 2026-07-19.)_

## Claude Hooks

**Q:** Which hook provides a compliance audit trail, and what does it log?
**A:** `PostToolUse` — every tool call and its parameters, written to an audit store.

**Q:** Why isn't "tell the model to log each action" an audit trail?
**A:** A prompt is an instruction the model may not follow; a hook is code that runs deterministically on every call, outside the model's control.

**Q:** What's the cost of audit logging via hooks?
**A:** Small overhead on every tool call — usually acceptable against the compliance requirement it satisfies.
