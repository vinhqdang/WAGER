"""Coverage of the mean-recall intervals: the case-level hit contrast and the share (R1 W4).

The mean-recall split scores a hit matrix rather than a proper score, and its case-level
interval is the same image-clustered Hajek interval; the group-level share is a ratio
whose interval comes from a delete-a-group jackknife over images. Neither was covered by
the proper-score coverage study. This simulates both. Cells have VG150's cell-size
distribution; relations are grouped into images of about seven that cut across cells; each
case has per-label evidence e_x(y) = 1[y = y_x] zeta_x + noise with zeta_x ~ N(1, 1), so cases
differ in how well their own label is supported; the old model hits label y with
probability sigmoid(b_c(y) + gamma e_x(y)), the new model with sigmoid(b_c(y) + delta_c(y)
+ gamma (1 + beta) e_x(y) + u_img), so delta moves the per-cell operating point (group-level),
beta uses the evidence better (case-level) and u_img, shared by an image's relations,
clusters the hits. Truth is the mean of the (unbiased) estimators over 2,000 replicates with
the design fixed; coverage is over 400 replicates.

Run: python experiments/sim_hit_coverage.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402

OUT = ROOT / "results/sim_hit_coverage.json"
K, N_TARGET, IMG, G = 5, 6000, 7, 100
GAMMA, BETA, SIG_IMG = 1.5, 0.4, 0.6


def sig(z):
    return 1 / (1 + np.exp(-z))


def vg_sizes():
    m = np.load(ROOT / "data/vg_motifs/wager_sgg/meta.npz")
    phi = m["subj"].astype(np.int64) * 151 + m["obj"].astype(np.int64)
    _, cnt = np.unique(phi, return_counts=True)
    return cnt[cnt >= 2]


def design(rng, pool):
    sizes, tot = [], 0
    while tot < N_TARGET:
        sizes.append(int(rng.choice(pool)))
        tot += sizes[-1]
    phi = np.repeat(np.arange(len(sizes)), sizes)
    n = len(phi)
    prior = rng.dirichlet(np.full(K, 0.8), size=len(sizes))
    b = rng.normal(-1.0, 0.7, size=(len(sizes), K))          # old operating point per cell, label
    delta = rng.normal(0.0, 0.8, size=(len(sizes), K))        # the new model's shift of it
    image = rng.permutation(n) // IMG
    return phi, prior, b, delta, image


def draw(rng, phi, prior, b, delta, image):
    n = len(phi)
    y = (prior[phi].cumsum(1) > rng.random(n)[:, None]).argmax(1)
    zeta = rng.normal(1.0, 1.0, size=n)
    e = rng.normal(0.0, 0.5, size=(n, K))
    e[np.arange(n), y] += zeta
    u = rng.normal(0.0, SIG_IMG, size=image.max() + 1)[image]
    p0 = sig(b[phi] + GAMMA * e)
    p1 = sig(b[phi] + delta[phi] + GAMMA * (1 + BETA) * e + u[:, None])
    h0 = rng.random((n, K)) < p0
    h1 = rng.random((n, K)) < p1
    return y, h0, h1


def split(y, h0, h1, phi, image, mask=None):
    if mask is None:
        mask = np.ones(len(y), bool)
    y, h0, h1, phi, image = y[mask], h0[mask], h1[mask], phi[mask], image[mask]
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv] >= 2
    n_y = np.bincount(y[elig], minlength=K).astype(float)
    w = np.where(n_y > 0, 1.0 / (K * np.maximum(n_y, 1)), 0.0)
    h = elig.sum() * w[None, :] * (h1.astype(float) - h0.astype(float))
    g = decompose_gain_matrix(h[elig], y[elig], phi[elig], groups=image[elig], score="hit")
    return g.total_gain, g.prior_gain, g.alignment_gain, g.alignment_ci


def main():
    pool = vg_sizes()
    rng = np.random.default_rng(20261013)
    phi, prior, b, delta, image = design(rng, pool)
    n_img = image.max() + 1
    est = np.array([split(*draw(np.random.default_rng(10_000 + r), phi, prior, b, delta, image), phi, image)[:3]
                    for r in range(2000)])
    truth_T, truth_P, truth_R = est.mean(0)
    truth_share = truth_P / truth_T
    print(f"truth: total {truth_T:+.5f} group {truth_P:+.5f} case {truth_R:+.5f} share {truth_share:.4f}", flush=True)
    cover_R, cover_share, width_R, se_ratio, share_ratio = [], [], [], [], []
    ests_R, ests_share = [], []
    for r in range(400):
        y, h0, h1 = draw(np.random.default_rng(50_000 + r), phi, prior, b, delta, image)
        T, P, R, ci = split(y, h0, h1, phi, image)
        cover_R.append(ci[0] <= truth_R <= ci[1])
        ests_R.append(R)
        width_R.append((ci[1] - ci[0]) / (2 * 1.959964))
        grp = np.random.default_rng(80_000 + r).permutation(n_img) % G
        jk = []
        for g in range(G):
            Tg, Pg, _, _ = split(y, h0, h1, phi, image, mask=grp[image] != g)
            jk.append(Pg / Tg)
        jk = np.asarray(jk)
        se = np.sqrt((G - 1) / G * np.sum((jk - jk.mean()) ** 2))
        share = P / T
        cover_share.append(share - 1.959964 * se <= truth_share <= share + 1.959964 * se)
        ests_share.append(share)
        share_ratio.append(se)
        if (r + 1) % 50 == 0:
            print(f"  {r+1}: case coverage {np.mean(cover_R):.3f}  share coverage {np.mean(cover_share):.3f}", flush=True)
    res = {"n_relations": int(len(phi)), "n_cells": int(len(prior)), "n_images": int(n_img),
           "truth": {"total": truth_T, "group": truth_P, "case": truth_R, "share": truth_share},
           "case": {"coverage": float(np.mean(cover_R)),
                    "se_over_sd": float(np.mean(width_R) / np.std(ests_R, ddof=1))},
           "share": {"coverage": float(np.mean(cover_share)),
                     "se_over_sd": float(np.mean(share_ratio) / np.std(ests_share, ddof=1))}}
    print(res)
    OUT.write_text(json.dumps(res, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
