# Tweet thread - Day 2 (post-revision)

**1/**
Most agent failures are not "the model was bad" or "the workflow was bad" alone. They happen at the boundary: model output gets treated like execution truth before ambiguity is resolved.

**2/**
In Gemechis's setup, two ambiguity patterns are load-bearing: (1) mixed intent in one reply (accept + clarification request), and (2) underspecified acceptance ("yes" without clear day/time).

**3/**
If your router assumes one intent per turn, mixed-intent replies get flattened. You either ignore the clarification or miss the booking signal. Both outcomes are avoidable architecture failures.

**4/**
If your system treats positive sentiment as execution readiness, underspecified acceptance becomes a bad schedule action. Acceptance and executable readiness are separate decisions and should be modeled separately.

**5/**
Practical rule: model proposes, scaffolding ratifies. Let the model interpret; require deterministic gates for side effects (field completeness, policy checks, idempotent execution conditions).

**6/**
The fix is boundary redesign: preserve uncertainty across handoffs, support multi-intent state, add `accepted_but_incomplete` / `needs_clarification` transitions, then commit only after ratification.