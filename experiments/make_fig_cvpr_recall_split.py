#!/usr/bin/env python3
"""Figure 3 of the CVPR paper: where TDE's mean recall went, predicate by predicate.

Each bar is one predicate's change in recall@50 (graph constraint) from the MOTIFS
baseline to TDE, split into its group-level part and its case-level part with the
case-level part's image-clustered 95% interval. The hollow marker is the same
predicate's change under post-hoc logit adjustment of the baseline (tau = 1), the
operating-point control, which changes no within-cell ranking.

Every plotted value is read from a committed results file.

Run: python experiments/make_fig_cvpr_recall_split.py
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
NAMES = json.loads((ROOT / "data/vg_motifs/wager_sgg/predicate_names.json")
                   .read_text())["names"]
GROUP = "#2a78d6"   # same palette as Figure 2
CASE = "#eb6834"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
MIN_ABS = 0.09      # predicates whose recall@50 moved by at least this much


def main() -> None:
    tde = json.loads((RES / "sgg_recall_split.json").read_text())["results"]["gc@50"]
    la = json.loads((RES / "sgg_recall_split_la1_vs_none.json").read_text())["results"]["gc@50"]
    rows = []
    for q in range(1, 51):
        p = tde["per_predicate"][q - 1]
        if p and abs(p["total"]) >= MIN_ABS:
            rows.append((p["total"], q, p, la["per_predicate"][q - 1]["total"]))
    rows.sort()
    fig, ax = plt.subplots(figsize=(3.3, 0.165 * len(rows) + 0.75))
    for k, (_, q, p, la_tot) in enumerate(rows):
        g, c = p["group"], p["case"]
        ax.barh(k, g, color=GROUP, height=0.72, linewidth=0)
        ax.barh(k, c, left=g, color=CASE, height=0.72, linewidth=0)
        lo, hi = p["case_ci"]
        ax.plot([g + lo, g + hi], [k, k], color=INK, lw=0.7)
        ax.plot(la_tot, k, marker="D", ms=3.2, mfc="none", mec=INK, mew=0.7)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([NAMES[q] for _, q, _, _ in rows], fontsize=6.5)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xlabel("change in recall@50 (TDE $-$ MOTIFS)", fontsize=7)
    ax.tick_params(axis="x", labelsize=6.5)
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    handles = [plt.Rectangle((0, 0), 1, 1, color=GROUP),
               plt.Rectangle((0, 0), 1, 1, color=CASE),
               plt.Line2D([], [], ls="", marker="D", ms=3.2, mfc="none", mec=INK, mew=0.7)]
    ax.legend(handles, ["group-level", "case-level (95% CI)", "logit adjustment, total"],
              fontsize=6, frameon=False, loc="lower right")
    ax.set_ylim(-0.6, len(rows) - 0.4)
    fig.tight_layout(pad=0.3)
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig3_recall_by_predicate.{ext}", dpi=300)
    print(f"{len(rows)} predicates -> {OUT / 'fig3_recall_by_predicate.pdf'}")


if __name__ == "__main__":
    main()
