# Knowledge Gap Formulation — Week 12 Portfolio

**Author:** Eyoel Nebiyu (`@eyorata`)
**Window:** 2026-05-04 → 2026-05-08 (four pair-days)

This repository tracks my Week 12 pair-day deliverables for the FDE portfolio track. Each `day_N/` folder contains the full evidence set: sharpened question, explainer, thread, call summaries, signoff, grounding commit, and sources.

---

## Final submission artifacts (this directory)

- [`synthesis.md`](synthesis.md) — 1,500-word week synthesis: ten gaps closed (four named, four researched, two cross-cutting), most surprising lesson, and pointers to the canonical list.
- [`canonical_list.md`](canonical_list.md) — annotated contribution to the cohort canon: 17 papers + 6 runnable tools/patterns, each tied to a specific Week 12 grounding commit.
- [`portfolio_update.md`](portfolio_update.md) — one-page summary of how the five grounding commits collectively improve my Week 10 + Week 11 portfolio, written for an FDE hiring manager.

---

## Folder structure

- [`day_1/`](day_1/) — bootstrap CI vs p-value at small-n (asker) + prefix-caching cost mechanism (explainer for Abdulaziz). Two grounding commits land here.
- [`day_2/`](day_2/) — commit-point/idempotency placement in dual-backend agents (asker) + scaffolding-vs-model planning boundary (explainer for Gemechis).
- [`day_3/`](day_3/) — KL anchor cost in SimPO / queued `cpo_alpha=0.5` ablation (asker) + LoRA intrinsic-rank derivation (explainer for Addisu).
- [`day_4/`](day_4/) — kappa paradox at concentrated marginals / Gwet's AC1 (asker) + centroid-cosine drift first-moment trap (explainer for Liul J. Teshome).

---

## Public artifacts

### Blog posts (4 published under `eyorata` on DEV)

> **Note on count:** the submission spec asks for five blog post URLs. I am submitting four — one per pair-day — and listing them honestly rather than padding the count. The four below are the full set of explainers I published under my identity in Week 12.

1. **Day 1** — *Why `$0.0029` and `$0.0047` Can Both Be Right: Prefix Caching for API-Served LLM Judges*
   https://dev.to/eyorata/-why-00029-and-00047-can-both-be-right-prefix-caching-for-api-served-llm-judges-by-3bd6
2. **Day 2** — *Scaffolding-Driven vs Model-Driven Planning: Where Agent Systems Actually Break*
   https://dev.to/eyorata/-scaffolding-driven-vs-model-driven-planning-where-agent-systems-actually-breakby-eyoel-nebiyu-50h1
3. **Day 3** — *What LoRA Actually Adapts — and Why Higher Rank Doesn't Always Buy What It Looks Like It Should*
   https://dev.to/eyorata/-what-lora-actually-adapts-and-why-higher-rank-doesnt-always-buy-what-it-looks-like-it-should-4bfp
4. **Day 4** — *Why `drift_score = 0.0` Is Not Yet Evidence of Semantic Stability — and What Your n=251 vs cap=200 Mismatch Actually Costs*
   https://dev.to/eyorata/-why-driftscore-00-is-not-yet-evidence-of-semantic-stability-and-what-your-n251-vs-2k9p

### Tweet threads (drafted in repo, not posted to X)

> **Note on count:** the submission spec asks for five published tweet thread URLs. I drafted threads in repo for two of the four pair-days and did not publish them to X under my identity. The drafts below ship in the repo so the message structure is reviewable; I am flagging this gap honestly rather than fabricating URLs.

1. **Day 1 thread (draft)** — [`day_1/thread.md`](day_1/thread.md) — six tweets walking through the n=12 paired-bootstrap CI/p-value paradox and the small-n FDE memo rule.
2. **Day 2 thread (draft)** — [`day_2/thread.md`](day_2/thread.md) — six tweets on the model-vs-scaffolding boundary and the "model proposes, scaffolding ratifies" rule.
3. **Day 3 thread** — not drafted in repo. The substance is in [`day_3/explainer.md`](day_3/explainer.md) and the published DEV post.
4. **Day 4 thread** — not drafted in repo. The substance is in [`day_4/explainer.md`](day_4/explainer.md) and the published DEV post.
5. *No fifth thread.* I'd rather flag the count gap than invent one.

---

## Five grounding commits (the load-bearing portfolio evidence)

The commits below are what convert this week from "I read papers and wrote explainers" into portfolio-grade evidence. Each lands in an artifact I had already published in Week 10 or Week 11.

| # | Day | Target repo | Files changed | Mechanism made explicit |
|---|-----|-------------|---------------|--------------------------|
| 1 | Day 1 (asker) | `eyorata/sales_evaluation_bench` | `blog/tenacious_bench_v0.1_blog.md` | n=12 paired-bootstrap discreteness; CI grazing zero alongside p=0.0316 derived from the spike at `diff=0.00`. See [`day_1/grounding_commit.md`](day_1/grounding_commit.md). |
| 2 | Day 1 (partner) | partner repo | `docs/blog_post.md` | Prefix-cache hit ratio (inter-call) ≠ KV cache (intra-call); cost gap explained without overclaiming provider telemetry. See [`day_1/partner_grounding_commit.md`](day_1/partner_grounding_commit.md). |
| 3 | Day 2 | `conversion_engine` | `agent/graphs/reply_langgraph.py`, `agent/graphs/reply_routing.py`, `agent/services/conversation/email_llm.py`, tests | `ratify_reply_boundary` node; multi-intent turns get dual-track state instead of single-label collapse; LLM `schedule` proposals are downgraded by scaffolding-visible signals. See [`day_2/day2_grounding_commit.md`](day_2/day2_grounding_commit.md). |
| 4 | Day 3 | `eyorata/sales_evaluation_bench` | `methodology_rationale.md §3`, `tenacious_bench_v0.1/MODEL_CARD.md`, `ablations/queued_v0.2.md` | KL-anchor cost named at gradient level; CPO ≠ ORPO disambiguation; defended `cpo_alpha=0.5` directional prediction queued. See [`day_3/grounding_commit.md`](day_3/grounding_commit.md). |
| 5 | Day 4 | `eyorata/sales_evaluation_bench` | `inter_rater_agreement.json`, `inter_rater_agreement.md`, `memo/memo.md` | `kappa_and_ac1` JSON block (κ=0.781, κ_w=0.801, AC1=0.851); paradox-resistant headline replaces raw 100%. See [`day_4/grounding_commit.md`](day_4/grounding_commit.md). |

---

## Runnable demos (NumPy-only, seconds to run)

- [`day_1/scripts/cache_cost_demo.py`](day_1/scripts/cache_cost_demo.py) — three regimes (stable-prefix, partial-hit, miss-heavy) reproducing the cost gap from rate-card arithmetic.
- [`day_3/scripts/lora_rank_demo.py`](day_3/scripts/lora_rank_demo.py) — synthetic rank-4 target fit at r=2 / r=4 / r=16; SVD on trained `B@A` reveals effective vs allocated rank.
- [`day_4/scripts/centroid_drift_demo.py`](day_4/scripts/centroid_drift_demo.py) — two cohorts mean-matched by construction with 10× dispersion ratio; centroid drift ≈ 1e-13, dispersion ratio reveals the real shift.

---

## Notes

- Artifacts are written to be both portfolio-ready and publicly publishable.
- Public links are added here as each daily artifact is published; gaps in the count are flagged rather than padded.
