# question.md — Day 4

**Topic (cohort-voted):** Evaluation and statistics — chance-corrected inter-rater agreement when ratings are concentrated, and what "100% agreement at ±1 tolerance" actually means for a benchmark's quality claim
**Asker:** Eyoel Nebiyu (`@eyorata`)
**Partner (explainer):** *[fill in once paired]*
**Date:** 2026-05-08

---

## The question

> **In my Tenacious-Bench v0.1 audit, [`inter_rater_agreement.json`](https://github.com/eyorata/sales_evaluation_bench/blob/master/inter_rater_agreement.json) reports `overall_avg_pct = 100.0` and `passes_80_pct_per_dim = true` across n=30 pairs on three ordinal dimensions (`input_coherence`, `ground_truth_verifiability`, `rubric_application_clarity`), each rated 1–5, with the agreement metric defined as `agree_within_1` (so `{4,4}`, `{4,5}`, `{5,4}`, `{5,5}` all count as agreement). My [`memo/memo.md`](https://github.com/eyorata/sales_evaluation_bench/blob/master/memo/memo.md) cites this as the evidence point that the benchmark is mechanically gradable. But scanning the per-pair JSON, ~87% of all t0 ratings are 4 or 5, which means the *prior probability* that both raters happen to land in the {4,5} basket — independent of any real "agreement" — is already very high. So: **what is the gradient between *raw agreement at ±1 tolerance* and *chance-corrected agreement* (Cohen's kappa, weighted kappa, Gwet's AC1) when the rating distribution is concentrated near the ceiling, why does Cohen's kappa famously paradox-collapse in this regime, which statistic should I be reporting in the memo, and concretely — what range should I expect kappa / Gwet's AC1 to fall into for *this specific* n=30 dataset, on what derivation?***

The question is one sentence on purpose. The "ratings are concentrated at 4–5 so raw agreement is misleading" is the load-bearing observation; the asked-for output is a derivation of the kappa-paradox mechanism plus a numerical prediction the explainer is willing to defend.

---

## Why this matters in my work (grounding)

This question is grounded in three specific artifacts already published:

1. **[`inter_rater_agreement.json`](https://github.com/eyorata/sales_evaluation_bench/blob/master/inter_rater_agreement.json)** — n=30, three dimensions, agreement metric is `agree_within_1`, summary fields `"overall_avg_pct": 100.0` and `"passes_80_pct_per_dim": true`. Inspecting the per-pair entries: across the 90 (pair × dim) cells, the t0 marginal distribution is roughly `{3: ~3, 4: ~30, 5: ~57}` — i.e., 97% of ratings are 4 or 5. The probability of *random* {4,5}-basket co-occurrence given the marginals is therefore ~0.85, not ~0.20.

2. **[`inter_rater_agreement.md`](https://github.com/eyorata/sales_evaluation_bench/blob/master/inter_rater_agreement.md)** — the prose document that says "all three dimensions clear the 80% bar" and uses that to certify the rubric is "mechanically gradable, not subjective." This sentence is what propagates into the memo. It does not name a chance-corrected statistic.

3. **[`memo/memo.md`](https://github.com/eyorata/sales_evaluation_bench/blob/master/memo/memo.md)** — the executive 2-pager cites "100% inter-rater agreement (within ±1) across all three quality dimensions" as one of three evidence points that the benchmark is fit for purpose. That sentence is what a senior FDE / reviewer would interrogate first. I cannot defend it if the kappa-paradox question lands on the table — the marginal distribution is *visible in the same JSON I'm citing*, and a chance-corrected statistic would almost certainly tell a different story.

The implication is that my published "100% IRR" claim might be a **prevalence artifact** — high agreement driven by raters concentrating their ratings at 4 or 5, not by the rubric forcing the same answer mechanically. If so, the memo's certification of "mechanical gradability" is overclaiming on the basis of a statistic that doesn't measure what the prose says it measures.

---

## What a satisfying answer looks like (one paragraph)

A satisfying explainer would (a) **derive** Cohen's kappa from first principles at one (rater-1, rater-2) confusion-matrix example, showing exactly where the *expected agreement by chance* term enters; (b) **name the kappa paradox** — Feinstein & Cicchetti (1990), Byrt et al. (1993) — where high raw agreement at extreme marginals produces low or even negative kappa, and explain *why* this is a feature of kappa, not a bug; (c) **derive the numerical prediction** for *my specific* n=30 × 3-dim dataset under reasonable marginal assumptions (e.g., `Pr(rating=5) ≈ 0.63`, `Pr(rating=4) ≈ 0.34`, `Pr(rating=3) ≈ 0.03`), giving a defended range for Cohen's kappa, weighted kappa with linear weights (since ratings are ordinal), and Gwet's AC1 (which is paradox-resistant); (d) **commit to a recommendation** — which statistic should I report in the memo, and one sentence on why that statistic is the honest summary of what my IRR exercise actually demonstrates; (e) **show with a runnable script** the difference between raw agreement and the three chance-corrected statistics on the actual rating distribution, so I (or a future reader) can re-run on a slightly different marginal and see how the gap behaves.

---

## Scope: in / out

**In scope (what the explainer should cover):**
- Cohen's kappa derivation at one 2-rater × k-category confusion matrix, with `p_o` (observed agreement) and `p_e` (expected agreement by chance) named explicitly.
- The kappa paradox at high-prevalence marginals: why `p_o` near 1 with `p_e` also near 1 collapses kappa.
- Linear-weighted kappa (Cohen 1968) for ordinal ratings — since 1–5 is ordinal, unweighted kappa understates the rubric's actual reliability.
- Gwet's AC1 (Gwet 2008) — one-sentence statement of why its expected-agreement term is paradox-resistant.
- A numerical prediction on *my* dataset's approximate marginals.
- A small numpy / pseudocode demonstration.
- A recommendation: which statistic to put in the memo, and the one-sentence honest framing.

**Out of scope (do not pad with):**
- Krippendorff's alpha, Fleiss' kappa beyond 2 raters, ICC. They're alternatives but not what my dataset's structure needs.
- A general "evaluation methodology" essay. The whole point is to make this *prevalence-paradox-mechanism-level*, not "you should have used kappa."
- The bootstrap CI on kappa at n=30 — that's a follow-up question; here I want the *point estimate* range and the mechanism, not the uncertainty quantification on top.
- IRR for non-ordinal labels (binary, nominal). My ratings are ordinal 1–5.

---

## Self-check against the four rubric properties

| Property | Self-rating (1–5) | Justification |
|---|---:|---|
| **Diagnostic** | 5 | Names a specific mechanism question (kappa paradox at concentrated marginals) tied to a specific published claim ("100% agreement, passes 80% bar") in a specific artifact (`inter_rater_agreement.md` cited in `memo/memo.md`). Not "how does Cohen's kappa work?" |
| **Grounded in cohort work** | 5 | Cites three artifacts with line-level pointers: the JSON with the marginal distribution, the markdown that propagates the 80% claim into prose, and the memo paragraph that certifies "mechanical gradability" on the basis of that prose. The asker-side *grounding commit* is concrete: rewrite the IRR markdown's certification sentence to honestly report (raw agreement, kappa, Gwet's AC1) as a triple, and update the memo paragraph to match. |
| **Generalizable** | 5 | Every FDE running rubric-graded LLM benchmarks at small n with concentrated rating distributions hits this — and the published-paper rate of "100% raw agreement!" claims that wouldn't survive a kappa check is high. The right statistic to report here is a recurring decision in any eval methodology section. |
| **Resolvable in one explainer** | 5 | Cohen's original 1960 paper has the derivation in three lines; the paradox proof is a one-paragraph algebraic argument; the numerical prediction is a 5-line numpy script on my actual marginals. ~800–1000 words covers derivation + paradox + prediction + recommendation + demo. Not a textbook chapter; not a one-liner. |

---

## Pointers to start the explainer (offered as starting points, not required)

- **Cohen, J.** *A coefficient of agreement for nominal scales*, Educational and Psychological Measurement, 1960. The original kappa derivation. Equations on p. 39–40 are all that's needed.
- **Cohen, J.** *Weighted kappa: nominal scale agreement provision for scaled disagreement or partial credit*, Psychological Bulletin, 1968. The linear-weighted kappa for ordinal scales — the right statistic for 1–5 ratings with ±1 tolerance baked into the disagreement weights.
- **Feinstein, A. R., & Cicchetti, D. V.** *High agreement but low kappa: I. The problems of two paradoxes*, Journal of Clinical Epidemiology, 1990. The canonical statement of the kappa paradox at concentrated marginals.
- **Gwet, K. L.** *Computing inter-rater reliability and its variance in the presence of high agreement*, British Journal of Mathematical and Statistical Psychology, 2008. AC1 derivation; the paradox-resistant alternative.
- **Byrt, T., Bishop, J., & Carlin, J. B.** *Bias, prevalence and kappa*, Journal of Clinical Epidemiology, 1993. Decomposes kappa into prevalence-adjusted and bias-adjusted components — gives the cleanest one-page intuition for why my dataset's marginals matter.

---

*This question is final post-morning-call sign-off. Partner: hand back the explainer by the evening call. I'll sign off "closed / partially / not closed" and write the grounding commit pointing to the rewritten IRR-certification sentence in `inter_rater_agreement.md` and the matching memo paragraph in `memo/memo.md`. The cleanest grounding commit, if the explainer's numerical prediction lands within a defensible range, is to add a `kappa_and_ac1` block to `inter_rater_agreement.json` reporting all three statistics (raw, kappa, AC1) and to update the memo to cite the triple instead of just the raw-agreement number.*
