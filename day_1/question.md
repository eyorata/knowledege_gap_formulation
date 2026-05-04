# question.md — Day 1

**Topic (cohort-voted):** Evaluation and statistics — bootstrap confidence intervals for agent benchmarks at small n
**Asker:** Eyoel Nebiyu (`@eyorata`)
**Partner (explainer):** *[fill in once paired]*
**Date:** *[Day 1 date]*

---

## The question

> **In my Week 11 Path B ablation harness, the paired-bootstrap output for `delta_a` (n = 12 held-out preference pairs) reports `bootstrap_mean_diff = +0.2512`, `bootstrap_p_value = 0.0316` (one-sided: `P(trained_acc ≤ baseline_acc)`), and simultaneously `bootstrap_ci_low = 0.00`, `bootstrap_ci_high = 0.50` — i.e., the percentile-method 95 % CI lower bound lands exactly on zero while the one-sided p-value clears 0.05. Why does the percentile-method CI lower bound coincide with exactly 0.00 here while the p-value reports a "significant" lift, what is the small-n discreteness mechanism that makes those two numbers apparently disagree, and as a Forward-Deployed Engineer reporting to a non-technical executive at small n, which of the two numbers (CI or p) should I treat as the binding statistical claim and why?**

The question is one sentence on purpose. The "two numbers in apparent tension" framing is the load-bearing diagnostic; the asked-for output is a mechanism-level explanation plus a defensible reporting rule for the FDE memo case.

---

## Why this matters in my work (grounding)

This question is grounded in a specific artifact. From `ablations/ablation_results.json` in the [Tenacious-Bench v0.1 repo](https://github.com/eyorata/sales_evaluation_bench), the `delta_a` block reads:

```json
"delta_a": {
  "trained_acc":         0.4167,
  "baseline_acc":        0.1667,
  "raw_lift_pp":         0.25,
  "bootstrap_mean_diff": 0.251225,
  "bootstrap_ci_low":    0.0,
  "bootstrap_ci_high":   0.5,
  "bootstrap_p_value":   0.0316,
  "verdict":             "POSITIVE_NOT_SIGNIFICANT"
}
```

That JSON feeds two downstream public artifacts:
1. **[memo/memo.md](https://github.com/eyorata/sales_evaluation_bench/blob/master/memo/memo.md), Page 1, "Headline numbers" table:** I report Delta A as "+25 pp, 95 % CI [0.00, 0.50], paired bootstrap p = 0.0316" — and on Page 2 I lean on Delta B's tighter CI rather than Delta A's CI to ground the production recommendation.
2. **[blog/tenacious_bench_v0.1_blog.md](https://github.com/eyorata/sales_evaluation_bench/blob/master/blog/tenacious_bench_v0.1_blog.md), §5 "The honest result":** I write that the CI "grazes zero" because of "small-n quantization." That phrase is currently smuggled in without a derivation. I don't actually know whether "quantization" is the right term, what the resample-level mechanism is, or whether my reporting choice (lead with p-value, treat CI conservatively) is statistically defensible or just rhetoric.

The bootstrap is run by [docs/act4_colab_path_b.md Cell 14](https://github.com/eyorata/sales_evaluation_bench/blob/master/docs/act4_colab_path_b.md), 10 000 resamples, paired by pair-index. Source code:

```python
def paired_bootstrap(a, b, n=10000, seed=42):
    rng = np.random.default_rng(seed)
    a, b = np.array(a), np.array(b)
    diffs = []
    for _ in range(n):
        idx = rng.integers(0, len(a), size=len(a))
        diffs.append(a[idx].mean() - b[idx].mean())
    diffs = np.array(diffs)
    return {
        "mean_diff": float(diffs.mean()),
        "ci_low":    float(np.percentile(diffs,  2.5)),
        "ci_high":   float(np.percentile(diffs, 97.5)),
        "p_value":   float((diffs <= 0).mean()),  # one-sided P(trained <= baseline)
    }
```

Inputs `a` and `b` are 0/1 correctness vectors (`prefers_chosen`) of length 12 from `ablations/held_out_traces.jsonl`.

---

## What a satisfying answer looks like (one paragraph)

A satisfying explainer would (a) **derive concretely** why the percentile-method 95 % CI lower bound at n = 12 with 0/1 outcomes is quantized — i.e., what specific resample-level events produce a `diff = 0.00` mass large enough to land the 2.5th percentile exactly there; (b) **show the (non-bijective) relationship** between the percentile lower bound and the one-sided `(diffs ≤ 0).mean()` p-value, ideally with a small simulation that varies n from 12 → 30 → 100 to expose where they decouple and where they re-converge; and (c) **give a clear FDE reporting rule** — "at n < 30 with discrete outcomes, lead with the p-value; report the CI as the honest range of where individual resamples land; do not claim non-significance from a CI that grazes zero alone" — or whatever the explainer judges to be the defensible rule, defended against the alternative.

---

## Scope: in / out

**In scope (what the explainer should cover):**
- Resample-level mechanism for `ci_low = 0.00` at n = 12 with 0/1 outcomes (quantization, ties, the discreteness of the resampling distribution).
- Why the percentile method is the version my harness uses (vs. basic / BCa) and whether it's the right choice at small n.
- The mathematical relationship between `np.percentile(diffs, 2.5)` and `(diffs <= 0).mean()` when both are computed over the same resample distribution.
- A small worked simulation a reader can paste and run — e.g., 12-pair vs 30-pair vs 100-pair side-by-side.
- A defended rule for which number to lead with in an executive memo at small n.

**Out of scope (do not pad with):**
- A general bootstrap tutorial. I know what bootstrap is; I just don't understand the small-n quantization regime.
- Bayesian alternatives. Stay frequentist; that's the regime my harness uses.
- BCa or studentized variants beyond a one-sentence pointer. I want the percentile-method derivation since that's what my code uses.
- Multiple-comparisons corrections across Delta A / B / C. Single-test inference is the focus.

---

## Self-check against the four rubric properties

| Property | Self-rating (1–5) | Justification |
|---|---:|---|
| **Diagnostic** | 5 | Names a specific apparent contradiction (`ci_low = 0.00` ∧ `p = 0.0316`) at a specific n (12) on a specific test (paired percentile-method bootstrap with 0/1 outcomes). Not "How does bootstrap work?" |
| **Grounded in cohort work** | 5 | Cites the exact JSON block in `ablations/ablation_results.json`, the harness code in `docs/act4_colab_path_b.md` Cell 14, and the two downstream artifacts (memo + blog) where the unexplained "small-n quantization" phrase currently lives. |
| **Generalizable** | 5 | Every FDE running an agent benchmark at n < 30 hits this exact pattern. Llm-as-a-judge held-out slices, preference-pair eval, retail/B2B small-n A/B — all have this regime. The current internet answer to "ci_low=0 AND p<0.05, what gives?" is mostly hand-waving. |
| **Resolvable in one explainer** | 5 | A 600–1 000 word blog can derive the quantization mechanism, run the n = 12 / 30 / 100 simulation, and state the FDE reporting rule. Not a textbook chapter; not a one-line answer. |

---

## Pointers to start the explainer (offered as starting points, not required)

- Efron & Tibshirani, *An Introduction to the Bootstrap* (1993), §13.3 "Percentile intervals" — the canonical small-n caveat is here.
- Hesterberg, *What Teachers Should Know About the Bootstrap* (2015) — discusses percentile vs. BCa at small n and the quantization issue.
- The 0/1 outcome case is identical to a McNemar-test setup; the "exact paired binomial" interpretation is one bridge to the p-value.
- A 30-line numpy simulation that varies n and plots `(ci_low, p_value)` jointly is the cleanest way to expose the regime.

---

*This question is final for the day per morning-call sign-off. Partner: hand back the explainer by the evening call. I'll sign off "closed / partially / not closed" and write the grounding commit pointing to the specific paragraph I rewrite in `blog/tenacious_bench_v0.1_blog.md` §5 once your explainer lands.*
