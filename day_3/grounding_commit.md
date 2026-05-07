# grounding_commit.md — Day 3 (asker side)

**Asker:** Eyoel Nebiyu (`@eyorata`)
**Date:** 2026-05-07
**Verdict from [`signoff.md`](signoff.md):** Closed
**Companion docs:** [`question.md`](question.md), [`explainer.md`](explainer.md) (the one I wrote for my partner), `partner_explainer.md` (Ruth Solomon's explainer to me — kept locally), [`signoff.md`](signoff.md)

---

## What this commit is

The paired explainer with Ruth Solomon closed my Week 11 question on **why removing the KL anchor in SimPO let the LoRA policy drift away from the prompt-aligned manifold**, and committed to a defended directional prediction for `cpo_alpha=0.5`. This commit is the asker-side grounding — three edits to my Week 11 portfolio that turn the new understanding into permanent artifacts: an honest rewrite of the methodology rationale, a limitation note in the model card, and a queued ablation that lets me verify the prediction.

**Target repo:** [`eyorata/sales_evaluation_bench`](https://github.com/eyorata/sales_evaluation_bench)
**Files changed:** 3
**Branch:** `day3-grounding-kl-anchor-cost`

---

## The edits

### 1. `methodology_rationale.md §3` — honest rewrite

**Before** (current `master` HEAD, `methodology_rationale.md` line 30):

> **SimPO (Meng, Xia, Chen, NeurIPS 2024)** is the chosen training algorithm. The decisive property for Path B on Tenacious data is reference-free, length-normalized scoring: ... DPO without length normalization would penalize the short chosen outputs by their margin term; SimPO does not. The reference-free property also halves Colab T4 VRAM, which is the binding constraint for the Day-5 run.

The paragraph names two SimPO advantages (length normalization, halved VRAM) and is **silent on the cost of dropping the reference policy**. That silence is what Ruth's explainer surfaced at gradient level.

**After** (this commit, appended to §3):

> **What this choice costs us, and why we name it.** Removing the reference policy removes the KL anchor that, in DPO's gradient, enters through the `z` term as `[log(π_θ(y_w|x)/π_ref(y_w|x)) − log(π_θ(y_l|x)/π_ref(y_l|x))]` and pulls the trained policy toward π_ref at every step. SimPO's `z` drops the π_ref terms entirely, so the only optimization pressure on the LoRA policy is the bare chosen-minus-rejected margin. At our operating point — high-capacity LoRA (r=16) on a small backbone (3B) trained on n=128 pairs — that pressure is enough to drive the policy to a region that perfectly separates the training pairs (train_acc = 1.00 by step 5; see [`training/training_run.log`](training/training_run.log)) but lies far from the SFT manifold the held-out evaluations come from (eval_acc plateaus at 0.50 through step 300). This drift is the predicted behavior of unconstrained preference optimization on small data, not a tuning failure. **It is the load-bearing explanation for why Delta B = −0.42 at p=0.992 in [`ablations/ablation_results.json`](ablations/ablation_results.json)** — the prompt-engineered baseline, which never left the SFT manifold, beat the trained LoRA, which did.

### 2. `tenacious_bench_v0.1/MODEL_CARD.md` — limitations section gets a CPO-vs-ORPO note

A new bullet in the "Known limitations and caveats" section:

> **Algorithm naming caveat.** The training script's `cpo_alpha` knob (in [`training_scripts/train_simpo.py`](training_scripts/train_simpo.py)) controls **CPO**'s additive NLL/SFT regularization term (Xu et al. 2024), not ORPO. ORPO (Hong, Lee, Thorne, EMNLP 2024) uses an odds-ratio loss term that is structurally different. The TRL `CPOTrainer` spans the SimPO ↔ CPO continuum cleanly; reaching ORPO's formulation would require a different trainer. Any future ablation with `cpo_alpha > 0` should be reported as **CPO-style SFT regularization**, not as ORPO. This caveat is added to prevent the same conflation from propagating to anyone who reads the model card.

### 3. `ablations/queued_v0.2.md` — new entry

A queued ablation entry with the directional prediction the explainer committed to:

> **Q-2: SimPO + CPO-style SFT regularization.** Re-run the Path B training with `CPO_ALPHA = 0.5` (all other hyperparameters identical to the v0.1 run); evaluate Delta B on the same held-out preference slice. **Predicted direction:** Delta B moves from −0.42 toward roughly **−0.15 to 0.0** — the CPO additive term contributes `α · ∇_θ ℒ_SFT` to the gradient, which pulls the policy back toward the fluent-text manifold even as the SimPO margin gradient pushes it outward. **Falsification condition:** if Delta B remains ≤ −0.30 with `cpo_alpha=0.5`, the drift hypothesis is wrong (or the regularization weight is too small), and Path B should be reconsidered against the prompt-engineered baseline as the primary judge. Estimated cost: ~60 minutes Colab T4 + zero new data.

---

## What changed in my mental model

Before this paired explainer, I would have read the v0.1 training log as "the run failed and I don't know why." After the explainer, I read it as: **the perfect-train / flat-eval signature is the predicted behavior of unconstrained preference optimization at small n, and the fix is a regularization term — not a new dataset, not a new backbone, not a new algorithm family**. That distinction is the difference between "Path B was a wrong call" and "Path B was under-regularized," and the queued `cpo_alpha=0.5` run is the cheapest experiment that can tell the two apart.

The CPO-vs-ORPO disambiguation matters less in absolute impact but matters for honesty: I would have published a model card that called the queued run an "ORPO ablation" and propagated the conflation to anyone who reads the bench. The model card edit closes that.

---

## What this commit deliberately does not do

It does *not* run the `cpo_alpha=0.5` ablation. The queued entry in `ablations/queued_v0.2.md` is the commitment; the run itself is a Day-4-or-later cohort experiment, not a Day-3 deliverable. It does *not* rewrite `methodology.md` (the algorithm-section description), only `methodology_rationale.md` (the "why this algorithm" defense) — that's the file that was silently overclaiming. It also does *not* attempt to add ORPO's odds-ratio gradient anywhere; the one residual gap from `signoff.md` is logged as a candidate Day-4 cohort topic instead.

---

*The commit will land on `eyorata/sales_evaluation_bench` as a single PR titled `day3: name the KL-anchor cost in methodology_rationale §3 + queue cpo_alpha=0.5 ablation`. Link will be added here once pushed.*
