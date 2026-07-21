# Capstone — Claude Code, MCP & Integration

**What this is.** A cross-domain review sheet for the class module of the same name — the third module in the series, following [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md). Where that module covered the *developer primitive library* (prompting, tools, context, agents), this one covers **configuration**: the decisions that make an agent safe to run, shareable as a team asset, and connectable to real systems. It introduces **no new mechanics** — every technical fact is already written up and verified in a domain `notes.md`, and this sheet points to where.

**How to use it.** Read after the domain notes for **D3** (Claude Code), **D8** (Tools and MCPs), and the **D7** identity/secrets section — not before. It's an integration pass, best run in exam week. _Source: class module "Claude Code, MCP & Integration" (Key Takeaways + Glossary screens, recorded 2026-07-19); cross-checked against the domain notes the same day._

> ⚖️ **Blueprint reality check.** D3 is **3.1%** of the exam — roughly **1–2 items**. Don't let the volume of Claude Code material here mislead you about its weight. The reason this module is worth an integration pass anyway: **D8 (10.6%)** and **D7 (8.1%)** carry most of its content, and the permission/config reasoning shows up as *scenario framing* across other domains. Study the judgment, not the CLI trivia.

---

## The one idea

The previous module's failure shape was *dev illusion → production stressor*. This module's is different and worth naming separately:

> 🔑 **Every takeaway here is a decision that looks like a convenience setting and is actually a governance boundary.** Permission mode looks like a prompt-frequency preference; it's a risk decision. Transport looks like a plumbing detail; it decides who can connect. A hard-coded path looks like a local shortcut; it's the reason the plugin fails on every other machine. The exam tests whether you can see the boundary under the convenience.

The corollary that runs through all seven: **these are cheap to set and expensive to retrofit.** Enterprise deny rules, audit hooks, and OAuth are each an afternoon of work before deployment — and a failed security review after it.

---

## Master crosswalk — the 7 takeaways, routed to where the mechanics live

| # | Takeaway | The convenience framing that hides it | The governance reality | Lives in |
|---|----------|---------------------------------------|------------------------|----------|
| 1 | **Permission mode is a risk decision, not a speed decision.** | "Fewer prompts = faster work." Bypass mode gets reached for out of impatience. | Match the mode to the **risk profile of the work and environment**. A bypass mode on a workstation against a live codebase removes every checkpoint between agent and files. **A deny rule at project or enterprise level covers the gap a mode alone doesn't** — and survives every mode, including bypass. | [D3 · Permission modes + the four settings levels](domain-3-claude-code/notes.md) |
| 2 | **An AI code review gives you findings to triage, not a verdict to apply.** | The reviewer writes with uniform confidence, so every finding reads equally proven. | **Trust what it can prove from the diff** (missing null check, unclosed resource) — and confirm on the cited lines. **Treat runtime/cross-system claims as hypotheses**, because it made them without the evidence that would prove them. Put the human gate where a finding becomes a **hard-to-reverse action**. Raise accuracy by supplying conventions it would otherwise guess. | [D2 · Software Engineering Foundations → AI-assisted code review](domain-2-applications/notes.md); gate placement is [D1 · HITL insertion points](domain-1-agents/notes.md) |
| 3 | **A skill is portable, but "runs everywhere" is something you design for.** | One `SKILL.md` runs in Claude Code, the Messages API, and the Agent SDK — so it must be runtime-agnostic by nature. | Each runtime **loads and sandboxes it differently**: filesystem discovery in Claude Code, **beta header + code execution container** on the API, **`settingSources`** on the SDK. Scoped description + no local-environment assumptions ports cleanly; a skill that shells out to a local command does not. **Subagents never preload skills** — in any runtime. | [D3 · Skills + the three portability rules](domain-3-claude-code/notes.md); [D1 · Skills as on-demand instruction loading](domain-1-agents/notes.md) |
| 4 | **Durable context requires the right mechanism per concern.** | CLAUDE.md is the "project memory" file, so put everything in it. | Four mechanisms, four problems: **CLAUDE.md** = session-persistent project memory (**dilutes with size**); **rules files** = guidance scoped to a path; **hooks** = **deterministic** enforcement, not probabilistic; **subagents** = keep exploration out of the main context. Collapsing all four into CLAUDE.md yields a file that's harder to maintain and easier to ignore. | [D3 · Durable Project Context → the mechanism map](domain-3-claude-code/notes.md) |
| 5 | **A shareable setup requires portable components.** | It installs and runs — on the author's machine. | An **absolute path to the author's home directory** installs once and fails everywhere else. Shared skills, hooks, and plugin components reference paths **relative to the project root**; env-var requirements are **documented or validated at install time**. **Test the install from a clean machine.** Corollary: a plugin carries only what it bundles — a deny rule or hook the author relied on locally **doesn't travel unless listed**. | [D3 · Plugins + Cost·Complexity·Risk](domain-3-claude-code/notes.md) |
| 6 | **Transport and scope are independent decisions with dependent consequences.** | Committing `.mcp.json` "shares the server with the team." | **stdio** = runs on your machine. **HTTP** = hosted remotely / multi-developer. **Local scope** keeps it personal; **project scope** ships it via `.mcp.json`. A shared team server needs **HTTP + project (or enterprise) scope**. ⚠️ **A stdio server in `.mcp.json` looks shareable and isn't** — every clone spawns its own subprocess and needs the runtime installed locally. | [D8 · Transports + Configuration scope + the MCP setup reference](domain-8-tools-mcps/notes.md) |
| 7 | **Enterprise integration means identifying security requirements before deployment.** | Auth works, so the integration is done. | A regulated customer asks four things: **identity** (OAuth for user identity, env-var credentials for service identity), **data residency** (regional endpoint + region-pinned deployment), **access logging** (`PostToolUse` hook → audit store, fires deterministically), **configuration control** (enterprise managed settings, non-overridable). None is hard to implement; **all are hard to retrofit after a deployment fails a security review.** | [D8 · Enterprise Integration](domain-8-tools-mcps/notes.md); [D7 · Identity, Secrets, Key Management + `PostToolUse`](domain-7-security/notes.md) |

---

## Unified decision table — "which mechanism answers this?"

The module's core skill is mapping a stated requirement to the one mechanism that satisfies it. Scattered by topic across the domain notes; consolidated here, which is how a scenario question actually reaches you.

| The requirement in the stem | The mechanism | Domain |
|-----------------------------|---------------|--------|
| "This path must never be edited, no matter what a developer configures locally" | **Enterprise-level deny rule** — survives every mode including bypass | D3 |
| "We need to review the intended changes before any file is written" | **Plan mode** — holds the agent in read-only explore | D3 |
| "The agent keeps writing in the legacy style we're migrating off" | **CLAUDE.md** carrying target conventions — it infers style from surrounding code otherwise | D3 |
| "This guidance only applies inside `/services/payments`" | **Rules instruction file**, not CLAUDE.md | D3 |
| "This check must run every time, regardless of what the model decides" | **Hook** — deterministic at a lifecycle event | D3 |
| "Exploration is filling the main session with content we won't reuse" | **Subagent** — isolated context, returns a summary | D3 |
| "This procedure should stay out of context until the work calls for it" | **Skill** — loads on description match | D3 |
| "This should run *only* when I explicitly call it" | Skill with **`disable-model-invocation: true`** | D3 |
| "The whole team needs my setup in one install" | **Plugin** via marketplace; managed settings for org-wide push | D3 |
| "It works for me and breaks for everyone else" | **Absolute path / undocumented env var** in a shared component | D3 |
| "Server runs as a subprocess on my machine" | **stdio** transport | D8 |
| "Hosted remotely, multiple developers connect" | **HTTP** transport | D8 |
| "Config should travel with the repo to everyone who clones" | **Project scope** — `.mcp.json` at repo root | D8 |
| "Let one MCP tool run unprompted but keep the rest gated" | Permission rule on **`mcp__server__tool`** | D8 |
| "Stop the model from even *seeing* this tool" (context cost) | **`enabled` flag** — not a permission rule | D8 |
| "401 → browser sign-in → token stored automatically" | **OAuth** — remote service, user identity | D8/D7 |
| "Credential belongs to the service, not a person" | **API key/PAT in an environment variable**, referenced by config | D8/D7 |
| "Local file-system server — what's the credential?" | **None.** File-system permissions + **deny rules** on paths | D8/D7 |
| "Compliance needs a record of every tool call and its parameters" | **`PostToolUse` hook** → audit store | D7 |
| "A developer must not be able to change auth config mid-audit" | **Enterprise managed settings** | D8/D7 |
| "Where is the data processed?" | **Data residency** — regional endpoint + region-pinned deployment | D8/D1 |

---

## What's genuinely new here vs. the domain notes

Most of this is review. Five framings are the value-add worth carrying into the exam:

1. **Convenience setting vs. governance boundary.** The recurring recognition task. If a stem describes someone choosing a setting *for speed or ease*, ask what checkpoint that removes — the correct answer usually restores it at a level the individual can't undo.
2. **Prove-from-the-diff vs. hypothesis.** The triage rule for AI review output is a genuinely portable heuristic: **does the evidence for this claim exist in the artifact the reviewer was given?** A missing null check is in the diff. "This will deadlock under load" is not. Same test applies to any AI-generated finding, which is why it's worth more than its 7.4%-skill footprint suggests.
3. **"Portable format" ≠ "portable artifact."** `SKILL.md` is a portable *format*; a specific skill is portable only if you wrote it that way. The same distinction covers plugins (a bundle isn't self-sufficient — it carries only what it lists) and MCP config (a committed `.mcp.json` isn't a shared server if the transport is stdio).
4. **Deterministic vs. probabilistic enforcement.** CLAUDE.md *asks* the model; a hook *runs* regardless. When a stem says "must," "every time," "regardless," or "for audit" — that's hook language, not instruction-file language. This is the single most reliable D3 tell.
5. **Retrofit asymmetry.** The four enterprise requirements (identity, residency, logging, config lock) are each cheap pre-deployment and expensive post-. That asymmetry — not the mechanisms themselves — is what the scenario questions are built on.

---

## Cross-domain practice questions

Blueprint-style, scenario-based, **original** (never real exam items). Answer key + per-option rationale follow the set. Tagged by domain · skill.

**Q1 · D3 · Claude Code Operation — select 1.**
A developer is running a large refactor against a live production repo on their workstation and switches to `bypassPermissions` because the confirmation prompts are slowing them down. Their team lead wants a guarantee that `/infra/secrets/` is never modified, regardless of what any individual developer configures. What provides that guarantee?

- A. Set `plan` mode as the user-level default in `~/.claude/settings.json`.
- B. A **deny** rule on that path in enterprise **managed settings**.
- C. An allow rule listing only the directories that may be edited, in `.claude/settings.json`.
- D. A `CLAUDE.md` instruction stating that `/infra/secrets/` must never be touched.

**Q2 · D3 · Claude Code Operation — select 1.**
Every session in a repo must run a lint-and-secret-scan step after any file write, and the security team requires that it happen on **every** write with no exceptions. Where does this belong?

- A. A line in `CLAUDE.md` instructing Claude to run the scan after each write.
- B. A `PostToolUse` **hook** bound to the write tools.
- C. A skill named `post-write-scan` with a clear description.
- D. A custom command the developer runs at the end of the session.

**Q3 · D3 · Claude Code Operation / Packaging — select 2.**
A team packages its Claude Code setup as a plugin. It installs and works perfectly for the author and fails for three teammates. Which are likely causes? (Select 2.)

- A. A skill body references `/Users/dana/projects/api/scripts/check.sh`.
- B. A hook command depends on `$INTERNAL_REGISTRY_URL`, which is set only in the author's shell profile.
- C. The plugin bundles more than one skill.
- D. The plugin's commands are namespaced under the plugin name.

**Q4 · D8 · MCP Server Development — select 1.**
A team wants every developer who clones the repo to reach the same internal analytics service through MCP. The lead adds a stdio server entry to `.mcp.json` and commits it. What's wrong with this configuration?

- A. Nothing — `.mcp.json` at the repo root is the correct project scope for team sharing.
- B. stdio runs the server as a **local subprocess on each machine**, so this isn't a shared hosted service; a shared internal service needs **HTTP transport** with project or enterprise scope.
- C. `.mcp.json` cannot hold stdio entries; it accepts HTTP servers only.
- D. Project scope is wrong — this should be user scope so it follows each developer everywhere.

**Q5 · D8 · Enterprise Integration / D7 · Identity and Secrets — select 1.**
An MCP integration with an internal API is being prepared for a regulated customer's security review. The current prototype passes an API key inline in the committed config, has no logging of tool calls, and lets each developer edit the server config locally. Which set of changes addresses all three gaps?

- A. Move the key to an environment variable; add a `PostToolUse` hook writing every tool call and its parameters to an audit store; deploy the server config via **enterprise managed settings**.
- B. Switch to OAuth; enable streaming; set `plan` mode as the default.
- C. Rotate the API key more frequently; log HTTP status codes and latencies; document the config in the README.
- D. Move the key to `.mcp.json` under a comment marking it secret; add a `PreToolUse` hook; use project scope.

**Q6 · D3 · Packaging / Skills portability — select 1.**
A `SKILL.md` works reliably in Claude Code. When the same file is invoked through the Messages API, it fails partway through. The most likely cause?

- A. The skill's description is too specific, so it doesn't match on the API.
- B. The skill body **shells out to a local command**; on the Messages API it runs in a container without that command or the local filesystem.
- C. Skills are not supported on the Messages API at all.
- D. The skill needs `disable-model-invocation: true` to run outside Claude Code.

**Q7 · D2 · Software Engineering Foundations — select 1.**
An AI reviewer returns two findings on a pull request, both stated with equal confidence: (1) a file handle opened at line 44 is never closed on the error path, and (2) "this change will cause a deadlock in the payments service under concurrent load." How should you treat them?

- A. Apply both — the reviewer read the full diff.
- B. Confirm (1) on the cited lines and act on it; treat (2) as a **hypothesis to test**, since the reviewer had no runtime or cross-service evidence for it.
- C. Reject both until a human reviewer independently re-derives them.
- D. Apply (2) first — a deadlock is higher severity than a leaked handle.

**Q8 · D3 · Durable Project Context — select 1.**
A project's `CLAUDE.md` has grown past 400 lines. Half of it is guidance that only applies inside `services/billing/`, and the team reports Claude increasingly ignores the critical rules at the top. Best correction?

- A. Move the billing-specific guidance into a **rules instruction file** scoped to that directory, leaving CLAUDE.md for universal project constraints.
- B. Add "IMPORTANT" to the rules being ignored.
- C. Convert the whole file into a skill.
- D. Split CLAUDE.md into two files at the project root and reference one from the other.

### Answer key & rationale

**Q1 — B.** An **enterprise-level deny rule** is the only control that (a) can't be removed by an individual developer and (b) **still applies under `bypassPermissions`**. That combination is exactly what "guarantee, regardless of local config" asks for.
- A wrong: a *user-level* default is a preference the developer can change, and modes don't bind other developers.
- C wrong: right idea, wrong level — `.claude/settings.json` is project scope, overridable locally, and an allow rule isn't what blocks; the deny is.
- D wrong: CLAUDE.md is an instruction to the model — **probabilistic**, not enforcement. Classic distractor.

**Q2 — B.** "Every time, no exceptions" is **hook** language. A hook fires **deterministically at the lifecycle event regardless of what the model decides**; nothing else in the D3 toolkit gives that.
- A wrong: same probabilistic-instruction trap as Q1-D.
- C wrong: skills load on **description match** — the model still decides.
- D wrong: manual invocation is the opposite of a guarantee.

**Q3 — A and B.** Both are the portability failure named in takeaway 5: an **absolute path into the author's home directory**, and an **undocumented environment-variable dependency**. Either installs fine for the author and breaks elsewhere; both are caught by testing the install from a clean machine.
- C wrong: bundling multiple skills is the normal purpose of a plugin.
- D wrong: automatic namespacing under the plugin name **prevents** collisions — it's a feature, not a fault.

**Q4 — B.** Transport and scope are **independent decisions with dependent consequences**. Project scope distributes the *config*; it doesn't make a stdio server shared. Each clone spawns its **own subprocess** and needs the runtime installed locally. A shared internal service = **HTTP**.
- A wrong: names the right scope but misses that the transport contradicts the intent — the trap the takeaway is built around.
- C wrong: `.mcp.json` does accept stdio entries; that's precisely why the mistake is easy to make.
- D wrong: user scope shares it across *your* projects, not across the team.

**Q5 — A.** The three gaps map one-to-one: credential → **environment variable**; no logging → **`PostToolUse` hook** to an audit store; local editability → **enterprise managed settings** (admin-deployed, non-overridable).
- B wrong: OAuth is the pattern for **user-identity** services; this credential belongs to a *service*. Streaming and plan mode are unrelated.
- C wrong: rotation is good hygiene but the key is still committed; **status codes and latencies are operational logs, not an access audit trail**.
- D wrong: a comment doesn't stop a secret entering **repository history** — the harm is permanent once committed.

**Q6 — B.** The portability rule: **don't assume a local filesystem or local tools exist inside the skill body.** On the Messages API the skill runs in a **code execution container** — no local files, no local shell commands.
- A wrong: a *specific* description is what makes a skill load correctly; vague descriptions fail everywhere.
- C wrong: skills do run on the Messages API — via a **beta header**, not filesystem discovery.
- D wrong: that flag suppresses automatic invocation; it has nothing to do with runtime sandboxing.

**Q7 — B.** The triage rule: **trust what the reviewer can prove from the diff in front of it**, and confirm it on the cited lines; **treat runtime or cross-system claims as hypotheses**, because the reviewer made them without access to the evidence that would prove them.
- A wrong: applying both treats a hypothesis as a verdict — the failure mode the takeaway names.
- C wrong: over-correction; the provable finding is checkable in seconds on the cited lines.
- D wrong: **stated severity is not evidence.** The deadlock claim is exactly the one with no supporting evidence in the artifact reviewed.

**Q8 — A.** Two problems, one fix: CLAUDE.md **dilutes with size** (which is why the top rules are being ignored), and **path-specific guidance belongs in a rules file** that activates only where it applies.
- B wrong: emphasis doesn't fix dilution — content weight is the cause.
- C wrong: skills are for **on-demand procedures**; universal project constraints must load every session.
- D wrong: splitting at the root doesn't scope anything to a path, and both files still load unconditionally.

---

## Capstone flashcards (meta-lessons)

Synthesis one-liners unique to this module. _These live here for self-test; per-domain mechanics cards sit in the domain `flashcards.md` decks and flow into `study-hub.html`._

**Q:** What single recognition task do all seven takeaways share?
**A:** Spotting a **governance boundary disguised as a convenience setting** — permission mode, transport, a hard-coded path, a config file's scope.

**Q:** Which control survives every permission mode, including `bypassPermissions`?
**A:** A **deny rule** — and at **enterprise** level, no individual developer can remove it.

**Q:** CLAUDE.md vs. a hook — what's the distinguishing word in the stem?
**A:** "Must / every time / regardless / for audit." CLAUDE.md **asks** the model (probabilistic); a hook **runs** at the lifecycle event (deterministic).

**Q:** Name the four durable-context mechanisms and the one problem each solves.
**A:** **CLAUDE.md** = universal project memory (dilutes with size); **rules file** = guidance scoped to a path; **hook** = deterministic enforcement; **subagent** = keeps exploration out of the main context.

**Q:** Why doesn't a portable skill format guarantee a portable skill?
**A:** Each runtime loads and sandboxes differently (filesystem / beta header + container / `settingSources`). A skill assuming local files or local commands breaks outside Claude Code.

**Q:** Do subagents inherit skills?
**A:** **No** — in any runtime. Subagents start clean and must be given what they need explicitly.

**Q:** Why is a stdio server committed to `.mcp.json` a trap?
**A:** It **looks shareable and isn't** — every clone spawns its own local subprocess and needs the runtime installed. A shared team server needs **HTTP + project/enterprise scope**.

**Q:** The two failure modes that break a shared plugin on someone else's machine?
**A:** **Absolute paths** into the author's home directory, and **undocumented environment-variable requirements**. Test the install from a clean machine.

**Q:** The four questions a regulated customer adds beyond "does it work?"
**A:** **Identity** (OAuth vs. service credential), **data residency**, **access logging** (`PostToolUse` → audit store), **configuration control** (enterprise managed settings).

**Q:** Which AI-review findings do you act on directly?
**A:** The ones **provable from the diff** — confirmed on the cited lines. Runtime and cross-system claims are **hypotheses to test**.

---

## What comes next

Per the class, **Module 4** covers **production engineering, evaluations, and security** — measuring whether integrations work correctly at scale, building eval harnesses, and designing production safety guardrails. ✅ **Done and filed** (2026-07-19): it landed in **[D4 · Eval, Testing, and Debugging](domain-4-eval-testing/notes.md)** (evals, test levels, tracing, failure handling), **[D5](domain-5-model-selection/notes.md)** + **[D1](domain-1-agents/notes.md)** (observability, cost levers, orchestrator-worker), and the now-complete **[D7](domain-7-security/notes.md)** sections *AI Application Security* (3.2%) and *Guardrails and Safe Deployment* (2.3%). Its recap sheet is **[`capstone-production-engineering-evals-security.md`](capstone-production-engineering-evals-security.md)** — read this one first, since the permission modes, hooks, and auth patterns above are the foundation those evaluations test against.

---

## Sources

- Class module: **"Claude Code, MCP & Integration"** — Key Takeaways (7) and Glossary (Key Terms) screens.
- Anthropic Academy modules cited by the class: **Claude 101**, **Claude Code 101 In Action**, **Building with the Claude API**.
- **code.claude.com**, **platform.claude.com**, **docs.claude.com** — canonical references for permission modes, settings hierarchy, hooks, skills, plugins, and MCP (re-verify at build time; this material is version-sensitive).
- Repo domain notes where each takeaway's mechanics are verified: `domain-3-claude-code/notes.md`, `domain-8-tools-mcps/notes.md`, `domain-7-security/notes.md`, `domain-2-applications/notes.md`, `domain-1-agents/notes.md`.
- Term definitions from this module's Glossary screen are merged into the repo-wide [`glossary.md`](glossary.md).

_Version-sensitive: permission mode names, settings file locations, skill loading mechanics (beta header / `settingSources`), and MCP rule syntax were current per the class recorded **2026-07-19**. Confirm against docs before relying on exact strings._
