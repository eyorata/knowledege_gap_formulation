# Grounding Commit

## Purpose
This note records exactly what I fixed in my prior blog draft after closing the inference-time mechanics gap.

## File updated
- `docs/blog_post.md`

## Old claim (too weak)
I reported cost and latency deltas as outcomes only, without mechanism-level grounding.

## New grounded claim
I now explain the cost/latency result using:
- prefill vs decode token work,
- API-served observability limits,
- cache-reuse assumptions stated as assumptions (not direct measurements).

## Concrete edits made
1. In **The Honest Result** section, replaced generic sentence:
   - from: "cost increased from $0.0029 to $0.0047 per task"
   - to: "cost increased primarily due to additional judge-token workload (prefill/decode), while near-flat p50 latency can be explained by network overhead and stable short decode behavior in this API-measured setup."
2. Added one explicit qualifier:
   - "Internal KV cache hit rates are not directly observable in this API-served ablation path."
3. Added one traceable numeric bridge:
   - `delta/task = $0.0018`, `n_tasks = 67`, total delta approx `$0.1206`.

## Why this improves artifact quality
- Converts a descriptive metric claim into a mechanism-aware claim.
- Separates what is measured from what is inferred.
- Makes the blog defensible under technical pushback from senior engineers.

## Date
2026-05-04
