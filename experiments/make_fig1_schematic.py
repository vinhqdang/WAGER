"""Concept figure (Fig. 1), drawn as a schematic rather than on real pixels.

The photographic version (two Visual Genome relations with their labels crossed)
is built by make_fig1_concept.py and now appears with the Visual Genome study in
the appendix.  A statistics readership meets the construction better through an
abstract diagram: the first figure of the paper should not commit it to a single
application domain.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIRS = [os.path.join(ROOT, "results", "figures"),
           os.path.join(ROOT, "manuscript", "figures")]

CELL_C = "#4d4d4d"
OBS_C = "#1a7a3a"
TRA_C = "#b3541e"
BAR_OLD = "#b8b8b8"
BAR_NEW = "#348ABD"

LABELS = ["$y_1$", "$y_2$", "$y_3$"]
# two cases in one cell: same phi, different observed label
CASES = [
    dict(name="case $i$", q0=[.34, .33, .33], q1=[.62, .22, .16], obs=0),
    dict(name="case $j$", q0=[.34, .33, .33], q1=[.20, .24, .56], obs=2),
]


def prediction_panel(ax, spec, title_color, title):
    x = np.arange(len(LABELS))
    ax.bar(x - 0.19, spec["q0"], width=0.36, color=BAR_OLD, label="$q_0$")
    ax.bar(x + 0.19, spec["q1"], width=0.36, color=BAR_NEW, label="$q_1$")
    ax.set_xticks(x)
    ax.set_xticklabels(LABELS, fontsize=10)
    ax.set_ylim(0, 0.78)
    ax.set_yticks([])
    ax.set_title(title, fontsize=10.5, color=title_color, pad=4)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="x", length=0)
    return ax


def main():
    fig = plt.figure(figsize=(13.6, 4.5))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.0, 1.45],
                          hspace=0.62, wspace=0.34,
                          left=0.045, right=0.975, top=0.80, bottom=0.08)

    # column 0: the observed assignment; column 1: after transport
    for r, spec in enumerate(CASES):
        ax = fig.add_subplot(gs[r, 0])
        prediction_panel(ax, spec, OBS_C,
                         f'{spec["name"]}:  observed label {LABELS[spec["obs"]]}')
        ax.plot([spec["obs"]], [0.735], marker="v", color=OBS_C, ms=9, clip_on=False)

    for r, spec in enumerate(CASES):
        other = CASES[1 - r]
        ax = fig.add_subplot(gs[r, 1])
        prediction_panel(ax, spec, TRA_C,
                         f'{spec["name"]}:  transported label {LABELS[other["obs"]]}')
        ax.plot([other["obs"]], [0.735], marker="v", color=TRA_C, ms=9, clip_on=False)

    # crossing arrows between the two columns
    for a, b in ((0.245, 0.60), (0.60, 0.245)):
        fig.add_artist(FancyArrowPatch((0.265, a), (0.475, b),
                                       transform=fig.transFigure,
                                       arrowstyle="-|>", mutation_scale=17,
                                       lw=2.0, color=TRA_C,
                                       connectionstyle="arc3,rad=0.0"))

    # column 2: the identity
    axr = fig.add_subplot(gs[:, 2]); axr.axis("off")
    axr.add_patch(FancyBboxPatch((0.02, 0.03), 0.96, 0.94,
                                 boxstyle="round,pad=0.02,rounding_size=0.03",
                                 transform=axr.transAxes, facecolor="#f5f5f3",
                                 edgecolor="#8a8a8a", lw=1.0))
    axr.text(0.5, 0.885, "score both frozen models under each assignment",
             transform=axr.transAxes, ha="center", fontsize=11)
    axr.text(0.5, 0.74, r"$\widehat{\Delta T}\;=\;\widehat{\Delta P}\;+\;\widehat{\Delta R}$",
             transform=axr.transAxes, ha="center", fontsize=20)
    axr.text(0.145, 0.605, "observed\ngain", transform=axr.transAxes,
             ha="center", fontsize=10, color="black")
    axr.text(0.475, 0.605, "transported\ngain", transform=axr.transAxes,
             ha="center", fontsize=10, color=TRA_C)
    axr.text(0.815, 0.605, "within-group\ncovariance gain", transform=axr.transAxes,
             ha="center", fontsize=10, color=OBS_C)
    axr.text(0.06, 0.45, r"$\widehat{\Delta P}$: the gain that survives relabelling."
             "\nThe cell and its label frequencies are\nunchanged, so this is the gain the new"
             "\nmodel earns over the group as a whole.",
             transform=axr.transAxes, fontsize=10.3, va="top", color=TRA_C)
    axr.text(0.06, 0.20, r"$\widehat{\Delta R}$: the exact remainder, credited"
             "\nonly when the right prediction meets\nthe right case. An antisymmetric"
             "\nU-statistic, with cluster-robust CIs.",
             transform=axr.transAxes, fontsize=10.3, va="top", color=OBS_C)

    fig.text(0.265, 0.925,
             r"Two cases in one cell $\{\phi=c\}$:  exchanging their labels removes case "
             r"identity and nothing else",
             ha="center", fontsize=13.5)
    fig.text(0.045, 0.845, "grey bars: old model $q_0$      blue bars: new model $q_1$",
             fontsize=9.5, color="#555555")

    for d in OUTDIRS:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "fig1_schematic.png")
        fig.savefig(p, dpi=400)
        print(f"wrote {p}", flush=True)


if __name__ == "__main__":
    main()
