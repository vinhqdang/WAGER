"""Equivalence margins and minimal detectable effects for the TDE ranking null (R3-2).

"No measure detects a change in TDE's within-cell ranking" is a non-detection. This turns
it into a bounded statement. For each within-cell AUC contrast the image-bootstrap 95%
interval gives a standard error SE = (hi - lo) / (2 * 1.96); the minimal detectable effect
at 80% power and 5% two-sided size is 2.80 * SE; and an equivalence margin declared in
advance, one tenth of what box geometry buys over the class pair under the same weighting
(Sec. 6, the smallest effect the paper reads as meaningful), is tested by two one-sided
tests: TDE's ranking is equivalent to the baseline's within the margin when the 90%
interval lies inside it. The same is done for the mean-recall case-level part of TDE
against the operating-point control, with one tenth of TDE's mean-recall gain as margin.

Run: python experiments/sgg_equivalence.py
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = RES / "sgg_equivalence.json"
Z95, Z90, Z80 = 1.959964, 1.644854, 0.841621


def band(d, ci, margin):
    se = (ci[1] - ci[0]) / (2 * Z95)
    return {"difference": d, "ci95": list(ci), "se": se, "mde80": (Z95 + Z80) * se,
            "margin": margin, "ci90": [d - Z90 * se, d + Z90 * se],
            "equivalent": bool(d - Z90 * se > -margin and d + Z90 * se < margin),
            "largest_gain_not_excluded": ci[1]}


def main():
    rr = json.loads((RES / "sgg_rank_robustness.json").read_text())
    rows = {(r["new"], r["old"]): r for r in rr["sgg_auc"] + rr["pixel_auc"]}
    rows[("TDE", "la1")] = json.loads((RES / "sgg_auc_tde_la.json").read_text())["rows"][0]
    ref = rows[("MLP-SPATIAL-S", "MLP-CLASS-S")]
    out = {"reference": "0.1 x (geometry vs class-pair AUC gain, Sec. 6)", "auc": {}}
    for pair in (("TDE", "none"), ("TDE", "la1"), ("ietrans", "none")):
        out["auc"][f"{pair[0]} vs {pair[1]}"] = {}
        for wt in ("comparison", "relation"):
            a = rows[pair][f"all, {wt}"]
            out["auc"][f"{pair[0]} vs {pair[1]}"][wt] = band(a["difference"], a["ci"],
                                                             0.1 * ref[f"all, {wt}"]["difference"])
    m = json.loads((RES / "sgg_recall_split_TDE_vs_la1.json").read_text())["results"]["gc@50"]["mean_recall"]
    tot = json.loads((RES / "sgg_recall_split.json").read_text())["results"]["gc@50"]["mean_recall"]["total"]
    out["mR_case_TDE_vs_la1"] = band(m["case"], m["case_ci"], 0.1 * tot)
    out["mR_case_TDE_vs_la1"]["reference"] = "0.1 x TDE's mR@50 gain"
    for k, v in out["auc"].items():
        for wt, b in v.items():
            print(f"AUC {k:14s} {wt:10s} d {b['difference']:+.4f} se {b['se']:.4f} mde80 {b['mde80']:.4f} "
                  f"margin {b['margin']:.4f} ci90 [{b['ci90'][0]:+.4f},{b['ci90'][1]:+.4f}] equiv {b['equivalent']}")
    b = out["mR_case_TDE_vs_la1"]
    print(f"mR case TDE vs LA d {b['difference']:+.4f} se {b['se']:.4f} mde80 {b['mde80']:.4f} margin {b['margin']:.4f} "
          f"ci90 [{b['ci90'][0]:+.4f},{b['ci90'][1]:+.4f}] equiv {b['equivalent']}")
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
