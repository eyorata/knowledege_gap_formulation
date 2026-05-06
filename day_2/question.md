# question.md - Day 2

**Topic (today):** Agent and tool-use internals  
**Asker:** Eyoel Nebiyu (`@eyorata`)  
**Partner (explainer):** *[fill in once paired]*  
**Date:** 2026-05-06

---

## The question

> In `conversion_engine`, the same booking workflow can run with two tool backends (HubSpot REST vs HubSpot MCP), and the orchestrator still has to decide tool order, retries, and fallback behavior under partial failure. Exactly where in the agent execution path should we place the "commit point" that makes side effects idempotent (contact upsert, note write, and booking linkage) so the agent can safely retry tool calls without duplicate writes, and how should that commit-point design change between REST mode and MCP mode?

---

## Why this matters in my work (grounding)

This is grounded in current workspace artifacts:

1. `conversion_engine/README.md` documents dual backend operation (`HUBSPOT_MODE=REST|MCP`) and notes that MCP mode is wired but environment-dependent.
2. `conversion_engine/STATUS.md` shows production-facing HubSpot write behavior (contact upsert + note + lifecycle webhook handling), where duplicate or out-of-order writes are costly.
3. `conversion_engine/WEEK11_PROMPT.md` and `conversion_engine/agent/` define the agent-orchestrator boundary where tool selection, sequencing, and retry policy belong.

The practical risk is not abstract: when retries happen after network/tool errors, we can accidentally perform duplicate side effects if the agent has no explicit commit-point model.

---

## What a satisfying answer looks like

A satisfying explainer should do three things:

1. Name the load-bearing mechanism in plain language: **"commit point + idempotency key placement"** for tool-using agents.
2. Trace one concrete flow end-to-end (booking -> contact upsert -> note append) and show how retries behave before vs after commit-point refactor.
3. Provide an implementation rule I can apply immediately in this repo, including where to persist operation IDs and how fallback differs between REST and MCP tool paths.

---

## Scope: in / out

**In scope:**
- Orchestrator-level decision boundary for tool retries and side effects.
- Idempotency keys, dedupe windows, and operation state transitions.
- Differences between direct REST client semantics and MCP-tool invocation semantics.
- One concrete, runnable or inspectable example from `conversion_engine/agent/`.

**Out of scope:**
- General "what is an agent" overviews.
- Prompt-writing tips unrelated to tool side effects.
- Vendor-agnostic theory that cannot be mapped back to this codebase.

---

## Named Week 10/11 connection

This question connects to Week 11 portfolio behavior where I had to defend reliability claims under real workflow execution, not just scoring quality. The key artifact bridge is the `conversion_engine` orchestrator/tooling path (documented in `README.md`, `STATUS.md`, and `WEEK11_PROMPT.md`) where retry-safe tool use determines whether the system is production-defensible.