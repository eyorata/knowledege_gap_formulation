# signoff.md — Day 3 (asker side)

**Asker:** Eyoel Nebiyu (`@eyorata`)
**Explainer received from:** Ruth Solomon
**Date:** 2026-05-07
**Verdict:** **Closed**

---

## What I now understand that I did not before

The load-bearing reframe landed at gradient level: **DPO contains a "stay close to π_ref" gravitational force inside its loss; SimPO removes that force entirely**, and the explainer shows exactly where it disappears. Specifically, the DPO and SimPO gradients at one preference pair share the same outer form

`∇_θ ℒ ∝ -β σ(-z) [∇_θ log π_θ(y_w|x) - ∇_θ log π_θ(y_l|x)]`

but their `z` differs: DPO's `z` measures the chosen-vs-rejected margin **relative to π_ref**, while SimPO's `z` is the bare margin minus a constant `γ`. That `π_ref` term in `z` is the KL anchor; its absence in SimPO's `z` is the entire mechanism behind my Delta B = −0.42. I could not have written that paragraph 24 hours ago.

The empirical reading also landed: my training log's "train_acc = 1.00 by step 5, eval_acc plateaus at 0.50 forever" signature is the *expected* signature of unconstrained preference optimization on small data — not a tuning failure, not a data bug, the predicted behavior of removing the KL anchor at our operating point (Qwen2.5-3B + LoRA r=16 + n=128). That changes how I read the same file: it's no longer a "what went wrong" log, it's a "what was always going to happen at `cpo_alpha=0`" log.

The directional prediction is committed and falsifiable: `cpo_alpha=0.5` should move Delta B from −0.42 toward roughly **−0.15 to 0.0**, defended on the gradient (the CPO-style additive SFT term contributes `α · ∇_θ ℒ_SFT`, which pulls the policy back toward the fluent-text manifold even as the SimPO margin gradient pushes it outward). That's a ~60-minute Colab T4 run I can verify, and it has a clean falsification condition (Delta B remains ≤ −0.30 → drift hypothesis is wrong, or α is too small).

The strongest thing in the explainer is one I did not ask for: **the CPO-vs-ORPO correction**. The explainer caught that TRL's `cpo_alpha` controls **CPO**'s additive NLL regularization (Xu et al. 2024), not ORPO's odds-ratio loss (Hong, Lee, Thorne 2024), and stated the distinction explicitly instead of letting the conflation propagate. My queued ablation is therefore a CPO-style run, and the model card needs to say so.

## The one residual gap (deliberate scope tradeoff)

The runnable demo computes **margins** for DPO and SimPO, not the **gradient triple** the question literally asked for, and it does not include ORPO's odds-ratio gradient (since the explainer made the principled call to disambiguate `cpo_alpha` from ORPO and stay focused on the CPO-style stabilization mechanism that actually maps to my code). I'm logging "ORPO odds-ratio gradient + a three-way numpy gradient demo" as a candidate Day-4 cohort gap rather than a hole in this explainer — the disambiguation Ruth made is more valuable than ticking that one rubric box would have been.

## Grounding commit — what changes in my Week 11 portfolio

Three concrete edits land on `eyorata/sales_evaluation_bench` (see [`grounding_commit.md`](grounding_commit.md) for the diff-level detail):

1. **`methodology_rationale.md §3`** — append a "what this choice costs us" paragraph that names the KL-anchor mechanism and ties it to the Delta B = −0.42 observation. The current paragraph names two SimPO advantages (length normalization, halved VRAM) and is silent on the cost of dropping the reference policy. After this edit, it isn't.
2. **`tenacious_bench_v0.1/MODEL_CARD.md` limitations** — add the CPO-vs-ORPO disambiguation note so the model card does not silently propagate the conflation.
3. **`ablations/queued_v0.2.md`** — queue the `cpo_alpha=0.5` run with the explainer's directional prediction (Delta B → −0.15 to 0.0) and an explicit falsification condition.
