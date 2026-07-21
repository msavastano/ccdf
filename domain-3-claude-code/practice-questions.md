# Domain 3: Claude Code — Practice Questions

Format per item: scenario stem · state how many responses to select · options A–D (or more for multiple-response) · tag (e.g., "D3 · Claude Code Operation") · answer key + per-option rationale at the end of the file.

24 original items written to blueprint objectives (not from the live exam). Q1–Q8 cover permission modes, settings levels, and human gates; Q9–Q16 cover durable project context (CLAUDE.md, rules files, hooks, subagents); Q17–Q24 cover packaging workflows (skills across runtimes, custom commands, plugins, marketplaces). Answer key with per-option rationale at the end — don't scroll past the line until you've committed to answers.

---

**Q1 · D3 · Claude Code Operation** (select ONE)
A developer joins a team and is handed a large codebase she has never seen. Her first task is a refactor that touches billing logic. She wants Claude Code to help but doesn't yet trust her own read of the blast radius. Which permission mode best fits the start of this work?

A. `acceptEdits` — the edits are code changes, and file operations are the bulk of the work.
B. `plan` — it holds Claude Code in the explore phase, blocking file edits and shell commands until she reviews and releases a plan.
C. `bypassPermissions` — the prompts will slow down a large refactor.
D. `dontAsk` — it prevents unwanted actions by denying anything not pre-approved.

---

**Q2 · D3 · Claude Code Operation** (select ONE)
An organization must guarantee that `.env` files are never edited by Claude Code on any developer machine, in any project, even if an individual developer sets a bypass mode out of impatience. What is the correct control?

A. A deny rule in each project's `.claude/settings.json`.
B. A deny rule in `.claude/settings.local.json` distributed to every developer.
C. A deny rule at the enterprise level in `managed-settings.json`.
D. Mandating `default` mode via a user-level `~/.claude/settings.json` on every machine.

---

**Q3 · D3 · Claude Code Operation** (select TWO)
Which statements about allow and deny rules are correct?

A. A deny rule always wins over an allow rule, regardless of the mode in effect.
B. An allow rule overrides a deny rule when both are set at the same level.
C. A deny rule still blocks a tool under `bypassPermissions`.
D. Deny rules are ignored in `plan` mode because nothing can be written anyway.
E. In `plan` mode, a matching allow rule will auto-approve a file edit.

---

**Q4 · D3 · Claude Code Operation** (select ONE)
A team runs Claude Code as an unattended step in CI: it inspects a pull request and posts a comment. No human is at a terminal to answer a permission prompt, and the team wants a fixed, explicit tool surface — anything not pre-approved should simply fail rather than hang or silently proceed. Which mode fits?

A. `auto`, so a model classifier can decide each call on the merits.
B. `bypassPermissions`, since no human is present to approve anything.
C. `dontAsk`, so pre-approved tools run and everything else is denied without prompting.
D. `acceptEdits`, since CI only needs to write a comment.

---

**Q5 · D3 · Claude Code Operation** (select ONE)
A developer argues that because Claude Code can review its own diff and reports high confidence, a change to a module the team has explicitly marked as security-sensitive can merge without a human reviewer. What is the best response?

A. Agreed, if the session ran in `plan` mode — the approved plan is the human gate.
B. Agreed, if a deny rule protected every other path during the session.
C. Disagreed — on code the team has marked sensitive, the agent's work is an input to a human decision, not a replacement for one; a person must review before merge.
D. Disagreed, but only because `auto` mode's classifier is not deterministic.

---

**Q6 · D3 · Claude Code Operation** (select ONE)
Which single question should drive the decision about where to place a human review gate?

A. How many tool calls the agent is likely to make in the session.
B. Whether the action is a file edit or a shell command.
C. What the worst outcome is if this action runs without a person checking it, and how hard it is to undo.
D. Whether the developer is familiar with the permission mode currently set.

---

**Q7 · D3 · Claude Code Operation** (select ONE)
A developer is doing a long, mechanical formatting pass on a repo she knows well. Every edit is confined to the working directory and is trivially revertible via version control. She's running in `default` mode and is frustrated by the pace. What's the best guidance?

A. Stay in `default` — oversight always outweighs latency.
B. Switch to `acceptEdits` — the actions are low-stakes and reversible, so per-edit approval buys oversight she doesn't need while adding prompt latency to every tool call.
C. Switch to `bypassPermissions` — it's the fastest option and the edits are reversible.
D. Switch to `plan` — reviewing one plan is faster than approving each edit.

---

**Q8 · D3 · Claude Code Operation** (select TWO)
Which statements about `bypassPermissions` are correct?

A. It auto-approves everything that reaches the permission step.
B. It removes the protected-path guard, unlike the other modes.
C. It causes deny rules to be skipped along with the prompts.
D. It is the recommended default for experienced developers on trusted repos.
E. It holds the agent in the explore phase until released.

---

**Q9 · D3 · Claude Code Operation** (select ONE)
A team's CLAUDE.md has grown to several hundred lines as each developer appended their own instruction. Developers now report that Claude Code frequently ignores a specific rule about the project's testing command. What best explains the problem and the fix?

A. CLAUDE.md is only read on the first session in a directory; the file must be re-loaded manually with `/init` each session.
B. A larger file consumes more of the context window, so any single instruction is a smaller fraction of what loads — trim CLAUDE.md to behavior-changing constraints and move the rest into Skills that load on demand.
C. CLAUDE.md is appended after the user's message, so later instructions in a long session override it — reorder the file so critical rules appear last.
D. Rules in CLAUDE.md are advisory only and have never been loaded into context; the testing command must be enforced with a deny rule.

---

**Q10 · D3 · Claude Code Operation** (select ONE)
A developer creates `.claude/rules/database/transactions.md` containing "all SQL in the database module must include an explicit transaction boundary," with no frontmatter. She expects it to load only when Claude Code touches database files. What actually happens?

A. It loads only when Claude reads files under a path matching the directory name `database/`.
B. It never loads, because a rules file requires a `paths` field to be valid.
C. It loads unconditionally at launch with the same priority as CLAUDE.md, because scoping comes from a `paths` glob in frontmatter, not from where the file sits.
D. It loads only when the developer invokes it by name as a slash command.

---

**Q11 · D3 · Claude Code Operation** (select ONE)
A team wants Prettier to run on every file Claude Code edits — not most of the time, every time. Which mechanism delivers that guarantee?

A. An instruction in CLAUDE.md, since it loads into every session unconditionally.
B. A PostToolUse hook matched to file-edit tools, since it fires after the call completes independently of what the model decides to do.
C. A PreToolUse hook, since only PreToolUse can enforce anything.
D. A `paths`-scoped rules file covering the source directory, since path scoping guarantees the rule is in context whenever an edit occurs.

---

**Q12 · D3 · Claude Code Operation** (select ONE)
A platform team must prevent Claude Code from editing a production configuration path, and wants the agent to receive a clear reason when it tries. Which hook configuration does this?

A. PostToolUse — inspect the completed call and revert the change, logging the reason.
B. PreToolUse — examine the tool call and exit with code 2 to block it, writing the reason to stderr as feedback the agent sees.
C. UserPromptSubmit — reject any prompt that mentions the production path.
D. SessionStart — validate the environment and refuse to start the session if the path exists.

---

**Q13 · D3 · Claude Code Operation** (select TWO)
Which statements about subagents are correct?

A. A subagent runs in its own separate context and does not inherit the main conversation history, accumulated files, or session state.
B. The Explore and Plan built-in subagents skip CLAUDE.md and git status to keep research fast and cheap.
C. Custom subagents automatically inherit every skill available to the main session.
D. Built-in subagents come with a preloaded set of skills appropriate to their role.
E. A subagent returns its full task history to the main session so nothing is lost.

---

**Q14 · D3 · Claude Code Operation** (select ONE)
A team's CLAUDE.md forbids modifying the database schema. A developer delegates an investigation task to the Explore subagent, and the returned work proposes a schema change. What is the correct diagnosis and remedy?

A. The rule was violated because CLAUDE.md constraints only apply to file edits, not proposals — no remedy needed.
B. Explore does not load CLAUDE.md, so the rule was never in its context — delegate to the general-purpose subagent, or a custom subagent that explicitly loads the rules it needs.
C. The rule belongs in `.claude/rules/` rather than CLAUDE.md; subagents read rules files but not CLAUDE.md.
D. Subagents ignore all project configuration by design; the only fix is a deny rule on the schema path.

---

**Q15 · D3 · Claude Code Operation** (select ONE)
A developer builds a custom subagent in `.claude/agents` for a code-migration task and finds it doesn't use the migration Skill the team wrote. What is required?

A. Nothing — Skills load automatically once they exist in the project; the subagent must be misconfigured elsewhere.
B. The Skill must be listed explicitly in the custom subagent's frontmatter, since custom subagents do not automatically see your skills.
C. The Skill's content must be copied into CLAUDE.md so it loads into every context, including subagents.
D. The task must be delegated to a built-in agent instead, since built-in agents come with skills preloaded.

---

**Q16 · D3 · Claude Code Operation** (select ONE)
A developer is doing a one-off exploration of an unfamiliar third-party repo she will not return to. She asks whether she should first set up CLAUDE.md, path-scoped rules files, and PreToolUse hooks. What's the best guidance?

A. Yes — hooks in particular should be configured before any session in an unfamiliar codebase.
B. Yes — without CLAUDE.md the agent has no project context and cannot explore effectively.
C. No — this machinery repays its setup cost on projects you return to across many sessions; for a one-off task you won't revisit, the overhead isn't warranted.
D. No — CLAUDE.md and rules files are only supported in repositories you own.

---

**Q17 · D3 · Claude Code Operation** (select ONE)
A team authors a code-review skill in `.claude/skills` and uses it successfully in Claude Code for weeks. When they wire the same skill into a Messages API integration, it fails partway through every run. The skill's body includes a step that calls a project-specific CLI installed on each developer's machine. What is the most likely cause?

A. The Messages API cannot load skills at all; skills are a Claude Code–only format.
B. The skill body assumes a local filesystem and local tools that the API runtime — which runs the skill in a container — does not provide.
C. The skill's description is too specific, so the API's matcher rejects it.
D. Skills must be rewritten in a different file format for each runtime.

---

**Q18 · D3 · Claude Code Operation** (select TWO)
Which statements about writing portable skills are correct?

A. The description should be written as the matching criterion — it must identify when the skill applies, because that's how the model loads it in every runtime.
B. A vague description still loads reliably in Claude Code because the file is discovered on the filesystem.
C. A subagent inherits the skills its parent had loaded, so no additional configuration is needed.
D. A skill that shells out to a local command should either be confined to what the runtime guarantees, or have that dependency documented.
E. Portability is a property of the `SKILL.md` format, so any skill ports cleanly by default.

---

**Q19 · D3 · Claude Code Operation** (select ONE)
A developer wants a deployment-checklist workflow that runs **only** when she explicitly invokes it — it should never be auto-loaded by Claude based on a description match. What is the current recommended approach?

A. Put it in `.claude/commands/`, since that legacy directory is the only format that prevents automatic invocation.
B. Author it as a skill with `disable-model-invocation: true` in the frontmatter.
C. Put it in CLAUDE.md so it's always present and never needs invoking.
D. Author it as a PreToolUse hook so it fires deterministically.

---

**Q20 · D3 · Claude Code Operation** (select ONE)
Two plugins installed in the same project each ship a command named `run-tests` — one in a plugin named `payments`, one in a plugin named `billing`. What happens?

A. The second plugin fails to install because of the name collision.
B. Nothing breaks — plugin commands are namespaced by plugin name, so they are invoked as `/payments:run-tests` and `/billing:run-tests`.
C. The last plugin installed silently overrides the earlier command.
D. Both are disabled until the developer manually renames one in settings.

---

**Q21 · D3 · Claude Code Operation** (select ONE)
An engineering director wants every developer in the org to have a specific internal marketplace available **without** each developer running `/plugin marketplace add`, and also wants to restrict developers from adding marketplaces the org hasn't approved. What configuration achieves both?

A. A managed marketplace allowlist alone — the allowlist automatically registers the approved marketplaces.
B. `extraKnownMarketplaces` alone — it both pushes the marketplace and blocks unapproved sources.
C. A managed marketplace allowlist paired with `extraKnownMarketplaces` in managed settings.
D. A project-level `.claude/settings.json` entry committed to every repo.

---

**Q22 · D3 · Claude Code Operation** (select ONE)
A developer packages her local setup as a plugin and shares it. It installs and works perfectly on her machine, but every teammate reports that a skill in the bundle errors immediately on first use. What is the most likely cause?

A. The plugin manifest is missing, so the skills directory never gets wired in.
B. The skill hard-codes absolute paths or otherwise assumes her local environment, which doesn't exist on other machines.
C. Plugins can only be installed from the official Anthropic marketplace.
D. Skills must be listed individually in each teammate's CLAUDE.md before they load.

---

**Q23 · D3 · Claude Code Operation** (select ONE)
A team relies on a local deny rule that blocks edits to production config, plus a PreToolUse hook that enforces it. They bundle their skills into a plugin and ship it to a partner team. The partner team runs the skills and a production config file gets modified. What went wrong?

A. Plugins disable deny rules on the installing machine by design.
B. The deny rule and hook were relied on locally but not explicitly included in the bundle — a plugin carries only the components it bundles, so the protection didn't transfer.
C. Deny rules only apply in `default` mode, and the partner team used `acceptEdits`.
D. The plugin's version was out of date relative to the partner team's Claude Code install.

---

**Q24 · D3 · Claude Code Operation** (select ONE)
A team has a working Claude Code setup on one lead engineer's machine: several skills, two hooks, a custom subagent, and an MCP server. Onboarding a new developer currently means walking them through a page of manual configuration. Which packaging layer addresses this?

A. A skill — author the setup steps as a procedure the new developer can invoke.
B. A custom command — give the onboarding procedure an explicit entry point.
C. A plugin — a versioned bundle of skills, hooks, subagents, and MCP servers, distributed through a marketplace and installed in one step.
D. CLAUDE.md — document the setup so it loads in every session.

---

## Answer Key & Rationale

**Q1: B.**
- A — `acceptEdits` auto-approves file operations, which is exactly the wrong default in an unfamiliar codebase touching billing logic. The concern isn't edit volume; it's that she can't yet judge the blast radius. ✗
- B — `plan` mode keeps Claude Code in the explore phase — blocking all file edits and shell commands — and produces a structured description of intended edits for her review. That's the designed default for unfamiliar codebases and high-stakes work. ✓
- C — `bypassPermissions` removes every prompt *and* the protected-path guard. Choosing it because prompts are slow, on unfamiliar high-stakes code, is the textbook wrong-mode-for-the-context risk. ✗
- D — `dontAsk` converts prompts into hard denials. On interactive exploratory work that just blocks her; it's built for unattended/headless runs. ✗

**Q2: C.**
- A — A project-level deny rule applies only to that repo, and does not survive a developer's own configuration choices across all their projects. ✗
- B — `settings.local.json` is a personal, git-ignored override file — any developer can edit or delete their own. It cannot guarantee anything organization-wide. ✗
- C — Enterprise-level `managed-settings.json` cannot be overridden by users or project files, and a deny rule applies **even when a bypass mode is set.** That combination is what makes it the most durable governance control. ✓
- D — A user-level file is user-editable, so it's not a guarantee. Mandating a mode also doesn't deterministically protect a specific path the way a deny rule does. ✗

**Q3: A and C.**
- A — Deny beats allow regardless of the mode in effect. ✓
- B — Reverses the precedence — deny always wins. ✗
- C — A deny rule blocks the tool even under `bypassPermissions`; it's the one control that survives every mode. ✓
- D — Deny rules are not conditional on mode. (`plan` also blocks writes for a different reason — that doesn't disable deny rules.) ✗
- E — In `plan` mode, file edits are never auto-approved even when an allow rule matches. ✗

**Q4: C.**
- A — `auto` delegates the decision to a model classifier. That's non-deterministic, so it doesn't give the fixed, explicit tool surface the team asked for. ✗
- B — "No human is present" is an argument for a hard deny, not for removing all safety controls. `bypassPermissions` also drops the protected-path guard. ✗
- C — `dontAsk` runs only what's pre-approved by allow rules and turns every other prompt into a denial without prompting — exactly the fixed-surface, fail-closed behavior wanted for headless runs. ✓
- D — `acceptEdits` auto-approves file operations broadly and still leaves non-filesystem tools prompting, which would hang an unattended run. ✗

**Q5: C.**
- A — An approved plan is a gate on the *approach*, not a substitute for human review of a change to code the team designated sensitive. ✗
- B — Deny rules constrain what the agent can touch; they don't supply the human judgment the sensitive-code rule requires. ✗
- C — Never let the agent be the only gate on a change to code the team has marked sensitive — the agent's output is an input to a human decision regardless of how confident it or its self-review sounds. ✓
- D — True about `auto`'s determinism, but that's not the reason here — the rule holds no matter which mode ran. ✗

**Q6: C.**
- A — Call volume is a cost/latency consideration, not a gate-placement criterion. ✗
- B — The tool type doesn't determine the stakes — an in-working-directory edit and a write outside it are both edits with very different worst cases. ✗
- C — Gate placement rests on worst-case cost if the action runs unchecked, and on how hard it is to undo. The same question applies to interactive and unattended runs alike. ✓
- D — Developer familiarity with the mode is not the risk being managed. ✗

**Q7: B.**
- A — Oversight you don't need is a real cost: `default` adds prompt latency to every tool call and it accumulates on a long pass. ✗
- B — Low-stakes, reversible, working-directory-confined edits are precisely the case `acceptEdits` is built for. ✓
- C — `bypassPermissions` removes the protected-path guard along with every prompt — far more than this task requires, and the classic impatience-driven misuse. ✗
- D — `plan` mode blocks the edits entirely; it doesn't speed up an approved mechanical pass. ✗

**Q8: A and B.**
- A — It approves everything that reaches the permission step. ✓
- B — Unlike the other modes, it also removes the protected-path guard — this is what makes it uniquely dangerous on a non-isolated machine. ✓
- C — Deny rules still block, even under `bypassPermissions`. ✗
- D — There is no such recommendation; the appropriate mode for trusted, reversible work is `acceptEdits`. `bypassPermissions` is only defensible on an isolated machine. ✗
- E — That describes `plan` mode. ✗

**Q9: B.**
- A — CLAUDE.md is read every time Claude Code starts in the project directory. `/init` generates a starter file; it isn't a per-session load step. ✗
- B — Size is the main failure mode. More file means more context window consumed, which makes any single instruction a smaller fraction of what loads — and lowers the chance the agent follows the one rule that catches a real mistake. The fix is to hold CLAUDE.md to constraints that change behavior and move everything else into Skills that load on demand. ✓
- C — The contents are appended to your prompt *before* any message from you arrives. Reordering is not the described mechanism. ✗
- D — CLAUDE.md contents are genuinely loaded into context. A deny rule is a permission control over what may be *touched*; it can't make the agent use a particular testing command. ✗

**Q10: C.**
- A — This is the trap. Directory structure inside `.claude/rules/` is organizational only and does not scope anything. ✗
- B — A rules file without `paths` is valid — it just loads unconditionally. ✗
- C — Scoping comes from the `paths` glob in YAML frontmatter. Without it, the file loads at launch with the same priority as CLAUDE.md, no matter where it sits inside `.claude/rules/`. To get the intended behavior she needs frontmatter with a glob such as `"src/db/**/*.sql"`. ✓
- D — Rules files are not slash commands. ✗

**Q11: B.**
- A — This is the exact contrast the topic draws: a CLAUDE.md instruction is followed *most* of the time because compliance depends on the model. The requirement is "every time." ✗
- B — PostToolUse fires after the tool call completes, independently of what the model decides. Running a formatter after an edit is the canonical PostToolUse use case, and the hook is what converts a convention into a guarantee. ✓
- C — PreToolUse is for blocking a call *before* it runs; formatting must happen after the edit exists. PreToolUse is not the only event that enforces anything — it's the only one that can *block*. ✗
- D — A rules file only puts guidance in context. Being in context still leaves compliance to the model. ✗

**Q12: B.**
- A — PostToolUse runs after the call has already happened, so it cannot block it — which is why it's the wrong choice for an access control. ✗
- B — PreToolUse runs first, can examine the tool call, and exits with code 2 to block it, writing the reason to stderr as feedback the agent sees. This enforces the constraint at the configuration layer rather than hoping the agent respects a CLAUDE.md instruction — and it holds regardless of permission mode. ✓
- C — UserPromptSubmit validates the request before work starts; it can't catch a tool call the agent decides to make mid-session for other reasons. ✗
- D — SessionStart initializes state and validates the environment. Refusing to start the session is a blunt instrument that blocks all legitimate work too. ✗

**Q13: A and B.**
- A — That isolation is the defining property — a subagent starts from a clean slate, does the work, and hands back the result. ✓
- B — Explore and Plan skip CLAUDE.md and git status as a speed/cost optimization, which is precisely why project rules aren't in their context. ✓
- C — Reversed. Custom subagents do *not* automatically see your skills; a skill must be listed in the agent's frontmatter. ✗
- D — Built-in agents have no preloaded skills. Skill-backed behavior requires a custom subagent with those skills listed. ✗
- E — A subagent returns a summary, not the full task history — that's the context benefit. ✗

**Q14: B.**
- A — The constraint isn't scoped to edits; the actual cause is that the rule was never loaded. ✗
- B — Explore skips CLAUDE.md and git status, so the schema rule was not in its context. For tasks where project constraints must be respected, use the general-purpose subagent (which loads both) or a custom subagent that explicitly loads the rules it needs. ✓
- C — Moving the rule to `.claude/rules/` doesn't fix it — the problem is which subagent received the task, not which file holds the rule. And a universal constraint like this belongs in CLAUDE.md. ✗
- D — Overstated: general-purpose loads CLAUDE.md and git status. The split between built-ins is the point. ✗

**Q15: B.**
- A — Skills existing in the project is not sufficient for a custom subagent. ✗
- B — Custom subagents do not automatically see your skills; if a subagent defined in `.claude/agents` needs a specific skill, that skill must be explicitly listed in the agent's frontmatter. ✓
- C — This inflates CLAUDE.md — the documented failure mode — and the Skill/on-demand loading pattern exists precisely to avoid it. ✗
- D — Backwards. Built-in agents have *no* preloaded skills; the correct path for skill-backed behavior is a custom subagent with those skills listed. ✗

**Q16: C.**
- A — Hooks repay their setup on work you repeat. Configuring them for a single exploratory pass is overhead without return. ✗
- B — Claude Code explores a codebase by reading it. CLAUDE.md supplies conventions and constraints, not the ability to explore. ✗
- C — This machinery handles well the case of projects you return to across many sessions, where a stable rule set, per-directory variation, or unconditional guardrails justify the configuration. For a one-off task, use a different approach. ✓
- D — No such ownership restriction exists; the constraint is whether the setup cost pays back. ✗

**Q17: B.**
- A — The same skill file can run in Claude Code, through the Messages API, and in the Agent SDK. The format is portable; the runtime differs. ✗
- B — The Messages API runs the skill in a container without local files or local commands. A skill body that shells out to a machine-specific CLI works in Claude Code and breaks on the API. Keep steps to what the runtime guarantees, or document the dependency. ✓
- C — Descriptions being *too specific* is not the failure mode — vagueness is. And the failure here is mid-run, not at load time. ✗
- D — No rewrite is needed; the same `SKILL.md` is used. What changes is where it runs and what it may touch. ✗

**Q18: A and D.**
- A — The model loads a skill by comparing the request to its description, so a description that identifies when the skill applies works in every runtime. ✓
- B — Filesystem discovery locates the file, but a vague description still fails to match — it fails in all runtimes, Claude Code included. ✗
- C — Reversed. Subagents start clean and do not inherit skills; the skill must be listed for the subagent explicitly. ✗
- D — This is portability rule 2 — confine steps to what the runtime guarantees, or document the dependency. ✓
- E — Portability is a design decision, not a property of the format. A skill with local-environment assumptions does not port. ✗

**Q19: B.**
- A — `.claude/commands/` still works but is the legacy format, and it isn't the mechanism that controls automatic invocation. ✗
- B — In current Claude Code, skills are the recommended format for both explicit and automatic invocation. `disable-model-invocation: true` in the frontmatter is how you get a workflow that runs only when explicitly called. ✓
- C — CLAUDE.md loads unconditionally into every session — the opposite of on-demand, and it inflates the file (the documented dilution failure mode). ✗
- D — A hook fires at a lifecycle event, not on user invocation. It's a guardrail mechanism, not an entry point for a checklist. ✗

**Q20: B.**
- A — Namespacing exists precisely so this doesn't happen. ✗
- B — Plugin commands are namespaced automatically by the plugin's name, which becomes the prefix. This is why the plugin name is part of the interface — renaming the plugin renames every command it ships. ✓
- C — No silent override; the prefix disambiguates. ✗
- D — No manual renaming is required. ✗

**Q21: C.**
- A — The allowlist gates which sources users are *permitted* to add. It restricts; it does not register marketplaces automatically. ✗
- B — `extraKnownMarketplaces` pushes the marketplace to users but is not the control that restricts which sources they may add. ✗
- C — The allowlist controls where plugins may come from; `extraKnownMarketplaces` in managed settings makes the marketplace available without each user running `add`. Pairing them achieves both goals — and because managed settings sit above user and project settings, neither can be overridden locally. ✓
- D — Project settings are below managed scope and can be overridden; they also don't gate marketplace sources org-wide. ✗

**Q22: B.**
- A — A missing manifest would break the install itself, not produce skills that install but fail at runtime for everyone except the author. ✗
- B — This is the canonical plugin complexity failure: any path or environment assumption baked into a skill or hook command installs correctly for the author and fails everywhere else. ✓
- C — Third-party marketplaces hosted in a GitHub repo can be added with `/plugin marketplace add <owner/repo>`. ✗
- D — Plugin skills land in the plugin's skills directory via the manifest; no per-user CLAUDE.md listing is involved. ✗

**Q23: B.**
- A — Plugins don't disable deny rules. Deny rules remain the strongest control — they beat allow rules and survive `bypassPermissions`. ✗
- B — A plugin carries the components it bundles and nothing else. A deny rule or hook the author relied on locally is not included unless explicitly listed, so the guardrail the skills depended on didn't reach the partner team's machine. ✓
- C — Deny rules apply in every mode, including `acceptEdits` and `bypassPermissions`. ✗
- D — Version skew isn't the described failure; the missing guardrail is. ✗

**Q24: C.**
- A — A skill is one procedure loaded on demand. It doesn't install hooks, subagents, or MCP servers on someone else's machine. ✗
- B — A custom command gives a procedure an explicit entry point; it isn't a distribution mechanism. ✗
- C — This is exactly the case a plugin is built for: a working setup that lives on one machine and needs to be shared, versioned, and kept consistent. The plugin replaces a page of manual setup steps with a versioned, auditable install. ✓
- D — CLAUDE.md documents conventions inside a project; it doesn't install hooks, subagents, or MCP servers. ✗
