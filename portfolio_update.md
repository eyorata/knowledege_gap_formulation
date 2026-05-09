# Portfolio Update — How Week 12 Grounding Commits Improve My Weeks 10 & 11 Portfolio

**Author:** Eyoel Nebiyu (`@eyorata`) · **Audience:** FDE hiring manager · **Window:** 2026-05-04 → 2026-05-08

## What changed and why it matters

Week 12 was four pair-days of mechanism-level questions. The output that matters for hiring is not the explainers themselves — it is the **five grounding commits** that landed in artifacts I had already published in Week 10 (`conversion_engine`) and Week 11 (`sales_evaluation_bench`). Each commit converted a hand-wavy or under-defended claim into a mechanism-level claim, in the file a senior reviewer would actually read.

| # | Day | Repo / file | Before (indefensible) | After (mechanism-level) |
|---|-----|-------------|-----------------------|--------------------------|
| 1 | Day 1 (asker) | Week 11 — `blog/tenacious_bench_v0.1_blog.md` | "CI grazes zero because of small-n quantization." | Explicit derivation: paired bootstrap on n=12 binary outcomes is discrete; resamples place mass at exactly `diff=0.00`; CI lower bound can equal zero while p=0.0316. Adds an FDE small-n reporting rule. |
| 2 | Day 1 (partner) | Week 11 — `docs/blog_post.md` | "Cost increased from $0.0029 to $0.0047 per task." | Cost gap attributed to prefix-cache hit-ratio differences (inter-call), not KV cache (intra-call); explicitly separates measured from inferred; latency stayed near-flat because decode + network dominate small-sample wall-clock. |
| 3 | Day 2 | Week 10 — `agent/graphs/reply_langgraph.py`, `agent/graphs/reply_routing.py`, `agent/services/conversation/email_llm.py` + tests | Single-label intent router; ambiguous accept/clarify replies collapsed to one branch; no explicit gate before scheduling side effects. | New `ratify_reply_boundary` node + `mixed_schedule_clarify` / `schedule_underspecified` intents; LLM `schedule` proposals are downgraded when scaffolding-visible signals say the world isn't ready; multi-intent turns get a dual-track `branch_pending` state. |
| 4 | Day 3 | Week 11 — `methodology_rationale.md §3` + `tenacious_bench_v0.1/MODEL_CARD.md` + `ablations/queued_v0.2.md` | "SimPO chosen because length-normalized + halves VRAM" — silent on the cost of dropping the KL anchor. | Names the gradient-level cost (no `π_ref` term → policy drifts off SFT manifold at small n + high-capacity LoRA → train_acc=1.00, eval_acc=0.50 plateau is *predicted*, not a tuning failure). Adds CPO-vs-ORPO disambiguation in the model card. Queues a defended `cpo_alpha=0.5` ablation with a directional prediction (Delta B → −0.15 to 0.0). |
| 5 | Day 4 | Week 11 — `inter_rater_agreement.json`, `inter_rater_agreement.md`, `memo/memo.md` | "100% inter-rater agreement (within ±1) across all three quality dimensions" — silent on chance correction at concentrated marginals (97.8% of ratings at 4 or 5). | New `kappa_and_ac1` block: κ = 0.781, weighted κ = 0.801, **AC1 = 0.851** (substantial agreement on Landis & Koch). Memo paragraph rewritten to lead with AC1 as paradox-resistant headline. Raw 100% kept as honest context, not as the load-bearing claim. |

## Why this is the right shape of evidence for an FDE role

A hiring manager reviewing my repo cares about three properties that grounding commits exercise simultaneously:

1. **I can be challenged on a specific line and have an answer.** Each commit names the exact file, the exact prior sentence, and the exact replacement. The audit trail is two diffs deep, not a vague "we improved the methodology."
2. **I distinguish what I measured from what I inferred.** Three of the five commits explicitly add this distinction (cost mechanism, drift mechanism, training drift). This is the discipline that separates "the model failed and I don't know why" from "the failure signature is the predicted behavior of mechanism X, and the cheapest disambiguating experiment is Y."
3. **I lead with the right statistic, not the conventional one.** Days 1, 3, and 4 each replaced a conventional headline number (CI grazing zero, raw IRR at 100%, raw `delta_b = -0.42` reported with no mechanism) with a more defensible primary signal (directional p with small-n caveat, AC1, `delta_b` with named drift mechanism + queued ablation). Picking the right statistic to lead with is a *judgment call FDEs make weekly*, and these commits show that judgment in writing.

## Net effect on the Week 10 + 11 portfolio

- **Week 10 (`conversion_engine`)** picks up a production-shaped reliability fix: multi-intent turns and underspecified acceptance no longer collapse into one branch, and high-risk writes are gated by an explicit ratification node.
- **Week 11 (`sales_evaluation_bench`)** picks up four upgrades in places a senior reviewer would interrogate first: the blog's small-n discussion, the methodology rationale's training-stability story, the model card's algorithm-naming honesty, and the IRR claim that propagates into the executive memo.
- **Together**, the portfolio reads as a Forward-Deployed Engineer who, when handed an artifact with an indefensible claim, identifies the mechanism, edits the right file, and ships a commit — rather than rewriting the whole thing or shipping a "v0.2" release note.

## Reproducibility

All five commits are linked from the four `day_N/grounding_commit.md` files in this repo. Each names the target repo, the branch, the files changed, and the rewritten paragraph verbatim. The runnable demos behind the mechanism claims (`day_1/scripts/cache_cost_demo.py`, `day_3/scripts/lora_rank_demo.py`, `day_4/scripts/centroid_drift_demo.py`) are NumPy-only and run in seconds.
