# Why "drift_score = 0.0" Is Not Yet Evidence of Semantic Stability — and What Your n=251 vs cap=200 Mismatch Actually Costs

**Day 4 explainer · Topic: Evaluation and statistics · Asked by: Liul J. Teshome · Explainer by: Eyoel Nebiyu**

**Published:** https://dev.to/eyorata/-why-driftscore-00-is-not-yet-evidence-of-semantic-stability-and-what-your-n251-vs-2k9p

**Repo under interrogation:** [Heban-7/Data-Contract-Enforcer](https://github.com/Heban-7/Data-Contract-Enforcer)
**Files in scope:** `report_final_pdf_ready.md`, `contracts/ai_extensions.py`

---

## The question, anchored

You have two questions stacked on top of each other in the same artifact:

1. **(a) effective sample size**: the report says `Sample size: 251` but the implementation caps embeddings at `200`. Which n is the statistic actually computed over, and what does the discrepancy cost you?
2. **(b) evidence chain**: when `drift_score = 0.0` from a centroid-based cosine method, what additional evidence do you need before writing "Text content is semantically stable" in the report?

Both have a single answer-shape: **a centroid is a first-moment summary, and a first-moment summary is silent on everything else** — sample size, dispersion, multi-modality, model identity, and fallback behavior. Each of those silences is a separate place where "0.0" can mean something other than "stable." This explainer narrows to that mechanism, gives you the corrections to make in each file, and ships a numpy script that demonstrates the failure mode in one screen.

---

## What centroid-based cosine drift mechanically computes

Given a baseline cohort `A` of `n_A` embeddings `e_1, ..., e_{n_A}` in `R^d` and a current cohort `B` of `n_B` embeddings, the drift statistic is:

```
c_A = (1 / n_A) * sum_i e_i^A
c_B = (1 / n_B) * sum_j e_j^B
drift_score = 1 - cos(c_A, c_B)
```

It is a **single scalar derived from the means of two samples**. The variance of each centroid coordinate is `Var(e_k) / n`, so the precision of `c_A` and `c_B` scales with `1/sqrt(n)`. Two consequences fall straight out:

- The statistic depends on `n` — but only through estimator variance, not through what is being measured.
- Every property of the cohort that is not the mean is invisible to it.

---

## (a) Your n=251 vs cap=200 mismatch — what it actually costs

If `contracts/ai_extensions.py` enforces a 200-sample cap on the embedding loop but the report cites `Sample size: 251`, the report is wrong about precision. The standard error of each centroid coordinate is `sigma_k / sqrt(n_eff)`, with `n_eff = 200`, not `251`. That's a `sqrt(251/200) = 1.12x` understatement of uncertainty — small, but it propagates into any downstream confidence interval and into the *threshold* below which you treat the score as "no drift."

The bigger cost is provenance, not precision. When a reader sees `Sample size: 251` next to `drift_score: 0.0`, the implicit promise is that 251 documents were embedded and contributed to the centroid. If 51 were silently dropped at the cap, that's a sampling decision (was it the first 200? a random 200? the 200 with the lowest tokens?) that changes whether the centroid is even drawn from the population the report claims. **Right fix: rename the field `n_reported` and add `n_effective` as a separate field in the metric output, then make the report cite the effective number with a one-sentence note on the cap policy.** This is the cheapest reproducibility win in the whole artifact.

---

## (b) Why drift_score ≈ 0 is not yet "semantic stability"

Run the demo at [`day_4/scripts/centroid_drift_demo.py`](scripts/centroid_drift_demo.py). It builds two cohorts of 200 vectors in R^128 with **identical sample means by construction** but a 10x ratio in dispersion, and prints:

```
  centroid_cosine_drift(A, B)            = 9.78e-13    <- the contract's drift_score
  within_cohort_dispersion(A) (mean L2)  = 2.2591
  within_cohort_dispersion(B) (mean L2)  = 22.5743
  dispersion ratio B/A                   = 9.99x
  permutation p-value on centroid drift  = 1.0000
```

The drift score is machine zero. A contract that maps `drift_score ~ 0 → "semantically stable"` will say so here. But cohort B is a cloud ten times wider than cohort A — clearly a different distribution. Even a permutation test that uses the **same statistic** can't see it (`p = 1.0` because no shuffle could make centroid drift smaller than zero). The test in that statistic family is blind by construction.

This is the **first-moment trap**. There are at least four mechanisms that produce small `drift_score` without semantic stability, and your contract should distinguish all four:

1. **Genuine stability** (what you want it to mean): the population didn't change.
2. **Dispersion shift only**: same mean, wider/narrower spread. The demo above. Common when content gets more diverse or more templated over time.
3. **Multimodal redistribution**: the cohort splits into clusters whose centroids cancel into the same overall mean. A bimodal `{p, -p}` cohort and a unimodal cohort at `0` have the same centroid.
4. **Provenance failure**: the embedding model returned a fallback (zero vector, last good cache, default vector) for some samples. If the fallback contributes the same constant to both cohorts, centroid distance shrinks toward zero artifactually.

(4) is the one to interrogate first in your repo. If `contracts/ai_extensions.py` has a try/except that catches embedding-API errors and returns a default vector (or skips the sample silently), then `drift_score = 0.0` could mean "all 51 over-cap samples failed and got dropped, plus the 200 that did embed are fine." That is a *very* different sentence from "Text content is semantically stable."

---

## The evidence chain a "semantically stable" claim needs

Before writing that sentence in `report_final_pdf_ready.md`, the chain should be:

1. **Embedding model identity pinned** — the model id and version of the embedding endpoint at baseline-time and at current-time. If the model changed between the two cohorts, the score is comparing apples to apples in a different orchard, and `drift = 0` is meaningless. Log it.
2. **Effective sample size logged** (the (a) fix above) — `n_effective` not `n_reported`.
3. **Fallback path documented** — what happens when an embedding call fails? Is the failure counted into `n_effective` or silently dropped? If silently dropped, what fraction of the cohort is the fallback vector?
4. **At least one 2nd-moment statistic** — within-cohort mean pairwise distance, or the trace of the covariance, or even just `np.std(embeddings, axis=0).mean()`. One number per cohort. The demo's `within_cohort_dispersion` is a starter.
5. **A distribution-level statistic** — Maximum Mean Discrepancy (MMD, Gretton et al. 2012) or energy distance (Székely & Rizzo 2013) is the standard upgrade. They're 5–10 lines of numpy on top of what you already compute.
6. **A semantic spot-check** — `k=20` randomly-sampled documents from each cohort, run through an LLM-judge or a human, scored for topic/intent equivalence. The word "semantic" in the claim is doing real work, and only humans or a language model can supply that signal. Centroid distance never can.

Only after (1)–(6) is "Text content is semantically stable" a defensible sentence. Until then, the honest claim is the strictly weaker one: **"The first-moment summary of the embedding distribution is unchanged within the noise floor of an n=200 estimator using model M, with fallback rate F."**

---

## What to actually change in your two files

**`contracts/ai_extensions.py`** — emit a triple, not a scalar:
```python
{
  "drift_score": 0.0,                  # 1 - cos(c_A, c_B)
  "dispersion_ratio": 1.02,            # within-cohort 2nd moment ratio
  "mmd_score": 0.014,                  # MMD with RBF kernel between cohorts
  "n_effective": 200,
  "n_reported_input": 251,
  "embedding_model_id": "text-embedding-3-small",
  "fallback_rate": 0.0
}
```

**`report_final_pdf_ready.md`** — rewrite the drift-results paragraph from:
> "drift_score: 0.0 — Text content is semantically stable."

to:

> "Centroid-cosine drift = 0.0 over n_effective = 200 (capped from 251 input documents) using `text-embedding-3-small` with a 0% fallback rate. Within-cohort dispersion ratio = 1.02; MMD between cohorts = 0.014. Consistent with no shift in the first-moment summary or the second-moment dispersion of the embedding distribution. A direct semantic-equivalence test on a `k=20` spot-check sample is queued and not yet reported here."

That paragraph is defensible to a senior reviewer; the original one is not.

---

## What I deliberately skipped

Bootstrap CI on the drift score itself; multi-batch streaming drift detectors (KS-windows, ADWIN, Page-Hinkley); contrastive-embedding identifiability; cross-model centroid alignment via Procrustes. Each is its own explainer. The mechanism above — *centroid is a first-moment summary, every other property of the cohort is silent* — is what binds your two specific questions (n_eff and evidence chain) to one underlying cause.

---

## Pointers

- **Gretton, Borgwardt, Rasch, Schölkopf, Smola** — *A Kernel Two-Sample Test*, JMLR 2012. The canonical Maximum Mean Discrepancy paper. §3 has the estimator; §6 has the test. Drop-in upgrade for any centroid-only comparison.
- **Székely, Rizzo** — *Energy statistics: A class of statistics based on distances*, Journal of Statistical Planning and Inference, 2013. Energy distance is MMD's distribution-free cousin; either works.
- **Rabanser, Günnemann, Lipton** — *Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift*, NeurIPS 2019. Empirical comparison of drift detectors. §4 explicitly shows that mean-only statistics miss dispersion shifts.
- **Anscombe, F.** — *Graphs in Statistical Analysis*, The American Statistician, 1973. The original demonstration that summary statistics agree across very different distributions. Centroid-only drift is the modern direct descendant of the problem Anscombe was warning about.

---

*Tool used hands-on: the `centroid_drift_demo.py` script in this folder. Numpy-only, no embedding-model dependency, runs in ~3 seconds. Modify the `0.2` and `2.0` spread constants to re-explore — try setting them equal to confirm `drift_score ~ 0` even when both cohorts are genuinely the same population.*
