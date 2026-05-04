# Tweet thread - Day 1, on why `ci_low = 0.00` and `p = 0.0316` can both be true

Six tweets, post-evening-call revision. Each tweet stands alone for readers who do not click through.

---

**1/**
In a 12-pair benchmark, I got `95% CI = [0.00, 0.50]` and `one-sided p = 0.0316` for the same lift estimate. Looks contradictory. It isn't. These two numbers answer different questions about the same bootstrap distribution.

---

**2/**
At small n with binary outcomes, paired-bootstrap differences are discrete (quantized). With only 12 pairs, many resamples land exactly at `diff = 0.00`. That spike at zero can pull the 2.5th percentile to exactly `0.00`.

---

**3/**
The p-value here is `mean(diffs <= 0)`. It asks: "How often did resamples show no lift or negative lift?" If that is 3.16%, then 96.84% of resamples still show positive lift. That can coexist with a CI edge at zero.

---

**4/**
So the right interpretation is not "CI includes zero therefore no signal." In this small-n discrete regime, CI-grazes-zero can be a mechanical artifact of quantization, not evidence that direction is ambiguous.

---

**5/**
Practical FDE reporting rule I learned: for small-n binary paired evals, lead with directional p-value for sign, report CI as uncertainty width, and explicitly state sample-size limits instead of over-claiming certainty.

---

**6/**
I documented the mechanism, runnable simulation (`n=12 -> 30 -> 100`), and memo-ready language in the explainer. This closed my gap and fixed how I write the Delta A interpretation in my Week 11 artifacts.

---

*Thread is final post-evening-call revision.*