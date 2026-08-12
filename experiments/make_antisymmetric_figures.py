"""Paper figures for the redesigned antisymmetric WAGER algorithm."""
from __future__ import annotations

import json
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "manuscript", "figures")
os.makedirs(OUT, exist_ok=True)

BLUE = "#2563eb"
ORANGE = "#f59e0b"
SLATE = "#475569"
GREEN = "#059669"
RED = "#dc2626"


def _save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def concept():
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.set_xlim(0, 12); ax.set_ylim(0, 3.2); ax.axis("off")
    boxes = [
        (0.25, "Two frozen models", "prediction contrasts\n$h_i(y)$"),
        (3.2, "Match within $\\phi$", "same class-pair prior\ndifferent images"),
        (6.15, "Cross the labels", "observed pairing $-$\ncounterfactual pairing"),
        (9.1, "Exact attribution", "$\\Delta T=\\Delta P+\\Delta R$\nwith uncertainty"),
    ]
    colors = [SLATE, ORANGE, BLUE, GREEN]
    for (x, title, body), color in zip(boxes, colors):
        patch = FancyBboxPatch((x, 0.65), 2.35, 1.8, boxstyle="round,pad=0.08",
                               facecolor="#f8fafc", edgecolor=color, linewidth=2)
        ax.add_patch(patch)
        ax.text(x + 1.175, 1.92, title, ha="center", va="center", fontsize=12,
                fontweight="bold", color=color)
        ax.text(x + 1.175, 1.28, body, ha="center", va="center", fontsize=10)
    for x in [2.65, 5.6, 8.55]:
        ax.add_patch(FancyArrowPatch((x, 1.55), (x + 0.48, 1.55), arrowstyle="-|>",
                                     mutation_scale=16, linewidth=1.8, color="#64748b"))
    ax.text(6, 2.95, "WAGER: Within-cell Antisymmetric Gain Evaluation of Reasoning",
            ha="center", va="center", fontsize=15, fontweight="bold")
    _save(fig, "fig1_new_concept.png")


def pair_mechanism():
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    labels = ["image $i$", "image $j$"]
    for ax, crossed in zip(axes, [False, True]):
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
        ax.set_title("Observed assignment" if not crossed else "Within-cell transport",
                     fontsize=13, fontweight="bold")
        for r, lab in zip([0.72, 0.28], labels):
            ax.add_patch(FancyBboxPatch((0.05, r - .09), .28, .18, boxstyle="round,pad=.03",
                                        facecolor="#eff6ff", edgecolor=BLUE, linewidth=1.6))
            ax.text(.19, r, lab + "\nmodel gain vector", ha="center", va="center", fontsize=9)
        ax.add_patch(FancyBboxPatch((.68, .63), .25, .18, boxstyle="round,pad=.03",
                                    facecolor="#fff7ed", edgecolor=ORANGE, linewidth=1.6))
        ax.add_patch(FancyBboxPatch((.68, .19), .25, .18, boxstyle="round,pad=.03",
                                    facecolor="#fff7ed", edgecolor=ORANGE, linewidth=1.6))
        ax.text(.805, .72, "$y_i$", ha="center", va="center", fontsize=13)
        ax.text(.805, .28, "$y_j$", ha="center", va="center", fontsize=13)
        targets = [.28, .72] if crossed else [.72, .28]
        for source, target in zip([.72, .28], targets):
            ax.add_patch(FancyArrowPatch((.34, source), (.67, target), arrowstyle="-|>",
                                         mutation_scale=14, color=RED if crossed else GREEN,
                                         linewidth=2))
        ax.text(.5, .05, "same $\\phi$: prior distribution unchanged", ha="center", fontsize=9)
    fig.suptitle("Antisymmetrization compares correct and crossed prediction-label alignment",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    _save(fig, "fig2_pair_mechanism.png")


def simulation():
    with open(os.path.join(RESULTS, "antisymmetric_simulation.json"), encoding="utf-8") as f:
        d = json.load(f)
    rec = d["recovery"]
    beta = np.array([x["beta"] for x in rec])
    mean = np.array([x["mean"] for x in rec])
    sd = np.array([x["sd"] for x in rec])
    pvals = np.array(d["null_p_values"])
    null_r = np.array(d["null_reasoning"])

    fig, axes = plt.subplots(1, 3, figsize=(12.8, 3.5))
    axes[0].errorbar(beta, mean, yerr=sd, color=BLUE, marker="o", capsize=3)
    axes[0].set(xlabel="injected instance signal $\\beta$", ylabel="$\\widehat{\\Delta R}$",
                title="Signal recovery")
    axes[1].hist(pvals, bins=np.linspace(0, 1, 11), color=SLATE, edgecolor="white")
    axes[1].axhline(len(pvals) / 10, color=ORANGE, linestyle="--", linewidth=1.5)
    axes[1].set(xlabel="randomization $p$-value", ylabel="count", title="Null calibration")
    axes[2].hist(null_r, bins=20, color=BLUE, alpha=.85, edgecolor="white")
    axes[2].axvline(0, color=RED, linestyle="--", linewidth=1.5)
    axes[2].set(xlabel="null $\\widehat{\\Delta R}$", ylabel="count",
                title=f"Type-I at .05 = {d['null_type1_alpha_005']:.3f}")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.18)
    fig.tight_layout()
    _save(fig, "fig3_new_simulation.png")


def real_results():
    with open(os.path.join(RESULTS, "antisymmetric_results.json"), encoding="utf-8") as f:
        d = json.load(f)
    rows = d["comparisons"]
    use = [rows[1], rows[2], rows[3], rows[4], rows[5]]
    names = [
        "CLASS - FREQ", "SPATIAL - FREQ", "SPATIAL+ - FREQ",
        "SPATIAL - CLASS", "SPATIAL+ - SPATIAL",
    ]
    prior = np.array([r["prior_gain"] for r in use])
    reason = np.array([r["reasoning_gain"] for r in use])
    lo = np.array([r["reasoning_ci"][0] for r in use])
    hi = np.array([r["reasoning_ci"][1] for r in use])
    y = np.arange(len(use))

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.5), gridspec_kw={"width_ratios": [1.2, 1]})
    axes[0].barh(y, prior, color=SLATE, label="prior-transported")
    axes[0].barh(y, reason, left=prior, color=BLUE, label="instance alignment")
    axes[0].axvline(0, color="black", linewidth=.8)
    axes[0].set_yticks(y, names); axes[0].invert_yaxis()
    axes[0].set_xlabel("quadratic-score gain")
    axes[0].set_title("Exact gain decomposition", fontweight="bold")
    axes[0].legend(frameon=False, loc="lower right")

    axes[1].errorbar(reason, y, xerr=[reason - lo, hi - reason], fmt="o", color=BLUE,
                     ecolor=SLATE, capsize=3, markersize=6)
    axes[1].axvline(0, color=RED, linestyle="--", linewidth=1.2)
    axes[1].set_yticks(y, names); axes[1].invert_yaxis()
    axes[1].set_xlabel("within-cell alignment gain $\\widehat{\\Delta R}$")
    axes[1].set_title("Image-cluster-robust 95% CI", fontweight="bold")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", alpha=.18)
    fig.tight_layout()
    _save(fig, "fig4_new_results.png")


def main():
    concept(); pair_mechanism(); simulation(); real_results()
    print("wrote fig1_new_concept.png through fig4_new_results.png")


if __name__ == "__main__":
    main()
