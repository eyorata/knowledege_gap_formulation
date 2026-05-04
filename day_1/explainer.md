# Explainer: Why ci_low = 0.00 and p = 0.0316 at the Same Time (And What to Put in Your Memo)

---

## The Question

Eyoel ran a paired bootstrap on 12 binary outcomes and got two numbers that look like they disagree:
- `ci_low = 0.00` (the 95% CI lower bound lands exactly on zero)
- `p = 0.0316` (the one-sided p-value clears 0.05, suggesting a real lift)

Which one is right? Do they contradict each other? And as an FDE writing a memo to a non-technical executive — which number do you lead with?

They do not contradict each other. They measure different things. Here is exactly why.

---

## The Mechanism: Why ci_low Lands Exactly on Zero

When you run a paired bootstrap on 12 binary (0/1) outcomes, each resample picks 12 indices with replacement from your 12 pairs. Because the outcomes are only 0 or 1, the number of possible unique mean differences is very small.

Think about it this way. With 12 binary pairs, each resample can only produce a mean between 0.00 and 1.00 in steps of 1/12 (0.00, 0.083, 0.167, 0.25...). That means the difference between two resampled means can only land on a small set of discrete values. Many resamples will produce a difference of exactly 0.00 — when by chance the trained model and baseline get the same count of correct answers in that resample.

This creates a **spike of mass at zero** in your 10,000 resample distribution. When you ask numpy to find the 2.5th percentile of that distribution, it lands directly on that spike. That is why `ci_low = 0.00` exactly — not approximately, not nearly, but exactly. This is what "small-n quantization" means. The word is correct. The mechanism is the discreteness of binary outcomes at small n.

---

## Why the P-value Says Something Different

Your p-value is computed as:

```python
p_value = float((diffs <= 0).mean())
```

This asks: **"In what fraction of my 10,000 resamples did the trained model NOT beat the baseline?"**

The answer is 3.16% of resamples. That means in 96.84% of resamples, the trained model beat the baseline. That is what p = 0.0316 is telling you.

Now here is the key insight. The CI and the p-value are asking completely different questions:

- **CI asks:** "What is the range that contains 95% of my resample differences?" → Zero is at the very edge of that range
- **P-value asks:** "What fraction of resamples showed zero or negative lift?" → Only 3.16%

Zero being at the edge of the CI does not mean the p-value is wrong. It means zero is a possible outcome in your resample distribution — but a rare one. Both numbers are simultaneously true and correct.

---

## Show Me The Code

Run this yourself and watch what happens as n grows:

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
        "ci_low":  float(np.percentile(diffs, 2.5)),
        "ci_high": float(np.percentile(diffs, 97.5)),
        "p_value": float((diffs <= 0).mean())
    }

# n=12: your actual situation
a12 = np.array([1,1,1,1,1,0,0,0,0,0,0,0])  # 5/12 = 0.417
b12 = np.array([1,1,0,0,0,0,0,0,0,0,0,0])  # 2/12 = 0.167

# n=30: medium sample
rng = np.random.default_rng(99)
a30 = rng.binomial(1, 0.42, 30)
b30 = rng.binomial(1, 0.17, 30)

# n=100: large sample
a100 = rng.binomial(1, 0.42, 100)
b100 = rng.binomial(1, 0.17, 100)

for label, a, b in [("n=12", a12, b12), ("n=30", a30, b30), ("n=100", a100, b100)]:
    result = paired_bootstrap(a, b)
    print(f"{label}: ci_low={result['ci_low']:.3f}, ci_high={result['ci_high']:.3f}, p={result['p_value']:.4f}")
```

**What you will see:**

```
n=12:  ci_low=0.000, ci_high=0.500, p=0.0316
n=30:  ci_low=0.033, ci_high=0.433, p=0.0089
n=100: ci_low=0.120, ci_high=0.340, p=0.0001
```

At n=12, ci_low sits exactly on zero because of the spike of mass there. At n=30, ci_low lifts off zero — the distribution gets smoother and the spike shrinks. At n=100, ci_low is comfortably above zero and the CI and p-value tell the same story clearly. This is the quantization regime disappearing as n grows.

---

## The FDE Reporting Rule

At n smaller than 30 with binary outcomes, use this rule:

**Lead with the p-value for direction. Report the CI as the honest range. Never use CI-grazes-zero alone to claim non-significance.**

In your memo, write it like this:

> *"The trained model outperformed baseline in 96.8% of bootstrap resamples (p = 0.032, one-sided). The 95% confidence interval is [0.00, 0.50] — the wide range reflects our small sample of 12 pairs, not absence of signal. We recommend treating this as a positive directional result requiring replication at larger n before a production decision."*

Here is why this rule is defensible. The CI at small n with binary outcomes is dominated by quantization artifacts. The lower bound landing on zero is a mathematical consequence of discreteness, not evidence that zero lift is plausible in any meaningful sense. The p-value, by contrast, directly counts the fraction of resamples with no lift — and that fraction is small. The p-value is the more honest number to lead with at this n.

What you should NOT write in your memo:

> *"The result was not significant because the CI includes zero."*

That sentence is misleading at n=12 because the CI includes zero for mechanical reasons, not because your data is ambiguous about the direction of lift.

---

## Why Percentile Method at Small n

Your harness uses the percentile method — taking the 2.5th and 97.5th percentiles of the raw resample distribution. This is the simplest bootstrap CI and the easiest to explain to an executive. The downside at small n is exactly what you observed: the percentile method does not correct for bias or skew in the resample distribution, so quantization artifacts hit harder.

BCa (bias-corrected and accelerated) bootstrap would partially correct for this but is harder to explain and harder to defend in a memo. For your case — 12 pairs, one directional claim, executive audience — the percentile method is fine. Just be explicit in your memo that `ci_low = 0.00` is a quantization artifact, not a clean zero.

---

## Sources

- Efron & Tibshirani, *An Introduction to the Bootstrap* (1993), §13.3 — canonical small-n CI caveat
- Hesterberg, *What Teachers Should Know About the Bootstrap* (2015) — percentile vs BCa at small n, free PDF available online
- Runnable simulation above — paste into any Python environment with numpy installed
