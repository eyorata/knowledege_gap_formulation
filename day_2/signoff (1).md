# Signoff

## What I accepted

- The core split: **scaffolding owns commitment and side-effect gates**; the **model owns interpretation**. Risk sits at the **boundary** where rich model output is collapsed into a single action or state step.
- **Multi-intent and underspecified acceptance** deserve explicit handling, not a single intent label per turn.
- **“Model proposes, scaffolding ratifies”** for high-risk paths (especially anything that looks like moving toward booking) is the right default.

## What I did not take on (or left narrow)

- I did **not** turn this into a full research paper, new external benchmarks, or a rewrite of every workflow spec—only the **reply-routing slice** of the codebase was hardened.
- I did **not** claim heuristic rules replace a good LLM; they are **guardrails and fallbacks**, not a complete theory of dialogue.

## What I understand now (that I did not before)

Failures I used to attribute to “bad prompts” or “the model being dumb” are often **interface and orchestration** problems: the workflow forces one branch too early, drops uncertainty, or treats **syntactically valid** state moves as **semantically safe** moves. Separating **acceptance** from **executable scheduling readiness**, and **clarification** from **scheduling**, makes the system easier to reason about than chasing better wording alone.

---

## Ask: gap-closure judgment

**Partially closed.**

I did not fully internalize every nuance of hybrid multi-agent theory or prove behavior across all channels and edge cases in production, but I **do** now have a stable mental model I can reuse: *where* the boundary is, *why* it breaks (compression of intent, premature commit), and *what* “good” looks like (explicit completeness and multi-track plans before side effects). That is enough to steer the next round of design and review without re-deriving the explainer from scratch.
