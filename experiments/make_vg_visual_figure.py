"""Figure for the matched-subsample real-pixel study on Visual Genome.

Left: the exact decomposition of each pair's gain into prior-transported and
instance-alignment channels, with 95% image-clustered intervals on the alignment term.
Right: the alignment term alone, which is the quantity the study is actually about --
whether real pixel content buys instance alignment beyond box geometry.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results", "vg_visual_results.json")
OUTDIRS = [os.path.join(ROOT, "results", "figures"),
           os.path.join(ROOT, "manuscript", "figures")]

PRIOR_C = "#4C72B0"
ALIGN_C = "#C44E52"
TOTAL_C = "#55A868"


def short(name):
    return name.replace("MLP-", "").replace("-S", "")


def main():
    with open(RESULTS, encoding="utf-8") as f:
        res = json.load(f)
    rows = res["comparisons"]
    labels = [f"{short(r['new'])}\nvs {short(r['old'])}" for r in rows]
    prior = np.array([r["prior_gain"] for r in rows])
    align = np.array([r["reasoning_gain"] for r in rows])
    total = np.array([r["total_gain"] for r in rows])
    lo = np.array([r["reasoning_ci"][0] for r in rows])
    hi = np.array([r["reasoning_ci"][1] for r in rows])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.9))
    y = np.arange(len(rows))
    h = 0.26
    ax1.barh(y + h, prior, h, color=PRIOR_C, label=r"prior-transported $\Delta P$")
    ax1.barh(y, align, h, color=ALIGN_C, label=r"instance alignment $\Delta R$",
             xerr=[align - lo, hi - align],
             error_kw=dict(ecolor="0.25", lw=1.1, capsize=3))
    ax1.barh(y - h, total, h, color=TOTAL_C, label=r"total $\Delta T$")
    ax1.axvline(0, color="0.3", lw=1)
    ax1.set_yticks(y); ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel("quadratic-score gain")
    ax1.set_title("Exact decomposition (class-pair audit)", fontsize=11)
    ax1.legend(fontsize=8.5, loc="best", framealpha=0.95)
    ax1.grid(axis="x", alpha=0.25)

    ax2.barh(y, align, 0.5, color=ALIGN_C,
             xerr=[align - lo, hi - align],
             error_kw=dict(ecolor="0.25", lw=1.2, capsize=4))
    ax2.axvline(0, color="0.3", lw=1)
    ax2.set_yticks(y); ax2.set_yticklabels(labels, fontsize=9)
    ax2.set_xlabel(r"instance-alignment gain $\Delta R$")
    ax2.set_title("Alignment channel with 95% CI", fontsize=11)
    ax2.grid(axis="x", alpha=0.25)

    fig.tight_layout()
    for d in OUTDIRS:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "fig7_vg_visual.png")
        fig.savefig(p, dpi=400, bbox_inches="tight")
        print(f"wrote {p}", flush=True)


if __name__ == "__main__":
    main()
