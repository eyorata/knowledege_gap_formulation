# Why Your Two Cost Numbers Differ — Prefix Caching and the FDE Rate Card

**Day 1 explainer · Topic: Inference-time mechanics · Asked by: [partner] · Explainer by: Eyoel Nebiyu**

---

## The question, anchored

You asked why your `cost_pareto` block reports `$0.0029` and `$0.0047` per call for two judge configurations on the same eval, why latency looks flat across them, and what gets recomputed each call versus what an inference cache reuses. For an API-served setup the answer is dominated by **one** mechanism: server-side **prefix caching**. KV-cache mechanics, prefill-vs-decode billing, and token-level billing all sit downstream of it. This explainer narrows hard to prefix caching and shows you how to derive your two numbers from first principles. The skipped sub-mechanisms are listed at the bottom as v0.2 follow-ups.

## The load-bearing mechanism

When you call a hosted LLM API with a system prompt that's identical across many calls, the provider doesn't reprocess those tokens from scratch every time. They store the prefix's KV-cache server-side under a hash of the prompt prefix; on the next call with the same prefix they read it back instead of recomputing it. Anthropic's contract is the most explicit and the cleanest to teach against:

- **TTL:** 5 minutes from last hit. The cache is refreshed each time it's read, so back-to-back evaluation runs keep it warm.
- **Minimum prefix:** 1024 tokens. Smaller prefixes are not cached at all — there is no partial discount, no proportional benefit; below the threshold you pay the full rate.
- **Three rates apply per call:**
  - **Cache write** (first time the prefix is seen): ~1.25× the normal prompt-token rate.
  - **Cache read** (every subsequent hit within the TTL): ~0.10× the normal rate — a 90% discount.
  - **Completion** (the new tokens you're generating): unchanged from the rate card.
- **Prefix matching is left-to-right exact.** Change one character of your system prompt and you invalidate the cache; you pay the cache-write rate again on the next call.

OpenAI and Google offer similar mechanisms with different parameters. The teaching point generalizes: **once your system prompt is stable and above the minimum length, cache reads become the dominant pricing event, not writes or completions.**

## Showing the math

Setup, using illustrative Anthropic-Sonnet-class rates:

- System prompt (rubric + examples): **1500 tokens** (above the 1024 minimum).
- Per-task: **200 prompt tokens** (scenario + candidate) + **100 completion tokens**.
- Rate card: **$3.00 per 1M prompt tokens**, **$15.00 per 1M completion tokens**.

**Configuration A — system prompt stable across 12 evaluations:**

```
Call 1 (cache write):
  prompt cost = 1500 * $3 * 1.25 / 1M  = $0.005625
  user cost   =  200 * $3        / 1M  = $0.000600
  output cost =  100 * $15       / 1M  = $0.001500
  total       = $0.007725
Calls 2–12 (cache read):
  prompt cost = 1500 * $3 * 0.10 / 1M  = $0.000450
  user cost   =  200 * $3        / 1M  = $0.000600
  output cost =  100 * $15       / 1M  = $0.001500
  total       = $0.002550
Mean per call = (0.007725 + 11 * 0.002550) / 12 ≈ $0.002995 ≈ $0.0030
```

**Configuration B — system prompt drifts per call (or is below the 1024 threshold):**

```
Every call is a cache miss/write equivalent:
  prompt cost = 1500 * $3        / 1M  = $0.004500
  user cost   =  200 * $3        / 1M  = $0.000600
  output cost =  100 * $15       / 1M  = $0.001500
  total per call = $0.006600
```

So Configuration A's `$0.0029` is what 11 cache reads + 1 cache write averages to. Configuration B's `$0.0047` is most consistent with a **partial-caching regime**: maybe 60% of calls hit the cache and 40% miss, or one of two judge variants has a stable prompt and the other has per-task templating. The two numbers aren't measuring different inference compute. They're measuring different **cache-hit ratios on the same compute.**

That's the diagnostic answer. To defend the cost claim in your model card, you need three numbers per arm: the cache-hit rate, the system-prompt token count, and the rate card. Drop those three into the calculation above and the per-task cost falls out.

## Why latency looks flat

Cache reads cut **prompt-processing time** by ~90%, but total API latency is dominated by decode (≈ completion-token-count × 30–50 ms/token) and network RTT, not prefill. For a 1500/200/100 split: prefill ≈ 1.7 s uncached → 0.27 s cached, decode ≈ 3.5 s, network ≈ 0.2 s. Total ~5.4 s uncached → ~4.0 s cached — a 25 % wall-time saving that doesn't show up in p95 latency because decode-time variance across 12 evaluations is usually larger than the prefill delta. Latency looks flat because you're measuring the wrong axis; per-call **prompt-processing time** would expose the effect.

## Two adjacent concepts (one paragraph each)

**KV cache vs prefix cache — same data structure, different scope.** The KV cache is the *intra-call* mechanism that makes transformer decode O(n) instead of O(n²): for each new token you generate, you reuse the keys and values already computed for the prior tokens within the same forward pass. Every API call uses a KV cache. Prefix caching is the *inter-call* mechanism: the provider persists the KV cache for a stable prompt prefix between your separate calls, hashed and stored server-side. Easy to conflate; they're the same idea applied at two different time scales.

**Why prompt tokens are usually 5–10× cheaper than completion tokens.** Prefill (processing the prompt) is parallel — the GPU computes attention for all prompt tokens at once, fully utilizing the matrix-multiply hardware. Decode is sequential — one token at a time, with the GPU's matmul units mostly idle while waiting for the previous token. The rate card reflects compute cost. The cache-read discount applies to prefill only; your completion rate is unchanged regardless of cache state.

## What I deliberately skipped (the v0.2 list)

This explainer does **not** cover: vLLM's `--enable-prefix-caching` and PagedAttention internals (the self-hosted analogue — Kwon et al. 2023 is the canonical paper); tokenizer billing nuance (BPE merges shifting per-call token counts in non-obvious ways); continuous batching and how the server packs your call into a batch with other tenants; or KV-cache memory-pressure failures on very long context. Each is a separate explainer that I'd write next; the partner has the v0.2 list to vote on.

## Pointers

- **Anthropic, *Prompt caching* documentation** — the contract: TTL, minimum prefix, three rates, exact-prefix matching. https://docs.claude.com/en/docs/build-with-claude/prompt-caching
- **Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention*, SOSP 2023** — the self-hosted analogue. Section 3 (the paged KV-cache structure) is the load-bearing read.
- **OpenAI prompt-cache release notes (Oct 2024)** — the OpenAI version of the same contract with different parameters.

---

*If your judge is self-hosted on vLLM rather than served via API, the same principle applies but the implementation is `--enable-prefix-caching` and the cost arithmetic is GPU-hour-based rather than per-token. That's the v0.2 follow-up if you tell me which deployment you're on.*
