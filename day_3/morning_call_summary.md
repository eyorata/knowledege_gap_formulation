# Morning call summary — Day 3

**Pair:** Eyoel Nebiyu (asker A) ↔ Addisu (asker B)
**Topic (cohort vote):** Training and post-training mechanics
**Date:** 2026-05-07
**Duration:** ~30 min
**Confirmed by both partners.**

---

## Question A — Eyoel's DPO/SimPO/ORPO gradient + KL-anchor question

**Original draft (what was ambiguous):** the question gestured at three loss families and one empirical observation (Delta B = −0.42 at p=0.992) without naming what kind of answer would close the gap. Risked landing as a "compare these three algorithms" survey rather than a gradient-level explanation tied to my specific run.

**Sharpening (Addisu's interrogation):** Ruth pushed me to pin four things — (a) what depth of derivation I needed (loss formulas only? full ∇_θ at one (x, y_w, y_l) pair? both?), (b) whether I cared about ORPO-the-algorithm or about TRL's `cpo_alpha` knob (these are not the same — `cpo_alpha` is CPO's additive NLL, not ORPO's odds ratio), (c) whether the directional `cpo_alpha=0.5` prediction was load-bearing or optional, (d) my actual operating point (Qwen2.5-3B + LoRA r=16 + n=128 — the small-n × high-capacity regime is where the drift mechanism bites). With those pinned, the resolvability property cleared 5/5: the explainer can give the gradients, the drift mechanism, and a defended directional prediction in ~1000 words plus a runnable demo.

**Final committed question:** scoped to *gradient-level derivation of where π_ref enters DPO's `z` and disappears in SimPO's `z`, the drift mechanism this licenses at small n × high LoRA capacity, and a defended directional prediction for `cpo_alpha=0.5`*. Grounding artifacts: `training_scripts/train_simpo.py` `CPO_ALPHA = 0.0` constant, `ablations/ablation_results.json` `delta_b` block, and the unsupported `methodology_rationale.md §3` paragraph that names two SimPO advantages while staying silent on the KL-anchor cost.

---

## Question B — Addisu's LoRA rank question

**Original draft (what was ambiguous):** Addisu's draft asked simultaneously *why* tiny LoRA adapters can shift behavior dramatically *and* why raising rank often doesn't help — two phenomena, one question, with no single mechanism named. Risked sprawling into a "LoRA from first principles" textbook chapter.

**Sharpening (Eyoel's interrogation):** I pushed Addisu to pin (a) which observation was load-bearing — answer: the rank-vs-quality plateau on the Week 10 Conversion Engine fine-tunes; (b) whether the *capacity* framing, the *expressive directions* framing, or the *compression-constraint* framing was the binding one — answer: they had been intuit-grouped as identical and Addisu wanted me to disambiguate; (c) whether `lora_alpha` and `target_modules` were in scope — out of scope, separate questions; (d) whether QLoRA / DoRA / VeRA / LoRA-XS variants needed coverage — out of scope. The answers narrowed the question to *one mechanism* (the intrinsic-low-rank hypothesis) explaining *both* observations Addisu had flagged.

**Final committed question:** scoped to *what LoRA mechanically adapts, why low rank suffices (intrinsic-low-rank hypothesis), and what allocated rank `r` actually controls vs. what it appears to control*. Grounding artifact: Addisu's Conversion Engine fine-tune logs showing flat held-out quality across r ∈ {4, 8, 16, 32}. Skipped (named honestly): QLoRA quantization, per-layer rank choice, `target_modules` selection, structured-update variants — each is its own explainer.
