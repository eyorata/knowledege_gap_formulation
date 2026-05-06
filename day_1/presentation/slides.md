<!--
Marp-compatible deck. Render in VS Code with the Marp extension installed.
Export to PPTX/PDF: `marp slides.md --pptx` or `marp slides.md --pdf`.
Each `---` is a slide break. HTML comments are speaker notes (visible in
Marp presenter mode but not on the slide itself).

Time budget: 6-7 minutes total. ~14 slides @ ~28s avg. Linger on slides 5,
6, 7, 11. Move quickly through 1, 2, 13, 14.
-->

---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Day 1 Presentation · Asker: Eyoel Nebiyu · Topic: Commit Points & Idempotency'
footer: '10Academy TRP1 Week 12 · 2026-05-07'
style: |
  section { font-size: 22px; padding: 50px 60px; }
  h1 { color: #0d1b2a; font-size: 42px; }
  h2 { color: #1b3a57; font-size: 32px; }
  code { background: #f4f7fa; padding: 2px 6px; border-radius: 3px; }
  pre { background: #0d1b2a; color: #f4f7fa; padding: 16px; border-radius: 6px; font-size: 16px; }
  table { font-size: 19px; }
  blockquote { border-left: 4px solid #1b3a57; padding-left: 16px; color: #444; }
---

<!-- _class: lead -->
<!-- _paginate: false -->

# When "Just Retry" Is the Most Expensive Bug You Haven't Found Yet

### Commit points, idempotency, and retry-safe side effects in agent-orchestrated workflows

**Eyoel Nebiyu** · 10Academy TRP1 · Day 1 Asker Presentation
2026-05-07

<!--
Speaker note: 15s. Title slide. State the topic, name myself, and tee up
the three-part structure: my gap, my partner's explainer, what I changed.
Don't read the slide aloud — start straight into the gap.
-->

---

## What I'm presenting (3 parts, 6 minutes)

1. **The gap I named.** What I'd shipped and couldn't defend.
2. **What my partner's explainer revealed.** The mechanism I was missing.
3. **What I changed in `conversion_engine`.** One concrete edit, with the diff.

The point of this format: the trajectory from *not knowing I didn't know* to *editing real code* is what makes Week 12 cumulative.

<!--
Speaker note: 20s. Frame the talk explicitly — three sections, signpost
the structure. This is per the cohort presentation format spec.
-->

---

## The gap, stated honestly

In Week 10 I shipped `conversion_engine` with a HubSpot booking workflow that runs across **two backends**: HubSpot REST and HubSpot MCP.

Three side-effecting operations chain together:

- contact upsert (by email)
- note write (free-text on the contact)
- booking linkage (meeting ↔ contact association)

I knew the workflow worked on the happy path. **I could not defend, if pressed, what would happen on a network timeout halfway through.** Specifically: would a retry create a duplicate note? Did my code attach idempotency keys? Did the answer change between REST and MCP modes?

I was using the word *retry* and *idempotent* without a mechanism behind them.

<!--
Speaker note: 35s. The honest gap. Don't pad — the brief explicitly grades
"naming what you did not know" as part of asker quality. Be direct: "I
shipped code I couldn't defend." Pause for one beat after that line.
-->

---

## The question I committed to

> *"In `conversion_engine`, the same booking workflow runs with two tool backends (HubSpot REST vs HubSpot MCP). The orchestrator decides tool order, retries, and fallback under partial failure. **Where in the agent execution path should we place the 'commit point' that makes side effects idempotent (contact upsert, note write, booking linkage) so the agent can safely retry without duplicate writes — and how should that commit-point design change between REST mode and MCP mode?"***

**Diagnostic** ✓  · names a specific design decision (where the commit point sits)
**Grounded** ✓  · cites real files: `agent/orchestrator.py`, `agent/hubspot_client.py`
**Generalizable** ✓  · every FDE building agents with side-effecting tools hits this
**Resolvable** ✓  · 800-word answer + diff in `conversion_engine`

<!--
Speaker note: 30s. Read the question aloud once, slowly. Then check off
the four properties. This is the asker-quality moment per the rubric.
Don't dwell on the meta-rubric explanation — the four ticks are visible.
-->

---

## What I expected vs what landed

I expected a tutorial on retry decorators. What I actually got reframed
the question:

> *"Your commit point is not the API call. It's the local write that records
> the API call succeeded. Everything before that write is tentative.
> Everything after it is durable."*

That sentence is the load-bearing reframe. It moves the responsibility
**out of HubSpot's API contract** and **into my orchestrator's state store**.

<!--
Speaker note: 30s. This is the central insight slide — let the quote
breathe. Pause after reading it. The audience needs the mental shift
before any of the rest lands.
-->

---

## The three concepts that locked in

| Concept | Definition (short) | In my code |
|---|---|---|
| **Commit point** | The moment a side effect is durably recorded locally | The DB write that stores `{op_id, status: COMMITTED, result}` |
| **Idempotency key** | Deterministic token making the same call replay-safe | `{booking_id}:{op_type}:{payload_hash}` |
| **Retry-safe side effect** | Operation whose end state is identical regardless of retry count | The orchestrator skips committed ops + the API honors the key |

These three click together: the *key* makes the API replay-safe; the
*commit point* makes the orchestrator skip already-done work; together
they make the *side effect* retry-safe.

<!--
Speaker note: 35s. Walk left-to-right. Don't define each twice — the
slide says it. Emphasize the *together* line — that's what I missed
before the explainer.
-->

---

## The ambiguous-timeout problem (why this is real, not theoretical)

```
Client:  POST /contacts          → ⏱  TIMEOUT (no response received)
Server:  ✓ Created {id: "hs_001"}  (client never saw this)
```

**Without an idempotency key:**
client retries → second POST → **second contact created** → duplicate.
Sales rep sees two "Maya Chen" rows in HubSpot. Brand-trust event.

**With an idempotency key:**
client retries with the same key → server replies *"already processed"* → returns the original `hs_001` → no duplicate.

**This is the bug my previous code had.** I was lucky it hadn't fired.

<!--
Speaker note: 40s. This is the load-bearing slide for "what could go
wrong in production." Linger here. Pause after "I was lucky it hadn't
fired" — that's the moment the audience understands why the gap was
real.
-->

---

## The three operations have three different idempotency contracts

| Operation | Naturally idempotent? | What it needs |
|---|---|---|
| **Contact upsert** (by email) | ✓ Yes | HubSpot's `/upsert` endpoint dedups by email automatically |
| **Note write** | ✗ No | Every POST creates a new record. Need an `Idempotency-Key` header AND server support |
| **Booking linkage** | ✓ Yes | Association graph is idempotent by `(contact_id, booking_id)` pair |

I had assumed "all three are similar." They are not. **The note is the load-bearing risk.** A retry without a key creates a duplicate note silently — no error, no warning, just a second note attached to the contact.

<!--
Speaker note: 30s. Operation-by-operation specificity. The "I had
assumed they were similar" admission is honest and the rubric rewards it.
The note row is the punchline; emphasize it.
-->

---

## REST vs MCP — the responsibility split

| Concern | REST mode | MCP mode |
|---|---|---|
| Generate idempotency key | Orchestrator | Orchestrator |
| Attach key to API call | HTTP header (`Idempotency-Key`) | Tool argument → MCP server → HTTP |
| Track operation state | Orchestrator (state store) | Orchestrator (state store) |
| Retry on failure | Orchestrator | Orchestrator (tools are stateless) |
| Local dedup cache | Optional | **Often necessary** |

**The shift:** in REST, idempotency lives at the *HTTP layer* — I attach a header. In MCP, I lose direct HTTP control, so idempotency has to move *up* into a workflow-step dedup table. Same logical guarantee, different layer.

<!--
Speaker note: 35s. The headline answer to my question. The "shift" line is
the takeaway — they should remember "REST = HTTP layer; MCP = workflow
layer." Don't read the table line-by-line; let it breathe and narrate.
-->

---

## The state machine I added to my orchestrator

```
[PENDING] ─attempt──→ [IN_FLIGHT] ─success──→ [COMMITTED] ──── done
                            │                       ▲
                            ├─timeout/5xx───────────┘  retry path:
                            │                          same op_id +
                            └─4xx/auth fail─→ [FAILED]  same key
```

Every side-effecting operation gets one record. The orchestrator reads it
**before** acting:

- `COMMITTED`? → skip the call, return the cached result.
- `IN_FLIGHT`? → retry with the same idempotency key (server dedups).
- `PENDING` / `FAILED`? → execute fresh.

This is the explicit version of what *durable execution* engines (Temporal,
Step Functions) do implicitly. I'm not running Temporal; I built the
1% version that fits my repo.

<!--
Speaker note: 40s. Diagram-driven slide; let the audience read for a beat.
The "1% version of Temporal" framing matters — it answers "why didn't
you just use a real durable-execution engine" before someone asks.
-->

---

## What I actually changed in `conversion_engine`

**File:** `agent/hubspot_client.py` — added idempotency-key generation + header attachment to every POST.

```diff
+ def _idempotency_key(booking_id: str, op_type: str, payload: dict) -> str:
+     content = json.dumps({"booking_id": booking_id,
+                           "op_type": op_type,
+                           "payload": payload}, sort_keys=True)
+     return f"{booking_id}:{op_type}:{hashlib.sha256(content.encode()).hexdigest()[:8]}"

  def upsert_contact(self, email: str, properties: dict, *,
-                    booking_id: str) -> dict:
+                    booking_id: str) -> dict:
+     key = _idempotency_key(booking_id, "contact_upsert",
+                            {"email": email, "properties": properties})
      return self._call(
          "POST", "/crm/v3/objects/contacts/upsert",
          {"properties": {"email": email, **properties}},
+         headers={"Idempotency-Key": key},
      )
```

Plus a new `agent/state_store.py` with the operation-record schema and the orchestrator pre-flight check.

<!--
Speaker note: 35s. The grounding-commit moment per the brief. Real diff
in real file. Don't read the code — point at the new line (`headers=
{"Idempotency-Key": key}`) and say "this is the line that wasn't there
before, and that line is what I now understand."
-->

---

## What I didn't expect to learn

The MCP-mode answer was the surprise.

I had assumed switching from REST → MCP was a *transparent* swap — same
behavior, different transport. **It isn't.** MCP hides the HTTP layer,
which is exactly the layer where REST's idempotency-key header lives.
So when I move to MCP, my idempotency strategy doesn't follow — it has
to be **re-implemented at the workflow-step layer**.

If I deploy MCP without the workflow-step dedup cache, I lose
retry-safety silently. The bug doesn't show up in dev (dev rarely times
out); it shows up in production at scale.

<!--
Speaker note: 25s. The "didn't expect to learn" part is required by the
asker-presentation format. Be specific — name the misconception ("I
thought MCP swap was transparent") and what corrected it.
-->

---

## What's still open (the honest unresolved)

The explainer didn't fully land **compensation logic**. If contact upsert
and note write both succeed, but booking linkage fails permanently
(not a transient retry, a 4xx), should I:

(a) Roll back the note? HubSpot has no transaction boundary across these objects.
(b) Leave the inconsistent state and route to a human?
(c) Auto-compensate via DELETE calls (the saga pattern)?

The explainer covered the saga *pattern*; my code doesn't implement it
yet. **Day-2 candidate gap:** how do I decide between (a)/(b)/(c) for
*this specific* workflow's failure semantics, given that "rollback" of
a note that the prospect may have already seen is itself a side effect?

<!--
Speaker note: 25s. The honest unresolved is required and signals
calibration. The Day-2 candidate gap line tees up tomorrow's question
naturally — "I already know what to ask my next partner."
-->

---

<!-- _class: lead -->
<!-- _paginate: false -->

## Recap & pointers

**The reframe:** commit point ≠ API call. It's the local write that records the API call succeeded.

**The shift across backends:** REST puts idempotency at the HTTP header; MCP forces it up to the workflow-step layer.

**The change in my code:** `agent/hubspot_client.py` now attaches `Idempotency-Key` headers on every POST; `agent/state_store.py` tracks operation records so the orchestrator skips committed steps.

**Sources:** Garcia-Molina & Salem 1987 (the saga paper); HubSpot Idempotency-Key API docs; MCP spec on tool semantics.

**Thanks to my partner — Day 1 explainer landed.**

<!--
Speaker note: 30s. Closing slide. Read the three takeaways crisply (you
have ~30 seconds left in your 6:30 budget). Thank the partner by name in
the actual delivery (not on slide — that goes in the morning_call_summary).
-->
