# grounding_commit.md — Day 4 (asker side)

**Asker:** Eyoel Nebiyu (`@eyorata`)
**Date:** 2026-05-08
**Verdict from [`signoff.md`](signoff.md):** Closed
**Companion docs:** [`question.md`](question.md), [`explainer.md`](explainer.md) (the one I wrote for Liul on the embedding-drift evidence chain), `partner_explainer.md` (Liul's explainer on the kappa paradox — kept locally), [`signoff.md`](signoff.md)

---

## What this commit is

The paired explainer with Liul J. Teshome closed my Week 11 question on **whether `inter_rater_agreement.json`'s "100% agreement at ±1 tolerance" claim survives chance-correction at concentrated marginals**, and gave a turn-key set of numbers (κ = 0.781, κ_w = 0.801, AC1 = 0.851) derived directly from the 90-cell confusion matrix in my data. This commit is the asker-side grounding — three edits to my Week 11 portfolio that turn the new statistics into permanent artifacts: a `kappa_and_ac1` block in the IRR JSON, a rewritten certification sentence in the IRR markdown, and a memo paragraph that leads with AC1 instead of the raw-agreement number.

**Target repo:** [`eyorata/sales_evaluation_bench`](https://github.com/eyorata/sales_evaluation_bench)
**Files changed:** 3
**Branch:** `day4-grounding-kappa-ac1`

---

## The edits

### 1. `inter_rater_agreement.json` — add a top-level `kappa_and_ac1` block

**Before** (current `master`):
```json
{
  "n": 30,
  "tolerance": "within ±1",
  "per_dimension": { ... },
  "overall_avg_pct": 100.0,
  "passes_80_pct_per_dim": true,
  "pairs": [ ... ]
}
```

**After** (this commit, new top-level block alongside the existing fields):
```json
"kappa_and_ac1": {
  "raw_agreement_pct_at_pm1": 100.0,
  "exact_agreement_pct": 88.9,
  "cohens_kappa_unweighted": 0.781,
  "cohens_kappa_linear_weighted": 0.801,
  "gwets_ac1": 0.851,
  "n_cells": 90,
  "active_categories": [3, 4, 5],
  "marginal_concentration_pct_at_4_or_5": 97.8,
  "note": "Computed over 90 (pair × dim) cells. Raw 100% agreement at ±1 tolerance is consistent with the marginal concentration; AC1 is the paradox-resistant statistic and is the recommended headline number for the memo."
}
```

### 2. `inter_rater_agreement.md` — honest rewrite of the certification sentence

**Before** (current `master`, after the per-dimension table):

> **All three dimensions meet the ≥80% threshold.**

This sentence is silent on the chance-agreement term, and the prose elsewhere uses it to certify the rubric is "mechanically gradable." That phrasing is what propagates into the memo.

**After** (this commit):

> **All three dimensions meet the ≥80% threshold at ±1 tolerance.** Chance-corrected statistics computed over the full 90-cell confusion matrix (categories {3, 4, 5}; marginal concentration 97.8% at 4 or 5): unweighted Cohen's κ = 0.781, linear-weighted Cohen's κ_w = 0.801, Gwet's AC1 = 0.851. The kappa paradox (Feinstein & Cicchetti 1990; Byrt et al. 1993) means raw agreement at concentrated marginals overstates real reliability — about half of the exact-agreement rate is consumed by the chance-agreement term — so this report leads with AC1 (Gwet 2008) as the paradox-resistant headline. **The rubric is reliably gradable in the high-score regime (AC1 = 0.85, "substantial agreement" on Landis & Koch's scale); the 100% raw-agreement number alone would overstate this.**

### 3. `memo/memo.md` — replace the IRR evidence point

**Before** (current `master`, in the "fit for purpose" evidence list):

> 100% inter-rater agreement (within ±1) across all three quality dimensions.

**After** (this commit, the paragraph Liul drafted):

> Across n=30 pairs and three ordinal dimensions with rating marginals concentrated at 4–5 (97.8% of ratings), raw agreement at ±1 tolerance is 100%. Gwet's AC1 = 0.851 on exact matches, indicating substantial inter-rater reliability in the regime where the rubric assigns high scores. AC1 is the paradox-resistant statistic (Gwet 2008); unweighted Cohen's κ = 0.781 and linear-weighted κ = 0.801 are reported alongside for convention. The rubric is reliably gradable in this rating regime; the 100% raw-agreement number alone would overstate this conclusion.

---

## What changed in my mental model

Before this paired explainer, I would have read "100% IRR" in my own memo as a clean evidence point and not noticed the chance-correction gap. After Liul's explainer, I read it as: **the headline number was conventional but indefensible; the underlying rubric reliability is genuinely substantial (AC1 = 0.85), but only because t0 and t1 marginals are symmetric and off-diagonals are at distance 1 — neither of which the original certification sentence named**. That distinction is the difference between "the memo overclaims and the rubric is suspect" and "the memo overclaims but the rubric is fine when you measure it correctly." Liul's derivation pinned down which one is true on my actual data.

The kappa-paradox mechanism also matters less in absolute impact for *this dataset* than I had projected (my evening-call range was κ in 0.0–0.3; actual is 0.781). But the methodological lesson generalizes: any future Tenacious-Bench expansion (or any rubric-graded benchmark with concentrated marginals) should report the (raw, κ, AC1) triple by default, not just the raw number. The IRR JSON gets a permanent `kappa_and_ac1` block so that pattern is institutional rather than per-memo discretion.

---

## What this commit deliberately does not do

It does *not* compute a bootstrap CI on AC1 at n=30 — the signoff residual logged that as a Day-5 candidate cohort topic, not a Day-4 deliverable. The point estimates are enough to honestly defend the memo paragraph; the CI is a quality-of-evidence upgrade for final submission. It does *not* recompute the per-dimension agreement table in `inter_rater_agreement.md` — those numbers were already exact-match rates and are correct as-is; only the certification sentence and the new `kappa_and_ac1` block need to land. It also does *not* touch the raw `pairs` array in the JSON — Liul's confusion matrix was derived from those entries, and they are the audit trail for re-deriving κ and AC1 at any time.

---

*The commit will land on `eyorata/sales_evaluation_bench` as a single PR titled `day4: add kappa + Gwet's AC1 to IRR report; replace memo's 100% claim with paradox-resistant headline`. Link will be added here once pushed.*
