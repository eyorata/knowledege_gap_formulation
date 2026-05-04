# Asker Signoff

## Did the explainer close my gap?
Yes. The gap is closed.

## My original gap
In my Week 11 paired-bootstrap output (`n=12`), I saw `ci_low = 0.00` and `p = 0.0316` at the same time. I could report those numbers, but I could not explain why they can both be true without sounding inconsistent.

## What specifically became clear
- I now understand the small-`n` discreteness mechanism: with binary outcomes and only 12 pairs, the bootstrap distribution is quantized and places real mass at exactly `diff = 0.00`.
- I can explain why a percentile CI lower bound can land on zero while the one-sided p-value still indicates positive directional signal.
- I can distinguish the two claims correctly: CI as range behavior of resamples, p-value as fraction of resamples with non-positive lift.
- I now have a defensible memo rule for FDE reporting at small `n`: lead with directional p-value, include CI honestly, and avoid claiming "no effect" from a CI that only grazes zero in this regime.

## What I will update in my artifacts
- `memo/memo.md` (interpretation text for Delta A)
- `blog/tenacious_bench_v0.1_blog.md` (replace hand-wavy "small-n quantization" line with mechanism-level explanation)
- `ablations/ablation_results.json` notes/README context (add explicit interpretation guidance)

## Remaining confusion
No blocker remains for this question. A follow-up I still want is a side-by-side percentile vs BCa comparison for the same `n=12` paired setup.

## Asker confirmation
- Name: Eyoel Nebiyu
- Date: 2026-05-04
- Status: **Explainer accepted**