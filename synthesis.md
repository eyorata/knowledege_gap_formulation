# Week 12 Synthesis — Knowledge Gap Formulation

**Author:** Eyoel Nebiyu (`@eyorata`)
**Window:** 2026-05-04 → 2026-05-08 (four pair-days)
**Companion artifacts:** [`canonical_list.md`](canonical_list.md), [`portfolio_update.md`](portfolio_update.md), and the four `day_N/` folders.

---

## What Week 12 actually was

The week was four pair-days. Each day, I produced two artifacts: a one-sentence diagnostic question grounded in a *specific line in a specific Week 10 or Week 11 artifact I had already published* (asker side), and an explainer for a partner's question of the same shape (explainer side). The non-negotiable was that every gap had to land as a **grounding commit** — an edit to an already-public artifact in my Week 10 (`conversion_engine`) or Week 11 (`sales_evaluation_bench`) repo that converted a hand-wavy claim into a mechanism-level claim. Five grounding commits landed: two from Day 1, one each from Days 2–4.

The discipline I am taking out of this week is that the *load-bearing question* is rarely "how does X work?" — it is "what is the precise mechanism by which the artifact I already published is overclaiming, and what is the smallest concrete edit that closes the gap?"

---

## The ten gaps closed

### Four I named (asker side)

**1. Day 1 — Why `ci_low = 0.00` and `p = 0.0316` can both be true at n=12.**
My Week 11 paired-bootstrap output for Delta A reported a 95% CI lower bound exactly at zero alongside a one-sided p-value of 0.0316. My blog draft hand-waved this as "small-n quantization." Abdulaziz's pairing pinned the actual mechanism: with binary outcomes at n=12, paired-bootstrap diffs are discrete and place real probability mass at exactly `diff = 0.00`, which can pin the 2.5th percentile to zero while only 3.16% of resamples are non-positive. The asker-side grounding commit replaced the hand-wave with an explicit derivation in `blog/tenacious_bench_v0.1_blog.md` and added a small-n FDE reporting rule (lead with directional p-value, report CI as uncertainty width).

**2. Day 2 — Where the commit point for idempotent side effects belongs in dual-backend agents.**
The `conversion_engine` orchestrator runs HubSpot writes via either REST or MCP, and my Week 10 artifact never specified where retries should be safe. The grounding commit landed `ratify_reply_boundary` in `agent/graphs/reply_langgraph.py` — model proposes an action, scaffolding ratifies before any side-effecting commit — plus explicit `mixed_schedule_clarify` and `schedule_underspecified` intents in `agent/graphs/reply_routing.py`. The boundary is the same in REST and MCP modes; only the idempotency-key persistence layer changes.

**3. Day 3 — Why removing the KL anchor in SimPO drove Delta B = −0.42 at p = 0.992.**
My Week 11 `methodology_rationale.md §3` defended SimPO over DPO on length-normalization and VRAM, and was silent on the cost of dropping the reference policy. Ruth Solomon's gradient-level explainer named the cost: SimPO's `z`-term drops the `π_ref` factor entirely, so at high-capacity LoRA (r=16) on a 3B backbone with n=128 pairs, the only optimization pressure is the chosen-minus-rejected margin and the policy drifts to a region that perfectly separates training pairs but lies far from the SFT manifold the held-out evaluations come from. The grounding commit rewrote §3 to name that cost, added a CPO-vs-ORPO disambiguation in the model card, and queued a `cpo_alpha=0.5` ablation with a defended directional prediction (Delta B improves toward roughly −0.15 to 0.0).

**4. Day 4 — Whether "100% IRR at ±1 tolerance" survives chance-correction at concentrated marginals.**
My `inter_rater_agreement.json` reported 100% agreement and the memo cited it as evidence the rubric was "mechanically gradable." But 97.8% of t0 ratings were 4 or 5 — a regime in which Cohen's kappa is known to paradox-collapse. Liul J. Teshome's explainer derived the actual numbers on my 90-cell confusion matrix (κ = 0.781, weighted κ = 0.801, AC1 = 0.851). The grounding commit added a `kappa_and_ac1` block to the JSON, rewrote the certification sentence in `inter_rater_agreement.md`, and replaced the memo's bare "100%" with the paradox-resistant triple led by AC1.

### Four I researched (explainer side)

**5. Day 1 (for Abdulaziz) — Why `$0.0029` and `$0.0047` per task can both be right.**
The mechanism is **prefix caching**, not model capability: hosted-LLM APIs cache stable system-prompt prefixes across calls, and the per-task cost gap reflects different cache-write/cache-read ratios across the two configurations. Latency can stay near-flat because decode-time variance and network RTT dominate observable wall-clock at small n. The explainer separated KV cache (intra-call) from prefix cache (inter-call) — a naming hygiene gap that is widely conflated — and gave Abdulaziz a defensible model-card paragraph plus a runnable arithmetic demo (`day_1/scripts/cache_cost_demo.py`).

**6. Day 2 (for Gemechis) — Where agent systems actually break: the model-scaffolding planning boundary.**
The published explainer reframed agent failures as boundary-compression failures, not prompt-quality failures. Two ambiguity patterns recur: mixed intent in one turn (acceptance + clarification) and underspecified acceptance ("yes, next week"). The portable rule is **model proposes, scaffolding ratifies**, with explicit intermediate states (`accepted_but_incomplete`, `needs_clarification`) before any side-effecting commit. This rule is what later landed as my own Day-2 grounding commit in `conversion_engine` — the explainer-side and asker-side gaps were the same gap from two angles.

**7. Day 3 (for Addisu) — What LoRA actually adapts, and why higher rank is a *cap*, not a smooth knob.**
Addisu had observed that tiny LoRA adapters dramatically shifted behavior while higher rank often barely helped. The explainer derived this from the intrinsic-low-rank hypothesis (Aghajanyan 2021, Hu 2022): if the task's intrinsic rank is `k`, then any allocated `r ≥ k` fits and any `r < k` fails. The runnable demo (`day_3/scripts/lora_rank_demo.py`) shows a synthetic rank-4 target fit at r=2 (fails), r=4 (tight fit), r=16 (only 4 large singular values, 12 collapsed to ~0.14). The post-hoc audit — run SVD on the trained `B @ A` once and look at where singular values fall off — is the single cheapest empirical signal in the adapter literature, and went on the cohort tool list.

**8. Day 4 (for Liul) — Why `drift_score = 0.0` is not yet evidence of semantic stability.**
Liul's `Data-Contract-Enforcer` report wrote "Text content is semantically stable" on the basis of a centroid-cosine drift score near zero. The mechanism: a centroid is a first-moment summary, and a first-moment summary is silent on dispersion, multimodality, embedding-model identity, and fallback behavior. The runnable demo (`day_4/scripts/centroid_drift_demo.py`) builds two cohorts mean-matched by construction (drift ≈ 1e-13) with a 10× dispersion ratio, and a same-statistic permutation test still says p=1.0. The explainer shipped file-level rewrites: emit `(drift_score, dispersion_ratio, mmd_score, n_effective, embedding_model_id, fallback_rate)` as the contract triple; replace the bare report sentence with one that names what it actually measured. It also separated `n_reported = 251` from `n_effective = 200` — a one-line provenance fix that is the cheapest reproducibility win in the artifact.

### Two cross-cutting gaps (the meta-pattern)

**9. The choice of *which statistic to lead with* is a design decision, not a default.**
Three of my four asker-side gaps reduced to the same shape: the headline number I had published (CI grazing zero, raw IRR at 100%, raw drift_score at 0.0) was conventional but indefensible, and the substantive reliability statement underneath it required a *different* statistic that I had not computed. Replacing the lead statistic — directional p-value with explicit small-n caveat (Day 1), AC1 instead of raw agreement (Day 4), MMD-plus-dispersion alongside centroid distance (Day 8 explainer) — is the load-bearing edit. The dataset rarely needed to change.

**10. Anchors and ratifications: most agent and training failures are missing-anchor failures.**
Day 2's "model proposes, scaffolding ratifies" and Day 3's "the KL anchor in DPO is what stops policy drift" turned out to be the same architectural pattern at different layers of the stack. In both, an unconstrained probabilistic process (model interpretation in the agent; preference-margin gradient in training) produces locally-optimal decisions that are globally off-manifold unless an explicit anchor pulls them back toward a known-good distribution. The asymmetric design rule — *flexible upstream, anchored downstream* — generalizes farther than I expected when I asked the questions.

---

## Most surprising thing I learned

That the same architectural pattern shows up in agents (Day 2) and in preference fine-tuning (Day 3) and in evaluation statistics (Days 1 and 4): **a single first-moment summary or single-pass interpretation is insufficient, and the fix is always to add a paradox-resistant secondary signal that anchors the headline claim.** I expected four loosely related gaps and got one mechanism repeated under four different names. That is the kind of compression I will look for actively in Week 13 — not "what is broken," but "which anchor is missing."

## Canonical reading list and tool list contributed

The full annotated list is in [`canonical_list.md`](canonical_list.md). The headline contributions to the cohort canon are:

- **Papers:** Aghajanyan 2021 (intrinsic-rank), Hu 2022 (LoRA), Rafailov 2023 (DPO), Meng 2024 (SimPO), Hong 2024 (ORPO), Cohen 1960/1968 (kappa, weighted kappa), Gwet 2008 (AC1), Feinstein & Cicchetti 1990 + Byrt 1993 (kappa paradox), Gretton 2012 (MMD), Rabanser 2019 (failing loudly on drift detectors), Hesterberg 2015 (small-n bootstrap caveats).
- **Tools:** the post-hoc SVD-on-`B@A` audit for LoRA effective rank; the paired-bootstrap-with-spike-at-zero demo; the centroid-vs-dispersion drift demo; the `kappa_and_ac1` JSON block as a permanent IRR reporting pattern; the `model proposes, scaffolding ratifies` boundary node as a portable agent-design pattern.

---

*Word count: ~1,490.*
