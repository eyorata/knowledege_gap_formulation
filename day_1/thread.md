# Tweet thread - Day 1 (post-ready)

**1/**
I hit a weird result in a paired bootstrap with `n=12`: `95% CI = [0.00, 0.50]` but one-sided `p = 0.0316`. Looks contradictory, but it isn't. They summarize different parts of the same resample distribution.

**2/**
At small `n` with binary outcomes, bootstrap diffs are discrete (quantized). With only 12 pairs, many resamples land exactly at `diff = 0.00`. That spike can force the 2.5th percentile (CI lower bound) to be exactly zero.

**3/**
My p-value was computed as `mean(diffs <= 0)`. It asks: “How often did resamples show no lift or negative lift?” Here: 3.16%. So ~96.84% of resamples still showed positive lift.

**4/**
So `ci_low = 0.00` and `p = 0.0316` can both be true. In small-sample discrete regimes, “CI touches zero” is not automatically “no signal.” You need the mechanism, not a one-line rule.

**5/**
Practical FDE memo rule I now use for small-`n` paired binary evals: lead with directional p-value, report CI as uncertainty width, and explicitly state small-sample limitations.

**6/**
I validated this with a simple simulation (`n=12 -> 30 -> 100`): as sample size grows, the zero-spike effect shrinks and CI/p summaries re-align. This closed a real gap in how I explain benchmark evidence.