"""Per-call cost arithmetic for an API-served LLM judge with prefix caching.

Runs the worked example from day_1/explainer.md to make the prefix-caching
mechanism visible: derives the partner's $0.0029 vs $0.0047 cost gap from
first principles, given the Anthropic-Sonnet-class rate card and a
1500/200/100 prompt/user/completion split across 12 evaluations.

Usage:
    python scripts/cache_cost_demo.py
    python scripts/cache_cost_demo.py --prompt-tokens 800   # below cache minimum
    python scripts/cache_cost_demo.py --hit-rate 0.5        # partial caching

Anthropic's prompt-cache contract used here:
    - 1024-token minimum prefix; below this, no cache
    - 5-minute TTL refreshed on each read
    - cache write rate = 1.25x normal prompt rate
    - cache read rate  = 0.10x normal prompt rate
    - completion rate  = unchanged

Source for the contract:
    https://docs.claude.com/en/docs/build-with-claude/prompt-caching
"""
from __future__ import annotations

import argparse
import sys

# Force UTF-8 output so unicode arrows render on Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


# Illustrative Anthropic-Sonnet-class rate card (USD per 1M tokens).
PROMPT_RATE = 3.00      # normal prompt-token rate
COMPLETION_RATE = 15.00 # completion-token rate

# Prompt-cache contract parameters.
CACHE_MIN_PREFIX_TOKENS = 1024
CACHE_WRITE_MULT = 1.25
CACHE_READ_MULT = 0.10


def per_call_cost(
    prompt_tokens: int,
    user_tokens: int,
    completion_tokens: int,
    cache_state: str,  # "write" | "read" | "miss"
) -> float:
    """Return per-call cost in USD given the cache state for the system prompt prefix."""
    if cache_state == "miss" or prompt_tokens < CACHE_MIN_PREFIX_TOKENS:
        prompt_cost = prompt_tokens * PROMPT_RATE
    elif cache_state == "write":
        prompt_cost = prompt_tokens * PROMPT_RATE * CACHE_WRITE_MULT
    elif cache_state == "read":
        prompt_cost = prompt_tokens * PROMPT_RATE * CACHE_READ_MULT
    else:
        raise ValueError(f"unknown cache_state: {cache_state}")

    user_cost = user_tokens * PROMPT_RATE
    completion_cost = completion_tokens * COMPLETION_RATE

    return (prompt_cost + user_cost + completion_cost) / 1_000_000


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--prompt-tokens", type=int, default=1500,
                   help="System prompt token count (default 1500, above cache minimum).")
    p.add_argument("--user-tokens", type=int, default=200,
                   help="Per-call user/scenario token count.")
    p.add_argument("--completion-tokens", type=int, default=100,
                   help="Per-call completion token count.")
    p.add_argument("--n-calls", type=int, default=12,
                   help="Number of held-out evaluations.")
    p.add_argument("--hit-rate", type=float, default=None,
                   help="If set, run the 'partial caching' regime: this fraction of calls are reads "
                        "(rest are misses/writes). If unset, runs both Configuration A and B.")
    args = p.parse_args()

    print("=" * 78)
    print("  Prefix-cache cost demo — per-call arithmetic for an API-served judge")
    print("=" * 78)
    print(f"  System prompt: {args.prompt_tokens} tokens  "
          f"(cache minimum: {CACHE_MIN_PREFIX_TOKENS}; "
          f"{'ABOVE → caches' if args.prompt_tokens >= CACHE_MIN_PREFIX_TOKENS else 'BELOW → never caches'})")
    print(f"  Per-call user prompt: {args.user_tokens} tokens")
    print(f"  Per-call completion:  {args.completion_tokens} tokens")
    print(f"  Number of calls:      {args.n_calls}")
    print(f"  Rate card:            ${PROMPT_RATE}/1M prompt, ${COMPLETION_RATE}/1M completion")
    print(f"  Cache rates:          {CACHE_WRITE_MULT}x write, {CACHE_READ_MULT}x read")
    print()

    if args.hit_rate is not None:
        # Partial caching regime
        n_reads = round(args.n_calls * args.hit_rate)
        n_misses = args.n_calls - n_reads
        cost_per_read = per_call_cost(args.prompt_tokens, args.user_tokens, args.completion_tokens, "read")
        cost_per_miss = per_call_cost(args.prompt_tokens, args.user_tokens, args.completion_tokens, "miss")
        total = n_reads * cost_per_read + n_misses * cost_per_miss
        mean = total / args.n_calls
        print(f"  Partial-caching regime (hit_rate = {args.hit_rate}):")
        print(f"    {n_reads}  cache reads  @ ${cost_per_read:.6f}/call")
        print(f"    {n_misses}  cache misses @ ${cost_per_miss:.6f}/call")
        print(f"    mean per-call cost = ${mean:.6f} ≈ ${mean:.4f}")
        return 0

    # Configuration A: stable system prompt across all calls
    cost_write = per_call_cost(args.prompt_tokens, args.user_tokens, args.completion_tokens, "write")
    cost_read = per_call_cost(args.prompt_tokens, args.user_tokens, args.completion_tokens, "read")
    total_a = cost_write + (args.n_calls - 1) * cost_read
    mean_a = total_a / args.n_calls
    print("  Configuration A — stable system prompt across all calls:")
    print(f"    Call 1 (cache write):       ${cost_write:.6f}")
    print(f"    Calls 2-{args.n_calls} (cache read):     ${cost_read:.6f}/call  "
          f"({args.n_calls - 1} calls)")
    print(f"    Total:                      ${total_a:.6f}")
    print(f"    Mean per call:              ${mean_a:.6f} ≈ ${mean_a:.4f}")
    print()

    # Configuration B: every call is a cache miss / full price
    cost_miss = per_call_cost(args.prompt_tokens, args.user_tokens, args.completion_tokens, "miss")
    total_b = args.n_calls * cost_miss
    mean_b = total_b / args.n_calls
    print("  Configuration B — every call is a cache miss (drift, or below 1024-token min):")
    print(f"    Per-call cost:              ${cost_miss:.6f}")
    print(f"    Total:                      ${total_b:.6f}")
    print(f"    Mean per call:              ${mean_b:.6f} ≈ ${mean_b:.4f}")
    print()

    print("=" * 78)
    print("  Diagnosis")
    print("=" * 78)
    diff_pp = (mean_b - mean_a) / mean_a * 100
    print(f"  Configuration A mean per-call cost:  ${mean_a:.4f}")
    print(f"  Configuration B mean per-call cost:  ${mean_b:.4f}  ({diff_pp:+.0f}% vs A)")
    print()
    print(f"  Same compute, same model, same eval — different cache-hit ratio.")
    print(f"  A partner reporting ${0.0029} (config A) vs ${0.0047} (config B-ish) is")
    print(f"  most consistent with a partial-caching regime where the second")
    print(f"  configuration's system prompt drifts per task or sits just below the")
    print(f"  1024-token cache-minimum threshold. To reproduce ~$0.0047:")
    print(f"    python scripts/cache_cost_demo.py --hit-rate 0.5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
