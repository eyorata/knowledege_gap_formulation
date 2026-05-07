"""LoRA rank demo — show why allocated rank ≠ effective rank.

Ground truth: a 64×64 "task-specific update" of *intrinsic* rank 4
(plus a tiny noise floor — real fine-tuning targets are not exactly
low-rank). We then fit it with a LoRA decomposition B @ A at three
allocated ranks (r = 2, 4, 16) using gradient descent, and inspect
the SVD spectrum of the trained B @ A.

The point of the demo is to make the "effective rank concentrates
on a few directions even when allocated rank is large" claim visible
and verifiable with a numpy-only script (no PyTorch dependency).

Run:
    python day_3/scripts/lora_rank_demo.py
"""
from __future__ import annotations

import sys

# Force UTF-8 output so unicode characters render on Windows consoles.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

import numpy as np


def fit_lora(target: np.ndarray, rank: int, n_steps: int = 5000, lr: float = 0.01) -> tuple[np.ndarray, np.ndarray, float]:
    """Fit target ≈ B @ A with B (D, r) and A (r, D) by gradient descent."""
    d_out, d_in = target.shape
    rng = np.random.default_rng(0)
    B = np.zeros((d_out, rank))            # LoRA init: B = 0
    A = rng.standard_normal((rank, d_in)) * 0.01  # LoRA init: A small Gaussian
    for _ in range(n_steps):
        pred = B @ A
        err = pred - target
        grad_B = err @ A.T
        grad_A = B.T @ err
        B -= lr * grad_B
        A -= lr * grad_A
    final_err = float(np.linalg.norm(target - B @ A) / np.linalg.norm(target))
    return B, A, final_err


def main() -> int:
    np.random.seed(42)
    D = 64
    TRUE_RANK = 4

    # Build a target "task-specific update" of known intrinsic rank 4.
    U_true = np.random.randn(D, TRUE_RANK)
    V_true = np.random.randn(TRUE_RANK, D)
    target = (U_true @ V_true) / np.sqrt(TRUE_RANK)
    target += 0.01 * np.random.randn(D, D)  # tiny noise — real targets aren't exactly low-rank

    print("=" * 78)
    print("  LoRA rank demo — allocated rank vs. effective rank")
    print("=" * 78)
    print(f"  Target matrix:           {D} x {D}")
    print(f"  Intrinsic rank of target: ~{TRUE_RANK}  (+ small noise floor)")
    print()
    print(f"  {'allocated r':>11}  | {'final rel err':>14}  | top-8 singular values of trained B @ A")
    print("  " + "-" * 74)

    for r in [2, 4, 16]:
        _, _, err = fit_lora(target, r)
        # SVD of the trained low-rank update
        from numpy.linalg import svd
        # Re-fit so we can grab B, A
        B, A, _ = fit_lora(target, r)
        s = svd(B @ A, compute_uv=False)
        top = s[: min(8, len(s))]
        top_str = "  ".join(f"{x:5.3f}" for x in top)
        print(f"  {r:>11d}  | {err:>14.4f}  | {top_str}")

    print()
    print("  Reading the table:")
    print(f"    r = 2 :  under-parameterized. Target's intrinsic rank is {TRUE_RANK};")
    print( "             rank 2 cannot reach it. Error stays high.")
    print(f"    r = 4 :  matches intrinsic rank exactly. Four large singular values,")
    print( "             tight fit.")
    print(f"    r = 16:  over-parameterized. Still fits, but only ~{TRUE_RANK} singular")
    print( "             values are non-trivial; the remaining ~12 collapse to near zero.")
    print( "             Effective rank << allocated rank.")
    print()
    print("  Takeaway: r is a CAP on expressive capacity. Useful capacity is set by")
    print("  the task's intrinsic rank, not by the allocated r. Allocating more r than")
    print("  needed is harmless asymptotically but wastes parameters and can")
    print("  destabilize training on small data — most of those extra dimensions are")
    print("  driven to ~zero, but they still receive gradient noise along the way.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
