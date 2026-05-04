# Morning call summary — Day 1

**Pair:** Eyoel Nebiyu (asker A) ↔ Abdulaziz (asker B)
**Topic (cohort vote):** Inference-time mechanics + Evaluation statistics
**Duration:** ~30 min
**Confirmed by both partners.**

---

## Question A — Eyoel's bootstrap-CI question

**Original draft (what was ambiguous):** the gap was real but the question shape was two-headed — asking simultaneously *why* `ci_low = 0.00` ∧ `p = 0.0316` co-occur, *and* which number to lead with in the memo. Risked landing as a textbook chapter on bootstrap rather than a focused FDE explainer.

**Sharpening (Abdulaziz's interrogation):** Abdulaziz pushed me to pin three things — (a) one-sided vs two-sided p-value, (b) percentile method vs basic / BCa bootstrap, (c) discrete-outcome regime. With those pinned, the resolvability property cleared 5/5: the explainer can derive the 0/1-outcome small-n quantization and the (non-bijective) CI-vs-p-value relationship in 800 words plus a 12-vs-30-vs-100 simulation.

**Final committed question:** unchanged in shape from the draft; pinned to *paired bootstrap, percentile method, n=12 with 0/1 prefers_chosen outcomes, one-sided p-value as `(diffs ≤ 0).mean()`*. Grounding artifact: `ablations/ablation_results.json` `delta_a` block in the Tenacious-Bench v0.1 repo, plus the unsupported "small-n quantization" phrase in `blog/tenacious_bench_v0.1_blog.md` §5.

---

## Question B — Abdulaziz's cost-decomposition question

**Original draft (what was ambiguous):** covered four sub-mechanisms simultaneously — prefill vs decode, KV cache reuse, prefix cache reuse, token-level billing effects. Too broad to land in one explainer; risked sprawling into a textbook chapter.

**Sharpening (Eyoel's interrogation):** I pushed Abdulaziz to pin (a) deployment mode — answered "mixed but the ablation scoring path is API-served"; (b) what the `$0.0029` vs `$0.0047` numbers actually compare; (c) KV cache (intra-call) vs prefix cache (inter-call) — they were being conflated; (d) whether the rubric system prompt is fixed or varies per task. The answers narrowed the question to one mechanism (prefix caching on the API path) on one comparison (the two cost numbers in `cost_pareto`). The other three sub-mechanisms moved to a v0.2 list.

**Final committed question:** scoped to *server-side prefix caching mechanics on the API-served scoring path, deriving the `$0.0029` vs `$0.0047` gap from cache-hit ratios and rate-card arithmetic*. Grounding artifacts: `ablations/ablation_results.json` `cost_pareto` block, `training/model_card.md` Cost-Pareto section, `docs/blog_post.md` cost-quality tradeoff paragraph in Abdulaziz's repo. Skipped (named honestly): KV-cache mechanics, prefill-vs-decode latency, tokenizer billing — each gets its own future explainer.
