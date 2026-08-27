"""Confounding-sensitivity bound (Proposition: sensitivity to an unrecorded
confounder) for the headline VG150 comparison.

For each eligible phi-cell, bounds how much an unrecorded confounder Z could move
the alignment estimate without observing Z at all: the bound needs only the
within-cell variance of the gain vector and the within-cell label frequencies,
both computable from the declared cell. See manuscript/3method.tex Section
"Sensitivity to an unrecorded confounder" and the proof in 7appendix.tex.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.antisymmetric import gain_matrix, decompose_gain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")


def confounding_bound(q_new, q_old, y, phi, score="brier"):
    """Dataset-level bound B and robustness value rho_dagger for the alignment gain.

    B = (1/N*) sum_{c: n_c>=2} n_c * B_c,
    B_c = sqrt(sum_y Var(H(y)|c)) * sqrt(sum_y p_y(c)(1-p_y(c)))
    -- a product of two square-root sums (Proposition: sensitivity bound), NOT a sum of
    per-label square roots: Cauchy-Schwarz bounds Var(a_y|c)<=Var(H(y)|c) and
    Var(b_y|c)<=p_y(1-p_y) termwise, but the square root of a sum of termwise-dominated
    values is only comparable to the *product* of the two sums' square roots, not to a
    sum of per-label products of square roots (a strictly different, non-comparable
    quantity). See manuscript/7appendix.tex's proof of the sensitivity proposition.
    rho_dagger = |Delta_R_hat| / B  (minimal confounding strength that could zero it out).
    """
    h = gain_matrix(q_new, q_old, score=score)
    n, k = h.shape
    y = np.asarray(y, dtype=np.int64)
    phi = np.asarray(phi)
    _, inv, counts = np.unique(phi, return_inverse=True, return_counts=True)

    total_weighted_b = 0.0
    n_star = 0
    for c in np.flatnonzero(counts >= 2):
        idx = np.flatnonzero(inv == c)
        nc = len(idx)
        hc = h[idx]
        yc = y[idx]
        var_h = hc.var(axis=0, ddof=0)  # Var(H(y) | phi=c) for each label y
        p_y = np.bincount(yc, minlength=k).astype(np.float64) / nc
        b_c = np.sqrt(np.sum(var_h)) * np.sqrt(np.sum(p_y * (1.0 - p_y)))
        total_weighted_b += nc * b_c
        n_star += nc
    b = total_weighted_b / n_star
    return b, n_star


def main():
    d = np.load(os.path.join(RESULTS, "sgg_dists.npz"), allow_pickle=True)
    q_new, q_old = d["MLP-SPATIAL"], d["MLP-CLASS"]
    y, phi = d["y"].astype(np.int64), d["phi"]

    result = decompose_gain(q_new, q_old, y, phi, score="brier")
    b, n_star = confounding_bound(q_new, q_old, y, phi, score="brier")
    rho_dagger = abs(result.reasoning_gain) / b

    out = {
        "pair": "MLP-SPATIAL vs MLP-CLASS",
        "phi": "class pair (default)",
        "reasoning_gain": result.reasoning_gain,
        "reasoning_ci": list(result.reasoning_ci),
        "bound_B": b,
        "robustness_value_rho_dagger": rho_dagger,
        "n_identified": n_star,
    }
    print(json.dumps(out, indent=2))
    with open(os.path.join(RESULTS, "sensitivity_bound.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
