"""Controlled validation for within-cell antisymmetric WAGER."""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.antisymmetric import cyclic_randomization_test, decompose_gain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "antisymmetric_simulation.json")


def generate(seed: int, beta: float, ncell: int = 24, per: int = 50, k: int = 5):
    """Generate a prior-only baseline and an oracle-mixture upgraded model."""
    rng = np.random.default_rng(seed)
    phi = np.repeat(np.arange(ncell), per)
    priors = rng.dirichlet(np.full(k, 0.8), size=ncell)
    y = np.array([rng.choice(k, p=priors[c]) for c in phi], dtype=np.int64)
    q_old = priors[phi]
    oracle = np.full((len(y), k), 0.02 / (k - 1))
    oracle[np.arange(len(y)), y] = 0.98
    q_new = (1.0 - beta) * q_old + beta * oracle
    return q_new, q_old, y, phi


def main():
    betas = np.linspace(0, 0.8, 9)
    recovery = []
    for beta in betas:
        vals = []
        for rep in range(40):
            q1, q0, y, phi = generate(1000 + rep, float(beta))
            vals.append(decompose_gain(q1, q0, y, phi).reasoning_gain)
        recovery.append({
            "beta": float(beta),
            "mean": float(np.mean(vals)),
            "sd": float(np.std(vals, ddof=1)),
        })

    # At beta=0 both models are identical.  Use a randomized, prediction-noise
    # null so p-values are not degenerate at one.
    rng = np.random.default_rng(17)
    null_p = []
    null_r = []
    for rep in range(200):
        q1, q0, y, phi = generate(5000 + rep, 0.0, ncell=16, per=30)
        noise = rng.normal(0, 0.03, size=q1.shape)
        q1 = np.maximum(q1 + noise, 1e-4)
        q1 /= q1.sum(1, keepdims=True)
        # Break any accidental noise-label alignment while preserving phi.
        for c in np.unique(phi):
            ix = np.flatnonzero(phi == c)
            q1[ix] = q1[rng.permutation(ix)]
        res = decompose_gain(q1, q0, y, phi)
        p, _ = cyclic_randomization_test(
            q1, q0, y, phi, n_randomizations=99, seed=9000 + rep
        )
        null_r.append(res.reasoning_gain)
        null_p.append(p)

    out = {
        "recovery": recovery,
        "null_runs": len(null_p),
        "null_type1_alpha_005": float(np.mean(np.asarray(null_p) <= 0.05)),
        "null_reasoning_mean": float(np.mean(null_r)),
        "null_p_values": null_p,
        "null_reasoning": null_r,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps({k: v for k, v in out.items() if not isinstance(v, list)}, indent=2))
    return out


if __name__ == "__main__":
    main()
