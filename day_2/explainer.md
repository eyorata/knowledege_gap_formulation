# Scaffolding-Driven vs Model-Driven Planning: Where Agent Systems Actually Break

*By Eyoel Nebiyu*

Most teams building agent systems focus on improving prompts or improving workflow logic. In production, many costly failures come from something else: the boundary between model interpretation and deterministic execution.

This post explains how to assign planning ownership between scaffolding and model reasoning, why ambiguity handling fails at handoff points, and how to design a safer boundary that still preserves adaptability.

## The core architecture problem

Hybrid agent systems combine:

- **Deterministic scaffolding**: states, routers, policy gates, retries, execution order.
- **Model judgment**: semantic interpretation under ambiguous user language.

Neither layer is enough alone. Scaffolding is stable but brittle under messy language. Model reasoning is flexible but probabilistic. The failure surface appears when we treat probabilistic interpretation as execution-ready truth.

In Gemechis's real setup, two ambiguity patterns repeatedly trigger this:

1. **Mixed intent in one turn**: prospects both accept a meeting direction and ask for clarification in the same message.
2. **Underspecified acceptance**: prospects indicate acceptance but do not provide enough schedule details (day/time/timezone) to execute safely.

## A practical decision-ownership model

Use three decision classes.

### 1) Deterministic-owned decisions (Class D)

These should stay in scaffolding:

- policy and compliance constraints,
- side-effect eligibility checks,
- idempotency/retry policy,
- action sequencing and commit control.

These are binary and auditable. If conditions fail, execution does not happen.

### 2) Model-owned decisions (Class M)

These should stay model-mediated:

- intent parsing from messy language,
- ambiguity detection,
- extraction of candidate entities/slots,
- clarification suggestion generation.

These are probabilistic and should carry uncertainty.

### 3) Hybrid arbitration decisions (Class H)

These require both layers:

- proceed vs clarify,
- branch selection when multiple intents coexist,
- mapping interpreted intent to an executable action.

A strong operating rule is simple: **model proposes, scaffolding ratifies** before side effects.

## Ambiguity pattern 1: mixed intent in one message

Example:

> "Thanks, that works. Can you also clarify whether onboarding support is included?"

This is not one intent. It is acceptance plus clarification.

### Common failure

A single-label router forces this into either `accept_meeting` or `ask_question`.

- If it picks clarification only, booking momentum is lost.
- If it picks acceptance only, user concern is ignored.

### Better design

Represent multi-intent explicitly at the interface, then execute a composite plan:

- acknowledge and answer clarification,
- keep scheduling flow alive,
- request any missing scheduling constraints.

If your transition model cannot represent dual-intent turns, this failure is structural, not incidental.

## Ambiguity pattern 2: underspecified acceptance

Example:

> "Yes, let's do it next week."

The intent is positive, but execution fields are incomplete.

### Common failure

System maps positive sentiment directly to `schedule_meeting` and advances to commit state.

This causes either:

- hard downstream failures, or
- silent wrong assumptions (bad day/time).

### Better design

Create explicit intermediate state (for example `accepted_but_incomplete`) and require deterministic completeness checks before execution.

Acceptance and execution-readiness are different decisions and must remain separate.

## How correctness is lost: one failure path

Input:

> "Sounds good. Could you clarify pricing tiers? Also maybe Thursday afternoon works."

1. **Interpretation**: model extracts partial acceptance, clarification intent, and fuzzy time.
2. **Routing**: brittle router collapses to one branch.
3. **State update**: system records only one intent path.
4. **Execution**: wrong downstream behavior (premature scheduling or missed conversion).

The loss happens at boundary compression: multiple uncertain signals are reduced to one deterministic action prematurely.

## Why brittleness clusters at handoff points

Three causes repeat across products:

1. **Premature commitment**: plausible interpretation treated as final intent.
2. **Uncertainty loss**: alternatives/confidence dropped by interface schema.
3. **Syntactic progression over semantic correctness**: workflow advances because fields exist, not because meaning is resolved.

This is the gap between "allowed by workflow" and "correct for user intent."

## A failure-attribution framework

When incident-reviewing hybrid agents, separate causes into three linked buckets:

- **Scaffolding failures**: rigid one-intent router, missing clarification states, permissive commit transitions.
- **Model failures**: semantic misreads, overconfidence on vague phrasing, weak modality handling.
- **Interface failures**: lossy model-output schema, no confidence-to-policy mapping, early single-action collapse.

Most serious incidents are mixed-cause. Treating them as "just prompt quality" usually misses the fix.

## Portable architecture rules for FDE teams

1. Never let acceptance alone trigger side effects.
2. Treat multi-intent turns as first-class state.
3. Preserve uncertainty across the model-to-router boundary.
4. Add explicit intermediate states (`needs_clarification`, `accepted_but_incomplete`).
5. Use stricter gates for high-risk writes than for read-only responses.
6. Log boundary artifacts (candidate intents, confidence, chosen branch, gate outcome).

## Conclusion

The healthiest hybrid systems are asymmetric by risk:

- model-driven upstream interpretation,
- deterministic downstream commitment.

If your team can specify, for each planning decision, **who owns it, what uncertainty is acceptable, and what gate must pass before action**, you will remove most brittle failures at the scaffolding-model boundary.

## Research references

1. ReAct: Synergizing Reasoning and Acting in Language Models (Yao et al., 2023)  
https://arxiv.org/abs/2210.03629

2. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation (Wu et al., 2023)  
https://arxiv.org/abs/2308.08155

3. OpenAI Model Spec (2024)  
https://model-spec.openai.com/