"""Centroid-cosine drift demo — show why drift_score ~ 0 does not entail semantic stability.

Setup: build two cohorts of "embeddings" in R^128. Cohort A is a tight cluster
around a fixed mean direction. Cohort B is constructed by sampling around the
same mean with much wider spread, then EXPLICITLY mean-shifted so that
A.mean(axis=0) == B.mean(axis=0) to float precision. The centroid-cosine
drift score is therefore zero by construction — but the cohorts' distributions
are obviously different, and that difference matters for any "semantic
stability" claim.

This demo treats embeddings as raw R^d vectors (the centroid math is identical
under L2-normalization; the punchline is the same: a centroid is a first
moment, and a first moment is silent on dispersion, multimodality, or shape).

Run:
    python day_4/scripts/centroid_drift_demo.py
"""
from __future__ import annotations

import sys

# Force UTF-8 output so unicode characters render on Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np


def centroid_cosine_drift(a: np.ndarray, b: np.ndarray) -> float:
    """The metric the contract uses: 1 - cos(centroid_a, centroid_b)."""
    ca = a.mean(axis=0)
    cb = b.mean(axis=0)
    cos = float(np.dot(ca, cb) / (np.linalg.norm(ca) * np.linalg.norm(cb) + 1e-12))
    return 1.0 - cos


def within_cohort_dispersion(x: np.ndarray) -> float:
    """Mean L2 distance from each sample to the cohort centroid. A 2nd-moment summary."""
    c = x.mean(axis=0)
    return float(np.mean(np.linalg.norm(x - c, axis=1)))


def permutation_test_centroid(
    a: np.ndarray, b: np.ndarray, n_perm: int = 1000, rng: np.random.Generator | None = None
) -> float:
    """One-sided permutation p-value on centroid-cosine drift under H0: A and B share a distribution."""
    if rng is None:
        rng = np.random.default_rng(0)
    observed = centroid_cosine_drift(a, b)
    pooled = np.concatenate([a, b], axis=0)
    n_a = a.shape[0]
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        permuted = centroid_cosine_drift(pooled[:n_a], pooled[n_a:])
        if permuted >= observed:
            count += 1
    return (count + 1) / (n_perm + 1)


def main() -> int:
    rng = np.random.default_rng(42)
    d = 128

    mean_dir = rng.standard_normal(d)
    mean_dir = mean_dir / np.linalg.norm(mean_dir)

    # Cohort A: tight cluster around mean_dir.
    a = mean_dir + 0.2 * rng.standard_normal((200, d))

    # Cohort B: much wider spread around mean_dir, then mean-shifted so its
    # sample mean equals A's exactly. drift_score = 0 by construction.
    b_raw = mean_dir + 2.0 * rng.standard_normal((200, d))
    b = b_raw - b_raw.mean(axis=0) + a.mean(axis=0)

    drift_centroid = centroid_cosine_drift(a, b)
    disp_a = within_cohort_dispersion(a)
    disp_b = within_cohort_dispersion(b)
    p_perm = permutation_test_centroid(a, b, n_perm=500, rng=np.random.default_rng(7))

    print("=" * 78)
    print("  Centroid-cosine drift demo - first moment is preserved, distribution is not")
    print("=" * 78)
    print("  Cohort A: n=200, low dispersion  (sigma=0.2 * I)")
    print("  Cohort B: n=200, high dispersion (sigma=2.0 * I), explicitly mean-shifted to A's mean")
    print()
    print(f"  centroid_cosine_drift(A, B)            = {drift_centroid:.2e}    <- the contract's drift_score")
    print(f"  within_cohort_dispersion(A) (mean L2)  = {disp_a:.4f}")
    print(f"  within_cohort_dispersion(B) (mean L2)  = {disp_b:.4f}")
    print(f"  dispersion ratio B/A                   = {disp_b / disp_a:.2f}x")
    print(f"  permutation p-value on centroid drift  = {p_perm:.4f}")
    print()
    print("  Reading:")
    print("    drift_centroid is exactly zero (to float precision).")
    print("    A contract that reads drift_score ~ 0 -> 'semantically stable' would say so here.")
    print("    But cohort B has ~10x the within-cohort dispersion of cohort A.")
    print("    A permutation test on centroid distance ALSO cannot tell the cohorts apart -")
    print("    because the centroid statistic is constant under this class of shift by")
    print("    construction. Even the test in the same family is blind to the change.")
    print()
    print("  Lesson: centroid-cosine drift is silent on every distributional moment beyond")
    print("  the mean. drift_score ~ 0 is necessary but NOT sufficient for distributional,")
    print("  let alone semantic, stability. The evidence chain has to include at least one")
    print("  2nd-moment statistic (within-cohort dispersion, MMD, energy distance) and a")
    print("  named provenance for the embeddings (model id, fallback path, n_eff).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
