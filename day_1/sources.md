# Sources - Day 1 explainer (small-n paired bootstrap: CI vs p-value)

The two canonical sources cited in `explainer.md`, plus the hands-on pattern used.

---

## Canonical source 1 - Efron & Tibshirani (1993)

**Reference:** Efron, B., & Tibshirani, R. J. *An Introduction to the Bootstrap*. Chapman & Hall/CRC, 1993.  
**Why canonical:** Foundational text for bootstrap inference and percentile-interval behavior.  
**What it contributed:** Grounding for how percentile bootstrap CIs are constructed and why small-sample settings can produce edge effects.

---

## Canonical source 2 - Hesterberg (2015)

**Reference:** Hesterberg, T. C. *What Teachers Should Know About the Bootstrap: Resampling in the Undergraduate Statistics Curriculum*. The American Statistician, 69(4), 2015.  
**Why canonical:** Widely cited practical treatment of bootstrap behavior and small-n caveats.  
**What it contributed:** Practical interpretation guidance for small-sample/discrete-outcome bootstrap intervals and why percentile intervals can mislead if interpreted naively.

---

## Tool / pattern run hands-on

**Pattern:** Runnable paired-bootstrap simulation over binary outcomes with fixed seeds and varying sample size (`n=12`, `n=30`, `n=100`).  
**What was demonstrated:**
1. At `n=12`, lower CI can land exactly at `0.00` while one-sided `p` remains small.
2. As `n` grows, the discrete spike at zero weakens and CI/p-value behavior re-converges.
3. This supports the memo rule used in the explainer: treat p-value as directional signal and CI as uncertainty width in this regime.

Attribution is clean and no fabricated references are used.