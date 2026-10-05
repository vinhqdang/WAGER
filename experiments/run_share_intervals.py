"""Intervals for the group-level share of each mean-recall gain (R2-9).

The paper reports that 87% of TDE's micro-averaged mR@50 gain (graph constraint) is
group-level, and 97% of IETrans's. A share is a ratio of two correlated estimates,
so its interval comes from a delete-a-group jackknife over images: the test images
are split at random into G = 100 groups, the whole split (eligibility, label
weights, decomposition) is recomputed with each group left out, and the jackknife
standard error gives a normal interval around the full-sample share.

Run: python experiments/run_share_intervals.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain_matrix  # noqa: E402
from sgg_variants import load_variant  # noqa: E402

DDIR = ROOT / "data/vg_motifs/wager_sgg"
OUT = ROOT / "results/sgg_share_intervals.json"
N_PRED, N_OBJ, K, G = 50, 151, 50, 100


def shares(hn_all, ho_all, y, phi, mask):
    y, phi = y[mask], phi[mask]
    hn, ho = hn_all[mask], ho_all[mask]
    _, inv, cnt = np.unique(phi, return_inverse=True, return_counts=True)
    elig = cnt[inv] >= 2
    n_y = np.bincount(y[elig], minlength=N_PRED + 1).astype(float)
    w = np.zeros(N_PRED + 1)
    w[1:] = np.where(n_y[1:] > 0, 1.0 / (N_PRED * np.maximum(n_y[1:], 1)), 0.0)
    h = elig.sum() * w[None, :] * (hn.astype(float) - ho.astype(float))
    g = decompose_gain_matrix(h, y, phi, score="hit")
    return g.total_gain, g.prior_gain, g.prior_gain / g.total_gain


def main():
    meta = np.load(DDIR / "meta.npz")
    y = meta["pred"].astype(np.int64)
    image = meta["image_index"].astype(np.int64)
    phi = meta["subj"].astype(np.int64) * N_OBJ + meta["obj"].astype(np.int64)
    imgs = np.unique(image)
    grp_of_img = np.random.default_rng(0).permutation(len(imgs)) % G
    grp = grp_of_img[np.searchsorted(imgs, image)]
    base = load_variant("none")["gc_rank"] < K
    out = {"K": K, "graph_constraint": True, "G": G, "rows": {}}
    for new in ("TDE", "la1", "ietrans"):
        hn = load_variant(new)["gc_rank"] < K
        T, P, s = shares(hn, base, y, phi, np.ones(len(y), bool))
        jk = np.array([shares(hn, base, y, phi, grp != g)[2] for g in range(G)])
        se = float(np.sqrt((G - 1) / G * ((jk - jk.mean()) ** 2).sum()))
        out["rows"][new] = {"total": T, "group": P, "share": s, "share_se": se,
                            "share_ci": [s - 1.96 * se, s + 1.96 * se]}
        print(f"{new}: share {s:.4f} [{s-1.96*se:.4f}, {s+1.96*se:.4f}]  (total {T:+.4f})", flush=True)
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
