# What LoRA Actually Adapts — and Why Higher Rank Doesn't Always Buy What It Looks Like It Should

**Day 3 explainer · Topic: Training and post-training mechanics · Asked by: [partner] · Explainer by: Eyoel Nebiyu**

---

## The question, anchored

You noticed two things in your Week 10 Conversion Engine fine-tunes that look paradoxical: tiny LoRA adapters often shifted model behavior dramatically, while raising LoRA rank sometimes barely helped and sometimes destabilized outputs. Both observations have a single mechanism behind them — the **intrinsic-low-rank hypothesis** of fine-tuning. This explainer narrows hard to that mechanism, derives why low rank suffices, and shows you with a runnable script what actually changes when you raise rank.

---

## What LoRA mechanically adapts

A transformer layer has weight matrices in the attention block (Q, K, V, O projections) and the MLP block (gate, up, down). For a hidden dimension `d`, each is roughly `d × d`. Full fine-tuning lets every entry of every matrix update; LoRA *freezes* them and adds a parallel learnable correction on a chosen subset:

```
forward pass at one layer:
  h = W_frozen · x  +  (α / r) · B · A · x
                            ↑          ↑
                       trainable   trainable
                        d × r       r × d
```

`B` is initialized to **zero**. `A` is initialized to a small random Gaussian. The combination `(α/r) · B · A` is the *update* — at training start it equals zero, so the net forward pass is identical to the frozen base model. As training proceeds, only `B` and `A` get gradients; the base weights never change.

Two consequences fall out:

- The full-rank weight matrix `W_frozen` is never altered. **No pretrained knowledge is forgotten.**
- The expressive update lives in a rank-`r` subspace. **No update outside that subspace is reachable, no matter how long you train.**

The second point is the crux of your question: what does choosing `r` do to the set of reachable updates?

---

## Why low rank works at all — the intrinsic-rank hypothesis

Hu et al. (LoRA, ICLR 2022) didn't argue low rank works because they wanted small models. They argued it works because the *update needed to adapt a pretrained model to a downstream task lies on a low-dimensional subspace of weight space*. This claim is empirically grounded by Aghajanyan et al. (ACL 2021), who showed pretrained language models can be fine-tuned through a randomly-projected ~200-dimensional update on tasks like GLUE and lose almost no performance. The full weight space has billions of dimensions; the *task-specific* subspace has hundreds.

The intuition: the pretrained model already encodes general syntactic, lexical, and semantic structure. Adapting it to a downstream classification or instruction-following task does not require *rewriting* that structure — it requires *nudging* a small number of directions in weight space that route the existing knowledge differently for the new objective.

LoRA at rank `r` exploits this by allocating exactly `r` learnable directions per matrix. If the task's *intrinsic rank* is `k`, then any `r ≥ k` will fit; any `r < k` will not. **`r` is a cap on expressive capacity, not a smooth quality knob.**

---

## Reproduce it

Run the demo at [`day_3/scripts/lora_rank_demo.py`](scripts/lora_rank_demo.py). It builds a synthetic 64×64 "task-specific update" of intrinsic rank 4 (plus a tiny noise floor — real fine-tuning targets are not *exactly* low-rank), fits LoRA at r = 2, 4, and 16 by gradient descent, and prints the SVD spectrum of the trained `B @ A`:

```
  allocated r  |  final rel err  | top-8 singular values of trained B @ A
  --------------------------------------------------------------------------
            2  |         0.5758  | 37.828  33.113  0.000  0.000  0.000  0.000  0.000  0.000
            4  |         0.0097  | 37.828  33.113  25.829  24.209  0.000  0.000  0.000  0.000
           16  |         0.0069  | 37.828  33.113  25.829  24.209  0.145  0.138  0.134  0.129
```

Three readings:

- **r = 2**: under-parameterized. Target's intrinsic rank is 4; rank-2 cannot reach it. Error stays high.
- **r = 4**: matches intrinsic rank exactly. Four large singular values, tight fit (rel-err 0.01).
- **r = 16**: over-parameterized. Still fits, but only the *first four* singular values are large (37.8, 33.1, 25.8, 24.2); the next four collapse to **0.14** — two orders of magnitude smaller. The optimizer found the four useful directions and drove the other twelve to noise-floor magnitude.

This is what your "higher rank only slightly improved performance" observation looks like under the hood. Once `r` exceeds the task's intrinsic rank, you are not gaining usable directions — you are allocating parameters that the optimizer drives toward zero, and they only contribute as gradient noise that can destabilize training on small data.

---

## The three framings of "what rank controls" — your specific options

All three of your options are formally true, but only one is *binding* in practice:

1. **"Higher rank increases expressive capacity"** — true, but only up to the task's intrinsic rank. Hu et al. §6.2 + Table 6 shows r = 4 and r = 64 reach similar quality on most GPT-3 adaptation benchmarks.
2. **"Allows adaptation across more directions"** — same answer reframed. r = 64 *can* express updates in 64 directions; the optimizer typically does not *find* useful gradient signal in all 64.
3. **"Reduces the compression constraint"** — true, but the constraint is rarely binding above the intrinsic rank.

Framing 1 is the binding one. Your observation — "higher rank sometimes barely improves" — is the expected mechanism, not a tuning failure.

---

## Two adjacent concepts

**`lora_alpha` is the effective learning rate of the adapter.** The forward pass scales the update by `α / r`. Raise `r` without raising `α` and per-direction scaling drops; raise `r` without lowering the optimizer LR and total update magnitude grows. Most "higher rank destabilized training" reports trace here, not to rank capacity. Rule of thumb: keep `α/r` constant (or set `α = r`).

**Effective rank ≠ allocated rank — audit it post-hoc.** Run SVD on the trained `B @ A` (one line of NumPy). Singular values concentrate on the first few directions; the rest decay sharply. If you trained at r = 32 and SVD shows 5 large values + 27 tiny, retrain at r = 8 with no loss. This audit is the cleanest empirical signal in the adapter-compression literature.

---

## What I deliberately skipped

QLoRA's 4-bit base-weight quantization layer; per-layer rank choice (different `r` for attention vs MLP); the `target_modules` selection question (which projections to LoRA at all); structured-update variants (DoRA, VeRA, LoRA-XS). Each is its own explainer. The mechanism above is what binds your specific observation — small adapter sufficient + larger rank only marginally helpful — to one underlying cause.

---

## Pointers

- **Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang, Chen** — *LoRA: Low-Rank Adaptation of Large Language Models*, ICLR 2022. arXiv: 2106.09685. §4 introduces the parallel-update form; §6.2 + Table 6 has the rank-vs-quality empirical curves on GPT-3 that show the "r = 4 is enough" pattern.
- **Aghajanyan, Zettlemoyer, Gupta** — *Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning*, ACL 2021. arXiv: 2012.13255. The empirical foundation of "task-specific updates live on a low-dim manifold" — Table 1 shows GLUE recovery via random projections at d_int as low as 200.

---

*Tool used hands-on: the `lora_rank_demo.py` script in this folder. Numpy-only, no PyTorch dependency, runs in ~5 seconds. Modify `TRUE_RANK` in the script to test your own intuition — try setting it to 8 and watch r = 4 fail, r = 8 succeed, r = 16 over-allocate.*
