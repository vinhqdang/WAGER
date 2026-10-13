"""Cross-fitted recalibration gains for the SGG matched split.

The matched split (run_sgg_rank_robustness.py) fits each model's recalibration on the
calibration half of the test images and splits the gain on the audit half. Here the
roles are swapped as well: fold A fits on the calibration half and splits on the audit
half (this reproduces the stored recalibration rows exactly, asserted below); fold B fits
on the audit half and splits on the calibration half. The cross-fit estimate averages the
two folds' total, group and case parts. Its case interval uses

    se = 0.5 * sqrt(se_A^2 + se_B^2),   se_X = half-width_X / 1.96,

which is valid because the two folds use disjoint images. Pairs: TDE, LA_1 and IETrans
against the baseline; families: one temperature per model, and temperature plus a
per-class bias per model; scores: quadratic (brier) and log.

Run: python experiments/run_sgg_crossfit.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from wager.antisymmetric import decompose_gain  # noqa: E402
import run_sgg_audit_wager as AU  # noqa: E402
import run_sgg_rank_robustness as RR  # noqa: E402

OUT = ROOT / "results/sgg_crossfit.json"
STORED = ROOT / "results/sgg_rank_robustness.json"
PAIRS = (("TDE", "none"), ("la1", "none"), ("ietrans", "none"))
MODELS = ("none", "TDE", "la1", "ietrans")
FAMILIES = ("temperature", "temperature + class bias")
SCORES = ("brier", "log")
Z = 1.96


def recalibrate(Q, y, fit, family):
    """Each model's recalibrated distribution over all relations, fitted on `fit` only."""
    out = {}
    for v in MODELS:
        if family == "temperature":
            T = AU.fit_temperature(Q[v][fit], y[fit])
            out[v] = AU.temp_scale(Q[v], T)
        else:
            L = np.log(np.clip(Q[v], RR.EPS, None))
            p = RR.fit_family(L[fit], y[fit], bias=True)
            out[v] = RR.apply_family(L, p, True)
    return out


def fold(Q, y, phi, image, fit, split):
    """Fit on `fit` images, split the gain on `split` images, for every pair/family/score."""
    res = {}
    for family in FAMILIES:
        R = recalibrate(Q, y, fit, family)
        for new, old in PAIRS:
            for sc in SCORES:
                with np.errstate(all="ignore"):
                    g = decompose_gain(R[new][split], R[old][split], y[split], phi[split],
                                       groups=image[split], score=sc)
                lo, hi = g.alignment_ci
                res[(new, family, sc)] = {
                    "total": float(g.total_gain), "group": float(g.prior_gain),
                    "case": float(g.alignment_gain), "case_ci": [float(lo), float(hi)],
                    "case_se": float((hi - lo) / 2 / Z),
                    "n_identified": int(g.n_identified), "n_total": int(g.n_total),
                }
    return res


def main():
    Q, _, y, phi, image, cal = RR.sgg_data()
    aud = ~cal
    A = fold(Q, y, phi, image, cal, aud)
    B = fold(Q, y, phi, image, aud, cal)

    # fold A must reproduce the stored matched-split recalibration rows exactly
    stored = {r["new"]: r for r in json.loads(STORED.read_text())["recalibration"]}
    for (new, family, sc), a in A.items():
        s = stored[new][f"{family}, {sc}"]
        for k in ("total", "group", "case"):
            assert a[k] == s[k], f"fold A {new} {family} {sc} {k}: {a[k]!r} != {s[k]!r}"
        assert a["case_ci"] == s["case_ci"], f"fold A {new} {family} {sc} case_ci mismatch"

    rows = []
    print(f"fold A: fit cal ({int(cal.sum())} relations), split audit; "
          f"fold B: fit audit, split cal. Case parts with 95% CI.")
    print(f"{'pair':<16}{'family':<26}{'score':<7}"
          f"{'fold A case [CI]':<36}{'fold B case [CI]':<36}"
          f"{'cross-fit total':>16}{'group':>11}{'case [CI]':>36}")
    for new, old in PAIRS:
        for family in FAMILIES:
            for sc in SCORES:
                a, b = A[(new, family, sc)], B[(new, family, sc)]
                se = 0.5 * np.sqrt(a["case_se"] ** 2 + b["case_se"] ** 2)
                case = (a["case"] + b["case"]) / 2
                cf = {"total": (a["total"] + b["total"]) / 2,
                      "group": (a["group"] + b["group"]) / 2,
                      "case": case, "case_se": float(se),
                      "case_ci": [float(case - Z * se), float(case + Z * se)]}
                rows.append({"new": new, "old": old, "family": family, "score": sc,
                             "fold_A": a, "fold_B": b, "cross_fit": cf})
                fa = f"{a['case']:+.5f} [{a['case_ci'][0]:+.5f},{a['case_ci'][1]:+.5f}]"
                fb = f"{b['case']:+.5f} [{b['case_ci'][0]:+.5f},{b['case_ci'][1]:+.5f}]"
                fc = f"{cf['case']:+.5f} [{cf['case_ci'][0]:+.5f},{cf['case_ci'][1]:+.5f}]"
                print(f"{new + ' vs ' + old:<16}{family:<26}{sc:<7}{fa:<36}{fb:<36}"
                      f"{cf['total']:>+16.5f}{cf['group']:>+11.5f}{fc:>36}")

    out = {"z": Z, "n_cal_images": int(len(np.unique(image[cal]))),
           "n_audit_images": int(len(np.unique(image[aud]))), "rows": rows}
    OUT.write_text(json.dumps(out, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
