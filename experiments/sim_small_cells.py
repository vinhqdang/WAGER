"""Coverage of the case-level interval when cells are small (R2-9).

The H\'ajek variance keeps the first-order projection of each cell's U-statistic. In
a cell of two cases the U-statistic is its single kernel, and the omitted degenerate
term is of the same order as the projection, so the interval can under-cover when
most relations sit in very small cells. This measures coverage of the nominal 95%
interval with every cell of size n_c (2, 3, 4, 8, 20; each relation its own image),
and with cell sizes drawn from the cell-size distribution of the
VG150 audit (Sec. 5). Cells and their label priors are fixed per regime and only the
labels are redrawn; truth is the mean of the (unbiased) estimator over 2,000 replicates.

Run: python experiments/sim_small_cells.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wager.antisymmetric import decompose_gain  # noqa: E402

OUT = ROOT / "results/sim_small_cells.json"
K, N_TARGET = 5, 4000


def vg_sizes():
    m = np.load(ROOT / "data/vg_motifs/wager_sgg/meta.npz")
    phi = m["subj"].astype(np.int64) * 151 + m["obj"].astype(np.int64)
    _, cnt = np.unique(phi, return_counts=True)
    return cnt[cnt >= 2]


def draw(rng, sizes, priors, beta):
    """One replicate: the cells and their label priors are fixed by the regime; only the
    labels are redrawn, so every replicate estimates the same population quantity."""
    phi = np.repeat(np.arange(len(sizes)), sizes)
    y = (priors[phi].cumsum(1) > rng.random(len(phi))[:, None]).argmax(1)
    q_old = priors[phi]
    oracle = np.full((len(y), K), 0.02 / (K - 1))
    oracle[np.arange(len(y)), y] = 0.98
    return (1 - beta) * q_old + beta * oracle, q_old, y, phi


def regime(name, pool):
    rng = np.random.default_rng(sum(map(ord, name)))
    if name.startswith("n_c="):
        n = int(name.split("=")[1])
        sizes = np.full(N_TARGET // n, n)
    else:                                  # VG mass-matched: sample cells by size
        out, tot = [], 0
        while tot < N_TARGET:
            out.append(int(rng.choice(pool)))
            tot += out[-1]
        sizes = np.asarray(out)
    return sizes, rng.dirichlet(np.full(K, 0.8), size=len(sizes))


def main():
    pool = vg_sizes()
    regimes = [("n_c=2", 0.3), ("n_c=3", 0.3), ("n_c=4", 0.3), ("n_c=8", 0.3),
               ("n_c=20", 0.3), ("VG150 cell sizes", 0.3)]
    res = {"vg_fraction_in_two_case_cells": float((pool == 2).sum() * 2 / pool.sum())}
    for name, beta in regimes:
        sizes, priors = regime(name, pool)
        truth = np.mean([decompose_gain(*draw(np.random.default_rng(10_000 + r), sizes, priors,
                                              beta)).alignment_gain for r in range(2000)])
        cover, ratio_se, ests = [], [], []
        for r in range(400):
            q1, q0, y, phi = draw(np.random.default_rng(50_000 + r), sizes, priors, beta)
            d = decompose_gain(q1, q0, y, phi, groups=np.arange(len(y)))
            lo, hi = d.alignment_ci
            cover.append(lo <= truth <= hi)
            ests.append(d.alignment_gain)
            ratio_se.append((hi - lo) / (2 * 1.959964))
        res[name] = {"coverage": float(np.mean(cover)),
                     "se_over_sd": float(np.mean(ratio_se) / np.std(ests, ddof=1)),
                     "truth": float(truth)}
        print(name, res[name], flush=True)
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
