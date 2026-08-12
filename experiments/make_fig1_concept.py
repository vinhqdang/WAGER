"""Concept figure (Fig. 1) built on real pixels: two Visual Genome relations
from one audit cell, the label-crossing transport between them, and the exact
identity it produces. Replaces the earlier text-only flowchart.

Uses the same cached images as the dataset-samples figure.
Run: conda run -n py313 python experiments/make_fig1_concept.py
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, FancyBboxPatch
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", "samples")
OUTDIRS = [os.path.join(ROOT, "results", "figures"),
           os.path.join(ROOT, "manuscript", "figures")]

SUBJ_C = "#E24A33"
OBJ_C = "#348ABD"
OBS_C = "#1a7a3a"
TRA_C = "#b3541e"

VG = [
    dict(image_id=2394072, predicate="riding",
         sbox=(189, 96, 179, 222), obox=(149, 254, 306, 102)),
    dict(image_id=61564, predicate="carrying",
         sbox=(158, 432, 120, 414), obox=(22, 438, 371, 291)),
]


def draw_box(ax, box, color, label, anchor="top"):
    x, y, w, h = box
    ax.add_patch(mpatches.Rectangle((x, y), w, h, fill=False, edgecolor=color, lw=2.6))
    ty, va = (y + 3, "top") if anchor == "top" else (y + h - 3, "bottom")
    ax.text(x + 3, ty, label, color="white", fontsize=9, va=va, ha="left",
            bbox=dict(facecolor=color, edgecolor="none", pad=1.6, alpha=0.95))


def image_panel(ax, spec, title, title_color):
    im = Image.open(os.path.join(CACHE, f"vg_{spec['image_id']}.jpg")).convert("RGB")
    ax.imshow(im)
    draw_box(ax, spec["sbox"], SUBJ_C, "man", anchor="top")
    draw_box(ax, spec["obox"], OBJ_C, "surfboard", anchor="bottom")
    ax.set_title(title, fontsize=11.5, pad=5, color=title_color)
    ax.set_xticks([])
    ax.set_yticks([])


def main():
    fig = plt.figure(figsize=(12.5, 5.4))
    gs = fig.add_gridspec(2, 3, width_ratios=[1.0, 1.0, 1.28],
                          hspace=0.24, wspace=0.16,
                          left=0.015, right=0.985, top=0.845, bottom=0.03)

    axes_obs, axes_tra = [], []
    for r, spec in enumerate(VG):
        ax = fig.add_subplot(gs[r, 0])
        image_panel(ax, spec, f'observed label:  "{spec["predicate"]}"', OBS_C)
        axes_obs.append(ax)
    for r, spec in enumerate(VG):
        other = VG[1 - r]
        ax = fig.add_subplot(gs[r, 1])
        image_panel(ax, spec, f'transported label:  "{other["predicate"]}"', TRA_C)
        axes_tra.append(ax)

    # crossing arrows: each observed label travels to the OTHER image
    for r in range(2):
        con = ConnectionPatch(
            xyA=(1.01, 0.55), coordsA=axes_obs[r].transAxes,
            xyB=(-0.02, 0.55), coordsB=axes_tra[1 - r].transAxes,
            arrowstyle="-|>", mutation_scale=22, lw=2.2, color=TRA_C, zorder=5)
        fig.add_artist(con)

    # right column: the identity the construction produces
    axr = fig.add_subplot(gs[:, 2])
    axr.axis("off")
    axr.add_patch(FancyBboxPatch((0.02, 0.06), 0.96, 0.88,
                                 boxstyle="round,pad=0.02,rounding_size=0.03",
                                 transform=axr.transAxes, facecolor="#f4f4f2",
                                 edgecolor="#888888", lw=1.0))
    axr.text(0.5, 0.86, "score both frozen models under each assignment",
             transform=axr.transAxes, ha="center", fontsize=11)
    axr.text(0.5, 0.70,
             r"$\widehat{\Delta T}\;=\;\widehat{\Delta P}\;+\;\widehat{\Delta R}$",
             transform=axr.transAxes, ha="center", fontsize=19)
    axr.text(0.145, 0.565, "observed\ngain", transform=axr.transAxes, ha="center",
             fontsize=10.5, color="black")
    axr.text(0.46, 0.565, "prior-transported\ngain", transform=axr.transAxes,
             ha="center", fontsize=10.5, color=TRA_C)
    axr.text(0.80, 0.565, "instance-alignment\ngain", transform=axr.transAxes,
             ha="center", fontsize=10.5, color=OBS_C)
    axr.text(0.06, 0.42, r"$\widehat{\Delta P}$: what the gain would be if predictions"
             "\nmet labels only through the cell: the label\nhistogram of "
             r"$\phi=$ (man, surfboard) is unchanged.",
             transform=axr.transAxes, fontsize=10.5, va="top", color=TRA_C)
    axr.text(0.06, 0.20, r"$\widehat{\Delta R}$: the exact remainder, credited only"
             "\nwhen the right prediction meets the right\nimage. An antisymmetric "
             "U-statistic with CIs.",
             transform=axr.transAxes, fontsize=10.5, va="top", color=OBS_C)

    fig.suptitle("Two frozen models, one audit cell:  crossing labels within "
                 r"$\phi$ removes instance identity and nothing else",
                 fontsize=13.5, y=0.965)

    for d in OUTDIRS:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, "fig1_new_concept.png")
        fig.savefig(p, dpi=400)
        print(f"wrote {p}", flush=True)


if __name__ == "__main__":
    main()
