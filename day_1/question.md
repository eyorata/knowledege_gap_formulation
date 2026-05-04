# question.md - Day 1

**Topic (cohort-voted):** Evaluation and statistics - bootstrap confidence intervals for agent benchmarks at small n  
**Asker:** Eyoel Nebiyu (`@eyorata`)  
**Partner (explainer):** Abdulaziz  
**Date:** 2026-05-04

---

## The question

> **In my Week 11 Path B ablation harness, the paired-bootstrap output for `delta_a` (n = 12 held-out preference pairs) reports `bootstrap_mean_diff = +0.2512`, `bootstrap_p_value = 0.0316` (one-sided: `P(trained_acc <= baseline_acc)`), and simultaneously `bootstrap_ci_low = 0.00`, `bootstrap_ci_high = 0.50` - i.e., the percentile-method 95% CI lower bound lands exactly on zero while the one-sided p-value clears 0.05. Why does the percentile-method CI lower bound coincide with exactly 0.00 here while the p-value reports a "significant" lift, what is the small-n discreteness mechanism that makes those two numbers apparently disagree, and as a Forward-Deployed Engineer reporting to a non-technical executive at small n, which of the two numbers (CI or p) should I treat as the binding statistical claim and why?**

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
1. **[memo/memo.md](https://github.com/eyorata/sales_evaluation_bench/blob/master/memo/memo.md), Page 1, "Headline numbers" table:** I report Delta A as "+25 pp, 95% CI [0.00, 0.50], paired bootstrap p = 0.0316" and on Page 2 I lean on Delta B's tighter CI rather than Delta A's CI to ground the production recommendation.
2. **[blog/tenacious_bench_v0.1_blog.md](https://github.com/eyorata/sales_evaluation_bench/blob/master/blog/tenacious_bench_v0.1_blog.md), Section 5 "The honest result":** I write that the CI "grazes zero" because of "small-n quantization." That phrase is currently smuggled in without a derivation.

The bootstrap is run by [docs/act4_colab_path_b.md Cell 14](https://github.com/eyorata/sales_evaluation_bench/blob/master/docs/act4_colab_path_b.md), 10,000 resamples, paired by pair-index. Source code:

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
        "p_value":   float((diffs <= 0).mean()),
    }
```

Inputs `a` and `b` are 0/1 correctness vectors (`prefers_chosen`) of length 12 from `ablations/held_out_traces.jsonl`.