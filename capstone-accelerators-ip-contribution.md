# Capstone — Accelerators & IP Contribution

**What this is.** The cross-domain review sheet for **Module 5** of the class series, following [`capstone-production-grade-prompting.md`](capstone-production-grade-prompting.md) (Module 2 — the developer primitive library), [`capstone-claude-code-mcp-integration.md`](capstone-claude-code-mcp-integration.md) (Module 3 — configuration and governance), and [`capstone-production-engineering-evals-security.md`](capstone-production-engineering-evals-security.md) (Module 4 — evidence and survival under real traffic). Those covered *how to build*, *how to configure*, and *how you know it works*. This one covers **what happens to the build after the engagement ends** — packaging, contribution, placement, versioning, and the seams between components.

It introduces **no new mechanics.** Every technical fact was written into [`domain-2-applications/notes.md`](domain-2-applications/notes.md) as the module's five lessons landed (Packaging for Reuse · Contributing Back · Deployment & Versioning · Comparing Platforms · Multi-Component Applications, all dated 2026-07-19). This sheet is the routing layer over them.

**How to use it.** Read after the D2 notes sections it points into — not before. Integration pass, best run in exam week. _Source: class module "Accelerators & IP Contribution" (Module 5 recap + glossary screens, recorded 2026-07-19); cross-checked against the domain notes the same day._

> ⚖️ **Blueprint reality check — this one is the opposite of Module 4.** Where Module 4's material routed into a 2.6% domain and had to be re-aimed at the big ones, Module 5 lands almost entirely inside **D2 · Applications and Integration (33.1%)** — and specifically in its two most-tested skills, **Claude Application Design (8.6%)** and **Systems Life Cycle**, plus **Configuration Management (4.1%)**. Secondary routes: **D8 (10.6%)** for the MCP-server asset type and contribution channel, **D7 (8.1%)** for the trust-boundary and least-privilege material, **D4 (2.6%)** for the portable eval suite, **D1 (14.7%)** for the agent-template asset type. There is no re-aiming to do here. **Study this sheet at full weight.**

> ⚠️ **Most version-sensitive content in the repo.** Model IDs, alias-resolution behavior, platform names and hosting forms, pinning conventions, and residency capabilities in the underlying notes are all **as stated 2026-07-19**. Re-verify at `platform.claude.com` and the partner's docs before relying on any specific string. The *judgment* is stable; the *strings* are not.

---

## The one idea

Module 2's failure shape was *dev illusion → production stressor*. Module 3's was *convenience setting → governance boundary*. Module 4's was *development hides what production reveals*. This module's:

> 🔑 **The asset has to survive the people who built it.** Every move in this module converts private, tacit knowledge into something a stranger can verify without you in the room. Packaging makes it verifiable **by configuration** — the parameters say what's customer-specific. Contribution makes it verifiable **by review** — a runnable example and a test say it works. Pinning makes it verifiable **by version** — the ID says what actually shipped. Measurement makes the placement verifiable **by number** — latency from their region, not your laptop. Trust boundaries make the seams verifiable **by scope** — least privilege at each hop, established explicitly rather than inherited.

The corollary the recap states outright: **the expensive thing is never the code — it's the knowledge of which parts were customer-specific**, and that knowledge decays the moment the engagement team disperses. Hence *package while the build is fresh*. The same logic runs through every takeaway: a maintainer accepts what they can verify; an alias is a claim you can't verify; an unmeasured platform choice is a preference, not an argument; an unestablished trust boundary is an assumption inherited from whichever component sent the data.

---

## Master crosswalk — the 5 takeaways, routed to where the mechanics live

| # | Takeaway | What decays or breaks without it | The move | Lives in |
|---|----------|----------------------------------|----------|----------|
| 1 | **Package while the build is fresh.** | The knowledge of *what was customer-specific* is the expensive part, and it's held by people who move on. Reconstructed months later it costs more than it did to build. | Keep the reusable logic; expose customer-specific parts as **documented parameters**; bundle the **eval** and the **audit log** alongside the asset. Correct packaging produces an asset teams **configure**, not one they copy and diverge. Three asset types parameterize differently: **agent template**, **MCP server package**, **portable eval suite**. | [D2 · Packaging for Reuse](domain-2-applications/notes.md#packaging-for-reuse--turning-a-working-build-into-an-accelerator); asset types route to [D1 · Agent Construction](domain-1-agents/notes.md), [D8 · MCP servers](domain-8-tools-mcps/notes.md), [D4 · portable eval suite](domain-4-eval-testing/notes.md) |
| 2 | **A maintainer accepts what they can verify.** | A contribution a reviewer can't verify **sits at the back of the queue** — indefinitely. | Match the asset to **the channel built for its shape** (Cookbook = one focused, self-contained pattern; tools and servers = their own repos), then clear the review bar: **focused code, a runnable example, a test, a statement of assumptions**. **Licensing rights confirmed *before* technical review.** Readiness is what moves a private asset into shared infrastructure others build on. | [D2 · Contributing Back](domain-2-applications/notes.md#contributing-back--from-private-reuse-to-shared-infrastructure); channel conventions in [D8](domain-8-tools-mcps/notes.md) |
| 3 | **Pin what ships.** | An upstream model change arrives **overnight, with no rollback path** — and your output changed without a commit. | Choose the platform on the customer's **cloud and compliance posture**, then **pin the specific model version rather than the moving alias**, and **keep the prior version available**. The class metaphor: an alias is *the current edition of a book* — convenient, but the text can change; pinning **cites a fixed edition**. Adoption becomes deliberate. | [D2 · Deployment and Versioning](domain-2-applications/notes.md#deployment-and-versioning--where-the-workload-runs-and-what-ships); promotion gate in [D4 · evals](domain-4-eval-testing/notes.md) |
| 4 | **Measure the dimension that decides the placement.** | The placement is a preference procurement and security won't sign off on. | Measure all three: **latency from the customer's region** (not your laptop), **compliance against their existing certification**, **cost as total per call** (egress + platform fees + integration, not the token rate). For regulated customers **compliance is pass-or-fail** — raise it **during scoping**, or it rejects the build later at **contract review**. | [D2 · Comparing platforms](domain-2-applications/notes.md#comparing-platforms--latency-compliance-cost-class-notes-2026-07-19); residency/compliance in [D7](domain-7-security/notes.md), regulation routes in [D1](domain-1-agents/notes.md) |
| 5 | **Mark every seam as a boundary.** | The app is **only as contained as its most privileged seam** — and trust silently inherits across hops nobody scoped. | Scope each component to **the minimum access its role requires**; treat **every point where data crosses as a trust boundary**; **fetched content is data, not instructions**. **Trust must be explicitly established at each boundary — it does not carry over from the component that sent the data.** When a seam **can't be secured, it goes to a human owner rather than shipping**. | [D2 · Multi-Component Applications](domain-2-applications/notes.md#multi-component-applications--trust-boundaries-where-components-meet); mechanics in [D7 · AI Application Security](domain-7-security/notes.md) |

---

## Unified decision table — "which move does this stem call for?"

The module's core skill is mapping a stated situation to **the one move that answers it**. Scattered across five lessons in the notes; consolidated here, which is how a scenario stem actually reaches you.

| The requirement or symptom in the stem | The move | Domain |
|---|---|---|
| "The next engagement shouldn't rebuild this" | **Package as an accelerator** — parameterize the customer-specific parts | D2 |
| "The scripts all run, so we're reusable" | **No** — loose scripts with embedded values get **copied and diverged** | D2 |
| "When should we package?" | **While the build is fresh** — the knowledge of what's customer-specific is what decays | D2 |
| "One-off the customer will never reuse" | **Don't package** — separation + documentation overhead loses; ship and move on | D2 |
| "Which parts get parameterized?" | Prompts, paths, scopes, thresholds, and **credentials by reference** (name, never value) | D2 |
| "What ships alongside the asset?" | The **eval** (proves it still works in a new context) and the **audit log** | D2 → D4 |
| "It's a working agent we want reusable" | **Agent template** — prompt + tool schemas + loop, domain values in documented config | D1 · D2 |
| "It's a set of tools other teams want" | **MCP server package** | D8 · D2 |
| "It's the test set that defines 'working'" | **Portable eval suite** — dataset **and** rubric, runnable in the next team's context | D4 · D2 |
| "Where does a focused, self-contained pattern go?" | **The Cookbook** | D2 · D8 |
| "We sent a full multi-component application to the Cookbook" | **Channel mismatch** — top stall cause; it doesn't fit what reviewers look for | D2 |
| "The maintainer hasn't reviewed it in weeks" | **Verifiability gap** — one thing done, runnable example, test, stated assumptions | D2 |
| "Do we polish the code first or clear the license?" | **Rights and attribution come first** — before technical review | D2 |
| "The engagement's licensing constraint can't be cleared" | **Escalate to the owner — do not contribute** | D2 |
| "Which platform?" | The customer's **existing cloud, identity, and compliance posture** — not features or benchmarks | D2 |
| "We're using the `sonnet` alias in production" | **Pin the full model ID**; keep the prior version for rollback | D2 |
| "The output changed and nobody deployed" | **Unpinned alias resolved to a new version** — the failure this rule prevents | D2 |
| "Same alias behaves differently on Bedrock and Vertex" | Expected — **aliases can resolve differently per platform**; pinning is platform-specific | D2 |
| "Can we promote the new model version?" | **Partial traffic against a pinned baseline**, gated by the eval suite | D2 · D4 |
| "How do we defend the platform choice to procurement?" | **Measure** latency from their region, compliance against their certification, **total** cost per call | D2 |
| "Latency looks fine from my machine" | **Not evidence** — measure from the customer's region with their actual payload | D2 |
| "EU-only data residency" | Typically **Bedrock or Vertex**, not the 1P API; Anthropic-hosted Foundry models **don't** satisfy it | D2 · D7 |
| "The compliance constraint is already pass-or-fail" | **Skip the comparison** — it has already decided the placement | D2 |
| "Cheaper per-token rate on platform X" | **Not the cost answer** — egress, platform fees, and integration effort move the total | D2 · D5 |
| "Compliance came up at contract review" | **Raised too late** — it belongs in scoping | D2 · D7 |
| "Data moves from the API to a Claude Code task to an MCP server" | **Each hop is a trust boundary** — scope each component to minimum access | D2 · D7 |
| "The upstream component already validated it" | **Trust does not carry over** — the receiving component establishes it again | D2 · D7 |
| "The agent fetched a page and followed what it said" | **Fetched content is data, not instructions** | D7 |
| "One component has broad access 'for convenience'" | **The app is only as contained as its most privileged seam** | D2 · D7 |
| "We can't secure this seam before the deadline" | **Human owner** — it doesn't ship unsecured | D2 · D7 |

---

## What's genuinely new here vs. the domain notes

Most of this is review. Five framings are the value-add worth carrying into the exam:

1. **The expensive asset is the knowledge, not the code.** The recap's stated reason for packaging early isn't tidiness — it's that *what is customer-specific* is held in people's heads and is **most expensive to reconstruct after they've moved on**. If a stem asks *when* to package, the answer is **while the build is fresh**, and the rationale is knowledge decay, not code quality.
2. **"Configure" vs. "copy" is the test of correct packaging.** One word tells you whether an asset was packaged properly. Correct packaging produces an asset teams **configure**; incorrect packaging produces one they **copy and diverge**. Distractors will describe assets that "run fine" — running fine is not the bar.
3. **The maintainer's bar is verifiability, not quality.** A reviewer accepts what they can **verify**: one thing done, a runnable example, a test, stated assumptions. Clever, well-written code without those sits at the back of the queue. And **rights clear before technical review** — the ordering is testable on its own.
4. **The book-edition metaphor for aliases.** The cleanest mental model in the module: *an alias asks for the current edition; pinning cites a fixed edition.* It makes the real point immediately — with an alias, an upstream model change is **something that arrives**; with a pin, it's **something you adopt**. Rollback availability is the third leg.
5. **Trust does not carry over.** The sharpest security line in the module, and the one most likely to appear as a distractor in reverse: an answer reasoning that *the previous component already checked it* has misread the boundary. Each seam **establishes trust explicitly**. Paired with the containment rule — **only as contained as your most privileged seam** — it converts least privilege from a setting into an architecture property.

---

## Cross-domain practice questions

Blueprint-style items written to these objectives. Each states how many to select. Answer key and per-option rationale follow.

**1. (D2 · Systems Life Cycle — select ONE)**
An engagement wrapped three weeks ago. The team wants to turn the build into an accelerator, but the two engineers who wrote it have rolled onto other work. What is the strongest stated reason this should have been done at the end of the build?

A. Code quality degrades in a repository that isn't actively maintained.
B. The knowledge of which parts are customer-specific is the most expensive thing to reconstruct later.
C. Licensing rights expire a fixed period after engagement close.
D. An eval bundled later cannot be run against the original baseline.

**2. (D2 · Systems Life Cycle — select ONE)**
A team says their build is already reusable: the scripts all run, and a new team can clone the repo. What is the most accurate assessment?

A. It is reusable, since a working repository is the definition of a reusable asset.
B. It is not packaged — customer-specific values scattered across files produce assets teams copy and diverge, not configure.
C. It is packaged, but missing a contribution channel.
D. It is not reusable until it has been accepted into the Cookbook.

**3. (D2 · Systems Life Cycle — select TWO)**
Which two artifacts does the module say ship **alongside** a packaged accelerator?

A. The eval that proves the asset still works in a new context.
B. A performance benchmark against competing implementations.
C. The audit log.
D. The original engagement's statement of work.

**4. (D2 · Systems Life Cycle — select ONE)**
An engineer wants to contribute a complete multi-component customer application to the Claude Cookbook. It is well-written, tested, and documented. What is the most likely outcome and why?

A. Accepted quickly, since it exceeds the review bar on code quality.
B. It stalls — the Cookbook's channel is built for one focused, self-contained pattern, not full applications.
C. Rejected for licensing reasons, since all engagement code is restricted.
D. Accepted after refactoring into smaller functions.

**5. (D2 · Systems Life Cycle — select ONE)**
A team is preparing a contribution. The code is focused, an example runs, and a test passes. Legal has not yet confirmed the right to contribute engagement code. What should happen next?

A. Submit for technical review in parallel; legal review typically clears before merge.
B. Confirm rights and attribution before technical review begins.
C. Submit with a disclaimer noting rights are pending.
D. Contribute a rewritten version to avoid the question entirely.

**6. (D2 · Configuration Management — select ONE)**
A production service configured with the `sonnet` alias starts producing different summaries. No deployment occurred. What happened, and what is the fix?

A. Prompt drift from accumulated conversation state; reset the sessions.
B. The alias resolved to a new model version; pin the full model ID and keep the prior version available for rollback.
C. Rate limiting degraded the responses; add exponential backoff.
D. A cache invalidation; disable prompt caching.

**7. (D2 · Claude Application Design — select TWO)**
A customer's security team asks the team to defend its platform choice. Which two are valid measurements per the module?

A. Latency measured from the customer's region against their actual payload.
B. Latency measured from the development team's machines during off-peak hours.
C. Total cost per call including egress, platform fees, and integration effort.
D. Published per-token pricing across the candidate platforms.

**8. (D2 · Claude Application Design — select ONE)**
A regulated customer has an absolute EU data-residency requirement, already certified on their existing cloud. The team is preparing a three-dimension latency/compliance/cost comparison across platforms. What is the best next step?

A. Complete the comparison; all three dimensions must be weighed before a defensible choice.
B. Skip the comparison — compliance is pass-or-fail and has already decided the placement.
C. Run the comparison but weight compliance at 50%.
D. Choose on latency, then request a residency exception.

**9. (D2 · Claude Application Design / Security — select ONE)**
In a multi-component app, an API layer passes user-supplied content to a Claude Code task, which passes results to an MCP server. An engineer argues the MCP server can skip validation because the API layer already validated the input. What is the correct response?

A. Correct — revalidating at each hop adds latency without reducing risk.
B. Incorrect — trust does not carry over; each boundary establishes it explicitly.
C. Correct, provided the API layer logs its validation.
D. Incorrect, but only because the MCP server runs in a different deployment environment.

**10. (D2 · Systems Life Cycle / Security — select ONE)**
A launch is one week out. One seam between components cannot be scoped to least privilege in time without breaking a dependency. What does the module prescribe?

A. Ship with the broad scope and file a follow-up ticket.
B. Ship with monitoring on that seam and tighten it post-launch.
C. Escalate the seam to a human owner rather than shipping it unsecured.
D. Remove the component and reimplement its function in the API layer before launch.

---

### Answer key & rationale

**1: B.**
- **A** — plausible-sounding but not the module's reason; the asset isn't degrading, the *knowledge about it* is.
- **B** ✅ — the stated rationale for *package while the build is fresh*: what's customer-specific is the expensive thing to reconstruct once the people who held it have moved on.
- **C** — invented mechanism; nothing in the module ties rights to a clock.
- **D** — an eval can be written later; the point is it's bundled as part of the package, not that it becomes impossible.

**2: B.**
- **A** — "the scripts run" is the module's named trap; running is not the same as configurable.
- **B** ✅ — correct packaging produces an asset teams **configure**; embedded customer-specific values produce copy-and-diverge.
- **C** — reverses the order: packaging precedes contribution, and packaging is what's missing.
- **D** — contribution is a separate step; an asset can be reusable privately without ever going to the Cookbook.

**3: A and C.**
- **A** ✅ — the bundled eval proves the asset still works in a new context.
- **B** — never mentioned; benchmarking against competitors isn't part of the package.
- **C** ✅ — the audit log ships alongside the asset.
- **D** — the SOW is engagement paperwork, not part of the reusable asset.

**4: B.**
- **A** — code quality isn't the gate; **channel fit** is, and this is the wrong channel.
- **B** ✅ — channel mismatch is the top stall cause; the Cookbook takes one focused, self-contained pattern.
- **C** — overbroad; engagement code isn't categorically restricted, it requires confirmed rights.
- **D** — refactoring doesn't fix a channel mismatch; a full application is still a full application.

**5: B.**
- **A** — inverts the stated gate order and creates the exact problem legal must unwind later.
- **B** ✅ — rights and attribution clear **before** technical review.
- **C** — a disclaimer does not substitute for confirmed rights.
- **D** — a rewrite doesn't resolve the underlying rights question and wastes the packaging work; if the constraint can't be cleared, escalate to the owner.

**6: B.**
- **A** — invents a mechanism; a stateless production call doesn't accumulate conversation drift.
- **B** ✅ — the canonical unpinned-alias failure: the change arrived rather than being adopted. Fix is the three-part move — pin the model, version the prompt/asset, keep the prior version for rollback.
- **C** — rate limiting produces errors and retries, not silently different content.
- **D** — caching affects cost and latency, not output semantics.

**7: A and C.**
- **A** ✅ — latency must be measured from the customer's actual region against their actual payload.
- **B** — the named anti-pattern; a laptop or dev-region number hides the round trip.
- **C** ✅ — cost is the **total per call**: egress, platform fees, integration effort.
- **D** — the per-token rate alone is the named cost trap.

**8: B.**
- **A** — treats a pass-or-fail constraint as a weighting problem.
- **B** ✅ — the module's stated exception: when compliance is already pass-or-fail, it has decided the placement and the comparison adds nothing.
- **C** — still a weighting model; pass-or-fail isn't 50%.
- **D** — exception-seeking against a hard residency requirement; also raises compliance after the fact, which is the failure mode the module warns lands at contract review.

**9: B.**
- **A** — the containment argument the module explicitly refuses.
- **B** ✅ — trust must be explicitly established at each boundary; it does not carry over from the sending component.
- **C** — logging is evidence of the upstream check, not an establishment of trust downstream.
- **D** — right answer, wrong reason: the boundary exists because data crosses, and deployment-environment difference is a common case rather than the rule itself.

**10: C.**
- **A** — ships the unsecured seam, which the module rules out; the app is only as contained as its most privileged seam.
- **B** — monitoring detects after the fact; it isn't a scope control.
- **C** ✅ — the stated prescription: a seam that can't be secured goes to a human owner rather than shipping.
- **D** — a plausible engineering option but not the module's answer, and it silently relocates the same privilege rather than resolving ownership.

---

## Capstone flashcards (meta-lessons)

**Q:** When do you package a build as an accelerator, and why then?
**A:** **While the build is fresh.** The knowledge of *what is customer-specific* is the most expensive thing to reconstruct once the people who held it have moved on.

**Q:** One-word test of correct packaging?
**A:** **Configure.** Correct packaging produces an asset teams configure; incorrect packaging produces one they copy and diverge.

**Q:** What ships alongside a packaged accelerator?
**A:** The **eval** (proves it still works in a new context) and the **audit log**.

**Q:** The three asset types?
**A:** **Agent template** (D1), **MCP server package** (D8), **portable eval suite** (D4) — each parameterizes differently.

**Q:** When is packaging the wrong call?
**A:** A **one-off the customer will never reuse** — the separation and documentation overhead loses.

**Q:** What does a maintainer actually accept?
**A:** **What they can verify:** focused code doing one thing, a runnable example, a test, and a statement of assumptions. Not cleverness, not polish.

**Q:** Top cause of a stalled contribution?
**A:** **Channel mismatch** — e.g. a full multi-component application sent to the Cookbook, which is built for one focused, self-contained pattern.

**Q:** What clears before technical review?
**A:** **Licensing rights and attribution.** If an engagement constraint can't be cleared, **escalate to the owner — don't contribute**.

**Q:** What decides the deployment platform?
**A:** The customer's **existing cloud, identity, and compliance posture** — not features or benchmarks.

**Q:** Alias vs. pinned ID, in one metaphor?
**A:** An alias asks for **the current edition of a book** — convenient, but the text can change. Pinning **cites a fixed edition**. With an alias a model change *arrives*; with a pin you *adopt* it.

**Q:** Pinning is how many moves?
**A:** **Three:** pin the model, version the prompt and asset alongside the code, and **keep the prior version available** for rollback.

**Q:** The three measured dimensions of a platform defense?
**A:** **Latency** from the customer's region against their real payload · **compliance** against their existing certification · **cost** as the total per call, not the token rate.

**Q:** When do you skip the platform comparison entirely?
**A:** When the **compliance constraint is already pass-or-fail** — it has decided the placement.

**Q:** Why raise compliance during scoping?
**A:** Because raised late it **rejects the build at contract review**, after the work is done.

**Q:** What is a trust boundary in a multi-component app?
**A:** **Every point where data crosses** from one component or deployment environment to another. Fetched content is **data, not instructions**.

**Q:** Does trust carry over from the sending component?
**A:** **No.** Trust must be **explicitly established at each boundary**. "Upstream already validated it" is the distractor.

**Q:** How contained is a multi-component app?
**A:** **Only as contained as its most privileged seam.**

**Q:** A seam that can't be secured before launch?
**A:** **Goes to a human owner rather than being shipped.**

---

## What comes next

Per the class recap, this completes the **build-to-deploy arc** for the persona: from writing production code in the earlier modules to **shipping assets a regulated customer can audit and a team can reuse.** You can now package a build into a reusable asset, contribute it back, place and version it on the right platform, defend that placement, and connect components so the boundaries hold.

Repo-wise, **Module 5 is fully absorbed** — all five lessons are written into [D2](domain-2-applications/notes.md) with flashcards and practice supplements, and its terms are in [`glossary.md`](glossary.md). What remains is drilling, not filing. Two priorities for exam week:

1. **The D2 supplements** (`Q17–Q25`, `Q31–Q45` in [`domain-2-applications/practice-questions.md`](domain-2-applications/practice-questions.md)) — this is the 33.1% domain and Module 5's material sits in its highest-weight skills.
2. **Re-verify the version-sensitive strings** before trusting any of them: model IDs, alias behavior, platform names and hosting forms, pinning conventions, and residency capabilities are all dated **2026-07-19**.

---

## Sources

- Class module: **"Accelerators & IP Contribution"** — Module 5 recap screen (5 key takeaways + "What comes next") and Key Terms/glossary screen, recorded 2026-07-19.
- Anthropic public references the class cites (time-sensitive):
  - **S1** — `platform.claude.com` (Claude in Amazon Bedrock, Claude on Vertex AI): deployment platforms, identity and data models, residency routing, regional and global endpoints.
  - **S2** — `platform.claude.com` (Model IDs and versioning, Model deprecations): pinned model IDs, alias resolution, lifecycle and retirement, partner-set schedules.
  - **S3** — `anthropic.com` and the Anthropic GitHub organization (**Cookbook**): contribution channels, the Cookbook as a home for focused examples, contribution conventions.
  - **S4** — Anthropic Academy, **Building with the Claude API**: eval datasets, graders, and the evaluation pipeline used as the deployment gate.
  - **S5** — Anthropic Academy, **Claude Code 101 In Action**: Claude Code agentic tasks and MCP server roles in a multi-component workflow.
- Repo domain notes where each takeaway's mechanics are written and verified: `domain-2-applications/notes.md` (all five lessons), `domain-1-agents/notes.md` (agent template), `domain-8-tools-mcps/notes.md` (MCP server package, contribution channel), `domain-4-eval-testing/notes.md` (portable eval suite, promotion gate), `domain-7-security/notes.md` (trust boundaries, least privilege, residency/compliance).
- Term definitions from this module are merged into the repo-wide [`glossary.md`](glossary.md).
