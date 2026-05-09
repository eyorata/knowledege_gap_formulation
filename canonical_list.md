# Canonical Reading & Tool List — Eyoel Nebiyu's Week 12 contribution

This is the annotated set of papers, tools, and patterns I am submitting to the cohort canon — i.e., the items I think other Forward-Deployed Engineers should read or run *before* their next post-training, agent-orchestration, or eval-statistics decision.

Selection rule: every entry below was load-bearing in at least one of my five Week 12 grounding commits. No entry was added because it is famous; every entry was added because removing it would have left a real gap unfixed.

---

## Papers — training and post-training mechanics

### 1. Hu et al. (2022) — *LoRA: Low-Rank Adaptation of Large Language Models*
**Cite:** ICLR 2022, arXiv 2106.09685.
**Why canonical:** Introduces the parallel-update form `(α/r) · B · A` and the empirical result (Table 6) that `r=4` and `r=64` reach similar quality on most GPT-3 adaptation benchmarks. This is what the "rank is a cap, not a knob" intuition rests on.
**Where I used it:** Day 3 explainer for Addisu.

### 2. Aghajanyan, Zettlemoyer, Gupta (2021) — *Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning*
**Cite:** ACL 2021, arXiv 2012.13255.
**Why canonical:** The empirical foundation behind LoRA. Pretrained LMs can be fine-tuned through a randomly-projected ~200-dimensional update on tasks like GLUE without much loss. Explains *why* low rank works at all.
**Where I used it:** Day 3 explainer for Addisu (load-bearing for the intrinsic-rank derivation).

### 3. Rafailov et al. (2023) — *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*
**Cite:** NeurIPS 2023.
**Why canonical:** §4 has the gradient derivation and the KL-implicit argument. This is the paper to read *before* picking SimPO/ORPO so you know what the reference policy is actually doing in DPO's gradient.
**Where I used it:** Day 3 asker side (the "what does removing the KL anchor cost" question is unanswerable without DPO's gradient on the table).

### 4. Meng, Xia, Chen (2024) — *SimPO: Simple Preference Optimization with a Reference-Free Reward*
**Cite:** NeurIPS 2024.
**Why canonical:** Reference-free, length-normalized preference loss. Halves training VRAM. The paper is largely silent on small-n stability cost, which is exactly the gap my Day 3 grounding commit closed in `methodology_rationale.md §3`.
**Where I used it:** Day 3 asker side. Recommended reading *with* the caveat that the silence in §4 about small-n drift is itself important.

### 5. Hong, Lee, Thorne (2024) — *ORPO: Monolithic Preference Optimization without Reference Model*
**Cite:** EMNLP 2024.
**Why canonical:** §3 introduces the additive SFT log-likelihood term that constrains policy drift without a reference model. The TRL `CPOTrainer`'s `cpo_alpha` knob spans the SimPO ↔ CPO ↔ ORPO continuum cleanly.
**Where I used it:** Day 3 asker side. The model-card disambiguation I added (CPO ≠ ORPO at the gradient level) prevents a conflation that propagates easily.

---

## Papers — evaluation and statistics

### 6. Cohen (1960) — *A coefficient of agreement for nominal scales*
**Cite:** Educational and Psychological Measurement, 20(1).
**Why canonical:** The original kappa derivation. Three lines of equations on p. 39–40 are all that is needed to see where the "expected agreement by chance" term enters.
**Where I used it:** Day 4 asker side.

### 7. Cohen (1968) — *Weighted kappa: nominal scale agreement provision for scaled disagreement or partial credit*
**Cite:** Psychological Bulletin, 70(4).
**Why canonical:** Linear-weighted kappa for ordinal scales. Unweighted kappa understates rubric reliability when the disagreement metric is "off by 1" rather than "off."
**Where I used it:** Day 4 asker side, and now baked into the `kappa_and_ac1` block in `inter_rater_agreement.json` as the `cohens_kappa_linear_weighted` field.

### 8. Feinstein & Cicchetti (1990) and Byrt, Bishop, Carlin (1993) — the kappa paradox papers
**Cites:** Feinstein & Cicchetti, *J. Clinical Epidemiology* 43(6); Byrt et al., *J. Clinical Epidemiology* 46(5).
**Why canonical:** The canonical statement and decomposition of the kappa paradox at concentrated marginals. Without these, anyone reading "raw agreement = 100% but κ = 0" thinks something is broken; with them, it is the predicted behavior.
**Where I used it:** Day 4 asker side.

### 9. Gwet (2008) — *Computing inter-rater reliability and its variance in the presence of high agreement*
**Cite:** British Journal of Mathematical and Statistical Psychology, 61(1).
**Why canonical:** AC1's expected-agreement term is paradox-resistant by construction. This is the statistic to **lead with** in any rubric-graded LLM-eval IRR section where ratings concentrate at one end.
**Where I used it:** Day 4 grounding commit. AC1 = 0.851 is now the headline number in `inter_rater_agreement.md` and `memo/memo.md`.

### 10. Gretton et al. (2012) — *A Kernel Two-Sample Test*
**Cite:** JMLR 13.
**Why canonical:** The MMD estimator. Drop-in upgrade for any centroid-only drift statistic that needs to see beyond first moments.
**Where I used it:** Day 4 explainer for Liul. The `mmd_score` field in the recommended drift-contract triple comes from here.

### 11. Rabanser, Günnemann, Lipton (2019) — *Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift*
**Cite:** NeurIPS 2019.
**Why canonical:** §4 explicitly shows mean-only statistics miss dispersion shifts. This is the empirical receipt for "a centroid is silent on everything that is not the mean."
**Where I used it:** Day 4 explainer for Liul.

### 12. Hesterberg (2015) — *What Teachers Should Know About the Bootstrap*
**Cite:** The American Statistician, 69(4).
**Why canonical:** Practical interpretation of bootstrap behavior at small n. This is where the "percentile intervals can mislead naively at small n with discrete outcomes" caveat is properly grounded.
**Where I used it:** Day 1 asker side.

### 13. Efron & Tibshirani (1993) — *An Introduction to the Bootstrap*
**Cite:** Chapman & Hall/CRC.
**Why canonical:** The foundational text. Section on percentile-interval construction is what makes the n=12 spike-at-zero behavior derivable rather than mysterious.
**Where I used it:** Day 1 asker side.

---

## Papers — agent and tool-use internals

### 14. Yao et al. (2023) — *ReAct: Synergizing Reasoning and Acting in Language Models*
**Cite:** ICLR 2023, arXiv 2210.03629.
**Why canonical:** Establishes the alternation between reasoning steps and tool-use steps. Read alongside Day 2's "model proposes, scaffolding ratifies" rule — ReAct is the framing layer; the boundary discipline is the production hardening.
**Where I used it:** Day 2 explainer for Gemechis.

### 15. OpenAI Model Spec (2024)
**URL:** https://model-spec.openai.com/
**Why canonical:** A concrete, public example of how to specify decision-ownership at the system/developer/user level. The closest published industrial reference for the deterministic-vs-model decision-class taxonomy I used in Day 2.
**Where I used it:** Day 2 explainer for Gemechis.

### 16. Anthropic Prompt Caching documentation
**URL:** https://docs.claude.com/en/docs/build-with-claude/prompt-caching
**Why canonical:** The production API contract for prefix caching. Without this, any "cost gap explained by caching" claim is unverifiable.
**Where I used it:** Day 1 explainer for Abdulaziz.

### 17. Kwon et al. (2023) — *Efficient Memory Management for Large Language Model Serving with PagedAttention*
**Cite:** SOSP 2023, arXiv 2309.06180.
**Why canonical:** Grounds the serving-side mechanism behind KV-cache reuse, which is what makes prefix-cache discounts feasible in the first place. Distinguishes intra-call (KV) from inter-call (prefix) cache cleanly.
**Where I used it:** Day 1 explainer for Abdulaziz.

---

## Tools and patterns — runnable

### A. Post-hoc SVD audit on the trained `B @ A` (LoRA effective-rank check)
**Where:** [`day_3/scripts/lora_rank_demo.py`](day_3/scripts/lora_rank_demo.py).
**Pattern:** After training a LoRA adapter at allocated rank `r`, run `np.linalg.svd(B @ A)` and inspect where the singular values fall off. If the first `k < r` are large and the rest collapse two orders of magnitude smaller, retrain at `r ≈ k` with no quality loss.
**Why FDEs should adopt it:** Cheapest empirical signal in the adapter-compression literature. One line of NumPy. No new training.

### B. Paired-bootstrap-with-spike-at-zero demo for small-n binary outcomes
**Where:** Day 1 (the simulation pattern in `sources.md` and the explainer).
**Pattern:** Run paired bootstrap on binary outcomes at n ∈ {12, 30, 100}. Plot the empirical distribution of resampled diffs. At n=12 the spike at `diff=0.00` is visible; at n=100 it vanishes. This is what makes the "CI lower bound = 0 alongside p < 0.05" behavior derivable rather than confusing.
**Why FDEs should adopt it:** Anyone reporting evidence at n < 30 needs to see this once.

### C. Centroid-vs-dispersion drift demo (the first-moment trap)
**Where:** [`day_4/scripts/centroid_drift_demo.py`](day_4/scripts/centroid_drift_demo.py).
**Pattern:** Build two cohorts of 200 vectors with identical means by construction and a 10× dispersion ratio. Compute centroid-cosine drift (≈ 1e-13), within-cohort dispersion (10× gap), and a permutation test on the same statistic (p = 1.0). The drift contract should emit a triple: `(drift_score, dispersion_ratio, mmd_score)` plus `n_effective` and `embedding_model_id` provenance.
**Why FDEs should adopt it:** Any contract that maps a single first-moment statistic to a semantic claim ("stable", "drifted") will fail this demo.

### D. The `kappa_and_ac1` JSON block as a permanent IRR reporting pattern
**Where:** Day 4 grounding commit in `inter_rater_agreement.json`.
**Pattern:** When raw agreement is reported, also emit `cohens_kappa_unweighted`, `cohens_kappa_linear_weighted`, and `gwets_ac1`, plus `marginal_concentration_pct` so readers can see *why* the gap exists. Lead the prose with AC1 when ratings concentrate.
**Why FDEs should adopt it:** Many published "100% agreement!" claims in LLM-eval methodology sections do not survive this audit.

### E. The `ratify_reply_boundary` node — model proposes, scaffolding ratifies
**Where:** Day 2 grounding commit in `agent/graphs/reply_langgraph.py`.
**Pattern:** Insert a deterministic ratification node between the model's proposed action and any side-effecting commit. The node downgrades probabilistic intents (e.g., LLM-proposed `schedule`) when scaffolding-visible signals (`has_clarification_request`, `scheduling_completeness`) say the world isn't ready. Multi-intent turns get explicit dual-track states (`branch_pending`) instead of single-label collapse.
**Why FDEs should adopt it:** The cheapest reliability upgrade in any hybrid agent doing high-risk writes. Generalizes across REST and MCP tool backends.

### F. The cache-cost arithmetic demo (cost-gap mechanism without provider telemetry)
**Where:** [`day_1/scripts/cache_cost_demo.py`](day_1/scripts/cache_cost_demo.py).
**Pattern:** Three regimes (stable-prefix, partial-hit, miss-heavy) reproducing the lower / middle / upper observed cost numbers from rate-card arithmetic alone. Distinguishes KV cache (intra-call) from prefix cache (inter-call) explicitly.
**Why FDEs should adopt it:** Lets you defend cost-gap explanations in model cards without claiming access to provider-internal cache telemetry you do not actually have.

---

## What I deliberately did **not** add

Famous-but-tangential papers (e.g., Christiano et al. RLHF lineage, KTO, IPO, RLOO, full RLHF/PPO) are out — they are not load-bearing for any Week 12 grounding commit and would dilute the canon. QLoRA, DoRA, VeRA are out for the same reason: real but adjacent. Krippendorff's α and Fleiss' κ are out because the IRR structure I had (2 raters, ordinal 1–5, 30 pairs) does not need them.

The canon is meant to be small enough that another FDE will actually read it.
