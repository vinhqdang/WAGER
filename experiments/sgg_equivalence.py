"""Equivalence margins and minimal detectable effects for the TDE ranking null.

"No measure detects a change in TDE's within-cell ranking" is a non-detection. This turns
it into a bounded statement. For each within-cell AUC contrast, the 90% interval is a
percentile image-bootstrap interval (wager.rank.within_cell_auc_contrast, alpha=0.10, same
seed and n_boot as the stored 95% run, so the 90% interval is nested in the 95% one). The
equivalence margins are 5%, 10% and 25% of the geometry-vs-class AUC gain under the same
weighting (MLP-SPATIAL-S vs MLP-CLASS-S, Sec. 6). A pair is equivalent within a margin m
when its 90% interval lies strictly inside (-m, m) (two one-sided tests at level 5%).

The mean-recall case-level part of TDE against the operating-point control (TDE vs la1)
keeps a normal 90% interval, d +/- 1.645 SE with SE from the stored 95% width. Its
margins are 5%, 10% and 25% of the baseline's mean-recall case-level part, TDE vs none
(+0.0130 in results/sgg_recall_split.json).

Run: python experiments/sgg_equivalence.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.rank import within_cell_auc_contrast  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402

RES = ROOT / "results"
OUT = RES / "sgg_equivalence.json"
Z90 = 1.644854
SEED, N_BOOT = 0, 200                       # as auc_rows in run_sgg_rank_robustness.py
FRACTIONS = (0.05, 0.10, 0.25)
WEIGHTINGS = ("comparison", "relation")


def verdicts(lo, hi, ref):
    """Margin m = f * ref; equivalent iff the interval lies strictly inside (-m, m)."""
    out = {}
    for f in FRACTIONS:
        m = f * ref
        out[f"{round(100 * f)}%"] = {"margin": m, "equivalent": bool(lo > -m and hi < m)}
    return out


def main():
    Q, raw, y, phi, image, cal = RR.sgg_data()
    stored = json.loads((RES / "sgg_rank_robustness.json").read_text())
    tde_la = json.loads((RES / "sgg_auc_tde_la.json").read_text())["rows"][0]
    rows = {(r["new"], r["old"]): r for r in stored["sgg_auc"] + stored["pixel_auc"]}
    rows[("TDE", "la1")] = tde_la
    ref_row = rows[("MLP-SPATIAL-S", "MLP-CLASS-S")]

    out = {"seed": SEED, "n_boot": N_BOOT,
           "reference": "geometry vs class-pair AUC gain (MLP-SPATIAL-S vs MLP-CLASS-S, "
                        "same weighting); margins are 5%, 10%, 25% of it",
           "auc": {}}
    for new, old in (("TDE", "none"), ("TDE", "la1"), ("ietrans", "none")):
        key = f"{new} vs {old}"
        out["auc"][key] = {}
        for wt in WEIGHTINGS:
            c = within_cell_auc_contrast(raw[new], raw[old], y, phi, image, n_boot=N_BOOT,
                                         alpha=0.10, seed=SEED, weighting=wt)
            s = rows[(new, old)][f"all, {wt}"]
            ref = ref_row[f"all, {wt}"]["difference"]
            lo, hi = float(c.ci[0]), float(c.ci[1])
            b = {"difference": float(c.difference), "ci95": s["ci"], "ci90": [lo, hi],
                 "largest_change_excluded": max(abs(lo), abs(hi)),
                 "reference_gain": ref, "tost": verdicts(lo, hi, ref)}
            out["auc"][key][wt] = b
            print(f"AUC {key:14s} {wt:10s} d {b['difference']:+.5f} ci90 [{lo:+.5f},{hi:+.5f}] "
                  f"largest {b['largest_change_excluded']:.5f} "
                  + " ".join(f"{k} {v['equivalent']}" for k, v in b["tost"].items()), flush=True)

    m = json.loads((RES / "sgg_recall_split_TDE_vs_la1.json").read_text())["results"]["gc@50"]["mean_recall"]
    base = json.loads((RES / "sgg_recall_split.json").read_text())["results"]["gc@50"]["mean_recall"]["case"]
    d, (l95, h95) = m["case"], m["case_ci"]
    se = (h95 - l95) / (2 * 1.959964)
    lo, hi = d - Z90 * se, d + Z90 * se
    out["mR_case_TDE_vs_la1"] = {"difference": d, "ci95": [l95, h95], "se": se,
                                 "ci90": [lo, hi], "ci90_method": "normal",
                                 "largest_change_excluded": max(abs(lo), abs(hi)),
                                 "reference_gain": base,
                                 "reference": "TDE vs none, mean-recall case-level part, gc@50",
                                 "tost": verdicts(lo, hi, base)}
    b = out["mR_case_TDE_vs_la1"]
    print(f"mR case TDE vs LA d {d:+.5f} ci90 [{lo:+.5f},{hi:+.5f}] largest {b['largest_change_excluded']:.5f} "
          + " ".join(f"{k} {v['equivalent']}" for k, v in b["tost"].items()))
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
