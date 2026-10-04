"""Seeds and a CLIP+geometry head for the real-pixel study (REV-7).

For every training seed in the predictions file and every comparison, report
top-1 accuracy, the quadratic-score split on raw outputs, the split with each
model's temperature fitted on a held-out half of the images (the paper's
protocol and split seed), and the within-cell AUC difference with an image
bootstrap. MLP-VISGEO-S adds the CLIP crop features to the geometry model, so
"pixels add to the proxy" is tested directly, as the review asked.

Seeds vary initialisation and batch order; the training subsample is the same
for every seed. Seed 0 must reproduce the archived predictions exactly, which
is checked when --reference is given.

Run (on the Colab VM, next to the predictions):
  python vg_visual_seed_stats.py --models /content/vg_visual_seeds.npz \
      --reference /content/vg_visual_models.npz --out /content/vg_visual_seeds.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from wager.antisymmetric import decompose_gain  # noqa: E402
from wager.rank import within_cell_auc_contrast  # noqa: E402

EPS = 1e-12
PAIRS = [("MLP-VISUAL-S", "MLP-SPATIAL-S"), ("MLP-VISGEO-S", "MLP-SPATIAL-S"),
         ("MLP-VISGEO-S", "MLP-VISUAL-S"), ("MLP-VISUAL-S", "MLP-CLASS-S"),
         ("MLP-SPATIAL-S", "MLP-CLASS-S")]


def temp_scale(p, T):
    z = np.log(np.clip(p, EPS, None)) / T
    z -= z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_temperature(p, labels):          # identical grid to vg_prior_consequence.py
    grid = np.linspace(0.25, 8.0, 311)
    nll = [float(-np.mean(np.log(np.clip(temp_scale(p, t)[np.arange(len(labels)), labels],
                                         EPS, None)))) for t in grid]
    return float(grid[int(np.argmin(nll))])


def split(q_new, q_old, y, phi, image):
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        r = decompose_gain(q_new, q_old, y, phi, groups=image, score="brier")
    return {"total": r.total_gain, "group": r.prior_gain, "case": r.reasoning_gain,
            "case_ci": list(r.reasoning_ci)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True)
    ap.add_argument("--reference")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-boot", type=int, default=200)
    a = ap.parse_args()
    d = np.load(a.models)
    y, phi, image = d["y"].astype(np.int64), d["phi"].astype(np.int64), d["image"]
    heads = sorted({k.split("@")[0] for k in d.files if k.startswith("MLP-")})
    seeds = sorted({int(k.split("@")[1]) if "@" in k else 0
                    for k in d.files if k.startswith("MLP-")})
    out = {"n_test": int(len(y)), "heads": heads, "seeds": seeds, "per_seed": {}}

    if a.reference:
        ref = np.load(a.reference)
        out["seed0_vs_reference"] = {
            h: float(np.abs(ref[h].astype(np.float64) - d[h].astype(np.float64)).max())
            for h in ref.files if h.startswith("MLP-") and h in d.files}
        print("seed 0 against the archived predictions (max |diff|):", out["seed0_vs_reference"])

    rng = np.random.default_rng(20260810)          # the paper's calibration split
    imgs = np.unique(image)
    cal_imgs = set(imgs[rng.permutation(len(imgs))[: len(imgs) // 2]].tolist())
    cal = np.array([i in cal_imgs for i in image])
    aud = ~cal

    for s in seeds:
        key = (lambda h: h) if s == 0 else (lambda h: f"{h}@{s}")
        Q = {h: d[key(h)].astype(np.float64) for h in heads if key(h) in d.files}
        Q = {h: q / q.sum(1, keepdims=True) for h, q in Q.items()}
        T = {h: fit_temperature(q[cal], y[cal]) for h, q in Q.items()}
        row = {"accuracy": {h: float((q.argmax(1) == y).mean()) for h, q in Q.items()},
               "temperature": T, "pairs": {}}
        for new, old in PAIRS:
            if new not in Q or old not in Q:
                continue
            auc = within_cell_auc_contrast(Q[new], Q[old], y, phi, image, n_boot=a.n_boot)
            row["pairs"][f"{new} vs {old}"] = {
                "raw": split(Q[new], Q[old], y, phi, image),
                "matched": split(temp_scale(Q[new], T[new])[aud], temp_scale(Q[old], T[old])[aud],
                                 y[aud], phi[aud], image[aud]),
                "auc": {"difference": auc.difference, "ci": list(auc.ci),
                        "auc_new": auc.auc_new, "auc_old": auc.auc_old}}
            m = row["pairs"][f"{new} vs {old}"]
            print(f"seed {s} {new:14s} vs {old:14s} matched case {m['matched']['case']:+.5f} "
                  f"[{m['matched']['case_ci'][0]:+.5f},{m['matched']['case_ci'][1]:+.5f}]  "
                  f"AUC {auc.difference:+.4f} [{auc.ci[0]:+.4f},{auc.ci[1]:+.4f}]", flush=True)
        out["per_seed"][str(s)] = row
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("STATS COMPLETE", flush=True)


if __name__ == "__main__":
    main()
