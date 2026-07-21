# Structured Outputs — Worked Examples (Domain 2)

Companion to `notes.md` → *Claude Application Design → Schema design*. Ties to **Claude API Mechanics (6.8%)** and **Claude Application Design (8.6%)**. Syntax verified against platform.claude.com/docs **2026-07-18**.

## The one-line idea
Instead of *asking* for a shape in the prompt (a request the model can slip on), you hand the API a **JSON schema** and the model is **constrained at generation time** — this is *constrained decoding*: each token is only allowed if it keeps the output valid against the schema. A schema-violating response can't be produced in the first place.

## Two mechanisms — constrain different halves of the exchange

| Mechanism | Parameter | Constrains | Reach for it when |
|---|---|---|---|
| **JSON outputs** | `output_config.format` (`type: "json_schema"`) | Claude's **final response text** | The model itself produces the structured payload your code consumes (extract fields, classify, format an API response) |
| **Strict tool use** | `strict: true` on a tool definition | The **arguments Claude passes to your tools** | A malformed tool argument would crash the function or trigger a wrong action in an agentic loop |

Use either alone or **both in the same request**. (GA as of the 2025-11 release — the old beta used `output_format` + header `structured-outputs-2025-11-13`; both still work during the transition but `output_config.format` is current.)

---

## Example 1 — JSON outputs: extract fields from a support ticket

The classic "the model produces the structured payload" case. No parse-and-retry code around the call.

```python
from anthropic import Anthropic

client = Anthropic()

ticket = (
    "Subject: Can't log in after the update\n"
    "From: dana@acme.co\n"
    "Body: Since the Tuesday release I get a 500 on every login attempt. "
    "This is blocking our whole team — need this fixed today."
)

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extract the ticket fields:\n{ticket}"}],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string"},
                    "category": {
                        "type": "string",
                        "enum": ["auth", "billing", "bug", "feature_request", "other"],
                    },
                    "severity": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "summary": {"type": "string"},
                },
                "required": ["customer_email", "category", "severity", "summary"],
                "additionalProperties": False,
            },
        }
    },
)

# Guaranteed valid JSON in the response text — no JSON.parse() guard needed for schema validity.
import json
data = json.loads(response.content[0].text)
```

Same call, **Pydantic helper** (Python SDK's `messages.parse()` — schema derived from the model, response validated for you):

```python
from pydantic import BaseModel
from typing import Literal

class Ticket(BaseModel):
    customer_email: str
    category: Literal["auth", "billing", "bug", "feature_request", "other"]
    severity: Literal["low", "medium", "high", "urgent"]
    summary: str

response = client.messages.parse(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extract the ticket fields:\n{ticket}"}],
    output_format=Ticket,   # convenience alias; SDK translates to output_config.format
)
ticket_obj = response.parsed_output   # already a typed Ticket instance
```

**Contrast (what this replaces):** a prompt that says *"Respond with only JSON: {...}"* holds on the cases you tested and slips on an edge case (a stray sentence, a wrong field name, a trailing comma) — exactly the failure mode structured outputs removes.

---

## Example 2 — Strict tool use: guard tool arguments in an agentic loop

Here the risk isn't the final message — it's Claude handing your function a bad argument. `strict: true` validates the arguments against `input_schema` before your code runs.

```python
tools = [
    {
        "name": "issue_refund",
        "description": "Refund a charge to the customer's original payment method.",
        "strict": True,                      # <-- constrains the arguments Claude sends
        "input_schema": {
            "type": "object",
            "properties": {
                "charge_id": {"type": "string"},
                "amount_cents": {"type": "integer"},   # never a string like "12.50"
                "reason": {"type": "string", "enum": ["duplicate", "fraud", "requested_by_customer"]},
            },
            "required": ["charge_id", "amount_cents", "reason"],
            "additionalProperties": False,
        },
    }
]

response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Refund charge ch_991 — customer was double-billed."}],
)

# When response.stop_reason == "tool_use", the tool_use block's input is guaranteed to match
# the schema: amount_cents is an int, reason is one of the three enums. Your handler can trust
# the contract instead of defensively coercing/validating every field.
```

Why it matters: without the constraint, `amount_cents: "twelve fifty"` or `reason: "chargeback"` (not in the enum) would reach your function and either crash it or trigger the wrong action. The guarantee is *type-safe, in-contract* arguments.

---

## Example 3 — Both together (agentic workflow)

JSON outputs and strict tool use solve **different** problems, so they compose: reliable tool calls *and* a structured final answer.

```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Plan a trip to Paris departing 2026-05-15."}],
    # Strict tool use: guaranteed-valid tool parameters
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["destination", "date"],
                "additionalProperties": False,
            },
        }
    ],
    # JSON outputs: structured shape for Claude's final response
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "next_steps"],
                "additionalProperties": False,
            },
        }
    },
)
```

Note: the grammar applies **only to Claude's direct output**. It resets between sections — tool-call arguments (governed separately by `strict`), tool results, and thinking blocks are *not* forced into the response schema, so Claude can still think freely and call tools, then emit the structured final answer.

---

## A guaranteed schema is NOT a guaranteed success — still check `stop_reason`

Two outcomes return output that won't match your schema. Production code checks `stop_reason` rather than assuming every response parses.

```python
def parse_structured(response):
    if response.stop_reason == "refusal":
        # Model declined for safety reasons. 200 status, you're billed for tokens,
        # and the refusal text takes precedence over the schema.
        raise RefusalError("Model refused the request.")

    if response.stop_reason == "max_tokens":
        # Cut off mid-structure — the JSON is incomplete. Retry with a higher max_tokens.
        raise TruncatedError("Hit max_tokens before completing the structure.")

    return json.loads(response.content[0].text)   # safe: end_turn with a complete object
```

| `stop_reason` | What happened | What to do |
|---|---|---|
| `end_turn` | Complete, schema-valid output | Parse it |
| `refusal` | Safety refusal; text overrides schema | Handle as a refusal (don't parse) |
| `max_tokens` | Truncated mid-structure | Raise `max_tokens` and retry |

(One more non-error surprise: **enum casing isn't guaranteed** — Claude may return `"High"` for an enum value `"high"`. Compare enum values case-insensitively, and never define two enum values that differ only in capitalization.)

---

## The costs — why you don't turn it on everywhere by default

| Cost | Detail | Practical implication |
|---|---|---|
| **First-request latency** | The schema compiles into a grammar before it can constrain output | Stable schema + steady traffic pays it **once** (grammar cached **24 h** from last use); a workload that churns schemas pays it repeatedly |
| **Higher input tokens** | The API injects a system prompt describing the expected format, billed like any input | Small per call; matters when estimating cost **at volume** |
| **Cache invalidation** | Changing the **schema structure** or the **set of tools** invalidates the grammar cache; changing only `name`/`description` does not | Keep schemas stable; editing `output_config.format` also busts the conversation's prompt cache |
| **Complexity limits** | Max **20** strict tools · **24** optional params · **16** union-type (`anyOf` / `["string","null"]`) params across all strict schemas in a request | Mark only critical tools `strict`; make params `required`; flatten nesting; split across requests |

---

## Incompatibilities (exam bait)

- **Message prefilling** — cannot combine with **JSON outputs**. A pattern that starts the assistant's message and a pattern that constrains the whole response to a schema can't run on the same request. Pick one.
- **Citations** — incompatible with `output_config.format` (returns **400**); citation blocks must interleave with text, which conflicts with a strict JSON shape.
- **Works fine with**: batch processing (still 50% off), streaming, and token counting.
- **PHI / HIPAA**: the schema is cached separately and *not* covered by the same protections as prompts/responses — keep PHI out of property names, enum/const values, and regex; PHI belongs only in message content.

---

## Exam traps to remember
1. **Prompt instruction ≠ schema constraint.** "Respond only in JSON" is a request the model can slip on; `output_config.format` is enforced per-token. The exam rewards the API-level guarantee for production, not better prompt wording.
2. **`output_config.format` constrains the response; `strict: true` constrains tool inputs.** Don't swap them — a scenario about *a tool argument crashing your function* wants `strict`, not JSON outputs.
3. **Schema-valid ≠ always succeeds.** `refusal` and `max_tokens` still return non-conforming output — checking `stop_reason` is the right answer, not "structured outputs guarantee a parse."
4. **First call is the slow one** (grammar compile); cached 24 h. "Structured outputs are always slower" is false — steady traffic pays once.
5. **Prefilling + JSON outputs are mutually exclusive.** A distractor pairing them is wrong.
6. Structured outputs **add** input tokens (injected format prompt) — they don't reduce token cost.
