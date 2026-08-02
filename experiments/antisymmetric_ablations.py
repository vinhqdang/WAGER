"""Sensitivity checks for the redesigned WAGER estimator."""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wager.antisymmetric import decompose_gain

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    d = np.load(os.path.join(ROOT, "results", "sgg_dists.npz"), allow_pickle=True)
    q1, q0, y, phi, image = d["MLP-SPATIAL"], d["MLP-CLASS"], d["y"], d["phi"], d["image"]
    rows = []

    for score in ["brier", "log"]:
        r = decompose_gain(q1, q0, y, phi, groups=image, score=score)
        rows.append({"factor": "score", "setting": score, **r.as_row()})

    n_obj = 150
    for name, key in [("class-pair", phi), ("subject-only", phi // n_obj)]:
        r = decompose_gain(q1, q0, y, key, groups=image, score="brier")
        rows.append({"factor": "prior feature", "setting": name, **r.as_row()})

    _, inv, counts = np.unique(phi, return_inverse=True, return_counts=True)
    for minimum in [2, 5, 10, 20]:
        keep = counts[inv] >= minimum
        r = decompose_gain(q1[keep], q0[keep], y[keep], phi[keep], groups=image[keep])
        rows.append({"factor": "minimum cell size", "setting": str(minimum), **r.as_row()})

    out = {"comparison": "MLP-SPATIAL vs MLP-CLASS", "rows": rows}
    with open(os.path.join(ROOT, "results", "antisymmetric_ablations.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    for x in rows:
        print(x["factor"], x["setting"], round(x["reasoning_gain"], 5), x["reasoning_ci"])
    return out


if __name__ == "__main__":
    main()
