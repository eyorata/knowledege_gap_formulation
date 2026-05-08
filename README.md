# Knowledge Gap Formulation - Week 12 Portfolio

This repository tracks my Week 12 pair-day deliverables for the FDE portfolio track.  
Each `day_N` folder contains the full evidence set: sharpened question, explainer, thread, call summaries, signoff, grounding commit, and sources.

## Day 1 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-why-00029-and-00047-can-both-be-right-prefix-caching-for-api-served-llm-judges-by-3bd6

## Day 2 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-scaffolding-driven-vs-model-driven-planning-where-agent-systems-actually-breakby-eyoel-nebiyu-50h1

## Day 3 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-what-lora-actually-adapts-and-why-higher-rank-doesnt-always-buy-what-it-looks-like-it-should-4bfp

## Day 4 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-why-driftscore-00-is-not-yet-evidence-of-semantic-stability-and-what-your-n251-vs-2k9p

## What Day 1 Covers

Day 1 focuses on a mechanism-level explanation of why two LLM judge configurations can show different per-task cost numbers in API-served evaluation, even when latency appears near-flat.  
The load-bearing concept is prefix caching and cache-hit behavior, with source-grounded interpretation and runnable demonstration in the repo artifacts.

## What Day 2 Covers

Day 2 focuses on agent and tool-use internals, specifically the brittle boundary between model interpretation and deterministic orchestration.  
The post explains planning ownership (scaffolding vs model vs hybrid arbitration), analyzes two real ambiguity patterns (mixed intent and underspecified acceptance), and proposes a boundary-safe execution rule: model proposes, scaffolding ratifies before side effects.

## What Day 3 Covers

Day 3 focuses on training and post-training mechanics, specifically what LoRA actually adapts and why allocated rank `r` is a cap on expressive capacity rather than a smooth quality knob.  
The explainer (written for Addisu's question) derives the intrinsic-low-rank hypothesis behind LoRA, shows with a runnable numpy demo that effective rank ≪ allocated rank once `r` exceeds the task's intrinsic rank, and gives a post-hoc SVD audit any practitioner can run on a trained `B @ A` to right-size `r`.

## What Day 4 Covers

Day 4 focuses on evaluation and statistics, specifically why a centroid-based cosine drift score reading near zero is not yet evidence of semantic stability in an embedding-drift contract.  
The explainer (written for Liul J. Teshome's question on the [Heban-7/Data-Contract-Enforcer](https://github.com/Heban-7/Data-Contract-Enforcer) report) binds two stacked gaps — the `n=251` reported vs `cap=200` effective sample-size mismatch, and the evidence chain a "semantically stable" claim actually needs — to a single mechanism: a centroid is a first-moment summary, and a first-moment summary is silent on dispersion, multimodality, model identity, and fallback behavior. The runnable numpy demo at `day_4/scripts/centroid_drift_demo.py` shows two cohorts mean-matched by construction (drift_score = 9.78e-13) but with a 10x dispersion ratio — proof that the same-family permutation test (p = 1.0) is also blind to the shift. The explainer ships file-level rewrites for `contracts/ai_extensions.py` (emit a `(drift_score, dispersion_ratio, mmd_score)` triple plus provenance fields) and `report_final_pdf_ready.md` (replace the bare "Text content is semantically stable" sentence with a provenance- and dispersion-aware paragraph).

## Folder Structure

- `day_1/` - complete Day 1 deliverables and supporting scripts
- `day_2/` - complete Day 2 deliverables on hybrid planning boundaries and ambiguity handling
- `day_3/` - complete Day 3 deliverables on LoRA rank mechanics + asker-side signoff/grounding for the DPO/SimPO/ORPO question Ruth Solomon answered
- `day_4/` - complete Day 4 deliverables on centroid-cosine drift evidence chains (explainer for Liul J. Teshome) + asker-side question/signoff/grounding for the kappa-paradox / chance-corrected IRR question

## Notes

- Artifacts are written to be both portfolio-ready and publicly publishable.
- Public links are added here as each daily artifact is published.
