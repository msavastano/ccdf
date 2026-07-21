# Domain 2: Applications and Integration — Flashcards

Format: **Q:** question / **A:** answer. Group by skill. Version-sensitive cards verified 2026-07-12.

## Understanding Requirements

**Q:** Functional vs. infrastructure (non-functional) requirements — what's the difference?
**A:** Functional = what the system does (features, I/O, integrations, output format). Infrastructure = how well (latency, throughput, availability, cost, residency, compliance).

**Q:** A scenario says "results needed by tomorrow morning, cost is primary." What requirement does this signal?
**A:** Latency-tolerant + cost-sensitive → Message Batches API.

**Q:** A capability must be reusable across several apps and maintained independently. What does this signal architecturally?
**A:** A shared service boundary — expose it as an MCP server, not per-app logic.

**Q:** Why is "help support agents answer faster" not a functional requirement?
**A:** It's a business problem/goal — not checkable. Functional requirements derive from it as specific statements of behavior ("classify each ticket into one of four queues"; "never auto-send without human approval").

**Q:** What is the practical test of a well-written functional requirement?
**A:** It's checkable — specific enough to become a line in an eval and a criterion at review. A vague goal becomes neither.

**Q:** Name the four infrastructure-requirement axes that most often decide the deployment platform.
**A:** Latency, scale, residency, identity.

**Q:** State the question behind each of the four infrastructure axes.
**A:** Latency — how fast, measured where the user is? Scale — how many requests, at what peak? Residency — where must data be processed, under which regulation? Identity — who acts, under what credentials, and what must be auditable?

**Q:** Why capture infrastructure constraints *before* choosing a platform?
**A:** They're rarely stated in the business problem and are easiest to elicit at the start — before a platform gets chosen for familiarity and justified afterward.

**Q:** What three things does a requirements record contain, and why the third?
**A:** Functional behaviors, infrastructure constraints, and **the regulation each constraint comes from** — because the decision is reviewed by people who didn't gather the requirements, and the constraint's source is what makes it defensible.

**Q:** When are lightweight notes enough instead of a full requirements record?
**A:** A throwaway prototype with no review and no regulated data.

## Systems Life Cycle

**Q:** Why must Claude apps plan for model retirement even when pinning versions?
**A:** Pinned snapshots are eventually deprecated/retired; maintenance phase must include eval-gated migration to newer models.

**Q:** How should prompt changes be treated in the SDLC?
**A:** Like production code changes: versioned, code-reviewed, eval-tested before deploy, rollbackable.

**Q:** List the seven lifecycle phases of a Claude application in order.
**A:** Requirements → Design → Build → Test → Deploy → Operate → Iterate (Iterate feeds findings back into Requirements — it's a cycle).

**Q:** What happens in the Design phase specifically?
**A:** Choose the platform, the model, and the trust boundaries.

**Q:** What is a "gate" in the lifecycle, and why does it matter in a regulated engagement?
**A:** The decision to move from one phase to the next — it's where control is kept. Two canonical gates: don't move design→build until the platform satisfies residency; don't promote to full production until the version clears the eval against the pinned baseline.

**Q:** What does the Operate phase instrument?
**A:** Cost, latency, and errors — plus enforcement of guardrails.

**Q:** What's the benefit of naming the phases as a *lifecycle* rather than teaching them individually?
**A:** It shows how they connect, so deployment, versioning, and boundary work land in the right phase instead of arriving as unrelated tasks.

**Q:** When is collapsing lifecycle phases acceptable?
**A:** A one-off experiment. A regulated deployment cannot collapse them.

## Claude API Mechanics

**Q:** Is the Messages API stateful or stateless?
**A:** Stateless — you resend the full conversation history on every request.

**Q:** Name the stop reason that means a server-tool loop paused mid-turn, and what you do with it.
**A:** `pause_turn` — resubmit the paused assistant content to continue the turn.

**Q:** What transport does Claude streaming use?
**A:** Server-sent events (SSE), via `stream: true`. Not websockets.

**Q:** Order the streaming events for a single message.
**A:** `message_start` → (`content_block_start` → `content_block_delta`… → `content_block_stop`) per block → `message_delta` → `message_stop`.

**Q:** How does a `tool_use` block's `input` arrive when streaming, and when can you parse it?
**A:** As `partial_json` string fragments across successive `input_json_delta` events — not valid JSON until `content_block_stop`. Parse/run the tool only after that block's `content_block_stop`.

**Q:** The core rule that keeps streamed state from being corrupted?
**A:** Never act on a partial block. Collect deltas; act (parse input, run a tool) only after `content_block_stop`, and add the turn to history only after `message_stop`.

**Q:** When streaming, where do you read `stop_reason`, and why check it before continuing an agent loop?
**A:** From the `message_delta` event. `tool_use` means the assembled calls are ready to run; any other value is a different path, not the tool path.

**Q:** A stream drops before `message_stop`. What do you do with what you've collected?
**A:** Treat it as provisional and **discard the partial assistant turn** — don't save it to history — then retry. A half-built `tool_use` block breaks the tool_use/tool_result pairing on the next request.

**Q:** Does streaming reduce cost or change the output?
**A:** No — it only changes *perceived* latency. The assembled message is identical to a non-streamed response; token cost is the same.

**Q:** Prompt cache hierarchy — what order, and what does a change at one level do?
**A:** tools → system → messages. A change invalidates that level and everything after it.

**Q:** Cache pricing multipliers vs. base input?
**A:** 5-min write 1.25×, 1-h write 2×, cache read 0.1×. Stacks with batch discount.

**Q:** Default cache TTL, and the alternative?
**A:** 5 minutes (refreshes free on each hit); 1-hour TTL available at 2× write cost.

**Q:** How many explicit cache breakpoints can a request have?
**A:** 4.

**Q:** What happens if you mark content below the model's minimum cacheable token count?
**A:** Silently processed without caching — no error. Check usage fields to confirm.

**Q:** Where should a cache breakpoint go if your prompt ends with a per-request timestamp block?
**A:** On the last block that is identical across requests (end of the static prefix) — never on the varying block.

**Q:** Batch API discount and what it applies to?
**A:** 50% off standard prices, both input and output tokens.

**Q:** Batch size limits and time windows?
**A:** 100,000 requests or 256 MB per batch; most finish <1 h; hard expiry 24 h; results downloadable 29 days.

**Q:** How do you match batch results to requests?
**A:** By `custom_id` — results can return in any order.

**Q:** Which batch result types are billed?
**A:** Only `succeeded`. `errored`, `canceled`, and `expired` are not billed.

**Q:** Can you stream inside a batch request?
**A:** No — `stream: true` is rejected; batch results come back as a file.

**Q:** Name the three third-party platforms offering Claude, and the key caveat.
**A:** Amazon Bedrock, Google Cloud (Vertex AI), Microsoft Foundry. Feature parity is NOT guaranteed (e.g., Bedrock lacks automatic caching).

**Q:** Total input tokens when caching — formula from usage fields?
**A:** `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`. (`input_tokens` counts only tokens after the last breakpoint.)

**Q:** How does Claude tokenize an image, and what's the token-cost formula?
**A:** It views the image in 28×28-pixel patches, one visual token per patch: `⌈width/28⌉ × ⌈height/28⌉`. A 1,000×1,000 image ≈ 36×36 = ~1,296 tokens.

**Q:** What happens to an image that exceeds a model's max edge or max visual-token limit?
**A:** It's downscaled *before* processing, so the token formula runs on the scaled dimensions. Limits differ by tier; newer models accept larger images. Cost scales with pixels, not file size.

**Q:** Three ways to send an image, and when each is right?
**A:** Inline base64 (one-off; full bytes every request); URL reference (asset already hosted); Files API (upload once, reference a `file_id` — best when the same/large asset is reused across requests or turns).

**Q:** Why is the Files API the clean choice for an image that appears across many conversation turns?
**A:** The `file_id` carries near-zero payload weight as history grows — you send the ID, not the bytes, on every later request. (Beta; not available on Bedrock or Vertex — verify your platform.)

**Q:** What block type sends a PDF, and which fields are required?
**A:** A `document` block (not `image`) with `media_type: "application/pdf"`. Only `source` is required; `title` and `context` are optional, and there is **no** required `name` field.

**Q:** A user uploads a photo and expects an immediate classification. Sync or batch?
**A:** Synchronous — the user is waiting. Vision *works* in batches, but batch latency (up to 24 h) is unacceptable for interactive use. This latency misread is the classic vision+batch failure.

**Q:** When do multimodal inputs and the Batch API fit together well?
**A:** Offline workloads that reuse assets and need structured output across thousands of inputs (e.g., a nightly image-classification pipeline): Files API removes redundant uploads, Batch absorbs latency, structured outputs keep results machine-readable.

**Q:** How does prompting for image analysis differ from prompting for text?
**A:** Same techniques (a bare "describe this image" underperforms), but images carry ambiguity text can't — overlap, depth, occlusion. Name how to handle each, e.g., "if objects overlap, describe each separately and note the overlap."

## Software Engineering Foundations

**Q:** Which HTTP errors should you retry, and how?
**A:** `429` and `5xx` (incl. `529` overloaded) with exponential backoff + jitter. Never blind-retry `400` — fix the request.

**Q:** What does HTTP 413 mean on a batch submission?
**A:** Request too large — batch exceeded the 256 MB limit.

**Q:** Concurrency vs. batching — one-line distinction?
**A:** Concurrency = many synchronous requests in flight now; batching = one asynchronous job processed within 24 h at 50% cost.

**Q:** Why can a language's JSON serialization break prompt caching?
**A:** Some languages randomize key order; cache hits require byte-identical prefixes.

## Claude Application Design

**Q:** Where do "trusted instructions" live in an API app vs. Claude Code vs. claude.ai?
**A:** API: `system` parameter. Claude Code: CLAUDE.md hierarchy + settings.json. claude.ai/Desktop: project instructions/preferences (atop Anthropic's system prompt).

**Q:** What's the Claude convention for marking content boundaries in a prompt?
**A:** XML tags (e.g., `<document>`, `<user_input>`) — untrusted content is referenced as data, never treated as instructions.

**Q:** Why do structured outputs / tool schemas beat "respond in JSON" prose instructions?
**A:** Enforced structure — validatable, typed, no parsing surprises; prose requests can drift or add commentary.

**Q:** What is session hygiene and why does it matter?
**A:** Keeping sessions scoped to a task, starting fresh rather than accumulating stale/contaminated context — prevents drift and instruction bleed-through.

## Configuration Management

**Q:** Order the CLAUDE.md hierarchy from broadest to most specific.
**A:** Enterprise/managed → user/global (~/.claude/CLAUDE.md) → project root → subdirectory.

**Q:** Model alias vs. dated snapshot — which goes in production and why?
**A:** Dated snapshot (pinned). Aliases auto-upgrade and behavior changes across releases can silently break prompts; upgrade deliberately behind evals.

**Q:** Why version prompts alongside code?
**A:** Eval results are only meaningful for a specific prompt+model pair; versioning enables review, attribution, and rollback.

**Q:** Why treat plugins as dependencies?
**A:** They inject model-visible context and capabilities; an unreviewed update can silently change app behavior. Pin and review like any dependency.

## Packaging for Reuse (Systems Life Cycle · Configuration Management)

**Q:** What is an accelerator, in one line?
**A:** A solution packaged so future engagements start from a working foundation rather than a blank repo — customer-specific values pulled out and exposed as parameters with documented defaults.

**Q:** Packaging for reuse — what's the actual operation?
**A:** Separate engagement-specific code from the reusable core, then parameterize the rest. The asset gets configured, not rewritten.

**Q:** Name the three asset types and what each bundles.
**A:** **Agent template** (system prompt + tool schemas + loop structure) · **MCP server package** (tools, their inputs, the scope the installing team controls) · **Eval suite** (graded test set + judge rubric).

**Q:** What does correct packaging require for an agent template?
**A:** Pull domain-specific values into configuration with documented defaults, so a new team sets values rather than editing the loop.

**Q:** What does correct packaging require for an MCP server package?
**A:** Document each tool input and let the installing team set the scope — it installs into a new environment without code edits.

**Q:** What does correct packaging require for an eval suite?
**A:** Ship dataset and rubric together, so a new team runs them in their own context and confirms the asset still works there.

**Q:** What second job does a portable eval suite do at deployment?
**A:** It's the promotion gate — a new model version runs against a pinned baseline score before it goes live.

**Q:** Why is "ship it as a set of loose scripts" the classic wrong answer?
**A:** The scripts run, so they look reusable, but customer-specific values are buried across files — the next team copies and diverges them instead of configuring one asset.

**Q:** What must documentation cover that code cannot?
**A:** Environment assumptions, expected inputs, failure modes already handled, and the eval that defines "still working." Without them the next team treats the asset as a black box and rebuilds it.

**Q:** The three audit questions a regulated reviewer asks?
**A:** What data does it touch, what identity does it act under, what log does it leave. Bundle the audit log as part of the package or the accelerator stalls at the first security review.

**Q:** How do credentials appear in a packaged asset?
**A:** **By reference** — the parameter names the secret; it never carries the value.

**Q:** When is packaging for reuse the wrong call?
**A:** A one-off the customer will never reuse — the separation and documentation overhead isn't worth it. Ship the build and move on.

**Q:** Why package while the build is fresh?
**A:** Reconstructing intent months later costs more — by then the person who knew why a value was hardcoded has moved on.

## Contributing Back (Systems Life Cycle · Configuration Management)

**Q:** What is contributing back, in one line?
**A:** Moving an asset from private reuse to shared infrastructure through a **documented channel**, so a team that never spoke to you installs it and gets the same working setup.

**Q:** How do the three packaging outputs map onto what a maintainer needs?
**A:** **Parameters** → the asset can be configured, not rewritten · **documented assumptions** → what environment it expects · **bundled eval** → a way to confirm it still works.

**Q:** What does the contribution channel carry as a single unit?
**A:** The **version**, the **installation steps**, and the **components** — that's what makes a stranger's install land on the same working setup.

**Q:** What is the Claude Cookbook built to receive?
**A:** A **self-contained single- or multi-pattern reference implementation**, demonstrated clearly and working end to end. Not a full application.

**Q:** Where do open-source MCP servers and tools get contributed?
**A:** Each lives in **its own repository with its own contribution conventions** — follow that repo's rules, not the Cookbook's.

**Q:** What's the most common reason a contribution never gets reviewed?
**A:** **Channel mismatch** — putting a full application where a focused example belongs. The repo is set up to review one pattern, so an application-sized submission stalls.

**Q:** Name the four things that make a contribution verifiable.
**A:** (1) The code **does one thing** · (2) an **example shows it running** · (3) a **test proves it works** · (4) a **short statement names the assumptions**.

**Q:** Why does a maintainer need a test rather than a description?
**A:** A test lets them verify the result **without reproducing your reasoning**. A description leaves the verification work on them.

**Q:** What happens if the assumptions aren't stated?
**A:** The **first failure becomes the maintainer's problem** — which is the outcome that gets contributions rejected or abandoned.

**Q:** Why do licensing and attribution come *before* technical review?
**A:** They decide whether the contribution **can be accepted at all**. Skipping the gate turns the contribution into a problem the legal team must unwind later.

**Q:** Engagement code carries a licensing constraint you can't clear. What do you do?
**A:** **Do not contribute it — escalate to the owner.** This is the module's "use a different approach" case.

**Q:** What is the worked example for this lesson?
**A:** A reusable **conversation-handling pattern** from a customer service agent engagement — stripped of customer specifics and prepared as a general Cookbook example. The *pattern* is contributed, not the application.

**Q:** In the shared contribution motion, what is the Developer's specific job?
**A:** **Technical readiness** — the focused code, the example, the test, the assumptions, and the rights check. Engagement context comes from the broader team.

**Q:** What does contributing back cost, over and above packaging?
**A:** Clearing the **maintainer bar** and the **licensing gate** is real work on top of making the code run for you.

## Deployment and Versioning _(class notes 2026-07-19 — version-sensitive; verify at build time)_

**Q:** What decides the deployment platform in practice?
**A:** **Where the customer already has cloud infrastructure, identity management, and compliance agreements** — not technical merit or which platform has the newest features.

**Q:** Which environment typically receives new Claude features first?
**A:** The **first-party Claude API** (Anthropic's own environment).

**Q:** How is **Claude Platform on AWS** different from **Claude in Amazon Bedrock**?
**A:** Platform-on-AWS is accessed **through the customer's AWS account** but uses **Anthropic's model IDs and lifecycle**, with inference **Anthropic-operated outside the AWS boundary**. Bedrock keeps data **inside the customer's configured AWS boundary** and has **partner retirement dates that differ from Anthropic's**.

**Q:** What API surface does **Claude in Amazon Bedrock** use, and what's the caveat?
**A:** The **Messages API** at `/anthropic/v1/messages` with **broad feature parity** — but a **features-not-supported list exists**; confirm feature-specific requirements against the Bedrock docs.

**Q:** What distinguishes **Claude on Amazon Bedrock (legacy)**?
**A:** The older **`InvokeModel` / `Converse`** APIs with **ARN-versioned** model identifiers. Choose it only when the customer is on an existing integration that hasn't migrated to the Messages API.

**Q:** How do you pin a version on Bedrock vs. Vertex vs. legacy Bedrock?
**A:** Bedrock → full model ID with the **`anthropic.` prefix**. Vertex → full model ID in **Vertex's format, pinned before rollout**. Legacy Bedrock → **ARN-versioned identifiers**.

**Q:** Which platform answers identity and data location — your code or the platform?
**A:** **The platform.** Bedrock uses AWS identity and boundary; Vertex uses Google Cloud identity, IAM, and boundary. Both offer **regional routing** for residency.

**Q:** What are Microsoft Foundry's two hosting forms?
**A:** **Hosted on Azure** — Claude Opus 4.8, Sonnet 5, Haiku 4.5, inference end-to-end on Azure, GA. **Hosted on Anthropic** — all other Foundry Claude models, inference on Anthropic-operated infrastructure. Residency for a regulated customer depends on **which form the specific model uses**. _(As stated 2026-07-19 — confirm with Microsoft.)_

**Q:** Why is a model alias like `Opus` or `Sonnet` unsafe for production?
**A:** Aliases **evolve over time** and **may resolve to different versions across deployment platforms**. Only a pinned full model ID resolves to a **fixed snapshot**.

**Q:** State the pinning convention split.
**A:** For **Claude 4.6 and later**, the **model ID alone pins** a snapshot. For **earlier models**, the ID **plus date suffix** is required (e.g. `claude-haiku-4-5-20251001` vs. the moving `claude-haiku-4-5`). Verify at `platform.claude.com` at build time.

**Q:** Pinning the model is one of three moves. Name all three.
**A:** (1) **Pin the model version**, not the alias · (2) **version the prompt and the asset alongside the code** · (3) **keep the prior version available** so a regression can be rolled back.

**Q:** What is the cost of an unpinned deployment, in one sentence?
**A:** **Every upstream model update becomes an untracked change to your output.**

**Q:** How does a new version get promoted?
**A:** **Gate promotion on the eval suite** — send the new version to **a portion of traffic**, compare against the **pinned baseline**, and **promote or roll back on the result**.

**Q:** When is a moving alias acceptable?
**A:** For a **throwaway prototype that never touches production**. **Pinning is for what ships.**

**Q:** What does matching the platform to the customer's existing compliance agreement buy you?
**A:** It **avoids a data-residency review from scratch** — the main practical argument for platform choice.

## Comparing Platforms _(class notes 2026-07-19 — version-sensitive; verify at build time)_

**Q:** You picked a platform because it matches the customer's cloud. Why isn't that enough?
**A:** "Right for their cloud" is a **placement**, not an argument. **Procurement and security** need it measured on **latency, compliance, and cost** before they sign off.

**Q:** Name the three dimensions of a defensible cross-platform comparison.
**A:** **Latency**, **compliance**, **cost**.

**Q:** What's wrong with measuring latency from your laptop?
**A:** It **hides the round-trip penalty** that appears once the workload runs where the customer is. Measure **from the customer's actual region against their actual payload**.

**Q:** What's the latency trade-off between an in-region cloud platform and the first-party API?
**A:** The **in-region platform** shortens the round trip; the **first-party API typically gets new capabilities first**. Round-trip speed vs. **timing of feature access**.

**Q:** On Bedrock, what does the global-vs-regional endpoint choice control?
**A:** It's the **primary residency control** and can also **affect cost**. Measure from the customer's region **against both options** before committing.

**Q:** Define data residency.
**A:** A rule that the customer's data must be **processed in a specific country or region**.

**Q:** Why does compliance usually end the platform debate?
**A:** A customer already certified on one cloud is **unlikely to re-certify on another**, and certifications/audit controls differ by platform. A regulated customer treats these as **pass-or-fail**, not tradeoffs.

**Q:** A customer requires EU data residency. Which platforms are in play?
**A:** **Bedrock or Vertex AI** — the **first-party Claude API may not offer EU residency** (confirm current coverage at `platform.claude.com`). Foundry only if the **specific model is Azure-hosted**; **Anthropic-hosted Foundry models do not satisfy EU regional residency**.

**Q:** How is residency confirmed on Microsoft Foundry?
**A:** **Per model and per deployment, with Microsoft** — hosting is **per-model**, not per-platform.

**Q:** When should the compliance constraint be raised?
**A:** During **scoping**. Otherwise it surfaces at **contract review, after the work is done**.

**Q:** Per-token rates are broadly aligned across platforms. So what actually moves total cost?
**A:** **Data egress, platform fees, and integration effort.** A **lower token price can cost more in total**.

**Q:** What's the right cost metric for a platform comparison?
**A:** **Total cost per call per platform** — including egress and integration — instrumented, not quoted from a token price. Confirm **current pricing pages at scoping**.

**Q:** When should you *skip* the full three-dimension comparison?
**A:** When the customer's **compliance requirement is already pass-or-fail** — that constraint **determines the placement on its own**.

**Q:** What does the three-dimension comparison cost you?
**A:** **Real measurement work before any code ships** — instrumenting latency, compliance, and cost across platforms.

## Multi-Component Applications & Trust Boundaries (Claude Application Design)

**Q:** What is a multi-component app, in one line?
**A:** A single workflow that coordinates **more than one Claude capability** — e.g. an API request triggers a Claude Code task, which reaches a customer system through an MCP server. Each component contributes a capability the others don't have.

**Q:** Why is connecting components a security event, not just an engineering one?
**A:** **Every connection creates a place where identity, secrets, and untrusted input can cross.** Connecting components **multiplies** those places.

**Q:** What's the first move, before wiring anything together?
**A:** **Map which component does what** — then name every seam as a boundary, *then* connect.

**Q:** Define a trust boundary.
**A:** The point where **data or instructions move from one deployment environment to another**. It's where the D7 injection and access controls apply.

**Q:** A Claude Code task fetches a web page and passes the result downstream. What is the receiving component's obligation?
**A:** Treat the fetched content as **untrusted data, not instructions** — the same principle as throughout the security material.

**Q:** What's the named trap in multi-component security?
**A:** Assuming a component is **trusted because it worked correctly on its own**. Correct behavior in isolation says nothing about the seam.

**Q:** How does least privilege scale to a whole application?
**A:** Each component runs under an identity scoped to what **its role in the workflow** requires — and **the application is only as contained as its most privileged seam.** One over-scoped component is the weak point even if every other is correct.

**Q:** In the integration map, what's the boundary and control for the **first-party API** component?
**A:** Boundary: the **request entering the app from outside**. Control: **input validation** + the **identity the call runs under**.

**Q:** …for the **Claude Code task**?
**A:** Boundary: the **content it fetched**, untrusted downstream. Control: **treat fetched content as data** at the next seam.

**Q:** …for the **MCP server**?
**A:** Boundary: the **system access it holds** on the app's behalf. Control: **scope it to least privilege and log the access**.

**Q:** What does a regulated review require of a multi-component app?
**A:** Justifying **audit logging, data-residency decisions, and permission controls across the full application** — not component by component.

**Q:** Which platforms typically satisfy regional residency for a multi-component app, and what must you still confirm?
**A:** **Bedrock and Vertex AI**. Confirm **ZDR and HIPAA BAA eligibility for each component** against the **Anthropic Trust Center** and **platform.claude.com** before scoping. _(Verified 2026-07-19.)_

**Q:** What does this discipline cost?
**A:** Mapping seams, enforcing a control at each, and **logging boundary crossings** — design and audit work added to **every** integration.

**Q:** A seam can't be secured. What's the correct move?
**A:** **Do not ship around it — escalate to a human owner.**
