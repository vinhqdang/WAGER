"""Figure for the 20 Newsgroups-LT cross-domain WAGER study.

Left panel: the exact decomposition of each model pair's total gain into the
prior-transported and instance-alignment channels, at the primary
coarse-supergroup audit.  Right panel: the alignment channel broken out by
training-frequency tier.  Mirrors ``make_cifar_figures.py`` exactly (same
colors, fonts, and layout) so the two cross-domain studies read as one figure
family.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results", "text_lt_results.json")
OUTDIRS = [os.path.join(ROOT, "results", "figures"),
           os.path.join(ROOT, "manuscript", "figures")]

PRIOR_C = "#4C72B0"
ALIGN_C = "#C44E52"
TOTAL_C = "#55A868"


def main():
    with open(RESULTS, encoding="utf-8") as f:
        res = json.load(f)

    rows = [r for r in res["comparisons"] if r["prior_feature"] == "superclass"]
    labels = [f"{r['new'].replace('MLP-','')} vs {r['old'].replace('MLP-','')}"
              for r in rows]
    prior = [r["prior_gain"] for r in rows]
    align = [r["reasoning_gain"] for r in rows]
    total = [r["total_gain"] for r in rows]
    lo = [r["reasoning_ci"][0] for r in rows]
    hi = [r["reasoning_ci"][1] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.1))

    y = np.arange(len(rows))
    h = 0.26
    ax1.barh(y + h, prior, h, color=PRIOR_C, label=r"prior-transported $\Delta P$")
    ax1.barh(y, align, h, color=ALIGN_C, label=r"instance alignment $\Delta R$",
             xerr=[np.array(align) - np.array(lo), np.array(hi) - np.array(align)],
             error_kw=dict(ecolor="0.25", lw=1.1, capsize=3))
    ax1.barh(y - h, total, h, color=TOTAL_C, label=r"total $\Delta T$")
    ax1.axvline(0, color="0.3", lw=1)
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels)
    ax1.set_xlabel("quadratic-score gain")
    ax1.set_title("Exact decomposition (coarse-supergroup audit)", fontsize=11)
    ax1.legend(fontsize=8.5, loc="lower right", framealpha=0.95)
    ax1.grid(axis="x", alpha=0.25)

    tiers = res["per_tier_at_superclass_phi"]
    names = [t["tier"] for t in tiers if t["new"] == "MLP-CB"]
    short = [n.split(" (")[0] for n in names]
    cb = [t["alignment_gain"] for t in tiers if t["new"] == "MLP-CB"]
    drw = [t["alignment_gain"] for t in tiers if t["new"] == "MLP-DRW"]

    x = np.arange(len(short))
    w = 0.36
    ax2.bar(x - w / 2, cb, w, color="#8C8C8C", label="CB vs CE")
    if drw:
        ax2.bar(x + w / 2, drw, w, color=ALIGN_C, label="DRW vs CE")
    ax2.axhline(0, color="0.3", lw=1)
    ax2.set_xticks(x)
    ax2.set_xticklabels(short)
    ax2.set_ylabel(r"alignment gain $\Delta R$")
    ax2.set_title("Alignment gain by frequency tier", fontsize=11)
    ax2.legend(fontsize=8.5, framealpha=0.95)
    ax2.grid(axis="y", alpha=0.25)

    fig.tight_layout()
    for d in OUTDIRS:
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, "fig8_text_lt.png")
        fig.savefig(path, dpi=400, bbox_inches="tight")
        print(f"wrote {path}", flush=True)


if __name__ == "__main__":
    main()
