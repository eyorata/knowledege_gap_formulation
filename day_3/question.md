# question.md — Day 3

**Topic (cohort-voted):** Training and post-training mechanics — the gradient mechanics of DPO vs SimPO vs ORPO and the role of KL / SFT regularization
**Asker:** Eyoel Nebiyu (`@eyorata`)
**Partner (explainer):** *[fill in once paired]*
**Date:** 2026-05-07

---

## The question

> **In my Week 11 Path B SimPO judge ([`sales_evaluation_bench`](https://github.com/eyorata/sales_evaluation_bench): Qwen2.5-3B + LoRA r=16, 128 LLM-rewritten preference pairs, β=2.0, γ=1.0, `cpo_alpha=0.0`), the trained model scored `0.417` on the held-out preference slice while the *same backbone with no training* and a careful Tenacious-rubric system prompt scored `0.833` on the same slice — Delta B = −42 pp at paired-bootstrap p = 0.992. SimPO is reference-free (no KL anchor to a frozen reference policy); the SimPO paper presents this as a feature that halves VRAM. So: **what is the gradient-level mechanism by which removing the KL anchor lets the LoRA policy drift away from the prompt-aligned manifold during preference fine-tuning, how does that drift compound with small training data (n=128) on a small backbone (3B), and would switching to ORPO's monolithic SFT-regularization term (`cpo_alpha > 0`) have constrained the drift back toward the prompt-aligned region — concretely, what direction should I expect a `cpo_alpha=0.5` ablation run to move my Delta B number, and on what gradient-mechanism grounds?***

The question is one sentence on purpose. The "Delta B negative at p=0.99" is the load-bearing observation; the asked-for output is a gradient-level explanation plus a directional prediction the explainer is willing to defend.

---

## Why this matters in my work (grounding)

This question is grounded in three specific artifacts:

1. **[`training_scripts/train_simpo.py`](https://github.com/eyorata/sales_evaluation_bench/blob/master/training_scripts/train_simpo.py)** — has the literal hyperparameters: `SIMPO_BETA = 2.0`, `SIMPO_GAMMA = 1.0`, `CPO_ALPHA = 0.0  # 0 = pure SimPO; nonzero adds CPO's SFT-loss regularization`. The `cpo_alpha=0.0` choice is a load-bearing knob I set without defending its consequence on training stability — I copied the SimPO paper's recommended default into a `CPOTrainer` config that supports the full DPO/SimPO/ORPO continuum.

2. **[`ablations/ablation_results.json`](https://github.com/eyorata/sales_evaluation_bench/blob/master/ablations/ablation_results.json)** `delta_b` block:
   ```json
   "delta_b": {
     "trained_acc": 0.4167, "prompt_acc": 0.8333,
     "raw_lift_pp": -0.4167,
     "ci_low": -0.75, "ci_high": 0.0, "p_value": 0.9922,
     "verdict": "FLAT_OR_NEGATIVE"
   }
   ```
   This is the empirical anchor. The number is honest and reported in the public memo and blog.

3. **[`methodology_rationale.md`](https://github.com/eyorata/sales_evaluation_bench/blob/master/methodology_rationale.md) §3** — I currently defend SimPO over DPO with: *"DPO without length normalization would penalize the short chosen outputs by their margin term; SimPO does not. The reference-free property also halves Colab T4 VRAM."* That paragraph names two SimPO advantages but is silent on the KL-anchor *cost* — which is the load-bearing question for why my Delta B might be negative. I cannot defend that paragraph if a senior engineer asks "what does removing the KL term cost you in training stability at small n?"

The training run that produced the numbers above is in [`training/training_run.log`](https://github.com/eyorata/sales_evaluation_bench/blob/master/training/training_run.log) — eval accuracy plateaued at 0.50 after step 50 and never improved through step 300, while train accuracy hit 1.00 at step 5 and stayed there. That signature (perfect train, flat eval) is consistent with policy drift to a manifold that perfectly fits 128 templated chosen/rejected pairs but doesn't generalize — which is exactly the failure mode KL-regularization in DPO is designed to prevent.

---

## What a satisfying answer looks like (one paragraph)

A satisfying explainer would (a) **derive concretely** the gradient of each loss — DPO, SimPO, ORPO — w.r.t. policy log-probabilities at a single (prompt, chosen, rejected) pair, showing where the KL term enters DPO's gradient and where it does *not* enter SimPO's; (b) **name the drift mechanism**: at small n with a high-capacity LoRA, the SimPO-only gradient pulls the policy toward maximizing the chosen-minus-rejected margin without any "stay close to the reference" force, so the policy converges to a region that perfectly separates training pairs but lies far from the SFT manifold the held-out evaluations come from; (c) **predict directionally** what `cpo_alpha=0.5` would do to Delta B — the prediction should be defended on the gradient (the cpo_alpha term adds a per-token NLL toward the chosen response, which constrains the policy from drifting too far from a "fluent text" manifold) and should commit to a sign (Delta B improves toward zero / Delta B unchanged / Delta B gets worse) with a one-sentence justification.

---

## Scope: in / out

**In scope (what the explainer should cover):**
- Side-by-side gradient derivations of DPO, SimPO, and ORPO at one (prompt, chosen, rejected) pair. Symbolic, not exhaustive.
- The KL-anchor mechanism in DPO: where in the gradient it enters, what it constrains.
- Why SimPO's reference-free formulation is *equivalent* to setting the KL coefficient β\_KL → 0 in a particular limit, and what fails when n is small.
- ORPO's monolithic objective: the additive SFT loss term, why Hong et al. argue it stabilizes training without a separate reference model.
- A directional prediction for what `cpo_alpha=0.5` would do to my specific run, with the gradient argument behind it.
- A small numpy / pseudocode demonstration of the three gradients that a reader can run.

**Out of scope (do not pad with):**
- General preference-tuning history. Skip the Christiano-et-al. / Ouyang-et-al. lineage; cite only if a specific section is load-bearing.
- IPO, KTO, RLOO. They're not in my code path.
- Reward-model-based RLHF (PPO). Different family; would dilute focus.
- LoRA-rank choice or learning-rate sweeps. Separate questions.
- Empirical claims about Delta B that aren't grounded in the gradient derivation. The whole point is to make this *mechanism-level*, not "I tried it once and it worked."

---

## Self-check against the four rubric properties

| Property | Self-rating (1–5) | Justification |
|---|---:|---|
| **Diagnostic** | 5 | Names a specific gradient-level mechanism question (where does the KL anchor enter and what does removing it cost), tied to a specific empirical observation (Delta B = −42 pp at p=0.99) and a specific algorithmic switch (`cpo_alpha=0.0 → 0.5`). Not "how does SimPO work?" |
| **Grounded in cohort work** | 5 | Cites three artifacts with line-level pointers: the `cpo_alpha` constant in `train_simpo.py`, the `delta_b` block in `ablation_results.json`, and the unsupported `methodology_rationale.md §3` paragraph that asserts SimPO advantages without naming the KL-anchor cost. The asker-side *grounding commit* lands cleanly: I will rewrite that §3 paragraph after the explainer. |
| **Generalizable** | 5 | Every FDE doing reference-free preference fine-tuning at small data on a small open-weights backbone (Qwen / Llama / Phi class) hits this regime. The DPO ↔ SimPO ↔ ORPO choice is among the top decisions in any post-training pipeline in 2026. |
| **Resolvable in one explainer** | 5 | The SimPO paper (Meng, Xia, Chen, NeurIPS 2024) §4 and the ORPO paper (Hong, Lee, Thorne, EMNLP 2024) §3 both have the gradient derivations needed; an 800–1000 word explainer can do the side-by-side derivation, the drift argument, and the directional prediction. Not a textbook chapter; not a one-line answer. |

---

## Pointers to start the explainer (offered as starting points, not required)

- **Rafailov, Sharma, Mitchell, Manning, Ermon, Finn,** *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*, NeurIPS 2023 — §4 has the canonical DPO gradient derivation and the KL-implicit argument.
- **Meng, Xia, Chen,** *SimPO: Simple Preference Optimization with a Reference-Free Reward*, NeurIPS 2024 — §3 derives the SimPO loss; §4 ablates length-normalization but is largely silent on the small-n stability cost of dropping the reference.
- **Hong, Lee, Thorne,** *ORPO: Monolithic Preference Optimization without Reference Model*, EMNLP 2024 — §3 introduces the additive SFT log-likelihood term that `cpo_alpha` controls in TRL's `CPOTrainer`.
- The TRL source for `CPOTrainer` (https://github.com/huggingface/trl/blob/main/trl/trainer/cpo_trainer.py) — the `loss_type="simpo"` branch and the `cpo_alpha` blend let the same trainer span the entire SimPO ↔ CPO ↔ ORPO continuum, which is why my specific question is operationally tractable: I can re-run with `cpo_alpha=0.5` and verify the explainer's prediction in ~60 minutes of Colab time.

---

*This question is final post-morning-call sign-off. Partner: hand back the explainer by the evening call. I'll sign off "closed / partially / not closed" and write the grounding commit pointing to the rewritten paragraph in `methodology_rationale.md §3` once your explainer lands. The cleanest grounding commit, if the explainer makes a directional prediction I can defend, is to add a queued ablation entry in `ablations/queued_v0.2.md` for the `cpo_alpha=0.5` run and to update the model card's "limitations" section to name the reference-free-drift risk.*
