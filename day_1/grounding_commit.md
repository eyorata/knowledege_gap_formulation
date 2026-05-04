# Grounding Commit

## Purpose
This note records the concrete artifact correction I made after my Day 1 bootstrap gap was closed.

## File updated
- `blog/tenacious_bench_v0.1_blog.md`

## Old claim (too weak)
I wrote that Delta A's CI "grazes zero" due to "small-n quantization" without explaining the actual mechanism, and this made the claim easy to challenge.

## New grounded claim
I now explain that with paired bootstrap on binary outcomes at `n=12`, the resample distribution is discrete and has a non-trivial mass at `diff=0.00`, which can place the percentile CI lower bound at zero while still yielding a small one-sided p-value (`p=0.0316`).

## Concrete edits made
1. Replaced the vague sentence in the results discussion:
   - from: "CI grazes zero because of small-n quantization."
   - to: "At `n=12` with binary outcomes, paired bootstrap diffs are discrete and include a spike at `0.00`, so percentile `ci_low` can equal zero even when only a small minority of resamples are non-positive (`p=0.0316`)."
2. Added one explicit reporting qualifier:
   - "For this small-`n` regime, we treat directional p-value as the binding directional signal and report CI as uncertainty width, not as standalone evidence of no effect."
3. Added a traceable bridge to the eval output:
   - `raw_lift_pp = +0.25`, `bootstrap_ci = [0.00, 0.50]`, `bootstrap_p_value = 0.0316`.

## Why this improves artifact quality
- Upgrades a hand-wavy phrase into a mechanism-level, testable explanation.
- Aligns memo/blog interpretation with the actual bootstrap outputs.
- Reduces reviewer confusion about "CI includes zero" versus directional significance in small-sample discrete settings.

## Date
2026-05-04