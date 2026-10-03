#!/usr/bin/env python3
"""Figure 2 of the CVPR paper: where each gain in the paper lives.

Two panels on separate axes, because the two quantities differ in scale by an order of
magnitude: TDE's group-level change is -0.18 of quadratic score while every case-level
gain in the paper is under 0.02. (a) splits each comparison's total gain into its
group-level and case-level parts; (b) zooms on the case-level part with its
image-clustered 95% interval, which is the panel the paper's argument rests on.

Every plotted value is read from a committed results file; nothing is typed in.

Run: python experiments/make_fig_cvpr_split.py
"""
from __future__ import annotations

import json
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = ROOT / "cvpr2027" / "figures"

# Validated with the dataviz skill's palette checker (light mode): categorical slots 1-2,
# CVD dE 24.7, normal-vision dE 33.6, both >= 3:1 against the surface.
GROUP = "#2a78d6"   # group-level part, dP
CASE = "#eb6834"    # case-level part, dR
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"


def load(name: str):
    return json.loads((RES / name).read_text())


def pick(rows, new, old):
    return next(r for r in rows if r["new"] == new and r["old"] == old)


def sgg_matched_quadratic(sgg):
    return next(r for r in sgg["comparisons"]
                if r["score"] == "brier" and r.get("regime") == "calibration-matched"
                and "prior_feature" not in r)


def clip_matched(cons):
    """The CLIP-vs-geometry pair with both models' confidence matched on held-out images --
    the comparison the paper reads, since the two differ visibly in confidence. Re-keyed to
    the field names the other rows use."""
    r = next(r for r in cons["rows"] if r["name"] == "VISUAL vs SPATIAL cal-both (audit half)")
    return {"total_gain": r["total"], "prior_gain": r["prior"],
            "reasoning_gain": r["reasoning"], "reasoning_ci": r["reasoning_ci"]}


def main() -> None:
    vg = load("antisymmetric_results.json")["comparisons"]
    vgv = load("vg_visual_results.json")["comparisons"]
    sgg = load("sgg_audit_motifs.json")

    rows = [
        ("MLP-CLASS vs FREQ\n(class pair only)", pick(vg, "MLP-CLASS", "FREQ")),
        ("+box geometry vs MLP-CLASS", pick(vg, "MLP-SPATIAL", "MLP-CLASS")),
        ("CLIP crops vs geometry\n(matched)", clip_matched(load("vg_prior_consequence.json"))),
        ("TDE vs MOTIFS\n(released, matched)", sgg_matched_quadratic(sgg)),
    ]
    labels = [r[0] for r in rows]
    T = [r[1]["total_gain"] for r in rows]
    P = [r[1]["prior_gain"] for r in rows]
    R = [r[1]["reasoning_gain"] for r in rows]
    lo = [r[1]["reasoning_ci"][0] for r in rows]
    hi = [r[1]["reasoning_ci"][1] for r in rows]

    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 7.5, "axes.edgecolor": MUTED,
        "axes.linewidth": 0.5, "xtick.color": MUTED, "ytick.color": INK,
        "xtick.major.width": 0.5, "ytick.major.width": 0, "axes.labelcolor": MUTED,
    })
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.9, 1.95),
                               gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.08})
    y = list(range(len(rows)))[::-1]
    h = 0.30

    for ax in (a, b):
        ax.grid(axis="x", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.axvline(0, color=MUTED, linewidth=0.6)

    # (a) composition: the two parts as bars, the total as a marker
    a.barh([v + h / 2 + 0.02 for v in y], P, height=h, color=GROUP, label=r"group-level $\widehat{\Delta P}$")
    a.barh([v - h / 2 - 0.02 for v in y], R, height=h, color=CASE, label=r"case-level $\widehat{\Delta R}$")
    a.scatter(T, y, marker="D", s=14, color=INK, zorder=3, linewidths=0,
              label=r"total $\widehat{\Delta T}$")
    a.set_yticks(y, labels)
    a.set_xlabel("quadratic-score gain")
    a.set_title("(a) Composition of each gain", loc="left", fontsize=8, color=INK)
    a.legend(loc="upper left", frameon=False, fontsize=6.8, handlelength=1.2,
             borderaxespad=0.2)

    # (b) the case-level part alone, with its image-clustered interval
    b.errorbar(R, y, xerr=[[r - l for r, l in zip(R, lo)], [u - r for r, u in zip(R, hi)]],
               fmt="o", color=CASE, ecolor=CASE, elinewidth=1.0, capsize=2.2, markersize=4.2,
               markeredgecolor="white", markeredgewidth=0.8, zorder=3)
    b.set_yticks(y, [""] * len(y))
    b.set_xlabel(r"case-level gain $\widehat{\Delta R}$, 95% CI (image-clustered)")
    b.set_title("(b) Case-level part, zoomed", loc="left", fontsize=8, color=INK)
    span = max(hi) * 1.12
    b.set_xlim(-0.004, span)
    # Two annotations carry meaning the reader would otherwise have to look up.
    b.annotate("exactly 0 (forced by Thm. 1)", (R[0], y[0]), xytext=(6, 0),
               textcoords="offset points", va="center", fontsize=6.6, color=MUTED)
    b.annotate("CI straddles 0", (hi[3], y[3]), xytext=(6, 0),
               textcoords="offset points", va="center", fontsize=6.6, color=MUTED)

    for ax in (a, b):
        ax.set_ylim(-0.6, len(rows) - 0.4)

    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig2_where_gains_live.{ext}", bbox_inches="tight",
                    dpi=300 if ext == "png" else None)
    print(f"wrote {OUT / 'fig2_where_gains_live.pdf'}")
    for lab, t, p, r, l, u in zip(labels, T, P, R, lo, hi):
        print(f"  {lab.splitlines()[0]:28s} dT={t:+.5f} dP={p:+.5f} dR={r:+.5f} [{l:+.5f},{u:+.5f}]")


if __name__ == "__main__":
    main()
