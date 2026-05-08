# Morning call summary — Day 4

**Pair:** Eyoel Nebiyu (asker A) ↔ Liul J. Teshome (asker B)
**Topic (cohort vote):** Evaluation and statistics
**Date:** 2026-05-08
**Duration:** ~30 min
**Confirmed by both partners.**

---

## Question A — Eyoel's kappa-paradox / chance-corrected IRR question

**Original draft (what was ambiguous):** the question gestured at three statistics (Cohen's kappa, weighted kappa, Gwet's AC1) and one published claim ("100% agreement, passes 80% bar" in `inter_rater_agreement.md`, propagated into `memo/memo.md`). Risked sprawling into a "which IRR statistic should I use?" survey rather than a *mechanism-level* explainer tied to the specific marginal distribution in my JSON.

**Sharpening (Liul's interrogation):** Liul pushed me to pin four things — (a) what depth of derivation I needed (loss/formula? full `p_o`/`p_e` decomposition at one confusion matrix? the prevalence-paradox proof?), (b) whether the load-bearing issue was the *±1 tolerance metric* or the *marginal concentration* (answer: marginal concentration — even at exact-match the ratings would still be 4/5-heavy), (c) whether unweighted vs linearly-weighted kappa was in scope (answer: in, since the rubric is explicitly ordinal 1–5), (d) whether I wanted the explainer to *commit to a single recommendation* (Gwet's AC1) or describe the (kappa, weighted κ, AC1) tradeoffs (answer: commit, with the tradeoff named in one sentence). With those pinned, the resolvability property cleared 5/5: the explainer can derive `p_o` − `p_e` at one confusion matrix, prove the paradox at concentrated marginals, predict a numerical range on my actual rating distribution, and close with a single defended recommendation in ~1000 words plus a runnable script.

**Final committed question:** scoped to *the gradient between raw `agree_within_1` and chance-corrected agreement (κ, weighted κ, AC1) when ratings concentrate at 4–5, the kappa-paradox derivation, and a defended numerical range for κ / weighted κ / AC1 on the actual n=30 marginals*. Grounding artifacts: `inter_rater_agreement.json` (with the `{3, 4, 5}` marginal already inspectable in the per-pair entries), `inter_rater_agreement.md` (the prose certification), and the memo paragraph in `memo/memo.md` that propagates "100% agreement" as evidence of mechanical gradability.

---

## Question B — Liul's embedding-drift / "semantic stability" question

**Original draft (what was ambiguous):** Liul's draft had two questions stacked in the same paragraph — (1) what `n_effective` should be when the impl caps at 200 but the report cites 251, and (2) what evidence chain is needed before claiming `drift_score = 0.0 → "Text content is semantically stable"`. Both real, both grounded in the same artifacts (`report_final_pdf_ready.md`, `contracts/ai_extensions.py`), but conceptually separate. Risked landing as two half-answered explainers in one document.

**Sharpening (Eyoel's interrogation):** I pushed Liul to pin (a) whether the two questions had a common cause — answer: yes, "centroid is a first-moment summary, every other property of the cohort is silent" binds both; (b) whether the embedding model identity was *currently pinned* in the code or the report — answer: not explicitly, which made fallback-path provenance a load-bearing third gap; (c) whether `n=251 vs n_eff=200` was a documentation issue or a sampling-decision issue — answer: both, and the *which 200 of 251* question matters more than the precision delta; (d) whether MMD / energy distance were strictly needed in the explainer or whether a simpler 2nd-moment statistic (within-cohort dispersion) would suffice — answer: include both — dispersion as the cheapest ladder rung, MMD as the standard upgrade. The answers narrowed to *one mechanism* (first-moment-summary insufficiency) explaining *both* of Liul's gaps and added embedding-provenance / fallback-rate logging as a third concrete fix.

**Final committed question:** scoped to *the evidence chain that turns `drift_score ~ 0` into a defensible "semantic stability" claim, with the n_eff vs n_reported correction folded in as one rung of that chain*. Grounding artifacts: the `Sample size: 251` and `drift_score: 0.0` claims in `report_final_pdf_ready.md`, the 200-cap and embedding-fallback paths in `contracts/ai_extensions.py`. Skipped (named honestly): bootstrap CI on the drift score itself, multi-batch streaming detectors (KS-windows, ADWIN, Page-Hinkley), contrastive-embedding identifiability, cross-model Procrustes alignment — each its own future explainer.
