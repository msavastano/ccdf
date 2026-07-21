# Domain 3: Claude Code — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Keep answers short enough to self-test.

## Claude Code Operation — The agent loop and phases

**Q:** How does the Claude Code loop differ from the raw API agent loop?
**A:** Same loop (model calls tools → gets results → continues), plus an added layer: a permission system that gates every action.

**Q:** Name the three phases of how Claude Code works through a task.
**A:** Explore → plan → code.

**Q:** What happens in the explore phase?
**A:** Reads files and traces relevant logic to build a picture of the codebase before proposing anything.

**Q:** What is a "plan" in Claude Code?
**A:** A structured description of the edits it intends to make — reviewed and approved by you before the code phase begins.

**Q:** Why does explore-before-code produce better output?
**A:** Claude understands the codebase before touching it, so it makes fewer assumptions and catches more downstream effects.

**Q:** Which phase does `plan` mode hold Claude Code in?
**A:** Explore — it blocks all file edits and shell commands until you release it.

## Claude Code Operation — Permission modes

**Q:** What do permission modes control?
**A:** How often Claude Code stops to ask for confirmation — the tradeoff between speed and oversight.

**Q:** What two variables should pick your permission mode?
**A:** How well you know the codebase, and how reversible the changes are.

**Q:** Name the six permission modes.
**A:** `default`, `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions`.

**Q:** `default` mode — what does it auto-approve?
**A:** Reads only. Every file edit and shell command requires confirmation.

**Q:** When is `default` mode the right call?
**A:** The baseline for any new project or unfamiliar codebase. Safe but slow on trusted work.

**Q:** `acceptEdits` — what's auto-approved and what still gates?
**A:** Auto-approves file edits/operations; non-filesystem tools (e.g. Bash commands) still go through normal permission checks.

**Q:** Which mode is built for low-stakes, reversible actions?
**A:** `acceptEdits` — formatting fixes, edits confined to the working directory.

**Q:** In `plan` mode, can an allow rule auto-approve a file edit?
**A:** No. Write operations are never auto-approved in plan mode, even when an allow rule matches.

**Q:** `auto` mode — how are decisions made?
**A:** A model classifier approves or denies each tool call. Not deterministic — don't use it as a governance control.

**Q:** `dontAsk` — what happens to an action that isn't pre-approved?
**A:** It's denied without prompting. Only tools pre-approved by allow rules run.

**Q:** Which mode fits a headless/unattended agent that needs a fixed, explicit tool surface?
**A:** `dontAsk` — a hard deny beats an unattended prompt hanging.

**Q:** What does `bypassPermissions` uniquely remove that other modes keep?
**A:** The protected-path guard — in addition to every safety prompt between the agent and your live files.

**Q:** Does a deny rule still apply under `bypassPermissions`?
**A:** Yes. A deny rule wins even there — it's the one control that survives every mode.

**Q:** Allow rule vs. deny rule — which wins?
**A:** Deny always wins, regardless of the mode in effect.

## Claude Code Operation — Settings levels

**Q:** Name the four settings levels and their files.
**A:** User (`~/.claude/settings.json`), project (`.claude/settings.json`, committed), local project (`.claude/settings.local.json`, git-ignored), enterprise (`managed-settings.json`).

**Q:** Which settings file is automatically git-ignored, and what belongs in it?
**A:** `.claude/settings.local.json` — personal per-project overrides you don't want committed to the team.

**Q:** Where do team-wide allow rules and protected-path deny rules belong?
**A:** Project level — `.claude/settings.json`, committed to the repo.

**Q:** Which settings level cannot be overridden by users or project files?
**A:** Enterprise — `managed-settings.json`, set by administrators.

**Q:** What is the most durable governance control, and why?
**A:** An enterprise-level deny rule — no individual developer can remove it, and it applies even when a bypass mode is set.

## Claude Code Operation — Human gates

**Q:** What single question places a human review gate?
**A:** What is the worst outcome if this action runs without a person checking it?

**Q:** Does the gate question change for an unattended automated step (e.g. a PR bot)?
**A:** No — the same worst-case question places the gate whether the agent is writing code interactively or running unattended.

**Q:** Which actions should pass without a gate?
**A:** Low-stakes, reversible ones — a formatting fix, an edit confined to the working directory. Gating them buys oversight you don't need.

**Q:** Give three action types that must be gated.
**A:** A write outside the working directory; a destructive shell command; an edit to a security-relevant or protected file.

**Q:** How do you enforce a gate deterministically vs. keep the prompt in place?
**A:** Deny rule = deterministic enforcement. `default` or `plan` mode = keeps the prompt while you decide.

**Q:** Can the agent be the only gate on a change to code the team marked sensitive?
**A:** Never. A person must review before it merges, no matter how confident the agent or its own review sounds — the agent's work is an input to a human decision, not a replacement for one.

**Q:** How do permission mode and human gate relate?
**A:** Same decision from two sides — the mode sets the session default; the gate overrides that default for the one action whose cost is too high.

## Claude Code Operation — Cost · Complexity · Risk

**Q:** What's the cost problem with running `default` on trusted work?
**A:** Prompt latency on every tool call, which accumulates on a long refactor.

**Q:** What's the complexity problem with the settings hierarchy?
**A:** Four levels with an override order — e.g. an enterprise deny rule contradicting a project allow rule must be understood by everyone maintaining the config.

**Q:** What's the core risk in this topic?
**A:** Using the wrong mode for the context — classically, `bypassPermissions` set out of impatience on a non-isolated machine.

## Claude Code Operation — CLAUDE.md

**Q:** What does permission/settings config control vs. what does this cluster control?
**A:** Permissions control what the agent is *allowed to do*; CLAUDE.md, rules files, hooks, and subagents control what it *knows and how it behaves* — and make that persist across sessions.

**Q:** Where does Claude Code look for CLAUDE.md, and when?
**A:** At the project root, every time it starts in that directory.

**Q:** How does CLAUDE.md reach the model?
**A:** Its contents are appended to your prompt *before any message from you arrives* — so it's present from the first prompt of every session.

**Q:** What does `/init` do, and what's the caveat?
**A:** Scans the codebase and generates a starter CLAUDE.md. It's a good baseline but should be validated and refined before you rely on it.

**Q:** What belongs in CLAUDE.md?
**A:** The rules that control the outcome of your prompts — testing commands, framework conventions, paths not to touch, style decisions that differ from defaults.

**Q:** What is the main failure mode of CLAUDE.md?
**A:** Size. It grows with every new instruction and dilutes the rules that matter most.

**Q:** Mechanically, why does a bloated CLAUDE.md reduce rule-following?
**A:** A larger file consumes more context window, so any single instruction is a smaller fraction of what loads — lowering the chance the agent follows the one rule that catches a real mistake.

**Q:** Where should content go that doesn't belong in CLAUDE.md?
**A:** Into Skills that load on demand.

## Claude Code Operation — Rules instruction files

**Q:** Where do rules instruction files live?
**A:** The project's `.claude/rules/` directory.

**Q:** How is a rules file scoped to part of the codebase?
**A:** A `paths` glob in its YAML frontmatter — it loads only when Claude Code works with matching files.

**Q:** Does putting a rules file in `.claude/rules/database/` scope it to database work?
**A:** No. Subdirectories are organizational only — scoping comes from frontmatter, not placement.

**Q:** What happens to a rules file with no `paths` field?
**A:** It loads unconditionally at launch with the same priority as CLAUDE.md, wherever it sits in `.claude/rules/`.

**Q:** CLAUDE.md vs. rules file — how do you split a constraint?
**A:** Universal constraints ("never modify the database schema") → CLAUDE.md. Narrow, path-specific guidance ("all SQL here needs an explicit transaction boundary") → a `paths`-scoped rules file.

## Claude Code Operation — Hooks

**Q:** What is a hook?
**A:** A mechanism to intercept and control tool calls before or after they execute, by running your own script at a lifecycle event.

**Q:** Why is a hook stronger than the same instruction in CLAUDE.md?
**A:** The instruction is followed most of the time; the hook fires every single time, independently of what the model decides to do.

**Q:** Where are hooks defined and configured?
**A:** Defined in settings files; configured with the `/hooks` command.

**Q:** What three parts make up a hook?
**A:** A lifecycle event, an optional matcher scoping it to tool types, and a command that runs when the event fires.

**Q:** Which hook event can block a tool call, and how?
**A:** PreToolUse — exit with code 2 to block, writing the reason to stderr as feedback the agent sees.

**Q:** Why can't PostToolUse block a call, and what is it for instead?
**A:** The call already happened. It's for automated side effects: formatting after an edit, tests after a file change, audit logging.

**Q:** What is UserPromptSubmit for?
**A:** Injecting context or validating the request after you submit a prompt but before the model processes it.

**Q:** What is the Stop event for?
**A:** End-of-turn follow-ups when the model finishes responding — notifications, cleanup, committing the audit log.

**Q:** When does the Notification event fire?
**A:** When Claude Code sends a notification — i.e. when it needs permission to use a tool, or after 60 seconds of idle.

**Q:** SessionStart vs. SessionEnd — what belongs in each?
**A:** SessionStart (start or resume): initialize state, validate env vars, confirm services are reachable. SessionEnd: teardown, final audit writes, session-closed notifications.

**Q:** What's the guardrail-vs-convention distinction?
**A:** A PreToolUse hook enforces a constraint at every tool call in every session regardless of permission mode (guardrail); a CLAUDE.md instruction only asks the model to comply (convention).

## Claude Code Operation — Subagents

**Q:** What is a subagent?
**A:** A specialized assistant Claude Code delegates a task to; it runs in its own separate context and returns only its output.

**Q:** What does a subagent *not* inherit?
**A:** Your main conversation history, the files accumulated in your context, and your current session state — it starts from a clean slate.

**Q:** Which built-in subagents skip CLAUDE.md and git status, and why?
**A:** Explore and Plan — to keep research fast and cheap.

**Q:** Which built-in subagent loads CLAUDE.md and git status?
**A:** general-purpose.

**Q:** A delegated task ignored a CLAUDE.md rule. Most likely cause?
**A:** It went to Explore or Plan, which don't load CLAUDE.md — that context was never there.

**Q:** Which subagent should carry a task where project constraints must be respected?
**A:** general-purpose, or a custom subagent that explicitly loads the rules it needs.

**Q:** Do custom subagents automatically see your skills?
**A:** No. A skill must be explicitly listed in the agent's frontmatter (`.claude/agents`).

**Q:** Built-in agents and skills — what's the rule?
**A:** Built-in agents have no preloaded skills. If you need skill-backed behavior, create a custom subagent with those skills listed in its configuration.

**Q:** What's the context benefit of a subagent?
**A:** It returns a summary rather than the full task history, so investigation output doesn't bloat the main context.

## Claude Code Operation — The mechanism map

**Q:** Context cost — CLAUDE.md?
**A:** Persistent per session, and it dilutes with size.

**Q:** Context cost — rules file?
**A:** Path-scoped: adds to context only when triggered. Unscoped: the same persistent cost as CLAUDE.md.

**Q:** Context cost — hook?
**A:** Minimal — the script runs at the lifecycle event and adds no content to context, except any output routed back to Claude.

**Q:** Context cost — subagent?
**A:** It returns a summary, not the full task history.

**Q:** What's the underlying tradeoff across all four mechanisms?
**A:** How much context it costs vs. how reliably it applies.

**Q:** When is this whole cluster *not* worth setting up?
**A:** One-off tasks you won't revisit — e.g. a quick exploration of an unfamiliar codebase. The setup overhead isn't warranted.

## Claude Code Operation — Skills as portable workflows

**Q:** What is a skill, physically?
**A:** A portable Markdown file (`SKILL.md`) in `.claude/skills` — frontmatter identifies it and describes when it applies; the body holds the steps.

**Q:** Which three runtimes can run the same skill file?
**A:** Claude Code, the Messages API, and the Agent SDK (plus Claude Managed Agents).

**Q:** What changes about a skill across runtimes?
**A:** Not the file — where it runs, how it gets loaded, and what it's allowed to touch.

**Q:** How does a skill load in Claude Code?
**A:** Discovered from `.claude/skills` on the filesystem; loads on a description match or when invoked by name.

**Q:** Where do a skill's steps run in Claude Code, and under what controls?
**A:** In your terminal session against your local files, under the active permission mode and deny rules — it's filesystem-based and governed by the settings layer.

**Q:** Portability rule 1 — what makes a description work?
**A:** Write it as the matching criterion: it must identify *when the skill applies*. A vague description fails to load in every runtime.

**Q:** Portability rule 2 — what breaks a skill on the Messages API?
**A:** Shelling out to a local command. The API runs the skill in a container without it. Keep steps to what the runtime guarantees, or document the dependency.

**Q:** Portability rule 3 — what do subagents do with skills?
**A:** Nothing automatically — they start clean. A skill the parent relied on must be listed for the subagent explicitly, in every runtime that supports subagents.

**Q:** What extra setup do the API and SDK require for skills?
**A:** A beta header on the Messages API; `settingSources` configured on the Agent SDK.

**Q:** Skill vs. CLAUDE.md — how do you split?
**A:** Instructions that must apply to *every session in a project* → CLAUDE.md. On-demand, portable procedures → skills.

## Claude Code Operation — Custom commands

**Q:** What is the recommended format for both explicit and automatic invocation in current Claude Code?
**A:** Skills. Invoke directly with `/skill-name`, or Claude loads it automatically when relevant.

**Q:** Is `.claude/commands/` still supported?
**A:** Yes, it still works — but it's the legacy format.

**Q:** How do you make a workflow run *only* when explicitly called?
**A:** A skill with `disable-model-invocation: true` in the frontmatter.

**Q:** How are plugin commands namespaced?
**A:** Automatically by plugin name — a `run-tests` command in a plugin named `payments` is `/payments:run-tests`.

**Q:** Why can two plugins both ship a `run-tests` command?
**A:** The plugin-name prefix keeps them from colliding.

**Q:** What should a plugin author remember about the plugin name?
**A:** It's part of the interface — it prefixes every command shipped, so renaming the plugin renames them all.

## Claude Code Operation — Plugins and marketplaces

**Q:** What does a plugin bundle?
**A:** Skills, hooks, subagents, and MCP servers, in a single installable unit.

**Q:** What is a marketplace?
**A:** A catalog of plugins someone has created and shared.

**Q:** Which marketplace is available without setup?
**A:** The official Anthropic marketplace, automatically when you start Claude Code.

**Q:** How do you add a third-party marketplace hosted on GitHub?
**A:** `/plugin marketplace add <owner/repo>`.

**Q:** In one sentence, what does a plugin buy you?
**A:** It replaces a page of manual setup steps with a versioned, auditable install.

**Q:** Where do a plugin's components land on install?
**A:** Skills in a skills directory; hooks, subagents, and settings in their respective locations. A plugin manifest describes the bundle, and the install command wires it in.

**Q:** What does a managed marketplace allowlist do — and not do?
**A:** It gates which marketplace sources users may add. It does *not* register marketplaces automatically.

**Q:** How do you push a marketplace to all users without them running the `add` command?
**A:** Pair the allowlist with `extraKnownMarketplaces` in managed settings.

**Q:** Why can't a user or project file override an org-deployed plugin?
**A:** Precedence comes from deployment scope — managed settings sit above user and project settings in the configuration hierarchy.

## Claude Code Operation — The packaging decision

**Q:** When do you reach for a skill?
**A:** When a task-specific procedure should stay out of context until it's needed — a PR review, a deployment checklist that only loads when the work calls for it.

**Q:** When do you reach for a custom command?
**A:** When the procedure has a clear name and you want to trigger it directly rather than rely on description matching.

**Q:** When do you reach for a plugin?
**A:** When a working setup lives on one machine and needs to be shared, versioned, and kept consistent across a team.

**Q:** Packaging — the cost question in one line?
**A:** Pay the setup cost once (plugin install) or repeatedly (every developer running the same manual steps by hand)?

**Q:** What's the classic complexity failure in a plugin?
**A:** Hard-coded absolute paths in its skills — installs correctly for the author, fails for everyone else. Any path or environment assumption baked into a skill or hook command is the thing most likely to break across machines.

**Q:** What's the risk when a teammate installs your plugin?
**A:** A plugin carries only what it bundles. A deny rule or hook you relied on locally isn't included unless explicitly listed — so the protection doesn't carry to their machine.
