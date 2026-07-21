# Domain 3: Claude Code — Notes

**Exam weight: 3.1%**

## Skills in this domain

| Skill | Weight | Focus |
|-------|--------|-------|
| Claude Code Operation | 3.1% | Rules, Skills, Commands, Agents, Agent Memory; session management; slash commands; headless/streaming/auto mode; CLAUDE.md hierarchy; settings.json; permission modes and human gates |

---

## Claude Code Operation (3.1%)

> **Central idea:** Claude Code runs the **same agent loop** described in Domain 1 — model calls tools, gets results, continues until done — but wraps it in a **permission system that gates every action**. The exam-relevant judgment is not "what does each mode do" as trivia; it's **which mode fits this context, and where does a human still have to look.** Both answer the same question: *what breaks if this runs unchecked?*

_Source: class module "Permission Modes & Human Gates" (recorded 2026-07-19). Mode behaviors cross-checked against docs.claude.com the same day._

---

### The three phases: explore → plan → code

Claude Code doesn't start writing on receipt of a task. It moves through three phases:

| Phase | What happens | Why it matters |
|-------|--------------|----------------|
| **Explore** | Reads files, traces relevant logic, builds a picture of the codebase. | Fewer assumptions, catches more downstream effects — it understands before it touches anything. |
| **Plan** | Produces a structured description of the edits it intends to make, for your review. | This is the review point. Nothing is written yet. |
| **Code** | Writes and executes the changes — **only after you approve the plan.** | The gate is the approval, not the code phase itself. |

🔑 **This is where permission modes plug in.** `plan` mode **holds Claude Code in the explore phase**, blocking all file edits and shell commands until you release it. That makes it the sensible default for an unfamiliar codebase or high-stakes work.

---

### Permission modes — the speed vs. oversight tradeoff

Each mode is a different point on the same tradeoff. **Pick by two variables: how well you know the codebase, and how reversible the changes are.**

| Mode | Auto-approves | Still gates | Limitation / when it fits |
|------|---------------|-------------|---------------------------|
| **`default`** | Reads only. | All file edits and shell commands require confirmation. | Safe but slow on trusted work. **The baseline for any new project or unfamiliar codebase.** |
| **`acceptEdits`** | File edits/operations — Claude edits code without prompting. | Non-filesystem tools (e.g. Bash commands) still go through normal permission checks. | The mode built for **low-stakes, reversible work** — formatting fixes, edits confined to the working directory. |
| **`plan`** | Read-only tools. | **All** file-edit and shell-write tools — write operations cannot be auto-approved while planning, **even when an allow rule matches.** | Deliberately can't ship anything. For exploration, unfamiliar codebases, high-stakes work where you want the plan before the diff. |
| **`auto`** | Decided per tool call by a **model classifier** that approves or denies. | Whatever the classifier denies. | Judgment is delegated to a model, so it is **not deterministic** the way an allow/deny rule is. Don't rely on it as a governance control. |
| **`dontAsk`** | Only what's **pre-approved** by allow rules / `allowed_tools`. | Everything else — any prompt becomes a **hard denial**, without prompting. | For **headless agents** where you want a fixed, explicit tool surface and prefer a hard deny over an unattended prompt hanging. |
| **`bypassPermissions`** | Everything that reaches the permission step. | **Deny rules still block** — a deny rule wins even here. | ⚠️ Removes every safety prompt between the agent and your live files, **and removes the protected-path guard** (unlike every other mode). Only defensible on an isolated machine. Reaching for it out of impatience is the classic risk. |

**Two rules that hold across all six modes:**

1. **A deny rule always beats an allow rule** — regardless of the mode in effect.
2. **A deny rule still applies under `bypassPermissions`.** It is the one control that survives every mode.

---

### Where the configuration lives — the four settings levels

Allow/deny rules and a default mode can be set at four levels. **The level determines scope and who can override it.**

| Level | File | Applies to | Put here |
|-------|------|------------|----------|
| **User** | `~/.claude/settings.json` | Every project on the machine. | Preferences that should follow you everywhere — e.g. a preferred default mode for exploration work. |
| **Project** | `.claude/settings.json` (committed) | Everyone who clones the repo. | Team-wide conventions: allow rules for the tools the project uses, deny rules for paths nobody should touch. |
| **Local project** | `.claude/settings.local.json` (auto git-ignored) | Just you, on this project. | Personal overrides you don't want committed to the team. |
| **Enterprise** | `managed-settings.json` (set by admins) | Organization-wide. **Cannot be overridden** by user or project files. | Security controls: denying edits to env files, blocking specific shell commands across all projects. |

🔑 **The most durable governance control is an enterprise-level deny rule.** No individual developer can remove it, and it applies **even when a bypass mode is set.** If an exam item asks how to guarantee a path is never touched regardless of what a developer configures locally — that's the answer.

---

### Placing the human gate — decide by worst-case cost

Permission modes and deny rules decide what the **agent** can do without asking. They do **not** decide where **you** still need to look. That's a separate placement decision, and it rests on one question:

> **What is the worst outcome if this action runs without a person checking it?**

Lower cost of being wrong → more you can let through. Higher cost, and harder to undo → the more a step needs a human gate before it executes. **The same question applies whether the agent is writing code interactively or running unattended** in an automated step (e.g. a bot that comments on or blocks a PR).

Three placements follow:

| Action profile | Gate? | Mechanism |
|---|---|---|
| **Low-stakes, reversible** — formatting fix, edit confined to the working directory. | **No gate.** Approving each one buys oversight you don't need and slows the work. | `acceptEdits` — this is the case it's built for. |
| **Hard to undo, or reaches a sensitive path** — write outside the working directory, destructive shell command, edit to a security-relevant or protected file. | **Gate it.** The agent should pause and surface the action to a person before it runs. | A **deny rule** enforces it deterministically; `default` or `plan` mode keeps the prompt in place while you decide. |
| **Code the team has marked sensitive.** | **Never let the agent be the only gate.** A person must review before it merges — no matter how confident the agent or its own review sounds. | The agent's work is an **input to a human decision, not a replacement for one.** |

🔑 **The mode and the gate are the same decision from two sides.** The **mode** sets the default for a whole session; the **gate** is where you override that default for the one action whose cost is too high to leave to the default. Both come from asking what breaks if this runs unchecked.

---

### Cost · Complexity · Risk

| Axis | The concrete failure |
|------|----------------------|
| **Cost** | Running `default` on trusted work adds prompt latency to **every** tool call — this accumulates painfully on a long refactor. |
| **Complexity** | Four settings levels with an override hierarchy require consistent care. An enterprise deny rule contradicting a project allow rule has to be understood by everyone maintaining the config. |
| **Risk** | **Using the wrong mode for the context.** A bypass mode set out of impatience on a non-isolated machine removes every safety prompt between the agent and your live files — and uniquely also removes the protected-path guard. |

---

### Exam-style decision cues

| If the stem says… | The answer is likely… |
|---|---|
| "unfamiliar codebase," "high-stakes," "want to see the approach first" | `plan` mode |
| "trusted repo," "long refactor," "prompts are slowing us down," edits are reversible/in-working-directory | `acceptEdits` |
| "headless," "unattended," "CI," "no one is there to answer a prompt" | `dontAsk` with explicit allow rules |
| "must be true for every developer regardless of local config" | **Enterprise-level deny rule** (`managed-settings.json`) |
| "guarantee this path is never edited even if someone bypasses permissions" | **Deny rule** — it wins over allow rules and survives `bypassPermissions` |
| "the agent reviewed it and says it's fine — can it merge?" | **No** — sensitive code requires a human reviewer; the agent is an input, not the gate |
| "how do we decide where to put the checkpoint?" | **Worst-case cost of the action running unchecked** (+ how reversible it is) |

> ⚠️ **Version-sensitive (verified 2026-07-19):** permission mode names (`default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`) and settings-file paths are platform surfaces that can change. Re-verify against docs.claude.com before the exam.

**Related:** human-in-the-loop checkpoint placement is the same reasoning applied to agent tool calls — see [Domain 1 · Agent Patterns](../domain-1-agents/notes.md) and [Domain 7 · Security](../domain-7-security/notes.md).

---

## Durable Project Context — CLAUDE.md, rules files, hooks, subagents

> **Central idea:** Permission modes and settings control **what the agent is allowed to do.** This cluster controls **what the agent knows and how it behaves** — and specifically, how to make that knowledge survive the end of a session. The exam judgment is *which mechanism should carry this particular piece of project knowledge*, because each one trades **context cost** against **reliability of application**.

_Source: class module "Durable Project Context" (recorded 2026-07-19). Builds directly on the permission modes / settings cluster above._

---

### CLAUDE.md — the always-on project file

When Claude Code starts in a project directory, it looks for `CLAUDE.md` at the root and reads it. The contents are **appended to your prompt before any message from you arrives**, so every convention and constraint in it is present from the first prompt of every session without you re-stating it.

- **`/init`** scans the codebase and generates a starter CLAUDE.md. Good baseline — **validate and refine it before relying on it.**
- What belongs in it: testing commands, framework conventions, paths the agent must not touch, style decisions that differ from defaults — i.e. **rules that change the outcome of your prompts.**

🔑 **Size is the main failure mode.** A CLAUDE.md that grows with every new instruction dilutes the rules that matter. A larger file consumes more context window, which makes any single instruction a **smaller fraction of what loads** — and lowers the chance the agent follows the one rule that catches a real mistake. Keep it to behavior-changing constraints; move the rest into **Skills that load on demand.**

---

### Rules instruction files — scoping guidance to where it applies

Rules files live in `.claude/rules/` and add a **narrower layer on top of** the CLAUDE.md baseline. They can be scoped to specific paths with a `paths` glob in YAML frontmatter, so a rule loads into context **only when Claude Code works with matching files**.

```yaml
---
paths:
  - "src/db/**/*.sql"
---
```

⚠️ **Scoping comes from the frontmatter, not from file placement.** You may organize rules into subdirectories (`.claude/rules/database/`), but that structure is **organizational only**. A rules file **without** a `paths` field loads **unconditionally at launch, with the same priority as CLAUDE.md**, no matter where it sits inside `.claude/rules/`.

**The split in practice:**

| Constraint | Where it lives | Why |
|---|---|---|
| "Never modify the database schema" | **CLAUDE.md** | Applies everywhere. |
| "All SQL in the database module must include an explicit transaction boundary" | **`.claude/rules/database.md`** with a `paths` glob | Noise in every other part of the codebase. |

---

### Hooks — your scripts at fixed lifecycle points

A hook intercepts and controls tool calls before or after they execute. **The difference from an instruction:** a CLAUDE.md rule saying "run Prettier after every edit" is followed *most of the time*; a hook fires **every single time, independently of what the model decides to do.**

Hooks are defined in settings files and configured with the **`/hooks`** command. Each binds an **event** + an optional **matcher** (scopes it to tool types) + a **command**.

| Event | Fires | Can it block? | Use it for |
|---|---|---|---|
| **PreToolUse** | Before a tool call executes | **Yes** — exit code **2** blocks the call; stderr becomes feedback the agent sees | Enforcing access controls at the config layer instead of hoping the agent respects a CLAUDE.md instruction |
| **PostToolUse** | After a tool call completes | No — it already happened | Automated side effects: formatter after an edit, tests after a file change, audit logging |
| **UserPromptSubmit** | On prompt submit, before the model processes it | — | Injecting context or validating the request before work starts |
| **Stop** | When the model finishes responding | — | End-of-turn follow-ups: notifications, cleanup, committing the audit log |
| **Notification** | When Claude Code notifies — needs tool permission, **or has been idle 60 seconds** | — | Routing those signals to an external channel or logging system |
| **SessionStart** | Session starts or resumes | — | Initialize state, validate env vars, confirm required services are reachable |
| **SessionEnd** | Session ends | — | Teardown, final audit writes, session-closed notifications |

🔑 A PreToolUse hook blocking edits to a production config path enforces that constraint **at every tool call, in every session, regardless of permission mode.** That is the difference between a **guardrail** and a **convention**.

---

### Subagents — delegating to an isolated context

A subagent runs a task in **its own separate context** and returns only its output. It does **not** inherit your main conversation history, accumulated files, or session state — it starts from a clean slate, does the work, hands back the result.

⚠️ **The built-in subagents differ in what they load at startup, and that difference decides whether your project rules apply:**

| Subagent | Loads CLAUDE.md + git status? | Implication |
|---|---|---|
| **Explore** | **No** — skipped to keep research fast and cheap | Project rules and repo state defined in CLAUDE.md are **not in its context** |
| **Plan** | **No** — same optimization | Same |
| **general-purpose** | **Yes** — both | Use it (or a custom subagent that explicitly loads what it needs) when project constraints **must** be respected |

> If you delegate to Explore or Plan and a CLAUDE.md rule doesn't get respected — that's why: the context was never loaded. Always check the current subagent list in the Claude Code docs, since the set has grown over time, but this split holds across versions.

**Skills and subagents:** custom subagents **do not automatically see your skills.** If a custom subagent in `.claude/agents` needs a specific skill, you must **list that skill in the agent's frontmatter.** Built-in agents have **no preloaded skills** — if you need skill-backed behavior, the correct path is a **custom subagent with those skills listed in its configuration.**

---

### The mechanism map — what carries which piece of knowledge

| Mechanism | What it loads | When it runs | Context cost | Belongs here |
|---|---|---|---|---|
| **CLAUDE.md** | Full file contents prepended at session start | Every session, unconditionally | Persistent per session; **dilutes with size** | Universal project constraints, commands, framework decisions |
| **Rules file** | File contents; scoped by a `paths` glob in frontmatter — **without `paths`, loads like CLAUDE.md** | When Claude reads a matching file; unscoped rules load at session start | Path-scoped: only when triggered. Unscoped: same persistent cost as CLAUDE.md | Path-specific guidance that would be noise everywhere else |
| **Hook** | Runs your script at the event — **no content added to context** | At the configured lifecycle event | Minimal — only script output, if routed back to Claude | Enforced guardrails, automated side effects, audit logging |
| **Subagent** | Task context only, isolated from the main session | When dispatched for a delegated task | Returns a **summary**, not the full task history | Exploration, investigation, work whose output would bloat the main context; parallelizable tasks |

---

### When this cluster is worth the setup

| Handles well | Use a different approach |
|---|---|
| Projects you return to across many sessions, where a stable rule set, per-directory variation, or unconditional guardrails repay the setup cost. | One-off tasks you won't revisit — e.g. a quick exploration of an unfamiliar codebase. The setup overhead isn't warranted. |

---

### Exam-style decision cues

| If the stem says… | The answer is likely… |
|---|---|
| "must apply in every session across the whole project" | **CLAUDE.md** |
| "only relevant to one module / directory," "don't want it loading everywhere" | **Rules file with a `paths` glob** |
| "the agent follows it *most* of the time — we need it every time" | **Hook** (deterministic; model-independent) |
| "block this tool call before it runs, and tell the agent why" | **PreToolUse hook**, exit code **2**, reason to **stderr** |
| "run the formatter / tests / audit log after the edit" | **PostToolUse hook** |
| "initialize state or verify services before work begins" | **SessionStart hook** |
| "CLAUDE.md keeps growing and rules are being missed" | **Trim it** — move on-demand content into **Skills**; dilution is the failure mode |
| "we put the rule in `.claude/rules/database/` so it only loads for DB work" | **Wrong** — placement doesn't scope; only a `paths` frontmatter field does |
| "the delegated task ignored our CLAUDE.md rule" | It went to **Explore or Plan**, which skip CLAUDE.md — use **general-purpose** or a custom subagent |
| "the custom subagent can't use the skill we built" | The skill must be **listed in the subagent's frontmatter** |
| "the investigation output would blow up the main context" | **Subagent** — isolated context, returns a summary |

> ⚠️ **Version-sensitive (verified 2026-07-19):** the hook event list, the `.claude/rules/` frontmatter schema, the built-in subagent roster, and `/init` / `/hooks` command behavior are all evolving platform surfaces. Re-verify against docs.claude.com before the exam.

**Related:** hooks as a deterministic control mirror deny rules in the permission cluster above — both beat convention. See also [Domain 8 · Tools and MCPs](../domain-8-tools-mcps/notes.md) for Skills vs. tools vs. MCPs, and [Domain 6 · Prompt and Context Engineering](../domain-6-prompt-context/notes.md) for the context-dilution principle behind the CLAUDE.md size rule.

---

## Packaging Workflows — Skills, custom commands, plugins, marketplaces

> **Central idea:** The previous cluster covered mechanisms that live in *your* `.claude` directory. This one answers the next question: **how do you package that setup so a teammate installs it in one step instead of repeating your manual configuration by hand?** The exam judgment is a **layer choice** — skill vs. custom command vs. plugin — decided by *who needs it* and *whether it has to be shared, versioned, and kept consistent.*

_Source: class module "Packaging Workflows" (recorded 2026-07-19). Third module in the Claude Code series; builds on the durable-context cluster above._

---

### Skills — reusable workflows loaded on demand

A skill is a **portable Markdown file (`SKILL.md`) placed in `.claude/skills`**. The **frontmatter** identifies the skill and describes **when it applies**; the **body** holds the steps.

🔑 **The same skill file runs in Claude Code, through the Messages API, or loaded by the Agent SDK.** What changes across runtimes isn't the file — it's **where the skill runs, how it gets loaded, and what it's allowed to touch.** A developer who has only seen skills in Claude Code will assume things that don't hold on the API.

| Runtime | How it loads | Where the steps run | What to know |
|---|---|---|---|
| **Claude Code** | Discovered from `.claude/skills` on the filesystem; loads on a **description match** or when invoked **by name**. | Your terminal session, against your local files, under the active permission mode and deny rules. | Filesystem-based and governed by the settings layer. |
| **Messages API** | Not filesystem-discovered; requires a **beta header**. | In a **code execution container** — no local files, no local shell commands. | Confirmed by the module's Key Takeaways screen (2026-07-19): "beta headers and a code execution container on the API." ⚠️ _Exact header string still unverified — check docs.claude.com._ |
| **Agent SDK** | Requires **`settingSources`** to be configured for the SDK to pick up `.claude` sources. | Headless SDK job. | ⚠️ _Class tab content not captured — verify against docs.claude.com._ |
| **Claude Managed Agents** | Server-hosted. | Anthropic-managed sandbox. | ⚠️ _Class tab content not captured — verify against docs.claude.com._ |

#### Three portability rules

1. **Write the description as the matching criterion.** The model loads a skill by comparing your request to its description. A description that **identifies when the skill applies** works in every runtime; a vague one **fails to load in all of them.**
2. **Don't assume a local filesystem or local tools exist inside the skill body.** A skill that shells out to a local command works in Claude Code but **breaks on the Messages API**, where it runs in a container without that command. Keep steps to what the runtime guarantees — or document the dependency.
3. **Subagents don't inherit skills.** Same rule as the cluster above: a subagent starts clean, so a skill the parent relied on must be **listed for the subagent explicitly**, in every runtime that supports subagents.

> **Takeaway:** you can author a skill once and reuse it, but **portability is a design decision, not a property of the format.** Scoped description + no local-environment assumptions = ports cleanly. Local-environment assumptions = does not.

| Handles well | Adds complexity | Use a different approach |
|---|---|---|
| A task-specific procedure authored once and reused across the interactive terminal, an API integration, and a headless SDK job. | Each runtime loads and sandboxes skills differently — beta headers on the API, `settingSources` on the SDK. | Instructions that must apply to **every session in a project** → **CLAUDE.md**. Skills are for **on-demand, portable procedures.** |

---

### Custom commands — giving a workflow an explicit entry point

A custom command is a shortcut for a defined procedure.

⚠️ **Current guidance:** in current Claude Code, **skills are the recommended format for both explicit and automatic invocation.** You invoke a skill directly with **`/skill-name`**, or Claude loads it automatically when relevant. The older **`.claude/commands/` directory format still works but is legacy.**

🔑 **To make a workflow run *only* when you explicitly call it, use a skill with `disable-model-invocation: true` in the frontmatter.** That's the modern replacement for "this should never auto-trigger."

**Namespacing:** plugin commands are namespaced automatically — **the plugin's name becomes the prefix.** A `run-tests` command in a plugin named `payments` is invoked as **`/payments:run-tests`**. That's why two plugins can both ship `run-tests` without colliding.

> Authors: treat the **plugin name as part of the interface.** It prefixes every command you ship, so **renaming the plugin renames them all.**

---

### Plugins — the packaging layer that makes a setup installable

A plugin **bundles skills, hooks, subagents, and MCP servers into a single installable unit**, distributed through a **marketplace** (a catalog of plugins someone has created and shared).

- The **official Anthropic marketplace** is available automatically when you start Claude Code.
- Third-party marketplaces hosted in a GitHub repo are added with `/plugin marketplace add <owner/repo>`.
- Teammates then run **one install command** to get the same setup.
- **A plugin replaces a page of manual setup steps with a versioned, auditable install.**

**How components land:** skills go in a `skills` directory; hooks, subagents, and settings go in their respective locations; a **plugin manifest** describes the bundle, and the install command wires it into the target installation. Plugins can be installed **by individuals or at enterprise scale.**

#### Enterprise deployment

| Setting | What it does | What it does *not* do |
|---|---|---|
| **Managed marketplace allowlist** | Gates **which marketplace sources users are permitted to add** — the org controls where plugins can come from. | ⚠️ **Does not register marketplaces automatically.** It restricts; it doesn't push. |
| **`extraKnownMarketplaces`** (managed settings) | Pushes a marketplace to all users **without requiring them to run the `add` command.** | — |

🔑 **Pair the allowlist with `extraKnownMarketplaces`** when you want both control over sources *and* automatic availability.

**Precedence comes from deployment scope:** managed settings sit **above user and project settings** in the configuration hierarchy, so **a plugin deployed at managed scope takes priority and cannot be overridden by users or project files** — the same hierarchy logic as the enterprise deny rule in the permissions cluster above.

---

### The packaging decision table

| Layer | What it is | Who it's for | Reach for it when… |
|---|---|---|---|
| **Skill** | A Markdown file in `.claude/skills` that loads when its **description matches** the task, or when invoked **by name**. | An individual developer or team using Claude Code interactively. | A task-specific procedure should **stay out of context until needed** — a PR review, a deployment checklist that only loads when the work calls for it. |
| **Custom command** | A **named shortcut** that runs a defined procedure when you **invoke it explicitly**. | Developers who want a predictable, explicit entry point for high-frequency procedures. | The procedure has a clear name and you want to **trigger it directly** rather than rely on description matching. |
| **Plugin** | A **versioned bundle** of skills, hooks, subagents, and MCP servers, distributed through a marketplace. | A team that wants **one-step installation** of a shared, versioned setup. | A working setup currently **lives on one machine** and needs to be shared, versioned, and kept consistent across a team. |

---

### Cost · Complexity · Risk

| Axis | The concrete failure |
|---|---|
| **Cost** | Skills add context cost **on activation**; a plugin adds **installation and maintenance overhead**. The question: pay the setup cost **once** (plugin install) or **repeatedly** (every developer running the same manual steps by hand)? |
| **Complexity** | **A plugin that hard-codes absolute paths in its skills installs correctly for the author and fails for everyone else.** Any path or environment assumption baked into a skill or hook command is the thing most likely to break across machines. |
| **Risk** | **A plugin only carries the components it bundles.** A deny rule or hook the author relied on locally is **not included unless explicitly listed** in the bundle. If a skill or hook depends on a guardrail that isn't bundled, **the protection doesn't carry to the teammate's machine.** |

---

### Exam-style decision cues

| If the stem says… | The answer is likely… |
|---|---|
| "one procedure, reused in the terminal *and* an API integration *and* a headless job" | **Skill** — author once; design for portability |
| "the skill doesn't load when we ask for it" | **Vague description** — the description is the matching criterion in every runtime |
| "works in Claude Code, breaks on the Messages API" | The skill body **shelled out to a local command**; the API runs it in a container |
| "the subagent didn't use our skill" | Skills **aren't inherited** — list it explicitly in the subagent's config |
| "should run only when I explicitly call it, never auto-trigger" | **Skill with `disable-model-invocation: true`** |
| "we're still using `.claude/commands/`" | Works, but **legacy** — skills are the recommended format now |
| "two plugins both ship `run-tests` — collision?" | **No** — commands are namespaced by plugin name (`/payments:run-tests`) |
| "the setup lives on one machine; the team needs it consistently" | **Plugin**, distributed via a marketplace |
| "restrict which marketplaces developers may add" | **Managed marketplace allowlist** — but it **only restricts** |
| "push a marketplace to all users without them running `add`" | **`extraKnownMarketplaces`** in managed settings (pair with the allowlist) |
| "a user or project file overrode our org plugin" | **Shouldn't happen** — managed scope sits above user and project settings |
| "installs fine for the author, fails for everyone else" | **Hard-coded absolute paths / environment assumptions** in a skill or hook command |
| "the teammate's install lost our protection" | The **deny rule or hook wasn't bundled** — a plugin carries only what it explicitly includes |

> ⚠️ **Version-sensitive (verified 2026-07-19):** `disable-model-invocation`, `extraKnownMarketplaces`, the managed marketplace allowlist setting name, the `/plugin marketplace add` syntax, the plugin manifest schema, and the Messages API beta header / SDK `settingSources` requirements are all evolving platform surfaces. **Re-verify the exact setting names against docs.claude.com before the exam** — the class explicitly deferred to the reference layer for these.
>
> 📌 **Gap in captured notes:** the class module had a tabbed section (Claude Code / Messages API / Agent SDK / Claude Managed Agents) and only the **Claude Code** tab was transcribed. The API, SDK, and Managed Agents loading mechanics need to be filled in from official docs.

**Related:** the managed-scope precedence here is the same hierarchy that makes an enterprise deny rule the most durable control (permissions cluster above). For Skills vs. tools vs. MCPs as a capability choice, see [Domain 8 · Tools and MCPs](../domain-8-tools-mcps/notes.md); for skills in the Agent SDK / Messages API context, see [Domain 2 · Applications and Integration](../domain-2-applications/notes.md).

---

## Applied case — code modernization and scoping high-risk agentic work

_Source: class module "MCP Servers" → Enterprise Integration (recorded 2026-07-19). Placed here because every mechanism it uses — plan mode, hooks, `CLAUDE.md` — is a Domain 3 tool. The **approval-gate** side of it is [D1 · Human-in-the-loop insertion points](../domain-1-agents/notes.md)._

### Why modernization is the stress test for this whole toolset

Large-scale changes to an **unfamiliar legacy codebase** concentrate exactly the risks each Claude Code mechanism was built to manage:

| Risk of the work | Mechanism that addresses it | How |
|------------------|----------------------------|-----|
| **High blast radius** | **Plan mode** | Holds the agent in the **read-only explore phase** while you build confidence. You review proposed edits, spot anything touching **paths you did not expect**, and push back **before a single file is modified**. |
| **Unpredictable dependencies** | **Hooks** | Enforce guardrails that **block edits to specific paths** during the most sensitive phases. |
| **Drift back to legacy patterns** | **`CLAUDE.md`** | Carries the conventions for the **new target patterns**, so the agent applies them consistently across the full scope instead of imitating the legacy code it reads in surrounding files. |
| **Limited reversibility** | The **explore → plan → code** loop itself | The core workflow for this class of work — see the phases section above. |

> ⚠️ The failure mode without `CLAUDE.md`: an agent reading legacy code around the edit site will **infer the legacy convention from context** and reproduce it. Nothing in the codebase tells it the target pattern — you have to.

### Three questions to answer *before* the session starts

A responsible scoping approach for high-risk work settles all three up front:

1. **What is the blast radius if something goes wrong?** Which systems depend on the code being changed, and what breaks downstream if an edit is wrong?
2. **How are changes audited?** Is there a **`PostToolUse` hook logging every tool call**, and does that log satisfy **whoever needs to review** what the agent touched? (See [D7 · `PostToolUse` as the compliance audit trail](../domain-7-security/notes.md).)
3. **Who approves each phase before the next begins?** Plan mode **enforces the boundary** between exploration and execution — but **the approval decision itself is yours to define and document** before work begins. The tool draws the line; it doesn't decide who stands on it.

🔑 **These three questions are not modernization-specific — they apply to any high-risk agentic task.** Modernization just surfaces them clearly: large scope, unfamiliar codebase, high cost of error.

### Exam-style decision cues — high-risk scoping

| Cue in the stem | Answer |
|-----------------|--------|
| "large refactor of a legacy codebase nobody on the team knows" | **Explore → plan → code**, with **plan mode** gating execution |
| "we need to review what the agent intends to change before any file is written" | **Plan mode** — read-only explore phase |
| "the agent keeps writing code in the old style we're migrating away from" | **`CLAUDE.md`** carrying the target conventions — the agent otherwise infers style from surrounding legacy code |
| "certain directories must not be edited during this phase" | **Hooks** blocking edits to those paths |
| "who signs off between phases?" | **Not a tool answer** — plan mode enforces the boundary, but the **approval policy is defined and documented by you** |
