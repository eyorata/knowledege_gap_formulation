# Explainer: Why `ci_low = 0.00` and `p = 0.0316` Can Both Be True

## The setup

In my Week 11 paired-bootstrap ablation (`n=12` held-out preference pairs), I got:

- `bootstrap_mean_diff = +0.2512`
- `bootstrap_ci = [0.00, 0.50]` (percentile 95% CI)
- `bootstrap_p_value = 0.0316` (one-sided, `P(diff <= 0)`)

At first glance this looks contradictory. If the CI lower bound is exactly zero, how can the p-value still indicate directional lift?

They are not contradictory. They answer different questions about the same resample distribution.

## The mechanism at small n

With paired bootstrap on binary outcomes (0/1), each resample is built by drawing 12 pair indices with replacement. Because outcomes are discrete and sample size is small, the possible mean differences are also discrete. You do not get a smooth continuum of values; you get a small lattice.

That discreteness creates a real probability mass at exactly `diff = 0.00`. In plain terms: many resamples accidentally produce equal effective success rates for trained and baseline, even when the original sample shows positive lift.

When you compute the percentile CI, `ci_low` is the 2.5th percentile of that discrete distribution. If enough mass sits at zero, the 2.5th percentile lands exactly on zero. This is why `ci_low = 0.00` can occur mechanically in small-`n` binary paired settings.

So the load-bearing point is this: the lower CI touching zero here can be a quantization artifact of small-sample discreteness, not automatically evidence of no directional signal.

## What the p-value is measuring

In this harness the one-sided p-value is:

```python
p_value = (diffs <= 0).mean()
```

This asks: in what fraction of bootstrap resamples did we see no lift or negative lift?

For this run, that fraction is 3.16%. Equivalently, about 96.84% of resamples showed positive lift.

That can coexist with `ci_low = 0.00` because the CI boundary and this tail probability summarize different aspects of the same distribution:

- CI boundary: where the lower 2.5% cutoff lies
- One-sided p-value: total mass at or below zero

In a smooth large-sample regime, these summaries tend to line up intuitively. In small discrete regimes, they can decouple.

## A quick simulation you can run

```python
import numpy as np

def paired_bootstrap(a, b, n_resamples=10000, seed=42):
    rng = np.random.default_rng(seed)
    a, b = np.array(a), np.array(b)
    diffs = []
    for _ in range(n_resamples):
        idx = rng.integers(0, len(a), size=len(a))
        diffs.append(a[idx].mean() - b[idx].mean())
    diffs = np.array(diffs)
    return {
        "ci_low": float(np.percentile(diffs, 2.5)),
        "ci_high": float(np.percentile(diffs, 97.5)),
        "p": float((diffs <= 0).mean()),
    }

# n=12 (small)
a12 = np.array([1,1,1,1,1,0,0,0,0,0,0,0])
b12 = np.array([1,1,0,0,0,0,0,0,0,0,0,0])

# n=30 and n=100 (larger)
rng = np.random.default_rng(99)
a30 = rng.binomial(1, 0.42, 30)
b30 = rng.binomial(1, 0.17, 30)
a100 = rng.binomial(1, 0.42, 100)
b100 = rng.binomial(1, 0.17, 100)

for label, a, b in [("n=12", a12, b12), ("n=30", a30, b30), ("n=100", a100, b100)]:
    r = paired_bootstrap(a, b)
    print(label, r)
```

Typical pattern:

- `n=12`: lower CI may land at `0.00`, with a still-small one-sided p-value
- `n=30`: lower CI usually lifts above zero
- `n=100`: CI and p-value behavior becomes more stable and aligned

This progression makes the regime change visible: as `n` increases, quantization effects shrink.

## The reporting rule I use for FDE memos

For small-`n` paired binary evals (`n < 30`), I use this rule:

1. Lead with directional p-value for the sign of the effect.
2. Report CI as uncertainty width and be explicit about small-sample discreteness.
3. Do not claim “no effect” from “CI touches zero” alone in this regime.
4. Add replication language: treat result as directional evidence pending larger sample confirmation.

Memo-ready wording:

> The trained arm outperformed baseline in most paired bootstrap resamples (`p = 0.0316`, one-sided). The 95% percentile CI is `[0.00, 0.50]`; the lower bound at zero is consistent with small-sample discreteness in a 12-pair binary setup. We treat this as positive directional evidence and recommend replication at larger `n` before high-stakes rollout.

## What this changed in my artifacts

This closed a real gap in my Week 11 writing. I previously wrote “small-n quantization” without mechanism-level backing. After this analysis, I can now:

- explain why `ci_low = 0.00` occurred,
- justify why `p = 0.0316` is not inconsistent with that CI,
- and report the result in a way that is honest, technically defensible, and executive-readable.

## Sources

- Efron, B., & Tibshirani, R. J. *An Introduction to the Bootstrap* (1993).
- Hesterberg, T. C. *What Teachers Should Know About the Bootstrap* (2015).

These are the two load-bearing references for percentile bootstrap behavior and small-sample interpretation.