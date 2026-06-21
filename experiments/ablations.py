"""Phase 5 (lite) - ablations for the WAGER SGG study (algorithm.md section 10E).

Stability of the headline verdict across:
  * phi granularity      : (subject, object) cell  vs  subject-only
  * clip c               : log K  vs  log K / 2  vs  2 log K
  * projection shrinkage : m in {0, 0.25, 1.0}
  * number of permutations R

Reuses the cached model distributions in results/sgg_dists.npz so it is fast.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wager.pipeline import ModelData, build_projection, run_wager_eval
from wager.rgr import reasoning_gain_ratio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
DISTS = os.path.join(RESULTS, "sgg_dists.npz")
VG = os.path.join(ROOT, "data", "vg", "vg_predcls.npz")


def _split(image, seed=0):
    img_u = np.unique(image)
    rng = np.random.default_rng(seed)
    rng.shuffle(img_u)
    proj_imgs = set(img_u[: len(img_u) // 2].tolist())
    in_proj = np.array([im in proj_imgs for im in image])
    return in_proj, ~in_proj


def run_one(q_fp, q_f, y, phi, image, coarse, K, c, m, R=20):
    in_proj, ev = _split(image)
    def wag(q, name):
        proj = build_projection(q[in_proj], phi[in_proj], K, m=m, coarse_proj=coarse[in_proj])
        return run_wager_eval(ModelData(name, q[ev], y[ev], phi[ev], image[ev], coarse=coarse[ev]),
                              proj, R=R, c=c, alpha=0.05, seed=0)
    rfp, rf = wag(q_fp, "fp"), wag(q_f, "f")
    return reasoning_gain_ratio(rfp, rf, c=c, alpha=0.05)


def main():
    dz = np.load(DISTS, allow_pickle=True)
    vg = np.load(VG, allow_pickle=True)
    y, phi, image = dz["y"], dz["phi"], dz["image"]
    K = int(vg["n_pred"]); n_obj = int(vg["n_obj"])
    # recover subject id from phi (= subj*n_obj + obj)
    subj = (phi // n_obj).astype(np.int64)
    obj = (phi % n_obj).astype(np.int64)

    q_sp = dz["MLP-SPATIAL"]
    q_freq = dz["FREQ"]
    base = float(np.log(K))

    abl = {}
    # phi granularity
    abl["phi_granularity"] = []
    for label, phi_use, coarse_use in [
        ("subj_obj_cell", phi.astype(np.int64), subj),
        ("subject_only", subj, np.zeros_like(subj)),
    ]:
        rgr = run_one(q_sp, q_freq, y, phi_use, image, coarse_use, K, base, m=0.25)
        abl["phi_granularity"].append({"phi": label, "RGR": rgr.rgr,
                                       "ci": list(rgr.fieller_ci), "verdict": rgr.verdict})
        print(f"phi={label:14s} RGR={rgr.rgr:.3f} {rgr.verdict}")

    # clip c
    abl["clip_c"] = []
    for label, c in [("logK/2", base / 2), ("logK", base), ("2logK", 2 * base)]:
        rgr = run_one(q_sp, q_freq, y, phi.astype(np.int64), image, subj, K, c, m=0.25)
        abl["clip_c"].append({"c": label, "RGR": rgr.rgr, "verdict": rgr.verdict})
        print(f"clip={label:8s} RGR={rgr.rgr:.3f} {rgr.verdict}")

    # shrinkage m
    abl["shrinkage_m"] = []
    for m in (0.0, 0.25, 1.0):
        rgr = run_one(q_sp, q_freq, y, phi.astype(np.int64), image, subj, K, base, m=m)
        abl["shrinkage_m"].append({"m": m, "RGR": rgr.rgr, "verdict": rgr.verdict})
        print(f"m={m:4} RGR={rgr.rgr:.3f} {rgr.verdict}")

    # permutations R
    abl["permutations_R"] = []
    for R in (10, 30, 60):
        rgr = run_one(q_sp, q_freq, y, phi.astype(np.int64), image, subj, K, base, m=0.25, R=R)
        abl["permutations_R"].append({"R": R, "RGR": rgr.rgr, "verdict": rgr.verdict})
        print(f"R={R:3} RGR={rgr.rgr:.3f} {rgr.verdict}")

    with open(os.path.join(RESULTS, "ablations.json"), "w") as f:
        json.dump(abl, f, indent=2)
    print("saved -> results/ablations.json")


if __name__ == "__main__":
    main()
