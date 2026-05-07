# Knowledge Gap Formulation - Week 12 Portfolio

This repository tracks my Week 12 pair-day deliverables for the FDE portfolio track.  
Each `day_N` folder contains the full evidence set: sharpened question, explainer, thread, call summaries, signoff, grounding commit, and sources.

## Day 1 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-why-00029-and-00047-can-both-be-right-prefix-caching-for-api-served-llm-judges-by-3bd6

## Day 2 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-scaffolding-driven-vs-model-driven-planning-where-agent-systems-actually-breakby-eyoel-nebiyu-50h1

## Day 3 Published Artifact

- Blog post (DEV): https://dev.to/eyorata/-what-lora-actually-adapts-and-why-higher-rank-doesnt-always-buy-what-it-looks-like-it-should-4bfp

## What Day 1 Covers

Day 1 focuses on a mechanism-level explanation of why two LLM judge configurations can show different per-task cost numbers in API-served evaluation, even when latency appears near-flat.  
The load-bearing concept is prefix caching and cache-hit behavior, with source-grounded interpretation and runnable demonstration in the repo artifacts.

## What Day 2 Covers

Day 2 focuses on agent and tool-use internals, specifically the brittle boundary between model interpretation and deterministic orchestration.  
The post explains planning ownership (scaffolding vs model vs hybrid arbitration), analyzes two real ambiguity patterns (mixed intent and underspecified acceptance), and proposes a boundary-safe execution rule: model proposes, scaffolding ratifies before side effects.

## What Day 3 Covers

Day 3 focuses on training and post-training mechanics, specifically what LoRA actually adapts and why allocated rank `r` is a cap on expressive capacity rather than a smooth quality knob.  
The explainer (written for Addisu's question) derives the intrinsic-low-rank hypothesis behind LoRA, shows with a runnable numpy demo that effective rank ≪ allocated rank once `r` exceeds the task's intrinsic rank, and gives a post-hoc SVD audit any practitioner can run on a trained `B @ A` to right-size `r`.

## Folder Structure

- `day_1/` - complete Day 1 deliverables and supporting scripts
- `day_2/` - complete Day 2 deliverables on hybrid planning boundaries and ambiguity handling
- `day_3/` - complete Day 3 deliverables on LoRA rank mechanics + asker-side signoff/grounding for the DPO/SimPO/ORPO question Ruth Solomon answered

## Notes

- Artifacts are written to be both portfolio-ready and publicly publishable.
- Public links are added here as each daily artifact is published.
