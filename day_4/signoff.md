# signoff.md — Day 4 (asker side)

**Asker:** Eyoel Nebiyu (`@eyorata`)
**Explainer received from:** Liul J. Teshome
**Date:** 2026-05-08
**Verdict:** **Closed**

---

## What I now understand that I did not before

The kappa-paradox mechanism landed at the level the question asked for, with one feature I had not budgeted for: **Liul actually built the 90-cell confusion matrix out of `inter_rater_agreement.json` and derived all three statistics on it directly.** That moves the answer from "here's how kappa works in principle" to "here is what your dataset's IRR actually looks like under each statistic." The numbers:

| Statistic | Value |
|-----------|------:|
| Raw agreement at ±1 tolerance | 100.0% |
| Exact agreement (`p_o`) | 88.9% |
| Unweighted Cohen's κ | 0.781 |
| Linear-weighted Cohen's κ_w | 0.801 |
| Gwet's AC1 | 0.851 |

The `p_o = 0.889`, `p_e = 0.493`, `κ = (0.889 − 0.493) / (1 − 0.493) = 0.781` derivation is the sentence I could not have written 24 hours ago. I now know exactly where the chance-agreement term enters and how much of my "100%" raw-agreement number it consumes — about half. AC1's redefinition of `p_e` as `(1/(q−1)) Σ π_k(1 − π_k)` is paradox-resistant because at concentrated marginals each `π_k(1 − π_k)` term shrinks (a Bernoulli variable near 0 or 1 has low variance), keeping the denominator `(1 − p_e_AC1) = 0.747` large where Cohen's `(1 − p_e) = 0.507` had already shrunk by half.

## Where my prior projection was wrong (and why this is the more interesting finding)

In the evening call summary I projected unweighted κ in **0.0–0.3** (paradox-collapsed), weighted κ in **0.4–0.6**, and AC1 in **0.7–0.85**. Two of the three were off — actual κ = 0.781, weighted κ_w = 0.801. AC1 = 0.851 lands at the top of my range, so that one was right.

The reason my projection overshot the pessimism is that the kappa paradox depends on *both* prevalence (concentrated marginals) and bias (asymmetry between t0 and t1 marginals). My dataset has high prevalence but low bias — both raters concentrate at 4 and 5 in roughly the same proportions — and the off-diagonal mass is almost entirely at distance 1 (4-vs-5 disagreements, not 3-vs-5). Together those keep `p_o − p_e` large enough that κ does not collapse, even though it does drop substantially from the raw-agreement number.

That changes what the memo paragraph should actually say. My prior mental model was "the paradox makes my IRR claim indefensible." The actual finding is **stronger and more honest**: the rubric *is* reliably gradable in the high-score regime — AC1 = 0.85 is "substantial agreement" by any benchmark — but the headline number should be 0.85, not 100%. The mechanism worry was correct; the magnitude worry was overcalibrated to worst-case.

## What did not fully close (deliberate scope tradeoff)

One residual remains, logged as a Day-5 candidate cohort topic: **the bootstrap CI on AC1 at n=30 was deliberately scoped out** of the question, and the published memo would benefit from a CI alongside the AC1 point estimate before final submission. Liul flagged this as a clean follow-up rather than a hole — and I agree, since the point estimate plus the paradox-mechanism explanation is what the memo needs to be honest, with the CI as a quality-of-evidence bonus rather than a load-bearing requirement.

## Grounding commit — what changes in my Week 11 portfolio

Three concrete edits land on `eyorata/sales_evaluation_bench` (see [`grounding_commit.md`](grounding_commit.md) for the diff-level detail):

1. **`inter_rater_agreement.json`** — add a new top-level `kappa_and_ac1` block reporting raw agreement, exact agreement, unweighted κ, linear-weighted κ_w, and Gwet's AC1, with a one-line note on the marginal-concentration regime.
2. **`inter_rater_agreement.md`** — rewrite the certification sentence to report the triple (raw, kappa, AC1) instead of the raw-agreement-only number, and downgrade "mechanically gradable" to "reliably gradable in the high-score regime" since that is what AC1 = 0.85 actually supports.
3. **`memo/memo.md`** — replace the "100% inter-rater agreement (within ±1)" evidence point with the paragraph Liul drafted, which leads with AC1 = 0.851 and reports the full triple alongside.
