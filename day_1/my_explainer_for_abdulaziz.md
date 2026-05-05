# Why `$0.0029` and `$0.0047` Can Both Be Right: Prefix Caching for API-Served LLM Judges

*By Eyoel Nebiyu*

## The question I was asked

Abdulaziz asked a practical evaluation question: in the same benchmark, why do two judge configurations produce different per-task costs (`$0.0029` vs `$0.0047`) while latency looks nearly flat? He needed a mechanism-level explanation he could defend in a model card or memo, not just "the numbers differ."

The short answer is: **prefix-cache state**, not model capability, is the load-bearing mechanism.

## The mechanism in plain language

In hosted LLM APIs, repeated calls often share a large fixed prefix (system prompt, rubric, instructions). Providers can cache that prefix so they do not recompute it from scratch each time.

That creates different billing states:

1. **Cache write**: first call with a new prefix (more expensive than a read).
2. **Cache read**: repeated call with the same prefix (discounted prompt-side cost).
3. **Completion tokens**: generated output (usually unchanged by prefix cache state).

So two eval runs can use the same model and same task set, but if one run has a stable prefix and the other has prompt drift, their effective cost per call diverges.

This is exactly the kind of hidden mechanism that creates cost deltas without obvious quality deltas.

## Why this maps to `$0.0029` vs `$0.0047`

Use a simple stylized setup:

- System prompt: 1500 tokens (large enough to be cache-relevant)
- Per task user tokens: 200
- Per task completion tokens: 100
- Prompt and completion rates fixed by provider rate card

If the prefix is stable across 12 calls:

- Call 1 pays cache-write behavior
- Calls 2–12 mostly pay cache-read behavior
- Mean cost drops toward the lower number (about `$0.003` range)

If prefix stability is partial (some misses from prompt variation, template drift, or multiple judge variants), average cost rises into a middle regime (around `$0.0047`).

If every call is effectively a miss, cost trends higher still.

So the two observed numbers are consistent with **different cache-hit ratios** across configurations, not contradictory accounting.

## Why latency can still look flat

A common expectation is: if caching reduces prompt-side compute, latency should clearly drop. Sometimes it does. But in many API eval paths, end-to-end latency also includes:

- decode-time variance,
- network RTT,
- provider-side batching/scheduling effects.

When those dominate p50/p95 behavior, cache gains on prompt processing may not appear as dramatic wall-clock separation, especially on small samples.

So it is defensible to say:

- cost changed due to cache-state differences,
- latency looked near-flat because wall-clock latency is multi-component and noisy.

That is not hand-waving if you clearly separate observed metrics from inferred internals.

## The distinction Abdulaziz needed

The most important conceptual cleanup was this:

- **KV cache (intra-call):** reuse inside a single generation pass.
- **Prefix cache (inter-call):** reuse across separate API calls.

People often mix them together as "cache." For cost explanation in API-served evals, inter-call prefix reuse is usually the key driver.

That naming clarity matters in peer review because otherwise the explanation sounds technically correct but operationally unfalsifiable.

## What should be claimed (and what should not)

### Defensible claim

> The per-task cost gap is primarily explained by different prefix-cache hit behavior under the same judge workload; some latency metrics can remain near-flat because decode/network components dominate observed wall-clock variance.

### Overclaim to avoid

> We directly measured internal provider KV hit-rate events from the API logs.

In most hosted setups, that internal event stream is not directly exposed. The safer framing is "inferred from token/rate behavior" unless explicit cache telemetry is available.

## Minimal reproducible demonstration

I also provided a runnable arithmetic demo (`day_1/scripts/cache_cost_demo.py`) to make this explanation testable:

- stable-prefix regime reproduces lower mean cost,
- partial-hit regime lands near the middle value,
- miss-heavy regime reproduces upper-cost behavior.

This matters because a mechanism explanation is stronger when another engineer can run it and see the same pattern.

## What changed after this explainer

Before this, Abdulaziz could report the cost numbers but not defend the mechanism. After the explainer, he could:

- name prefix caching as the load-bearing cause,
- distinguish measured facts from inferred internals,
- and write a cleaner, more defensible cost interpretation in downstream artifacts.

That is the real objective of a Week 12 explainer: not just technical correctness, but better grounded communication in portfolio-quality artifacts.

## Sources

1. Anthropic Prompt Caching Documentation: https://docs.claude.com/en/docs/build-with-claude/prompt-caching
2. Kwon et al. (2023), *Efficient Memory Management for Large Language Model Serving with PagedAttention* (SOSP): https://arxiv.org/abs/2309.06180

These two sources are load-bearing: one defines the production API contract, the other grounds the serving mechanism.